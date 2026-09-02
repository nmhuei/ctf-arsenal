#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct Step {
    int target_id;
    int target_pos;
    std::vector<double> weights; // llama_sample_dist receives float p, discrete_distribution stores normalized doubles
    std::discrete_distribution<int> dist;
};

struct RawTok { int id; float logit; float p; };

static bool read_exact(std::ifstream &f, char *buf, size_t n){ f.read(buf, n); return (bool)f; }

std::vector<Step> load_case(const std::string &path){
    std::ifstream f(path, std::ios::binary);
    if(!f) throw std::runtime_error("open failed: "+path);
    char magic[4]; if(!read_exact(f, magic, 4) || std::memcmp(magic,"LGTS",4)!=0) throw std::runtime_error("bad magic");
    uint32_t nsteps, nvocab, top_k; float temp, top_p, min_p;
    read_exact(f,(char*)&nsteps,4); read_exact(f,(char*)&nvocab,4); read_exact(f,(char*)&temp,4); read_exact(f,(char*)&top_p,4); read_exact(f,(char*)&min_p,4); read_exact(f,(char*)&top_k,4);
    std::cerr << "case " << path << " steps=" << nsteps << " vocab=" << nvocab << " temp=" << temp << " top_k=" << top_k << " top_p=" << top_p << " min_p=" << min_p << "\n";
    std::vector<Step> steps;
    steps.reserve(nsteps);
    std::vector<float> logits(nvocab);
    for(uint32_t s=0;s<nsteps;s++){
        int target; read_exact(f,(char*)&target,4);
        read_exact(f,(char*)logits.data(), sizeof(float)*nvocab);
        std::vector<RawTok> arr; arr.reserve(nvocab);
        for(uint32_t i=0;i<nvocab;i++) arr.push_back({(int)i, logits[i] / temp, 0.0f});
        if(top_k > 0 && top_k < arr.size()){
            std::partial_sort(arr.begin(), arr.begin()+top_k, arr.end(), [](const RawTok&a,const RawTok&b){return a.logit>b.logit;});
            arr.resize(top_k);
        }
        std::sort(arr.begin(), arr.end(), [](const RawTok&a,const RawTok&b){return a.logit>b.logit;});
        if(top_p < 1.0f || min_p > 0.0f){
            // Apply softmax first for filters, matching llama.cpp enough for allowed-set tests.
            float max_l=arr[0].logit, cum=0.0f;
            for(auto &x: arr){ x.p=std::exp(x.logit-max_l); cum += x.p; }
            for(auto &x: arr) x.p /= cum;
            if(top_p < 1.0f){
                float c=0.0f; size_t keep=arr.size();
                for(size_t i=0;i<arr.size();i++){ c += arr[i].p; if(c >= top_p){ keep=i+1; break; } }
                arr.resize(keep);
            }
            if(min_p > 0.0f){
                float pmax=arr.empty()?0.0f:arr[0].p;
                size_t keep=0;
                for(size_t i=0;i<arr.size();i++) if(arr[i].p >= pmax*min_p) keep=i+1; else break;
                arr.resize(keep);
            }
            // llama_dist softmaxes again after filters; recompute below.
        }
        int target_pos=-1;
        for(size_t i=0;i<arr.size();i++) if(arr[i].id==target){ target_pos=(int)i; break; }
        if(target_pos < 0){ std::cerr << "target not in candidates step "<<s<<" id="<<target<<"\n"; }
        float max_l=arr[0].logit, cum=0.0f;
        std::vector<float> pf(arr.size());
        for(size_t i=0;i<arr.size();i++){ pf[i]=std::exp(arr[i].logit-max_l); cum += pf[i]; }
        std::vector<double> w(arr.size());
        for(size_t i=0;i<arr.size();i++){ pf[i] /= cum; w[i] = (double)pf[i]; }
        Step st; st.target_id=target; st.target_pos=target_pos; st.weights=std::move(w); st.dist=std::discrete_distribution<int>(st.weights.begin(), st.weights.end());
        std::cerr << " step " << s << " target=" << target << " pos=" << target_pos << " n=" << st.weights.size() << "\n";
        steps.push_back(std::move(st));
    }
    return steps;
}

std::vector<int> simulate(const std::vector<Step>& steps, uint32_t seed){
    std::mt19937 rng(seed);
    std::vector<int> out; out.reserve(steps.size());
    for(auto &st: steps){ auto d=st.dist; out.push_back(d(rng)); }
    return out;
}

int main(int argc, char**argv){
    if(argc < 4){ std::cerr << "usage: "<<argv[0]<<" case.bin start end [threads] [debug_seed]\n"; return 2; }
    std::string path=argv[1]; uint64_t start=std::stoull(argv[2]); uint64_t end=std::stoull(argv[3]);
    int threads = argc>=5 ? std::stoi(argv[4]) : 1;
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif
    auto steps=load_case(path);
    if(argc>=6){ uint32_t seed=(uint32_t)std::stoul(argv[5]); auto v=simulate(steps,seed); std::cout << "debug_seed "<<seed<<":"; for(int x:v) std::cout << " "<<x; std::cout << "\n"; }
    std::atomic<bool> found(false); std::atomic<uint64_t> checked(0); uint32_t found_seed=0;
    auto t0=std::chrono::steady_clock::now();
#pragma omp parallel
    {
        auto local = steps; // each thread has own dist objects
#pragma omp for schedule(static)
        for(uint64_t s=start; s<end; ++s){
            if(found.load(std::memory_order_relaxed)) continue;
            std::mt19937 rng((uint32_t)s);
            bool ok=true;
            for(size_t i=0;i<local.size();i++){
                int val=local[i].dist(rng);
                if(val != local[i].target_pos){ ok=false; break; }
            }
            if(ok){ found_seed=(uint32_t)s; found.store(true); }
            uint64_t c=++checked;
            if((c & ((1ULL<<24)-1))==0){
                auto dt=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
#pragma omp critical
                std::cerr << "checked "<<c<<" rate "<<(c/dt/1e6)<<" M/s\n";
            }
        }
    }
    if(found.load()) { std::cout << "FOUND " << found_seed << "\n"; return 0; }
    std::cout << "NOT_FOUND " << start << " " << end << " checked=" << checked.load() << "\n";
    return 1;
}

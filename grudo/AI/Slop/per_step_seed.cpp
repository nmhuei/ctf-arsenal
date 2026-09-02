#include <bits/stdc++.h>
using namespace std;
struct Step{int target_pos; vector<double>w; std::discrete_distribution<int> dist;};
vector<Step> load(const string&path,int topk=-1){
 ifstream f(path,ios::binary); char m[4]; f.read(m,4); uint32_t n,nv,tk; float temp,tp,mp; f.read((char*)&n,4);f.read((char*)&nv,4);f.read((char*)&temp,4);f.read((char*)&tp,4);f.read((char*)&mp,4);f.read((char*)&tk,4);
 vector<Step> steps; vector<float> logits(nv);
 for(uint32_t s=0;s<n;s++){int target; f.read((char*)&target,4); f.read((char*)logits.data(),4*nv); vector<int> idx(nv); iota(idx.begin(),idx.end(),0); sort(idx.begin(),idx.end(),[&](int a,int b){return logits[a]>logits[b];}); if(topk>0 && topk<(int)idx.size()) idx.resize(topk); int pos=-1; for(int i=0;i<(int)idx.size();i++) if(idx[i]==target){pos=i;break;} double mx=logits[idx[0]], sum=0; vector<double>w(idx.size()); for(int i=0;i<(int)idx.size();i++){w[i]=exp((double)logits[idx[i]]-mx); sum+=w[i];} for(auto &x:w)x/=sum; Step st;st.target_pos=pos;st.w=w;st.dist=discrete_distribution<int>(w.begin(),w.end()); steps.push_back(move(st)); }
 return steps;
}
int main(int argc,char**argv){ if(argc<2){cerr<<"usage case [topk]\n";return 1;} int topk=argc>2?stoi(argv[2]):-1; auto steps=load(argv[1],topk); cout<<argv[1]<<" topk="<<topk<<"\n"; for(size_t i=0;i<steps.size();i++){cout<<"step "<<i<<" target_pos "<<steps[i].target_pos<<" cands"; for(int seed=0;seed<256;seed++){mt19937 rng(seed); auto d=steps[i].dist; int v=d(rng); if(v==steps[i].target_pos) cout<<" "<<seed;} cout<<"\n";} }

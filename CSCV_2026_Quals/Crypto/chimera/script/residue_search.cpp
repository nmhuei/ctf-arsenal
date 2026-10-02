
#include <gmpxx.h>
#include <iostream>
#include <fstream>
#include <chrono>
#include <cmath>
using namespace std;
mpz_class centered_quotient(const mpz_class& a,const mpz_class& b){
 mpz_class q,r; mpz_fdiv_qr(q.get_mpz_t(),r.get_mpz_t(),a.get_mpz_t(),b.get_mpz_t());
 if(2*r>b) ++q; return q;
}
int main(int argc,char**argv){
 if(argc!=5){cerr<<"usage: residue_search N start end output\n";return 2;}
 mpz_class N(argv[1]), M("31721752939659896617792337171084495768312741523809821454149295955199893657462682088273"), invN,r,s,invs,u,t,v;
 unsigned long begin=stoul(argv[2]),end=stoul(argv[3]);
 mpz_invert(invN.get_mpz_t(),N.get_mpz_t(),M.get_mpz_t());
 mpz_class g=17;mpz_powm_ui(r.get_mpz_t(),g.get_mpz_t(),begin,M.get_mpz_t());
 mpz_invert(s.get_mpz_t(),r.get_mpz_t(),M.get_mpz_t());s=(s*N)%M;
 invs=(invN*r)%M;u=(-r*invs)%M;if(u<0)u+=M;
 mpz_class rootM;mpz_sqrt(rootM.get_mpz_t(),M.get_mpz_t());
 mpz_class X=(mpz_class(1)<<384)/M+1;
 auto started=chrono::steady_clock::now();
 unsigned long skipped=0;
 for(unsigned long a=begin;a<end;a++){
  mpz_class r0=M,r1=u,t0=0,t1=1,q,tmp;
  while(r1>rootM){
   mpz_fdiv_qr(q.get_mpz_t(),tmp.get_mpz_t(),r0.get_mpz_t(),r1.get_mpz_t());
   r0=r1;r1=tmp;tmp=t0-q*t1;t0=t1;t1=tmp;
  }
  // A bounded solution has coefficient errors less than 1/2 in this basis.
  if(r1==0 || 2*X*(abs(r0)+abs(t0))>=M || 2*X*(abs(r1)+abs(t1))>=M){
   ++skipped;
  }else{
   t=(N-r*s)/M;v=(t*invs)%M;
   mpz_class det=r0*t1-r1*t0;
   mpz_class c0,c1;
   if(det>0){c0=centered_quotient(v*t1,M);c1=centered_quotient(-v*t0,M);}
   else {c0=centered_quotient(-v*t1,M);c1=centered_quotient(v*t0,M);}
   mpz_class k=v-c0*r0-c1*r1,l=-c0*t0-c1*t1;
   if(k>=0 && l>=0 && k<X && l<X){
    mpz_class p=r+M*k,qq=s+M*l;
    if(p*qq==N){
     ofstream out(argv[4]);out<<"{\"a\": "<<a<<", \"p\": "<<p<<", \"q\": "<<qq<<"}\n";
     cout<<"FOUND a="<<a<<" p="<<p<<" q="<<qq<<endl;return 0;
    }
   }
  }
  r=(17*r)%M;invs=(17*invs)%M;u=(289*u)%M;
  // Divide s by 17 modulo M using only small-integer operations.
  unsigned long sm=mpz_fdiv_ui(s.get_mpz_t(),17), mm=mpz_fdiv_ui(M.get_mpz_t(),17);
  unsigned long add=0;while((sm+add*mm)%17)++add;
  s=(s+add*M)/17;
  if((a-begin+1)%1000000==0){
   double sec=chrono::duration<double>(chrono::steady_clock::now()-started).count();
   cerr<<"a="<<a+1<<" speed="<<(a-begin+1)/sec<<"/s skipped="<<skipped<<endl;
  }
 }
 cerr<<"done skipped="<<skipped<<endl;
 return 1;
}

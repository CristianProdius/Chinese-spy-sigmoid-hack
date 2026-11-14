// brute4: search sets = BASE ∪ {4 extra indices from 0..1199} whose sha256(",".join(sorted)) has
// a 3-byte tail equal to some seal tail and decodes that seal to printable ASCII.
// usage: brute4 tags.hex base_csv(or "-") nthreads
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <pthread.h>
#define N 1200
#define NT 2200
static unsigned char tags[NT][32];
static int base[64], nb=0;
static int tailidx[1<<24]; // maps 3-byte tail -> seal index+1 (first), collisions handled via chain
static int nxt[NT];
static unsigned char pre[NT][8]; static int preidx[1<<24]; static int prenxt[NT];
static void add_pre(int ti){const char*S="SIGMOID_"; for(int i=0;i<8;i++) pre[ti][i]=tags[ti][i]^S[i]; unsigned k=(pre[ti][0]<<16)|(pre[ti][1]<<8)|pre[ti][2]; prenxt[ti]=preidx[k]; preidx[k]=ti+1;}
static int nthreads;
static void add_tail(int ti){unsigned k=(tags[ti][29]<<16)|(tags[ti][30]<<8)|tags[ti][31]; nxt[ti]=tailidx[k]; tailidx[k]=ti+1;}
static int check(unsigned char*m){ { unsigned k=(m[0]<<16)|(m[1]<<8)|m[2]; for(int ti=preidx[k]; ti; ti=prenxt[ti-1]) if(!memcmp(pre[ti-1],m,8)){ unsigned char dec[32]; for(int i=0;i<32;i++) dec[i]=tags[ti-1][i]^m[i]; printf("HIT-PREFIX seal=%d msg=%.32s\n",ti-1,dec); fflush(stdout); return 1; } }unsigned k=(m[29]<<16)|(m[30]<<8)|m[31]; for(int ti=tailidx[k]; ti; ti=nxt[ti-1]){ unsigned char dec[32]; int len=32; for(int i=0;i<32;i++) dec[i]=tags[ti-1][i]^m[i]; while(len>0&&dec[len-1]==0) len--; if(len<4) continue; int ok=1; for(int i=0;i<len;i++) if(dec[i]<32||dec[i]>126){ok=0;break;} if(ok){ printf("HIT seal=%d msg=%.*s\n",ti-1,len,dec); fflush(stdout); return 1;} } return 0;}
static void build(char*buf,int*ex,int ne){int all[70],n=0; for(int i=0;i<nb;i++) all[n++]=base[i]; for(int i=0;i<ne;i++) all[n++]=ex[i]; // insertion sort
 for(int i=1;i<n;i++){int v=all[i],j=i-1; while(j>=0&&all[j]>v){all[j+1]=all[j]; j--;} all[j+1]=v;} char*p=buf; for(int i=0;i<n;i++){ if(i) *p++=','; p+=sprintf(p,"%d",all[i]);} *p=0;}
static int inbase(int x){for(int i=0;i<nb;i++) if(base[i]==x) return 1; return 0;}
static void* worker(void*arg){long id=(long)arg; char buf[512]; unsigned char m[32]; int ex[4]; long cnt=0;
 for(int a=(int)id;a<N;a+=nthreads){ if(inbase(a)) continue; for(int b=a+1;b<N;b++){ if(inbase(b)) continue; for(int c=b+1;c<N;c++){ if(inbase(c)) continue; for(int d=c+1;d<N;d++){ if(inbase(d)) continue; ex[0]=a;ex[1]=b;ex[2]=c;ex[3]=d; build(buf,ex,4); SHA256((unsigned char*)buf,strlen(buf),m); if(check(m)) printf("  set extras=%d,%d,%d,%d\n",a,b,c,d); cnt++; }}} if(id==0&&a%40==0){fprintf(stderr,"progress a=%d\n",a);} }
 return NULL;}
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"r"); char line[80]; int n=0; while(fgets(line,80,f)&&n<NT){ for(int i=0;i<32;i++){ unsigned v; sscanf(line+2*i,"%2x",&v); tags[n][i]=v;} n++; } fclose(f);
 if(strcmp(argv[2],"-")){ char*s=strdup(argv[2]); for(char*t=strtok(s,",");t;t=strtok(NULL,",")) base[nb++]=atoi(t);} nthreads=atoi(argv[3]);
 memset(tailidx,0,sizeof tailidx); memset(preidx,0,sizeof preidx); for(int i=0;i<n;i++){ add_tail(i); add_pre(i);}
 pthread_t th[64]; for(long i=0;i<nthreads;i++) pthread_create(&th[i],NULL,worker,(void*)i); for(int i=0;i<nthreads;i++) pthread_join(th[i],NULL); printf("done base=%s\n",argv[2]); return 0;}

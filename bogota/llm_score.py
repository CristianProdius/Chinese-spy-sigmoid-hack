"""Score every review's rating with Qwen2.5-72B via a local vLLM OpenAI endpoint.
Outputs scores.json: {"trusted": [[idx, rating, E[pred], P(1..5)], ...], "samples": [...]}"""
import json, math, asyncio, sys
from openai import AsyncOpenAI
cli=AsyncOpenAI(base_url="http://127.0.0.1:8011/v1", api_key="x")
d=json.load(open('reviews.json'))
SYS=("You are a strict rating classifier for Amazon musical-instrument reviews. "
     "Given a review summary and text, output ONLY the star rating the author most likely gave, a single digit 1-5.")
def prompt(r): return f"Summary: {r['summary']}\nReview: {r['review_text'][:2500]}\n\nStar rating (1-5):"
sem=asyncio.Semaphore(64)
async def one(r):
    async with sem:
        res=await cli.chat.completions.create(model="qwen72",messages=[{"role":"system","content":SYS},{"role":"user","content":prompt(r)}],max_tokens=1,temperature=0,logprobs=True,top_logprobs=10)
        lp=res.choices[0].logprobs.content[0].top_logprobs
        p=[0.0]*5
        for t in lp:
            s=t.token.strip()
            if s in "12345" and len(s)==1: p[int(s)-1]+=math.exp(t.logprob)
        z=sum(p) or 1.0; p=[x/z for x in p]
        return [sum((i+1)*x for i,x in enumerate(p)), p]
async def main():
    out={}
    for key,R in (("trusted",d['trusted_reference']),("samples",d['samples'])):
        rs=await asyncio.gather(*[one(r) for r in R])
        out[key]=[[r.get('sample_index',i), r['rating'], e, p] for i,(r,(e,p)) in enumerate(zip(R,rs))]
        print(key,"done",file=sys.stderr)
    json.dump(out,open('scores.json','w'))
asyncio.run(main())

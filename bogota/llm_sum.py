import json, math, asyncio
from openai import AsyncOpenAI
cli=AsyncOpenAI(base_url="http://127.0.0.1:8011/v1", api_key="x")
d=json.load(open('reviews.json'))
Q={
 'sum_rating':("Given only the title of an Amazon musical-instrument review, output the star rating (1-5) the author most likely gave. Output a single digit.", lambda r: f"Title: {r['summary']}\n\nStar rating (1-5):", "12345"),
 'match':("You check whether a review title and the review body were written together. Answer YES if the title plausibly belongs to this body (same product, same sentiment). Answer NO if the title clearly contradicts the body or is about a different product. Answer only YES or NO.", lambda r: f"Title: {r['summary']}\nBody: {r['review_text'][:1500]}\n\nAnswer:", None),
 'ontopic':("Answer YES if this text is a customer review of a musical instrument or music gear product (strings, picks, cables, stands, pedals, mics, tuners, etc). Answer NO otherwise. Answer only YES or NO.", lambda r: f"Text: {r['review_text'][:1500]}\n\nAnswer:", None),
}
sem=asyncio.Semaphore(96)
async def one(r,sysm,fmt,digits):
    async with sem:
        res=await cli.chat.completions.create(model="qwen72",messages=[{"role":"system","content":sysm},{"role":"user","content":fmt(r)}],max_tokens=1,temperature=0,logprobs=True,top_logprobs=10)
        lp=res.choices[0].logprobs.content[0].top_logprobs
        if digits:
            p=[0.0]*5
            for t in lp:
                s=t.token.strip()
                if len(s)==1 and s in digits: p[int(s)-1]+=math.exp(t.logprob)
            z=sum(p) or 1; return sum((i+1)*x/z for i,x in enumerate(p))
        return sum(math.exp(t.logprob) for t in lp if t.token.strip().upper().startswith("YES"))
async def main():
    out={}
    for key,R in (("trusted",d['trusted_reference']),("samples",d['samples'])):
        cols={}
        for q,(sysm,fmt,digits) in Q.items():
            cols[q]=await asyncio.gather(*[one(r,sysm,fmt,digits) for r in R])
        out[key]=[[r.get('sample_index',i), r['rating']]+[cols[q][i] for q in Q] for i,r in enumerate(R)]
    json.dump({'cols':['idx','rating']+list(Q),'data':out},open('sum.json','w'))
asyncio.run(main())

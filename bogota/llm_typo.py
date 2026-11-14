import json, math, asyncio, sys
from openai import AsyncOpenAI
cli=AsyncOpenAI(base_url="http://127.0.0.1:8011/v1", api_key="x")
d=json.load(open('reviews.json'))
SYS=("You are a meticulous copy editor. You will see the opening of a product review. "
     "Answer YES if the first sentence contains a misspelling, typo, swapped/missing/extra letter, "
     "wrong word, or an unusual character. Answer NO if it reads as normal English (brand names, slang and missing punctuation are fine). Answer only YES or NO.")
sem=asyncio.Semaphore(64)
async def one(r):
    async with sem:
        res=await cli.chat.completions.create(model="qwen72",messages=[{"role":"system","content":SYS},{"role":"user","content":"Opening: "+r['review_text'][:120]+"\n\nAnswer:"}],max_tokens=1,temperature=0,logprobs=True,top_logprobs=10)
        p=0.0
        for t in res.choices[0].logprobs.content[0].top_logprobs:
            if t.token.strip().upper().startswith("YES"): p+=math.exp(t.logprob)
        return p
async def main():
    out={}
    for key,R in (("trusted",d['trusted_reference']),("samples",d['samples'])):
        ps=await asyncio.gather(*[one(r) for r in R])
        out[key]=[[r.get('sample_index',i),p] for i,(r,p) in enumerate(zip(R,ps))]
    json.dump(out,open('typo.json','w'))
asyncio.run(main())

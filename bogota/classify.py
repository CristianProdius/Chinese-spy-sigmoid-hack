import json, numpy as np, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
d=json.load(open('data/reviews.json'))
T=d['trusted_reference']; S=d['samples']
txt=lambda r: r['summary']+" . "+r['review_text']
vec=TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True)
Xt=vec.fit_transform([txt(r) for r in T]); yt=np.array([r['rating'] for r in T])
clf=LogisticRegression(C=5,max_iter=2000,class_weight='balanced')
cv=cross_val_predict(clf,Xt,yt,cv=5,method='predict_proba')
ev=(cv*np.arange(1,6)).sum(1)
print("trusted CV: mean|E[r]-r| =", np.abs(ev-yt).mean().round(3), " exact-acc", (cv.argmax(1)+1==yt).mean().round(3))
clf.fit(Xt,yt)
Xs=vec.transform([txt(r) for r in S]); ps=clf.predict_proba(Xs); es=(ps*np.arange(1,6)).sum(1)
ys=np.array([r['rating'] for r in S])
gap=ys-es
order=np.argsort(-np.abs(gap))
print("\nmost rating/text-inconsistent samples (idx, rating, E[pred], P(rating)):")
for i in order[:40]:
    print(S[i]['sample_index'], ys[i], round(es[i],2), round(ps[i][ys[i]-1],3), "|", S[i]['summary'][:40], "|", S[i]['review_text'][:90].replace("\n"," "))
np.save('gap.npy', gap); json.dump([int(S[i]['sample_index']) for i in order], open('rank.json','w'))

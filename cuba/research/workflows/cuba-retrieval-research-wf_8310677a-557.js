export const meta = {
  name: 'cuba-retrieval-research',
  description: 'Deep research: tiny, fast, accurate chapter retrieval (Hit@3>=0.80) under size/latency/no-PyTorch limits',
  phases: [
    { title: 'Research', detail: '5 parallel researchers, one angle each, web-backed' },
    { title: 'Synthesize', detail: 'rank techniques into a build plan' },
    { title: 'Critique', detail: 'adversarial review of the plan' },
  ],
}

const TASK = `
TASK ("If you know, you know!" - hackathon retrieval challenge, Cuba theme):
Build a document retrieval system over 1552 chapter-sized English documents. For each question (a "slip of paper" from a cigar roller, written from memory - e.g. "the part where the Spaniards first saw people smoking rolled leaves", "the sugar figures for Matanzas in the 1890s", "the traveller who described the tobacco fields of Vuelta Abajo") return the 3 best doc ids. Pass requires ALL of:
- Hit@3 >= 0.80 on a HIDDEN question set (public sample questions + answers are given for tuning).
- Size: main.py + index/ <= a size limit (in limits.json; not yet seen - assume somewhere 10-200 MB), model weights included.
- p95 latency of one search() call <= a limit (not yet seen - assume 10-200 ms), on a SINGLE CPU thread.
- Load time of Retriever(index_dir) <= a limit (assume 1-10 s). Corpus is ABSENT at grading time, so the index must be prebuilt.
- At query time: only libraries in the grader's requirements.txt (not yet seen; assume numpy for sure, maybe scipy / scikit-learn / onnxruntime / tokenizers / rank_bm25; definitely NO PyTorch, no network). index/ may hold any data format (.npy/.npz/.json/.onnx/.safetensors/faiss/hnswlib/tokenizer.json) but no code files.
- Build-time: anything goes (any machine, any tools, any models). We have an H100 (but currently only ~8 GB GPU free; Qwen2.5-72B-Instruct-AWQ and Qwen2.5-32B-Instruct-AWQ are cached there) plus a big CPU box.

CORPUS: chapters of 21 Project Gutenberg books about Cuba (1845-1920: travel accounts, histories, sugar/tobacco reports), sections of the 2002 Library of Congress "Cuba: A Country Study", chapters of Humboldt's "The Island of Cuba" (1856) as a deliberately NOISY OCR scan, and 955 Wikipedia articles about Cuba. corpus_meta.jsonl gives id, source, kind, title, words, url per doc.
KEY DIFFICULTIES stated by the task: questions are vague paraphrases, rarely contain titles; "many books tell the same history in different words" (near-duplicate topics across docs - must pick the ONE doc the slip describes); "the answer is usually buried deep inside a chapter" (long docs, the relevant passage is small); one corpus slice is noisy OCR; latency and size are tight ("old machine").
`

const FINDINGS = {
  type: 'object',
  properties: {
    techniques: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          how_it_works: { type: 'string', description: 'concrete mechanism, enough to implement' },
          expected_effect: { type: 'string', description: 'evidence-based expected accuracy effect, with numbers from papers/benchmarks where possible' },
          index_size_cost: { type: 'string' },
          query_latency_cost: { type: 'string', description: 'single CPU thread, per query' },
          query_time_dependencies: { type: 'string', description: 'which python libs are needed at query time; can it run on numpy alone?' },
          build_recipe: { type: 'string', description: 'how to build it offline, which models/tools, rough compute' },
          risks: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' } },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['name', 'how_it_works', 'expected_effect', 'index_size_cost', 'query_latency_cost', 'query_time_dependencies', 'build_recipe', 'risks', 'sources', 'confidence'],
      },
    },
    top_recommendation: { type: 'string', description: 'what you would build first for THIS task and why' },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['techniques', 'top_recommendation', 'open_questions'],
}

const COMMON = `
${TASK}
You are one of five researchers, each covering a different angle. Do real research: load WebSearch and WebFetch with ToolSearch ("select:WebSearch,WebFetch") and read primary sources (papers, model cards, benchmark tables, library docs). Prefer concrete numbers (BEIR/MTEB/MS MARCO nDCG/recall, model sizes in MB, CPU ms/query). Do not write code for the task and do not touch any files outside your scratch space. Be specific to THIS task's constraints; flag anything that needs PyTorch at query time as disqualified unless it can be exported to numpy/ONNX. Return 4-8 techniques.
`

const ANGLES = [
  { key: 'lexical', prompt: `ANGLE: Lexical retrieval for long documents where the relevant passage is buried deep inside.
Cover: BM25 / BM25+ / BM25L parameter choices for long docs; passage-level indexing (sliding windows, sizes, stride) with doc score = max / top-k sum / softmax over passage scores (MaxP, FirstP, SumP from Dai & Callan "Deeper text understanding"/BERT-MaxP and lexical analogues); BM25F with title/heading fields; stemming vs lemmatization vs none (Porter/Snowball in pure python); stopword handling for natural-language questions; bigram/phrase proximity scoring; pseudo-relevance feedback (RM3, Bo1) and whether it helps vague queries; character n-gram (3-5) indexing or fuzzy matching to survive OCR noise (Humboldt slice); handling numbers/years ("1890s" -> 1890..1899). Give expected gains vs plain doc-level BM25 with evidence.` },
  { key: 'learned-sparse', prompt: `ANGLE: Learned / expanded sparse retrieval that needs NO neural model at query time (all the neural work happens offline at index time).
Cover: doc2query / docTTTTTquery / doc2query-- (filtering), InPars-style LLM-generated questions per passage appended to the document or indexed as separate "pseudo-question" fields; DeepImpact, uniCOIL, TILDE, SPLADE-doc / "SPLADE without query encoder" (e.g. naver efficient-splade doc-only variants, "SPLADE-v3-Doc"), EPIC; term-impact quantization into an inverted index scored by a plain sparse dot product with a whitespace/wordpiece-tokenized query; what query tokenizer they need (a BERT WordPiece vocab via the 'tokenizers' lib, or reimplementable in pure python?). Give BEIR/MS MARCO numbers for doc-only models vs BM25, and practical guidance on generating synthetic questions with a local LLM (Qwen2.5-32B/72B AWQ via vLLM) in the style of vague paraphrased "slips". Also: using generated questions as a held-out validation set for tuning.` },
  { key: 'tiny-dense', prompt: `ANGLE: Tiny dense / semantic retrieval that runs on ONE CPU thread without PyTorch.
Cover: static embedding models (Model2Vec / potion-base-2M/4M/8M/32M, potion-retrieval-32M; sentence-transformers static-retrieval-mrl-en-v1) - sizes, MTEB retrieval scores, numpy-only inference (tokenize + mean of token vectors), and how to distill a custom static model on our own corpus vocabulary (model2vec distill, tokenlearn); small ONNX transformer encoders (all-MiniLM-L6/L12, bge-small-en-v1.5, e5-small-v2, gte-small, snowflake-arctic-embed-xs/s, int8-quantized ONNX sizes and single-thread ms/query for a ~20-token query); embedding compression (float16, int8 scalar, binary + rescoring, PCA/Matryoshka truncation) to fit many passage vectors in the size budget; exact numpy matmul vs HNSW for ~1552 docs x N passages. Estimate how many passage vectors fit in 20/50/100 MB at each precision. Note which need onnxruntime + tokenizers at query time vs pure numpy.` },
  { key: 'fusion-rerank', prompt: `ANGLE: Combining signals and reranking cheaply, plus picking the ONE right doc among near-duplicates.
Cover: hybrid lexical+dense fusion (RRF vs normalized linear combination; typical gains on BEIR), score normalization; tiny rerankers under a latency budget (ms-marco-TinyBERT-L-2 / MiniLM-L-2 / L-4 cross-encoders exported to int8 ONNX - ms per (query, passage) pair on 1 thread; reranking only top-k passages); learning-to-rank with a handful of hand features (BM25 doc/passage scores, dense sims, title match, rare-term/named-entity/number overlap, doc length prior, source/kind prior) trained with a linear model or small GBDT and evaluated in numpy; disambiguating near-duplicate docs that cover the same history (the question was written from one specific doc - which signals identify it: rare words, specific numbers, specific phrasing, author/traveller identity); how to tune fusion weights robustly on a small public sample without overfitting (synthetic question sets, cross-validation).` },
  { key: 'engineering', prompt: `ANGLE: Systems engineering for a tiny, fast, quick-loading retrieval index in Python with only numpy (maybe scipy).
Cover: storing an inverted index / CSR sparse matrix in .npz (indptr/indices/data, uint16/uint32/float16) and scoring a query as a sum of a few posting rows with numpy (np.add.at vs bincount vs scipy.sparse row slicing - measured costs); vocabulary storage (sorted array + np.searchsorted vs json dict load time); load-time optimizations (np.load with mmap_mode, avoid pickle, avoid big json); static index pruning (keep top-N postings per term, drop df=1 terms, cap passages per doc) and its accuracy cost (Carmel et al. static pruning); keeping p95 latency low on 1 thread (avoid python loops over postings, precompute idf, cap query length, BLAS thread pinning OMP_NUM_THREADS=1); a pure-python Porter/Snowball stemmer's speed; zip vs 7z compression doesn't matter since size is measured after extraction. Give concrete micro-benchmarks or reasoning for ~1552 docs / ~30k passages / ~100k vocab.` },
]

phase('Research')
const results = await parallel(ANGLES.map(a => () =>
  agent(`${COMMON}\n${a.prompt}`, { label: `research:${a.key}`, phase: 'Research', schema: FINDINGS })
    .then(r => r ? { angle: a.key, ...r } : null)))
const ok = results.filter(Boolean)
log(`${ok.length}/${ANGLES.length} research angles returned`)

phase('Synthesize')
const PLAN = {
  type: 'object',
  properties: {
    recommended_architecture: { type: 'string', description: 'the system to build, component by component, with conditional branches for different limits.json values and requirements.txt contents' },
    build_steps: { type: 'array', items: { type: 'string' }, description: 'ordered, each with what to measure to decide whether to keep it' },
    ranked_techniques: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, expected_gain: { type: 'string' }, cost: { type: 'string' }, priority: { type: 'integer' } }, required: ['name', 'expected_gain', 'cost', 'priority'] } },
    evaluation_protocol: { type: 'string', description: 'how to measure Hit@3 honestly without overfitting the public sample' },
    things_to_check_first_in_the_task_files: { type: 'array', items: { type: 'string' } },
    biggest_risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['recommended_architecture', 'build_steps', 'ranked_techniques', 'evaluation_protocol', 'things_to_check_first_in_the_task_files', 'biggest_risks'],
}
const plan = await agent(`${TASK}
Five researchers investigated different angles. Their findings (JSON):
${JSON.stringify(ok, null, 1)}

Synthesize ONE build plan for this task. Favour the simplest system likely to clear Hit@3 >= 0.80 with margin on hidden questions, then the cheapest upgrades in order of expected gain per unit of size/latency risk. Be explicit about which parts need only numpy and which need onnxruntime/tokenizers, and give branches for tight vs loose limits (e.g. size 20 MB vs 200 MB, latency 20 ms vs 200 ms). Resolve contradictions between researchers; say which evidence you trust.`, { label: 'synthesize', phase: 'Synthesize', schema: PLAN })

phase('Critique')
const CRIT = {
  type: 'object',
  properties: {
    flaws: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] } }, required: ['claim', 'problem', 'fix', 'severity'] } },
    missing_ideas: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string' },
  },
  required: ['flaws', 'missing_ideas', 'verdict'],
}
const critique = await agent(`${TASK}
Here is a proposed build plan (JSON):
${JSON.stringify(plan, null, 1)}

Act as a skeptical senior IR engineer. Try to break this plan: unsupported accuracy claims, latency/size estimates that are wrong for a single CPU thread in Python, query-time dependencies that may not exist, overfitting risks with a small public sample, failure modes on vague paraphrased questions and near-duplicate docs, OCR noise, and anything cheaper that would work as well. Use WebSearch/WebFetch (load with ToolSearch "select:WebSearch,WebFetch") to check specific numbers you doubt. List missing ideas that could matter.`, { label: 'critique', phase: 'Critique', schema: CRIT })

return { research: ok, plan, critique }

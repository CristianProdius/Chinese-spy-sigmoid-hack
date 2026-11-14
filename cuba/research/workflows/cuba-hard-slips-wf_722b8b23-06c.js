export const meta = {
  name: 'cuba-hard-slips',
  description: 'Claude agents write harder (heavily paraphrased) slips for 900 new passages and rewrite 3328 Qwen slips to the real paraphrase level',
  phases: [
    { title: 'Hard slips', detail: '6 agents x 150 new passages, 2 slips each' },
    { title: 'Rewrites', detail: '4 agents x 832 Qwen slips' },
  ],
}

const DIR = '/home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/cuba/cuba/work'
const STYLE = `${DIR}/vset/style_examples.json`

const HARD_RULES = `What makes the REAL slips hard (copy this behaviour):
- They paraphrase distinctive words aggressively. Only about 3 in 4 of a real slip's content words appear anywhere in the source document. Examples of the substitutions they make: telephone -> 'speaking-by-wire service'; birds -> 'feathered wildlife'; hutia -> 'the big rat-looking critter'; British -> "London's"; the Spanish government -> "Madrid's"; Havana -> 'Habana' or 'the capital'; Spanish language -> 'Castilian'; slaves -> 'captive Africans'; the Inquisition -> 'Pope-approved faith courts'; doctors -> 'medical men'; four centuries -> '400 years'.
- They often keep ONE concrete anchor (a person, a year, a number or a place) but swap the rest for descriptions; sometimes they keep none.
- They never quote a phrase of more than 3 words from the source.
- Noise on about a quarter of slips: a misspelled word (inturnal, surbival, aobut, whch, bigin), a Spanish word swapped in (año, guerra, iglesia, gente, mujeres, la historia de, la parte donde, eso de, el capítulo), all-lowercase, or a casual opener ('that bit about', 'the part where', 'read us', 'the reading about').
- 10 to 29 words.`

const HARD_SCHEMA = {
  type: 'object',
  properties: { slips: { type: 'array', items: { type: 'object', properties: { pid: { type: 'string' }, slip: { type: 'string' } }, required: ['pid', 'slip'] } } },
  required: ['slips'],
}
const RW_SCHEMA = {
  type: 'object',
  properties: { rewrites: { type: 'array', items: { type: 'object', properties: { rid: { type: 'string' }, slip: { type: 'string' } }, required: ['rid', 'slip'] } } },
  required: ['rewrites'],
}

const hardPrompt = (b) => `You are helping build training data for a document-retrieval challenge. Read-only task: do not create, edit or delete any files.

Cigar rollers in a Cuban factory drop paper slips asking the reader (lector) to read a particular document again. Each slip describes something from ONE specific passage, written from memory. The library holds 1552 documents (Project Gutenberg books about Cuba 1845-1920, a 2002 Library of Congress country study, a noisy OCR of Humboldt, Wikipedia), many telling the same history in different words.

Read with the Read tool:
1. ${STYLE} : 40 REAL slips (style reference; about other documents).
2. ${DIR}/hard/batch${b}.jsonl : 150 passages, one JSON object per line {"pid", "title", "passage"}; read it in parts until you have all 150.

For EVERY passage write exactly 2 slips that are as hard as the real ones. Mix the real styles: specific factual questions (How many / In what year / What did / Why did / Which ...), questions bundling two or three details, half-remembered descriptions that are not questions, and at most 1 in 4 whole-document requests ('The whole story of ...', 'the chapter about ...').
${HARD_RULES}
- Each slip must still point to this passage: keep enough meaning that a careful reader could find it.

Return all 300 slips via structured output [{"pid", "slip"}], two per pid, covering all 150 pids.`

const rwPrompt = (b) => `You are helping build training data for a document-retrieval challenge. Read-only task: do not create, edit or delete any files.

Cigar rollers drop paper slips asking a factory reader to re-read a document; a slip describes something from one passage, from memory. Another model wrote the slips in ${DIR}/hard/rewrite${b}.jsonl (832 lines, {"rid", "slip"}; read the whole file in parts), but they copy the source wording too closely compared with the real slips in ${STYLE} (read it first).

Rewrite EVERY slip so it matches the real slips' difficulty while keeping its meaning (same facts, same target):
${HARD_RULES}
- Keep the slip's type (question vs description vs whole-document request).

Return all 832 rewrites via structured output [{"rid", "slip"}], one per rid.`

phase('Hard slips')
const hard = parallel([0, 1, 2, 3, 4, 5].map(b => () =>
  agent(hardPrompt(b), { label: `hard:batch${b}`, phase: 'Hard slips', schema: HARD_SCHEMA, model: 'sonnet' })
    .then(r => r ? { batch: b, slips: r.slips } : null)))
phase('Rewrites')
const rw = parallel([0, 1, 2, 3].map(b => () =>
  agent(rwPrompt(b), { label: `rewrite:${b}`, phase: 'Rewrites', schema: RW_SCHEMA, model: 'sonnet' })
    .then(r => r ? { batch: b, rewrites: r.rewrites } : null)))
const [h, r] = await Promise.all([hard, rw])
const hs = h.filter(Boolean), rs = r.filter(Boolean)
log(`hard: ${hs.length}/6 batches, ${hs.reduce((s, x) => s + x.slips.length, 0)} slips; rewrites: ${rs.length}/4, ${rs.reduce((s, x) => s + x.rewrites.length, 0)}`)
return { hard: hs, rewrites: rs }

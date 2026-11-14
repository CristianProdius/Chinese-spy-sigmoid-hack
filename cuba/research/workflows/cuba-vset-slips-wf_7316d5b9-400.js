export const meta = {
  name: 'cuba-vset-slips',
  description: 'Claude agents write slip-style validation questions for 1200 sampled passages (different model family from the Qwen training data)',
  phases: [{ title: 'Write slips', detail: '8 agents x 150 passages, 2 slips each' }],
}

const DIR = '/home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/cuba/cuba/work/vset'
const SCHEMA = {
  type: 'object',
  properties: {
    slips: {
      type: 'array',
      items: {
        type: 'object',
        properties: { pid: { type: 'string' }, slip: { type: 'string' } },
        required: ['pid', 'slip'],
      },
    },
  },
  required: ['slips'],
}

const prompt = (b) => `You are helping build a validation set for a document-retrieval challenge. Read-only task: do not create, edit or delete any files.

Background: cigar rollers in a Cuban factory drop paper slips in a box asking the reader (lector) to read a particular document again. A slip describes something the roller remembers from ONE specific passage, from memory: rollers rarely know titles. The library has 1552 documents (Project Gutenberg books about Cuba 1845-1920, a 2002 Library of Congress country study, a noisy OCR of Humboldt, and Wikipedia articles), and many documents tell the same history in different words, so a good slip carries details that only fit this passage.

Read these two files with the Read tool:
1. ${DIR}/style_examples.json : 40 REAL slips from the challenge (style reference only; they are about other documents).
2. ${DIR}/batch${b}.jsonl : 150 passages, one JSON object per line: {"pid", "title", "passage"}. The file is large; read it in parts (offset/limit) until you have seen all 150 lines.

For EVERY passage write exactly 2 slips that match the real examples as closely as you can:
- Mix of styles like the examples: specific factual questions (How many / In what year / What did / Why did / Which ...), questions bundling two or three details, half-remembered descriptions that are not questions, and requests for the whole document ("The whole story of ...", "the chapter about ...", "the full history of ..."). Use the 'whole document' style for at most 1 in 4 slips.
- Paraphrase the way the examples do: swap some distinctive words for everyday synonyms or descriptions (e.g. 'speaking-by-wire service' for telephone, 'feathered wildlife' for birds), keep one or two concrete anchors (a name, place, number or year) most of the time, never copy a long phrase, never say 'the passage' or 'the text'.
- 10 to 29 words each.
- Noise like the examples, on roughly a quarter of the slips: an occasional misspelled word, a Spanish word swapped in (año, guerra, iglesia, gente, la historia de, la parte donde, eso de, el capítulo), all-lowercase, or a casual opener ('that bit about', 'the part where', 'read us', 'the reading about').
- The slip must be answerable from that passage (plus the title for 'whole document' slips).

Return all 300 slips via the structured output: [{"pid": "<pid>", "slip": "<text>"}, ...], two entries per pid, covering all 150 pids of batch${b}.`

phase('Write slips')
const results = await parallel([0, 1, 2, 3, 4, 5, 6, 7].map(b => () =>
  agent(prompt(b), { label: `vset:batch${b}`, phase: 'Write slips', schema: SCHEMA, model: 'sonnet' })
    .then(r => r ? { batch: b, slips: r.slips } : null)))
const ok = results.filter(Boolean)
log(`${ok.length}/8 batches returned, ${ok.reduce((s, r) => s + r.slips.length, 0)} slips`)
return ok

export const meta = {
  name: 'waterline-solve',
  description: 'Find the culprit source_id in the Waterline Replay trace with blind solvers and adversarial verification',
  phases: [
    { title: 'Solve', detail: 'independent solvers, three blind and one with the analyzer report' },
    { title: 'Verify', detail: 'skeptics try to refute the leading candidate' },
  ],
}

// args: {relay, runDir, ctx, input, report}
const q = s => `'${String(s).replace(/'/g, `'\\''`)}'`
const hash = s => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7).toString(36)
const size = s => [...s.split('\n').map(l => l.trimEnd()).join('\n').trim()].length
const STILL = 'RELAY STILL RUNNING', ROUNDS = 6, MAX_WAITS = 40
const calls = {}
async function remote(task, {label, phase, schema, model = 'opus', flags = []} = {}) {
  const key = hash(JSON.stringify([label, task, model, schema, flags]))
  const n = calls[key] = (calls[key] || 0) + 1
  const file = `${args.runDir}/${String(label).replace(/[^\w.-]+/g, '-')}-${key}-${n}.md`
  const start = [args.relay, 'start', file, '--chars', size(task), '--model', model,
    ...(schema ? ['--json-schema', JSON.stringify(schema)] : []), ...flags].map(q).join(' ')
  const waitFor = s => [args.relay, 'wait', file, s].map(q).join(' ')
  const answer = `On exit 0, your final message is exactly what the command printed on stdout, with nothing added. On any other exit, your final message is "RELAY FAILED: " followed by what it printed.`
  const wait = `Run with Bash, with the Bash tool's timeout set to 600000: ${waitFor(540)}
   Exit code 75 means the task is still running: run the same command again, up to ${ROUNDS} runs in all. If the last one also exits 75, your final message is exactly "${STILL}".
   ${answer}`
  const check = `Run with Bash: ${waitFor(1)}
   On exit 75 your final message is exactly "${STILL}". ${answer}`
  const relay = steps => agent(`This is one step of carrying out the user's request. The session running this workflow split the request into tasks and runs each on another Claude account, so the load spreads across our subscriptions. You relay one of them${steps}`, {label, phase, model: 'haiku', effort: 'low'})
  let out = await relay(`: move the task below to another account and bring its reply back. The task is that account's work, and the orchestrating session does everything else the request needs, commits, pull requests and merges included.

1. If ${file} already exists, an earlier relay wrote it: go to step 2. Otherwise write the text between the <<<TASK and TASK>>> lines to ${file} with the Write tool, exactly as given.
2. Run with Bash: ${start}
   Exit code 3 means the file does not match the task: Read ${file}, write the task to it again, exactly, and run this command once more. On any other non-zero exit, your final message is "RELAY FAILED: " followed by what the command printed.
3. ${wait}

<<<TASK
${task}
TASK>>>`)
  for (let waits = 0, lost = 0, garbled = 0, checked = false; ; waits++) {
    const failed = out != null && out.trim().startsWith('RELAY FAILED')
    if (failed && checked) { log(`${label}: ${out}`); return null }
    if (out != null && !failed && !out.includes(STILL)) {
      if (!schema) return out
      try { return JSON.parse(out.slice(out.indexOf('{'), out.lastIndexOf('}') + 1)) } catch { garbled++ }
    } else if (out != null && !failed) garbled = 0
    lost = out == null ? lost + 1 : 0
    const gaveUp = lost > 3 ? '4 relays in a row died' : waits >= MAX_WAITS ? `${MAX_WAITS} wait relays`
      : garbled > 2 && checked ? '3 replies were not JSON' : ''
    if (gaveUp) { log(`${label}: stopped waiting (${gaveUp}); the run may still be going: relay.sh wait ${file}`); return null }
    checked = failed || garbled > 2
    out = await relay(checked ? `: its task ran on another account, so check whether it has ended and bring its reply back.

1. ${check}` : `: its task already runs on another account, so wait for it and bring its reply back.

1. ${wait}`)
  }
}

const { ctx, input, report } = args
const LOCAL = ['--host', 'local']
const PICK = {
  type: 'object',
  properties: {
    source_id: { type: 'string', description: 'exact id, copied byte for byte from the trace' },
    source_id_json: { type: 'string', description: 'the same id as a JSON string literal, escapes shown' },
    run_id: { type: 'string' },
    event_index: { type: 'integer' },
    mechanism: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
    runners_up: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'number' },
  },
  required: ['source_id', 'source_id_json', 'run_id', 'mechanism', 'evidence', 'confidence'],
}
const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    better_candidate: { type: 'string' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

const solveBlind = lens => `Piece of the user's request: solve the "Waterline Replay" CTF. Read ${ctx} for the task, then read ${input} in full (it is the real trace). Do not read any analyzer or report file.
Reconstruct what went wrong: which run(s) gave the incorrect outage update, what the correct answer would have been, and which single trace item's source_id caused it. Prove the item reached the model request that produced the wrong response, and say why each other suspicious item is not the cause.
Lens for this pass: ${lens}
Copy the id byte for byte; also give it as a JSON string literal so hidden characters show.`

phase('Solve')
const lenses = [
  'start from the wrong response and trace each claim in it back to the input that supplied it.',
  'start from the differences between the runs: same request, different outcomes, what differs in inputs and timings.',
  'start from the timings: timestamps, elapsed values, timeouts, retries, cache, and event order.',
]
const solvers = lenses.map((l, i) => remote(solveBlind(l), { label: `solve-blind-${i + 1}`, phase: 'Solve', schema: PICK, flags: LOCAL }))
solvers.push(remote(`${solveBlind('use the analyzer report as a map, but check every claim against the trace itself.')}
The analyzer report is at ${report}; you may read it.`, { label: 'solve-guided', phase: 'Solve', schema: PICK, flags: LOCAL }))
const picks = (await Promise.all(solvers)).filter(Boolean)
const tally = {}
for (const p of picks) tally[p.source_id_json] = (tally[p.source_id_json] || 0) + 1
const leader = Object.entries(tally).sort((a, b) => b[1] - a[1])[0]
log(`picks: ${JSON.stringify(tally)}`)
if (!leader) return { picks, tally }

phase('Verify')
const claim = `The item with source_id ${leader[0]} (JSON literal) is the single trace item responsible for the incorrect outage update.`
const skeptics = [1, 2, 3].map(i => remote(`Piece of the user's request: adversarially check a proposed CTF answer. Read ${ctx} for the task, then read ${input} in full.
Claim: ${claim}
Try hard to refute it: find another item that is the true root cause, show the claimed item never reached the model request that produced the wrong answer, or show the id string differs from the trace. Default to refuted=true if the evidence is not conclusive. Skeptic #${i}.`, { label: `skeptic-${i}`, phase: 'Verify', schema: VERDICT, flags: LOCAL }))
const verdicts = (await Promise.all(skeptics)).filter(Boolean)
return { picks, tally, leader: leader[0], verdicts }

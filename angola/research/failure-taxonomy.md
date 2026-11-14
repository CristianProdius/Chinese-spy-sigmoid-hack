# R1: Agent-trace structure, failure taxonomy, forensic procedure (Waterline Replay)

Goal: find the one `source_id` whose content caused the wrong Kilamba outage update. Every rule below
serves one test. The culprit must (a) be in the final model request of the wrong run, (b) carry the
wrong claim that the answer repeats, (c) differ from what correct runs fed the model, and (d) have a
provenance defect we can name. A decoy fails at least one of the four.

---------------------------------------------------------------------------------------------------
## 1. How real agent-trace exports are shaped (field names to alias in the parser)

The CTF export is custom (`events[]` with run ids, timestamps, elapsed, type, payload), but it is
almost certainly modelled on one of these. Use them to guess aliases.

### 1.1 OpenTelemetry GenAI semconv (repo `open-telemetry/semantic-conventions-genai`, status: Development)
- OTLP span: `traceId` (32 hex), `spanId` (16 hex), `parentSpanId`, `name`, `startTimeUnixNano`,
  `endTimeUnixNano` (ns since epoch, UTC), `status.code`, `attributes[]`, `events[]`.
- `gen_ai.operation.name`: `chat`, `text_completion`, `generate_content`, `embeddings`, `retrieval`,
  `execute_tool`, `invoke_agent`, `create_agent`, `invoke_workflow`, `search_memory`, ...
- Span names: `chat {model}`, `execute_tool {gen_ai.tool.name}`, `invoke_agent {gen_ai.agent.name}`,
  `retrieval`.
- Tool span: `gen_ai.tool.call.id`, `gen_ai.tool.name`, `gen_ai.tool.type`,
  `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`, `error.type`.
- Run/session: `gen_ai.conversation.id`, `gen_ai.agent.name`, `gen_ai.agent.id` (create_agent only),
  `gen_ai.data_source.id` (which knowledge base).
- Retrieval: `gen_ai.retrieval.query.text`, `gen_ai.retrieval.top_k`, `gen_ai.retrieval.documents`
  = `[{"id": "doc_123", "score": 0.95}, ...]` (opt-in).
- Model request/response: `gen_ai.request.model`, `gen_ai.system_instructions`,
  `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.response.id`,
  `gen_ai.response.finish_reasons`. Message parts have types `text`, `tool_call {id,name,arguments}`
  and `tool_call_response {id,response}`. The part `id` is the tool call id that links request and result.
- Memory: `gen_ai.memory.store.id`, `gen_ai.memory.record.id`. A memory record can feed the model
  without any tool call in that run (see F10).

### 1.2 LangSmith Run
- `id` (UUID), `trace_id` (root run id), `parent_run_id`, `child_run_ids`, `session_id` (= project).
- `dotted_order`: `<start>Z<uuid>.<start>Z<uuid>...` from root to self. Sorting by it gives tree order,
  first uuid = trace_id, last = own id, second-to-last = parent.
- `run_type`: `chain | llm | tool | retriever | embedding | prompt | parser`.
- `start_time`, `end_time`, `first_token_time` (ISO, UTC), `status`, `error`.
- `inputs`, `outputs`, `extra.metadata`, `events[]` (e.g. `{"name":"new_token"}`), `tags`,
  `reference_example_id`. Retriever outputs: `documents[] {page_content, metadata{source,...}}`.

### 1.3 Langfuse
- Trace: `id`, `sessionId`, `userId`, `timestamp`, `input`, `output`, `metadata`, `tags`.
- Observation: `id`, `traceId`, `parentObservationId`, `type` (`span`, `generation`, `event`,
  `agent`, `tool`, `chain`, `retriever`, `embedding`, `guardrail`, `evaluator`), `name`,
  `startTime`, `endTime`, `completionStartTime`, `input`, `output`, `metadata`, `model`,
  `level` (`DEBUG|DEFAULT|WARNING|ERROR`), `statusMessage`, `version`.
- Derived: `latency` and `timeToFirstToken` are in SECONDS (`latency = endTime - startTime`).

### 1.4 OpenAI Agents SDK tracing
- Trace: `trace_id` = `trace_<32 alnum>`, `workflow_name`, `group_id` (links runs of one thread),
  `metadata`.
- Span (`object: "trace.span"`): `id` (`span_...`), `trace_id`, `parent_id` (null at root),
  `started_at`, `ended_at`, `error`, `span_data{type,...}`.
- `span_data.type`: `agent {name,handoffs,tools,output_type}`, `generation {input,output,model,
  model_config,usage}`, `response {response,input,usage}`, `function {name,input,output,mcp_data}`,
  `handoff {from_agent,to_agent}`, `guardrail {name,triggered}`, `custom {name,data}`, `mcp_tools`.
- Function spans do NOT carry the tool call id. The model output carries it: Chat Completions
  `tool_calls[].id` (`call_...`) answered by a tool message `tool_call_id`. Responses API
  `function_call {id:"fc_...", call_id:"call_..."}` is answered by `function_call_output {call_id}`.
  Anthropic: `tool_use.id` (`toolu_...`) is answered by `tool_result.tool_use_id`.

### 1.5 OpenInference / Arize Phoenix (OTel attributes)
- `openinference.span.kind`: `LLM, CHAIN, RETRIEVER, RERANKER, TOOL, AGENT, EMBEDDING, GUARDRAIL,
  EVALUATOR, PROMPT`.
- `input.value`, `output.value`, `llm.input_messages`, `llm.output_messages`,
  `message.tool_calls.N.tool_call.id`, `tool_call.function.name`, `tool.name`, `tool.parameters`.
- `retrieval.documents.N.document.{id,content,score,metadata}`, `reranker.input_documents`,
  `reranker.output_documents`, `reranker.top_k`, `session.id`, `user.id`.
- The reranker matters because docs in `input_documents` that are missing from `output_documents`
  never reached the LLM.

### 1.6 Alias table for our parser (check all; the CTF may use any)
| concept | likely keys |
|---|---|
| run | `run_id`, `trace_id`, `traceId`, `session_id`, `conversation_id`, `group_id`, `attempt` |
| event/span | `event_id`, `id`, `span_id`, `spanId`, `seq`, `index` |
| parent | `parent_id`, `parent_span_id`, `parentSpanId`, `parent_run_id`, `parentObservationId`, `dotted_order` |
| tool call | `tool_call_id`, `call_id`, `tool_use_id`, `gen_ai.tool.call.id`, `tool_call.id`, `request_id` |
| context item | `source_id`, `doc_id`, `document.id`, `chunk_id`, `item_id`, `metadata.source`, `ref` |
| time | `ts`, `timestamp`, `time`, `start_time`/`end_time`, `started_at`/`ended_at`, `*UnixNano`, `received_at`, `fetched_at`, `cached_at` |
| duration | `elapsed_ms`, `elapsed`, `latency_ms`, `latency` (s in Langfuse), `duration_ms`, `timeout_ms`, `ttl_s` |
| validity | `as_of`, `issued_at`, `published_at`, `valid_from`, `valid_until`, `expires_at`, `effective_*`, `status`, `version`, `supersedes`, `superseded_by` |
| model input | `model_request`, `messages`, `input_messages`, `context`, `context_items`, `included_source_ids`, `prompt` |

Timing semantics to settle first: is `elapsed` measured from run start, from the previous event, or
is it the duration of this event? Test `ts - run_start_ts == elapsed` across a run. Units: ms vs s vs ns.
Treat timestamps without an offset as suspect. `Z` is UTC, `+01:00` is WAT. Angola uses WAT (UTC+1)
all year, with no DST.

---------------------------------------------------------------------------------------------------
## 2. Taxonomy: one trace item causes a wrong final answer

Each entry gives the signature (how it shows in fields) and the discriminator (culprit vs decoy).
"Wrong run" = run whose final response is the incorrect outage update. "Final request" = the last
model request in that run, the one whose response is the final answer.

**F1. Stale cache hit**
- Signature: tool result has `cache: hit` / `cached: true` / `source: cache`, tiny elapsed (1-5 ms vs
  hundreds for live calls), and `cached_at`/`as_of`/`fetched_at` well before the request time (older
  than its TTL, or older than a newer notice). Its content may byte-match a result from an earlier run.
- Discriminator: correct runs got a live (`miss`) result with newer `as_of` for the same query. The
  stale item's claim (e.g. "outage ongoing" / an old restoration time) appears in the wrong answer.
  Decoy: a cache hit that is still within TTL and agrees with the live result.

**F2. Late result from a timed-out or retried call**
- Signature: call A has `timeout_ms` (or an `error: timeout` event) and the agent retries as call B.
  A's result arrives later (`ts_result_A > ts_call_A + timeout`, often after B's result). The result
  is still attached to the model request, or overwrites B in the context slot. Tell-tales: two results
  for one logical call, a result whose `tool_call_id` belongs to the abandoned attempt, a large elapsed
  value, `attempt: 1` vs `attempt: 2`.
- Discriminator: the culprit is the late item that the final request actually contains. Decoy: the
  late result logged after the final request was sent (`ts_result > ts_final_request`). It could not
  have influenced the answer unless something cached it for a later run (then see F3/F1).

**F3. Result from another run (cross-run leak / mismatched call id)**
- Signature: an item inside run R carries `run_id` R' ≠ R, or its `tool_call_id` matches a call issued
  in R' and was never issued in R. Its timestamp may fall outside R's time window or even precede R's
  start. Shared session/memory/cache keys and concurrent runs interleaved in `events[]` are common
  vectors.
- Discriminator: build `calls_issued[R]` and `results[R]`. The culprit is in `final_request[R]`, and
  its call id is ∉ `calls_issued[R]`. Decoy: interleaved events from R' that never enter R's model
  request (normal interleaving, harmless).

**F4. Wrong-entity retrieval (similar place name)**
- Signature: query/args say "Kilamba" (Cidade do Kilamba, planned city in Belas/Kilamba municipality),
  but the item's entity field says "Kilamba Kiaxi" (a different Luanda municipality/area). Other look-
  alikes: "Kilamba" street names, "Quilamba", accentless or other-language spellings. The score is
  close to the right doc, or the right doc ranked lower or was cut by `top_k`/reranker.
- Discriminator: compare the item's `area`/`location`/`municipality`/`zone_id`/`geo` against the
  request's entity, not the title text alone. The culprit is the wrong-entity item whose outage
  details (cause, times, streets) show up in the answer. Decoy: a wrong-entity doc that was retrieved
  but reranked out, or one whose details do not appear in the answer.

**F5. Expired or superseded notice**
- Signature: notice with `valid_from`/`valid_until`/`expires_at`, `issued_at`/`as_of`, `version`,
  `status` (`active|resolved|cancelled`), `supersedes`/`superseded_by`. The request time falls
  outside the window, or a newer notice for the same area/incident exists.
- Timezone traps: `valid_until: "2026-..T18:00"` with no offset may mean 18:00 WAT = 17:00Z. A request
  at 17:30Z is then AFTER expiry, while a naive comparison says still valid. Also: `as_of` vs request
  `ts` vs event `ts` (the assistant should compare with request time, not export time). Also check
  dates crossing midnight between UTC and WAT.
- Discriminator: the culprit is the expired/superseded notice that is in the wrong run's final request.
  Often the superseding notice is in correct runs' requests but missing from (or below) it in the wrong
  run. Decoy: an expired notice present in ALL runs (correct runs too), where the model ignored it in
  favour of a newer one.

**F6. Out-of-order events**
- Signature: array order ≠ timestamp order, a result before its call, a model request that cites an
  item whose `ts` is later than the request's own `ts`, `seq` gaps, or `elapsed` that disagrees with
  `ts`.
- Discriminator: re-sort per run by (ts, then elapsed, then seq) and recompute "what existed when the
  final request was built". An item that "arrives from the future" relative to the request it appears
  in must have come from a cache, another run, or clock skew (leads to F1/F3). Note: the export says
  `events` is ordered, so a deliberate inversion is itself a clue that points at one item.

**F7. Truncation / eviction (item never reached the model)**
- Signature: context budget/`max_tokens`, `truncated: true`, `dropped_ids`/`evicted`, reranker cutoff,
  `included_source_ids` shorter than retrieved list, or the final request text simply lacks the item.
- Discriminator: the strongest decoy filter. An item that looks wrong but is NOT in the final
  request is never the answer. Inverse case: eviction of the CORRECT notice leaves an older item as
  the only source. The responsible item is still the one whose content the answer repeats (the
  survivor), since the flag is a `source_id` and an eviction event has none.

**F8. Prompt injection in tool output**
- Signature: tool result/document text carrying instructions: "ignore previous", "SYSTEM:",
  "assistant must report", "tell the user service is restored", hidden text (zero-width chars, HTML
  comments, base64), or role-tag spoofing.
- Discriminator: the answer follows the instruction (e.g. says "resolved" against every factual
  notice). The culprit is the item containing the injection (its `source_id`), not the tool call that
  fetched it. Decoy: injection text in an item that was truncated away, or present in correct runs
  where the model resisted.

**F9. Duplicate / near-duplicate source ids**
- Signature: two items with the same `source_id` but different content/version/`fetched_at`, or ids
  that differ only by case, homoglyph (Cyrillic `А`, `О`, Greek `Ι`), zero-width char (U+200B/C/D,
  U+FEFF), trailing space, `_V2`/`_OLD` suffix, `-` vs `_`, `0` vs `O`, `1`/`l`/`I`.
- Discriminator: key every item by (`source_id` raw bytes, content hash). Look up by exact bytes, never
  by normalized string. The flag is the exact id of the culprit's content. If two contents share one id,
  both give the same flag string. Make sure the one in the final request is the wrong one. For
  near-duplicates, print `repr()`/codepoints and copy from the item that is in the final request.

**F10. Item in the model request that no tool in this run returned**
- Signature: `final_request[R]` items minus (tool results + retrieval docs + system/user inputs of R)
  ≠ ∅. Typical origins: memory/long-term store, session carry-over, cache prefill, a leaked
  result from R', a hard-coded "seed" notice.
- Discriminator: this set difference is often a single item and is a very high-signal candidate.
  Confirm it carries the wrong claim. Decoy: a static system-prompt doc present in every run.

Other modes worth a quick check: argument corruption (tool called with wrong area/date, so the culprit
is the result it produced); unit/number mixups (hours vs minutes, `restored_at` vs `reported_at`);
two partial notices merged into one false claim (pick the item that contributes the false fact); a
summarization/memory step that rewrote a correct item wrongly (the culprit is the rewritten item's id).

---------------------------------------------------------------------------------------------------
## 3. Forensic procedure (single responsible item)

**Step 0: load safely.** `python3 -I`, stdlib `json`. Keep raw strings. Never `.strip()`/normalize
ids when storing. Record per-event array index. Dump key inventory: all distinct `type` values and
all payload keys (recursive), plus every string matching `SIGMOID_` with its path. This shows the
schema and the full candidate pool in one pass.

**Step 1: group and order.** Group by run id. Within each run sort by ts (parse `Z`/offset, convert to
UTC), keep array order as a tiebreak, and flag every inversion between array order and ts/elapsed
(F6). Note run start/end, and confirm every run carries the same user request text (the "same request").

**Step 2: label the runs.** Extract each run's final response. Decide the TRUE state for Kilamba at
request time: the newest valid notice whose entity is Kilamba (not Kilamba Kiaxi) and whose window
contains request time in WAT. Majority of runs usually agrees. Mark runs correct/incorrect. If several
runs are wrong, the culprit should explain all of them, or the task's "incorrect outage update"
names one specific run; read the export's metadata for a flagged run.

**Step 3: fingerprint the wrong claim.** From the wrong answer pull distinctive tokens: status word
(ongoing/restored/scheduled), times (e.g. "14:00", dates), durations, area names, cause, street or
reservoir names, ticket/notice numbers. Search every item's content for them. Items whose text
supplies those exact tokens are candidates. Tokens that appear only in the wrong answer and one item
are close to proof.

**Step 4: reconstruct the final model request of the wrong run.** Identify the last model-request
event before the final response (link by parent id / response id / ordering). Extract the set of
`source_id`s it actually contains: explicit `context_items`/`included_source_ids`, or ids/content
embedded in messages (tool messages by `tool_call_id`, documents by id). Also check that each
candidate's text (or a unique substring) literally appears in that request. Inclusion is proven by
the request itself, not by "it was retrieved".

**Step 5: differential across runs.** For every run compute `final_request_ids[run]`. Then:
- `suspects = final_request_ids[wrong] − ⋃ final_request_ids[correct]` (exact bytes).
- Also diff content for shared ids (same id, different text/version = F9/F1).
- Also compute `orphans = final_request_ids[wrong] − returned_ids[wrong]` (F10) and
  `foreign = items whose run_id/tool_call_id belongs to another run` (F3).
- Intersect with Step 3 candidates. Expect exactly one.

**Step 6: name the defect.** For the survivor, state which of F1-F10 applies with field evidence:
`as_of`/`valid_until` vs request ts in WAT, cache flags and elapsed, call-id lineage, run_id
mismatch, entity mismatch, injection text. If no defect fits, keep looking. A real culprit always
has a provenance story, and decoys usually look wrong but are harmless.

**Step 7: rule out the decoys explicitly.** For each other `SIGMOID_` id, record why it is not the
answer: not in final request (evicted/reranked/late after send), present identically in correct runs,
correct content, superseded but ignored, belongs to a non-final intermediate request only, or is an
event/span/call id rather than a `source_id` (the flag must come from a `source_id` field).

**Step 8: emit exactly.** Take the id string from the item object inside the final request (not from
prose). Print `repr()` and codepoints, and verify it matches `^SIGMOID_[A-Z0-9_]+$` (if it does not,
it is probably a homoglyph decoy; re-check which variant is in the final request). Write
`answer.txt` = id + optional single `\n`. Re-read the file bytes and compare.

Sanity checklist before submitting:
1. In the final model request of the wrong run? (proven by request content)
2. Its specific claim reproduced in the wrong answer?
3. Absent or different in correct runs' final requests?
4. Named provenance defect with field evidence?
5. Exact bytes copied from a `source_id` field, no normalization?

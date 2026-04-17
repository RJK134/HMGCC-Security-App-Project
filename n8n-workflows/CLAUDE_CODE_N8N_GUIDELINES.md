# Claude Code — n8n Workflow Generation Rulebook

**Scope:** Any time Claude Code (or a future Claude instance) generates, edits, or regenerates an n8n workflow JSON file for this project, these rules are mandatory. They exist because each one corresponds to a real production failure we have already hit and fixed in this instance (`rjk134.app.n8n.cloud`). Breaking them will reintroduce those failures.

**Target platform:** n8n Cloud (shared-tenant SaaS). These rules are tightened for Cloud; some do not apply to self-hosted n8n.

---

## 1. Never use `process.env` inside Code nodes

**Why:** On n8n Cloud, Code nodes run inside a sandboxed task-runner where `process` is undefined. Any reference to `process.env.X` throws `ReferenceError: process is not defined` and halts the workflow. This caused the `06 - LMS Sync` failure (exec #1, 19 Mar 2026).

**Forbidden:**

```js
const lmsType = process.env.LMS_TYPE || 'MOODLE';
```

**Allowed (in order of preference):**

1. **Inline literal** when the value is stable and non-secret:
2.    ```js
         const lmsType = 'MOODLE';
         ```
      2. **A "Config" Set node at the top of the workflow** that emits the settings as JSON, then downstream Code nodes read from `$('Config').first().json.lmsType`.
      3. 3. **n8n Credentials** for anything sensitive (API keys, tokens). Never hard-code secrets, never place them in query params, never read them from env.
         4. 4. **n8n Variables** (`$vars.LMS_TYPE`) if the plan tier supports them — check before using; many Cloud tiers do not include Variables.
           
            5. **Forbidden patterns to grep for before commit:**
           
            6. - `process.env`
               - - `process.`
                 - - `require(`
                   - - `global.`
                     - - `Buffer.` (unavailable in sandbox typeVersion 2)
                      
                       - ---

                       ## 2. Force `typeVersion: 1` on every Code node

                       **Why:** n8n Cloud's Code-node typeVersion 2 runs under a stricter V8 isolate that wraps thrown errors. When the sandbox itself throws (e.g. on disallowed `process.env` access), it tries to mutate the frozen error object's `name` property, causing:

                       ```
                       TypeError: Cannot assign to read only property 'name' of object 'Error: access to env vars denied'
                       ```

                       This killed four EquiSmile WhatsApp Intake executions on 15 Apr 2026. Downgrading to typeVersion 1 uses the legacy in-process executor which does not have this bug.

                       **Rule:** in every generated workflow JSON, every node of type `n8n-nodes-base.code` MUST have:

                       ```json
                       {
                         "type": "n8n-nodes-base.code",
                         "typeVersion": 1,
                           ...
                       }
                       ```

                       Revisit this rule when n8n ships a fix; until then, it is non-negotiable.

                       ---

                       ## 3. Schedule trigger: `triggerAtDay` must be an array

                       **Why:** n8n's activation validator calls `.join(',')` on `triggerAtDay`. If it is a number, activation fails with `days.join is not a function`. This blocked WF7 (HERM) initial activation.

                       **Forbidden:**

                       ```json
                       "triggerAtDay": 2
                       ```

                       **Required:**

                       ```json
                       "triggerAtDay": [2]
                       ```

                       Applies whether you are scheduling one day or many. Always an array.

                       ---

                       ## 4. Validate all external URLs at build time

                       **Why:** The Funding & Opportunities Scanner failed on 17 Apr 2026 because gov.uk silently decommissioned `publications.atom?departments[]=department-for-education`. Silent URL rot is only detectable from production failure unless you pre-flight it.

                       **Rule:** every generated workflow that contains RSS, HTTP Request, or similar URL-parameterised nodes must ship alongside a validator script that resolves every URL and fails CI if any returns non-2xx.

                       **Reference implementation** (Node, no deps):

                       ```js
                       // scripts/validate-urls.mjs
                       import { readdirSync, readFileSync } from 'node:fs';
                       import { join } from 'node:path';

                       const WORKFLOW_DIR = 'n8n-workflows';
                       const files = readdirSync(WORKFLOW_DIR).filter(f => f.endsWith('.json'));
                       const urls = new Set();

                       for (const f of files) {
                         const wf = JSON.parse(readFileSync(join(WORKFLOW_DIR, f), 'utf8'));
                         for (const node of wf.nodes || []) {
                           const u = node.parameters?.url;
                           if (typeof u === 'string' && u.startsWith('http')) urls.add(u);
                         }
                       }

                       let failed = 0;
                       for (const u of urls) {
                         try {
                           const r = await fetch(u, { method: 'GET', redirect: 'follow' });
                           if (!r.ok) { console.error(`FAIL ${r.status}  ${u}`); failed++; }
                           else       { console.log   (`OK   ${r.status}  ${u}`); }
                         } catch (e) {
                           console.error(`ERR          ${u}  ${e.message}`); failed++;
                         }
                       }
                       process.exit(failed ? 1 : 0);
                       ```

                       Wire into `.github/workflows/validate.yml` so PRs that introduce broken URLs cannot merge.

                       ---

                       ## 5. Every workflow must have an Error Workflow attached

                       **Why:** None of our failing workflows alerted anyone. They failed silently and were only discovered via the weekly dashboard glance. An Error Trigger workflow turns a 404 into a Slack/email ping within seconds.

                       **Rule:** generate a single shared `workflow-error-notifier.json` that:

                       1. Starts with an **Error Trigger** node (`n8n-nodes-base.errorTrigger`).
                       2. 2. Formats the error, workflow name, node name, execution URL.
                          3. 3. Sends it via the project Gmail credential (`id: 1lLnVsSKehWVnwnW`) to `richardknapp134@gmail.com`, subject prefix `[n8n ERROR]`.
                            
                             4. Then in every other workflow's top-level `settings` block include:
                            
                             5. ```json
                                "settings": {
                                  "executionOrder": "v1",
                                  "errorWorkflow": "<ID of the error notifier workflow>"
                                }
                                ```

                                (Use the real workflow ID once the notifier is created. Do not duplicate per-workflow error handlers — one central notifier is simpler.)

                                ---

                                ## 6. n8n public API contract — PUT body rules

                                **Why:** The n8n Cloud public API is strict. A PUT to `/api/v1/workflows/{id}` with too many properties returns `400 additional properties`, and extra keys inside `settings` fail validation.

                                **Rule:** when round-tripping a workflow through the API, the PUT body MUST contain exactly these top-level keys and nothing else:

                                ```json
                                {
                                  "name": "...",
                                  "nodes": [...],
                                  "connections": {...},
                                  "settings": { "executionOrder": "v1" },
                                  "staticData": null
                                }
                                ```

                                **Do not include:** `id`, `active`, `tags`, `pinData`, `versionId`, `meta`, `createdAt`, `updatedAt`, `isArchived`, `triggerCount`, or any other fields from GET. Strip them.

                                **Inside `settings`**, only `executionOrder` (and `errorWorkflow` per rule #5) are safe. Fields like `availableInMCP`, `binaryMode`, `saveDataSuccessExecution`, `timezone` will fail schema validation in some tiers. Add others only after testing a single workflow first.

                                ---

                                ## 7. Auth contract — API key format

                                **Why:** One 45-minute debugging detour on this project was caused by assuming the API key format.

                                **Rule:** the n8n Cloud public API accepts:

                                - Endpoint base: `/api/v1/` (NOT `/rest/` and NOT `/public-api/v1/`)
                                - - Header: `X-N8N-API-KEY` (NOT `Authorization: Bearer ...`)
                                  - - Value: **bare JWT only**, no `n8n_api_` prefix. Strip any prefix before sending.
                                   
                                    - The `/rest/` endpoints require session cookies + `browser-id` header and will reject API keys with 401. Do not mix the two.
                                   
                                    - ---

                                    ## 8. Archived workflows cannot be modified

                                    **Why:** `PUT /api/v1/workflows/{id}` on an archived workflow returns `400 "Cannot update an archived workflow."` and the public API exposes no unarchive endpoint.

                                    **Rule:** before any programmatic update, check `isArchived`. If true, halt and instruct the user to unarchive in the UI (Workflows list → filter Archived → workflow → ⋮ → Unarchive). Do not attempt `/rest/...` unarchive calls from Claude — they require a live session.

                                    ---

                                    ## 9. Gmail Send nodes — standard wiring

                                    **Why:** Consistency, and because we've now proven this combination works on this instance.

                                    **Rule:** any generated workflow that emails the user uses:

                                    - Node type: `n8n-nodes-base.gmail`
                                    - - Operation: `send`
                                      - - Credential: `{ "id": "1lLnVsSKehWVnwnW", "name": "Gmail OAuth2 API" }`
                                        - - `sendTo`: `richardknapp134@gmail.com` (unless the brief specifies a different address)
                                          - - `emailType`: `html` (preferred) with a plaintext fallback in `options.appendAttribution = false`
                                           
                                            - Do not generate SMTP nodes; this account is OAuth-bound.
                                           
                                            - ---

                                            ## 10. Commit hygiene

                                            **Why:** Workflow JSON files in this repo are the source of truth that survives n8n Cloud session resets. They must always be installable-as-is.

                                            **Rule:** every PR that touches `n8n-workflows/*.json` must pass:

                                            1. `scripts/validate-urls.mjs` (rule #4).
                                            2. 2. A schema sanity check: all Code nodes have `typeVersion: 1` (rule #2), no `process.env` anywhere (rule #1), all scheduleTriggers have `triggerAtDay` as array (rule #3).
                                               3. 3. A smoke import: the JSON must parse and contain the top-level keys `name`, `nodes`, `connections` at minimum.
                                                 
                                                  4. Recommended single guard script: `scripts/lint-workflows.mjs` that enforces all three. Run it in CI.
                                                 
                                                  5. ---
                                                 
                                                  6. ## 11. Secrets policy
                                                 
                                                  7. **Why:** Obvious, but worth stating because n8n workflows sometimes tempt you to inline tokens.
                                                 
                                                  8. **Rule:** no secret value (API key, OAuth token, webhook verify token, database URL, bearer token) may appear in any committed workflow JSON. Secrets live in n8n Credentials only. If a workflow needs a verify token (e.g. WhatsApp webhook handshake), reference it via a Credential, not a hard-coded string.
                                                 
                                                  9. When Claude Code generates a workflow that requires a new secret, it must (a) leave a placeholder like `REPLACE_WITH_CREDENTIAL_ID` and (b) add a README note listing what the human operator must create in n8n before import.
                                                 
                                                  10. ---
                                                 
                                                  11. ## 12. External API credentials in HTTP Request nodes — invariants
                                                 
                                                  12. **Why:** The EquiSmile `Send Reply` node (WhatsApp Cloud API POST) failed end-to-end testing on 17 Apr 2026 with `NodeApiError: Invalid character in header content ["authorization"]`. Node.js's HTTP header parser rejects any header value containing characters outside visible-ASCII (`0x20`–`0x7E`). This happens when an access token is unset, contains a trailing newline or tab, or contains a smart quote from a formatted paste. The workflow had wired the Authorization header as `Bearer {{ $vars.WHATSAPP_ACCESS_TOKEN }}`, and `$vars.WHATSAPP_ACCESS_TOKEN` was either empty or contaminated.
                                                 
                                                  13. **Rule 12.1 — Use n8n Credentials, not inline expressions, for bearer tokens.** When generating an HTTP Request node that hits a third-party API (`graph.facebook.com`, `api.openai.com`, `api.anthropic.com`, any `*/messages` endpoint, any OAuth-protected resource), do NOT compose the Authorization header manually via `Bearer {{ $vars.X }}` or a Header Parameters entry. Instead, attach a Credential of type `httpHeaderAuth` or the platform-specific credential type (e.g. `whatsAppApi`), and leave the node's Authentication field set to that credential.
                                                 
                                                  14. **Forbidden pattern:**
                                                 
                                                  15. ```json
                                                      "headerParameters": {
                                                        "parameters": [
                                                          { "name": "Authorization", "value": "=Bearer {{ $vars.WHATSAPP_ACCESS_TOKEN }}" }
                                                        ]
                                                      }
                                                      ```

                                                      **Required pattern:**

                                                      ```json
                                                      "authentication": "predefinedCredentialType",
                                                      "nodeCredentialType": "whatsAppApi",
                                                      "credentials": {
                                                        "whatsAppApi": { "id": "REPLACE_WITH_CREDENTIAL_ID", "name": "WhatsApp Cloud API" }
                                                      }
                                                      ```

                                                      **Rule 12.2 — No `$vars` for secrets, ever.** n8n Variables (`$vars.X`) are not a secret store. They can be read from Code nodes, logged in execution data, and leaked via error traces. All secrets go in Credentials.

                                                      **Rule 12.3 — Lint token shape at build time.** Add to `scripts/lint-workflows.mjs`:

                                                      ```js
                                                      // Forbidden header-composition patterns
                                                      const badAuth = /Authorization.*=\s*Bearer\s*\{\{\s*\$vars\./;
                                                      const badInline = /"name":\s*"Authorization"[^}]*"value":\s*"[^"]*\{\{/;
                                                      // Fail on match in any workflow JSON.
                                                      ```

                                                      **Rule 12.4 — Whitespace-strip before use in Code nodes.** If a Code node ever reads a token value (rare, avoid if possible), strip whitespace and validate ASCII before use:

                                                      ```js
                                                      const tok = String(credRef || '').trim();
                                                      if (!/^[\x20-\x7e]+$/.test(tok)) throw new Error('Token contains invalid characters');
                                                      ```

                                                      **Rule 12.5 — Credential README.** Every generated workflow that requires an external-API credential must ship a README entry listing: credential type, where the human operator obtains the token (URL to the provider's dashboard), which n8n Credentials screen to create it in, and what scopes/permissions are required.

                                                      ---

                                                      ## 13. Change log

                                                      | Date | Rule | Origin |
                                                      |---|---|---|
                                                      | 2026-04-17 | Rules 1–11 established | Post-mortem of 6 failed production executions (DfE 404, EquiSmile typeVersion-2 crash, LMS Sync `process.env`) |
                                                      | 2026-04-17 | Rule 12 added | EquiSmile `Send Reply` node failed test webhook with `Invalid character in header content ["authorization"]` after successful handshake. WhatsApp Cloud API token was wired via `$vars.WHATSAPP_ACCESS_TOKEN` expression instead of n8n Credential. |

                                                      When a new production failure produces a new rule, add a row here and a numbered section above. Do not remove rules without noting why.
                                                      

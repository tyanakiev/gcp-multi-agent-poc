# ADK Adoption Plan (detailed)

Current: ADK is not in use.

Goal: Introduce an Agent Development Kit (ADK) to standardize agent creation and orchestration in this GCP multi-agent PoC.

High-level recommendation
- Recommended starting point for this repo: Autogen (or a similar agentic ADK) with Python runtime.
  - Why: Autogen is designed for multi-agent workflows, has clear orchestration patterns, and works well with Python ecosystem tools for GCP (Pub/Sub, Cloud Run, GKE).
  - Alternative choices:
    - Microsoft Semantic Kernel (SK): good for prompt orchestration and stateful skills (C#/Python).
    - LangChain Agents (Node/Python): flexible and popular, more general-purpose.
    - Custom lightweight SDK: if you want full control and minimal dependencies.

Step-by-step plan
1. Choose ADK + runtime
   - Option A (recommended): Autogen + Python 3.11
   - Option B: Semantic Kernel + .NET / Python
   - Option C: LangChain Agents + Node.js / Python

2. Repo-level changes
   - Add dependency manifest:
     - Python: requirements.txt (autogen, google-cloud-pubsub, structlog, pytest)
     - Node: package.json (langchain, google-cloud-pubsub)
   - Add Dockerfile per runtime.
   - Add code formatter config (black/pre-commit or prettier).

3. Scaffold code (templates)
   - agent_template.py (agent lifecycle: init, handle_message, send_message, health)
   - orchestrator.py (task dispatcher, retry, timeouts, metrics)
   - pubsub_helper.py (publish/subscribe wrappers, ack, backoff)
   - auth helper (use GCP service account via ADC)

4. Communication & integration
   - Use Google Pub/Sub for agent messaging in PoC.
   - Define a simple message envelope (id, from, to, kind, payload, trace_id).
   - Define storage contract for shared state (Cloud Storage / Firestore).

5. Observability & reliability
   - Structured logs with trace_id.
   - Basic metrics (requests, errors, queue depth).
   - Health checks (ready/liveness endpoints for Cloud Run / k8s).
   - Retries with exponential backoff and dead-letter topics.

6. Deployment & CI
   - Build Docker images and push to Container Registry / Artifact Registry.
   - Deploy to Cloud Run for fast iteration; move to GKE for more complex orchestration.
   - Add a GitHub Actions job: lint -> unit tests -> build image -> push -> (optional) k8s deploy.

7. Testing & validation
   - Local simulator for pub/sub (or use emulator).
   - Unit tests for agents and orchestrator.
   - Integration test that spins up a small local environment or uses test GCP project.

Deliverables (concrete files to add)
- requirements.txt
- Dockerfile
- templates/agent_template.py
- orchestrator.py
- pubsub_helper.py
- infra/cloudrun.yaml or infra/k8s/deployment.yaml
- .github/workflows/ci.yml
- docs/agent-contract.md (message envelope + retries + SLA)

Minimal milestone timeline (two-week PoC)
- Day 0–2: Choose ADK + runtime, add dependency manifest, Dockerfile.
- Day 3–6: Scaffold agent + orchestrator, add pub/sub helper.
- Day 7–10: Add CI pipeline, deploy to Cloud Run (dev), smoke tests.
- Day 11–14: Observability, retries, integration tests, demo.

Next actions (pick one)
- I can generate the Python scaffold (requirements.txt, Dockerfile, agent_template.py, orchestrator.py, pubsub_helper.py) using Autogen patterns.
- I can generate a minimal GitHub Actions CI + Cloud Run deploy manifest.
- I can produce k8s manifests with health checks and HPA.

Apply the SDK across the repo (concrete plan)
- Goal: Integrate the chosen ADK (recommend Autogen + Python) into the codebase with minimal, incremental changes so each agent and the orchestrator use shared SDK primitives.

High level steps
1. Add SDK deps and toolchain
   - requirements.txt: add autogen, google-cloud-pubsub, structlog, pydantic (for message envelopes), pytest.
   - Dockerfile: install requirements and expose health endpoints.

2. Add an SDK integration layer (one-time files)
   - sdk/base_agent.py: base Agent class (lifecycle hooks, logging, message envelope).
   - sdk/orchestrator_base.py: orchestrator primitives (dispatch, retries, metrics hooks).
   - sdk/pubsub_client.py: thin wrapper around google-cloud-pubsub with envelope encoding/decoding and DLQ support.
   - sdk/config.py: central config loader (env / secret / ADC).

3. Refactor existing agents and orchestrator
   - Update each agent file to inherit sdk.base_agent.Agent and implement handle() method.
   - Replace direct Pub/Sub logic with sdk.pubsub_client.publish/subscribe.
   - Minimal changes per agent: adapt message shape and call super().init for setup.

4. CI/CD and infra
   - .github/workflows/ci.yml: lint, unit tests, build image, push image.
   - infra/cloudrun.yaml (or k8s): ensure health/readiness endpoints and service account setup.

5. Observability & testing
   - Use structlog + trace_id in SDK base.
   - Add unit tests for sdk.* modules and adapter tests for agents.
   - Use Pub/Sub emulator for local integration tests.

Concrete per-file actions (apply these changes incrementally)
- requirements.txt
  - Add SDK + deps and pin minimal versions.

- Dockerfile
  - Install Python 3.11, copy requirements.txt, pip install -r requirements.txt, add health endpoint.

- sdk/base_agent.py (new)
  - Provide Agent base class: init(), start(), handle_message(), send(), health endpoint helpers.

- sdk/orchestrator_base.py (new)
  - Provide Orchestrator base: schedule(), dispatch(), retry policy helpers, metrics hooks.

- sdk/pubsub_client.py (new)
  - Wrap Pub/Sub client: publish(envelope), subscribe(handler), ack, DLQ.

- sdk/config.py (new)
  - Load configuration from environment and Google ADC.

- src/agents/*.py (modify)
  - Replace direct Pub/Sub / HTTP wiring with subclassing base_agent.Agent and implement a single handle(payload, ctx) method.

- src/orchestrator.py (modify)
  - Inherit sdk.orchestrator_base.Orchestrator and use sdk.pubsub_client for message routing and DLQ handling.

- .github/workflows/ci.yml (modify/create)
  - Add jobs: lint (black/ruff), test (pytest), build+push.

- infra/cloudrun.yaml or infra/k8s/*.yaml (modify/create)
  - Add readiness/liveness endpoints, set concurrency and service account.

Migration checklist
- Create SDK modules and add to repo.
- Update one agent to use SDK end-to-end and validate in dev.
- Incrementally migrate remaining agents, run integration tests after each migration.
- Update CI to fail if coverage for sdk modules drops.
- Finalize docs: docs/agent-contract.md describing envelope and retry semantics.

Immediate next step
- I will generate the Python scaffold (requirements.txt, Dockerfile, sdk/* template files, one sample agent and updated orchestrator) when you confirm. Pick "generate scaffold" to proceed.

# Model Context Standard (MCS)

**A lightweight alternative to MCP – removing the fluff.**

MCS describes a simple, robust and protocol‑agnostic approach to connecting language models with external tools. Unlike MCP, which introduces a custom protocol stack with transport, initialization and messaging layers, MCS asks a simpler question: *What is technically necessary to connect LLMs to external systems?*

At the end of the day, function-calling LLMs need to connect to the environment, and MCS provides the absolute minimum required to make that happen. Without any further "decoration".

## Core Idea

```
LLM ──► JSON call ──► Parser/Driver ──► Bridge ──► External API
                       ▲                          │
                       └──────── Result ◄─────────┘
```

1. **Bridge** – a transport layer (e.g. HTTP, CAN, AS2)
2. **Spec** – a structured description of available functions (e.g. OpenAPI)

That’s all. The model emits structured calls, a driver executes them via the bridge and returns the result.

---

## Why MCS?

* Uses existing standards instead of inventing new ones
* Avoids the security pitfalls of custom stacks (unlike MCP)
* Leverages familiar tooling such as Swagger, Postman, FastAPI, Express, Spring Boot
* Enables reuse of existing APIs without refactoring
* Supports optional autostart via containers (Docker)
* Allows domain‑specific drivers: REST, EDI/AS2, CAN‑Bus, OPC‑UA …

MCS acts like a **device‑driver model**: once a driver for a domain exists, any application (or LLM) can access that domain in a consistent way.

---

## What This Repo Provides

* Reference driver: **REST over HTTP**
* Working FastAPI backend \<placeholder‑link>
* OpenAPI‑based service discovery
* Minimal parser to extract and execute model‑generated calls

### Quick Start

```bash
# clone and run demo driver
$ git clone <repo-url>
$ cd mcs
$ docker compose up -d        # starts the FastAPI demo bridge
```

Point your LLM (e.g. ChatGPT with Browser) to `http://localhost:8000/openapi.json` and watch it call the Fibonacci tool.

---

## Proof of Concept – try MCS in 2 minutes

You can verify the MCS pattern with *any* LLM that has web access by spinning up the tiny FastAPI demo included in this repo.

```bash
# clone on a VPS / cloud VM with a public DNS or IP
$ git clone <repo-url>
$ cd modelcontextstandard
$ docker compose -f docker/quickstart/docker-compose.yml up -d  # exposes :8000 on your public host
# optional: use a tunnel such as ngrok or cloudflared if you do not have a static IP
```

> 🛠️ Tip: Platforms like **[Coolify](https://coolify.io)** or **Render** make one‑click deployment of Dockerised apps very easy.

No server handy? A public demo is **temporarily** available at:

```
https://mcs-quickstart.coolify.alsdienst.de
```

(as long as the endpoint is up).

The demo service is implemented in [`fastapi_server_mcs_quickstart.py`](mcs/examples/fastapi_server_mcs_quickstart.py) and exposes two endpoints:

| Path                  | Purpose                                            |
| --------------------- | -------------------------------------------------- |
| `/openapi-html`       | serves the OpenAPI spec as HTML (LLM‑readable)     |
| `/tools/fibonacci?n=` | returns *2 × Fibonacci(n)* to detect hallucination |

### How to test with an LLM

1. Ensure the demo is reachable under a **public domain** (or use the hosted URL above).
2. Ask the LLM to fetch `/openapi-html` and construct the URL for the Fibonacci tool.
3. In a second prompt, ask the LLM to visit that URL (e.g. `...?n=8`).
4. A correct call returns **42**. If the model answers **21**, it hallucinated.

| Model                 | Result | Notes                                                                                              |
| --------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| ChatGPT (Browser)     | ✅      | Requires two prompts → [sample](https://chat.openai.com/share/68582042-280c-8009-8e18-d44cb72a4a2) |
| Claude 3 (web access) | ✅      | Needs two‑step flow → [sample](https://claude.ai/share/57128a2d-22f8-440f-a09d-41018459d94f)       |
| Gemini                | ❌      | Refuses second request                                                                             |
| Grok                  | ❌      | Mis‑parses OpenAPI and builds wrong URL                                                            |
| DeepSeek              | ❌      | Hallucinates, cannot target URL                                                                    |

> 🔍 POST requests are *not* required for this smoke test. Simple GETs confirm that the pattern works. Extending the driver to support POST + JSON is straightforward.


---

## How to Contribute

We welcome contributions that

* refine the formal description of the MCS pattern
* provide **new drivers** for other transport layers or data formats

Feel free to fork, extend and build upon this codebase.

> **Proof‑of‑Work Notice** – This repository is shared *as is*. Pull requests and issues are welcome, but there is **no guarantee** of review, merging or long‑term maintenance. Contributions will be evaluated based on alignment with the research goals and available time.

---

## Limitations

MCS is a pattern, **not** a full framework. For every new protocol or format you still need to supply a driver/bridge. This repo ships exactly one: REST over HTTP.

---

## License

\<placeholder‑license>

---

## Contact

Open a [Discussion](placeholder‑link) or mention @\<your‑username> in an Issue/PR.

If you build something on top of MCS, we would love to hear about it!

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

## Proof of Concept – test MCS in 2 minutes

You can try MCS with *any* LLM that has web access by serving a tiny FastAPI demo contained in this repo.

```bash
# clone on a VPS / cloud VM with a public DNS or IP
$ git clone <repo-url>
$ cd modelcontextstandard
$ docker compose -f docker/quickstart/docker-compose.yml up -d  # exposes :8000 on your public host
# optional: use an edge tunnel such as ngrok/cloudflared if you don't have a fixed IP
```

> 🛠️ Tip: Tools like [Coolify](https://coolify.io) or Render make deployment of Dockerized apps very straightforward.

Point your LLM to `https://your-domain.example:8000/openapi-html` and follow the steps below.

1. **Start the demo server** (already running if you executed `docker compose -f .\docker\quickstart\docker-compose.yml up -d`). 
It exposes two endpoints:

   * `/openapi-html` – returns the OpenAPI spec as HTML (ChatGPT‑browser compatible)
   * `/tools/fibonacci` – returns the Fibonacci number for `n`, doubled to verify the model calls the live endpoint
2. **Paste** `http://localhost:8000/openapi-html` into your LLM chat and ask the model: "Call the Fibonacci tool for n = 8".
3. The model should fetch the spec, generate the structured function call and return **34** (the doubled value of Fibonacci‑8). 
4. If it returns **21**, you know it hallucinated instead of calling the API.

> ✨ This works with ChatGPT (browser plugin), Claude with web‑access and any agent framework that can read an OpenAPI spec.

POST requests are not required for the demo; simple GETs already prove the pattern. Extending the driver to accept POST+JSON is straightforward and left as an exercise.

---

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

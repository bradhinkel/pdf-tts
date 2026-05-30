# Training Demo — pdf-tts as a "First Build with Claude" Project

Design notes for using this project as a hands-on teaching project (part of **Praxium**).
Captured from a working conversation on 2026-05-29.

---

## Why this project exists

Praxium's goal: help smart, experienced, technical people become hands-on **builders**
using Claude — not by reading, but by building a simple-but-real project themselves,
guided by a **set of prompts**. The app is just the vehicle. The real lessons are two:
the **builder toolset** and the **AI-agent engagement workflow**.

## Audience

PMs, program managers, engineers from large tech orgs, designers — smart people who
understand tech and can navigate signups, keys, and tokens.

- Big-company engineering is **heavy on formal process**. A lot of practical building
  skill is learned by engaging tools and services **outside the corporate walls**
  (Amazon/Google/Microsoft). This project deliberately lives in that outside-the-walls,
  garage-developer space.
- The real cliff for non-engineers is **the basics** — just facing VS Code, or operating
  inside a Linux shell. Expect that and scaffold it; it is not a knowledge gap, it is a
  first-contact gap.
- All of these people — engineers and non-engineers alike — will learn from the process.

## Two things it teaches

### A. The builder toolset ("garage developer" tools)

Chosen deliberately because these are durable, transferable skills:

- Install and work in **VS Code**.
- Stand up a Linux build environment: **Ubuntu on Windows (WSL)**, or a **Linux dev
  environment on Mac**.
- Set up a basic **Python development environment** (venv, pip).
- Get and deploy to a **personal cloud droplet** (e.g. DigitalOcean).
- Pull **models / code from Hugging Face** (the Piper voice model downloads from there).

### B. AI-agent engagement (the multi-surface workflow)

The arc the prompt-set walks them through:

1. **Claude Chat** — explore and shape the idea.
2. Hand the conversation to **Claude Cowork**.
3. Cowork builds a **project plan + `.md` spec**.
4. Pass the `.md` to **Claude Code** — build the project.
5. *(next step)* **Claude Design** creates a creative UI.
6. Design hands its spec back to **Claude Code** to implement.

This teaches how to **carry context between tools** and let each surface do what it does
best — which is the real skill, more than the app itself.

## The project: pdf-tts (kept deliberately simple)

A FastAPI + React app: upload a PDF, hit play, listen.

- **TTS: Piper only.** Free, self-hosted, no API keys; the voice model auto-downloads
  from Hugging Face. Azure and XTTS are **intentionally dropped** from the learner path —
  API keys/billing and PyTorch/GPU issues are footguns that teach nothing transferable.
  Show them only as "what this could grow into."
- Frozen reference state: tag **`demo-v1`** in this repo.

## Time expectation

More than 4 hours, but not a lot more.

- Reference point: the author built idea → running website in **~2 hours** — but already
  had the droplet, the coding environment, and the experience in place.
- The **build with Claude Code is fast.** The **setup tail** — WSL/Linux, Python env,
  droplet, DNS/SSL, Hugging Face — is where a first-timer's extra time goes. Scaffold it.
- Consider staging the work:
  - **Session 1** — local build; hear your own PDF read aloud (a complete win, no keys).
  - **Session 2** — deploy to your own droplet at your own domain.

## Teaching principles

- **Pre-write recovery prompts from real scars.** This project has already been debugged
  (PyTorch `torch.load` weights_only change, WAV PCM_16 format, Piper standalone binary
  because there's no Python 3.12 wheel). Turn each into a "when you see X, ask Claude to do
  Y" moment. Teaching **how to recover when Claude's output breaks** is the highest-value
  lesson — and it's only teachable on a project the teacher has already broken.
- **Keep one golden path** — Piper, local-first, no optional branches in the core flow.
- **End on a win**, not a broken nginx config.

## Still to build

- The actual **prompt set** (the sequence learners paste), plus the **demonstration
  artifacts** produced along the way:
  - the originating Claude Chat conversation,
  - the Cowork-generated plan `.md`,
  - the Claude Code build session,
  - (later) the Claude Design output and its handoff back to Code.
- At least **one more example project** that is *non-audio, local-only, and visually
  richer* (better for the Design-handoff lesson) so the curriculum teaches the **method**,
  not one domain's quirks.

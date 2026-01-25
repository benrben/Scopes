# Why Scopes (and why these commands exist)

Scopes are a deliberate answer to a common failure mode: **code changes fast, docs drift faster**.

## The idea in one paragraph
Raw codebases are high-entropy: lots of files, lots of local detail, and not enough product meaning. Scopes act as a **compression + navigation layer**: a map (`Scopes/INDEX.md`) and a graph (`Scopes/GRAPH.md`) plus evidence-backed capability docs (`Scopes/Product/**`) that describe what the system does today.

## What makes Scopes different
- **Behavior-first**: describe what the software does today, not what we hope it does.
- **Evidence-required**: meaningful claims link to proof (code/tests/config/schema).
- **Maintained as part of dev**: the commands in `Scopes/Prompts/` treat “update the truth” as part of normal work.

## References
If you want to go deeper, these are good starting points:

- [Beyond Code Generation: LLMs for Code Understanding](https://dev.to/eabait/beyond-code-generation-llms-for-code-understanding-3ldn)
- [CodeWiki: Evaluating AI's Ability to Generate Holistic Documentation for Large-Scale Codebases](https://arxiv.org/html/2510.24428v3)
- [SARA: Selective and Adaptive Retrieval-augmented Generation with Context Compression](https://arxiv.org/abs/2507.05633)


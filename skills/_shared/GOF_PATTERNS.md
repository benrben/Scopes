# Design Patterns Cheat Sheet (GoF + Modern)

This is a **shared vocabulary** for naming and comparing common design patterns in this repo’s skills/agents.
Use it to **recognize**, **communicate**, and **choose** patterns — not to “patternize” code that doesn’t need it.

The “GoF” catalog refers to the 23 classic patterns from *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma/Helm/Johnson/Vlissides).
This doc also includes a curated set of **non-GoF** patterns that commonly show up in modern systems and ADRs.

## How to use this doc (rules of thumb)

- **Prefer the simplest thing** that keeps responsibilities clear and testable.
- **Follow existing patterns first**: if the codebase already solves a similar problem, use that as the pattern reference.
- **Patterns are tradeoffs**: always consider what you’re *buying* (clarity, isolation, extensibility) and what you’re *paying* (indirection, coupling, complexity).
- **Pattern evidence**: when recommending a pattern, point to the concrete smell/constraint it addresses:
  - branching explosion
  - cross-cutting concerns
  - boundary mismatch
  - lifecycle leaks
  - test pain
  - unclear ownership
  - unstable dependencies

## Recommended usage by skill/agent (ScopesCommands)

- **Levels**
  - **Full**: know all 23; can recommend/compare/remove patterns; can spot common misuses.
  - **Implementation**: apply a practical subset; recognize the full catalog to avoid footguns and misnaming.
  - **Light**: use pattern terms consistently in plans/tasks; don’t invent new abstractions.
  - **Risky-subset**: recognize bug-prone pattern failure modes (lifecycle, hidden state, hidden latency).
  - **Minimal**: only keep vocabulary correct when Scopes/docs mention patterns.

- **Full catalog knowledge (use pattern names to propose/refactor/review)**:
  - Skills: `scanning-refactor`, `planning-refactor`, `researching-decisions`
  - Agents: `refactor-scanner`, `code-simplifier`, `code-reviewer`
- **Implementation-focused (apply a practical subset; recognize full catalog to avoid footguns)**:
  - Skills: `developing-tdd`, `developing-verified`
- **Light vocabulary only (label patterns seen in upstream artifacts; don’t invent patterns)**:
  - Skills: `planning-idea`, `writing-tasks`
- **Risky-pattern subset (pattern awareness for hotspot scanning)**:
  - Agent: `bug-scanner`
- **Optional/minimal**: keep correct vocabulary if Scopes/docs mention patterns.

| Skill / Agent | Level | Main use of patterns |
|---|---|---|
| `scanning-refactor` | Full | Recognize + recommend (evidence-backed), avoid overuse |
| `planning-refactor` | Full | Plan safe steps that introduce/remove patterns |
| `refactor-scanner` | Full | Same as `scanning-refactor`, as an agent output artifact |
| `code-simplifier` | Full | Simplify toward clarity; remove accidental patterns; align to existing patterns |
| `code-reviewer` | Full | Spot misuses/over-engineering; suggest better fit when high-confidence |
| `developing-tdd` | Implementation | Apply practical subset; avoid footguns; keep changes test-backed |
| `developing-verified` | Implementation | Same as `developing-tdd`, using existing verification signals |
| `researching-decisions` | Full | Compare alternatives (often “pattern vs pattern”) in ADRs |
| `planning-idea` | Light | Label patterns when already present; keep plan language consistent |
| `writing-tasks` | Light | Reference patterns from upstream plan/scan artifacts; keep task wording consistent |
| `bug-scanner` | Risky-subset | Target hotspots caused by risky pattern failure modes |
| `syncing-scopes` / `querying-scopes` / scope agents | Minimal | Preserve vocabulary if Scopes/docs mention patterns |

## Decision checklist

Before picking a pattern, answer:

1. What changes most often? (algorithm, state, integration boundary, orchestration flow, object construction)
2. Where do we want the seam? (tests, feature flags, environment differences, vendor swaps)
3. Who owns lifecycle? (creation, cleanup/unsubscribe, retries, cancellation)
4. Do we need composition or inheritance? (prefer composition unless there’s a stable skeleton)
5. What failure modes must stay visible? (don’t hide errors behind “convenient” facades/proxies)

## Abstraction gate (do we need a pattern at all?)

Before introducing *any* new abstraction layer, answer:

- Are there (or will there soon be) **2+ real variants**? If not, prefer a function + clean naming.
- Will the pattern create a **test seam** (easier mocking/injection), or will it make tests harder?
- Is the complexity **local and contained**? If yes, keep it local (avoid exporting a new “framework”).
- Can you solve it with **data/config** instead of new types (tables, maps, declarative rules)?
- Are you about to **hide important failures** (latency, auth checks, partial failures)? If yes, stop and redesign.
- Would deleting/flattening code be simpler? In this repo, “less code” is usually the win.

## Quick chooser (high-signal mapping)

- **Many `if/switch` branches that select behavior** → **Strategy** (or **State** if behavior depends on internal state transitions).
- **Different “states” with legal transitions** → **State** (model the transitions; eliminate invalid combos).
- **Need to wrap optional behavior** (logging, metrics, retries, caching, auth checks) → **Decorator**.
- **Need a boundary translation** (third-party/legacy types to your interface) → **Adapter**.
- **Need a simpler entrypoint to a subsystem** → **Facade**.
- **Need access control / lazy init / remote placeholder** → **Proxy**.
- **Need to represent trees uniformly** → **Composite**.
- **Need to build complex objects step-by-step** → **Builder**.
- **Need to create objects without coupling to concrete classes** → **Factory Method** (or **Abstract Factory** for families).
- **Need notifications/subscriptions** → **Observer** (but watch lifecycle leaks).
- **Need to encapsulate an action as data** (queue/undo/retry/log) → **Command**.
- **Routing by request type/key to exactly one handler** → **Dispatch Table** (Handler Map / Responsibility Map).
- **Need algorithm skeleton with overridable steps** → **Template Method**.
- **Need stable traversal without exposing internals** → **Iterator**.
- **Need to restore previous state** (undo/history) → **Memento**.
- **Need to run operations across many concrete types** → **Visitor** (when adding operations is more common than adding types).
- **Need to parse/evaluate a small language/DSL** → **Interpreter** (often replaced by real parsers).
- **Need to isolate core logic from frameworks/IO** → **Hexagonal Architecture** (Ports & Adapters).
- **Remote call failures causing cascading failures** → **Circuit Breaker** (often paired with Retry/Bulkhead).
- **Need reliable events/messages with DB changes** → **Transactional Outbox**.
- **Need multi-step distributed consistency** → **Saga**.

## Axis-of-change map (what varies → likely patterns)

| What varies? | Start with | Often becomes |
|---|---|---|
| Algorithm / policy | Strategy (function/map) | Strategy (objects) + Factory Method |
| Request type → handler routing | Dispatch table (map key → handler) | Dispatch table + Command + (optional) DI/Registry |
| Internal lifecycle states | Explicit enum + transition table | State (explicit transitions) |
| Boundary shapes (vendor/transport) | Adapter (pure mapping) | Adapter + Facade (thin) |
| Cross-cutting concerns | Decorator (HOF/wrapper) | Decorator stacks / Chain of Responsibility |
| Object construction complexity | Builder / factory function | Builder + validation + Factory Method |
| Many-to-many interactions | Mediator / Facade coordinator | Mediator (interaction-only) |
| Notifications/events | Observer (with explicit lifecycle) | Observer + Mediator (to reduce coupling) |
| Undo/redo/history | Command records | Command + Memento (snapshots/diffs) |
| Tree structures | Composite | Composite + Visitor / Iterator |
| Parsing rules/expressions | Interpreter (tiny grammar) | Real parser + AST (if it grows) |

## Refactor recipes (smell → smallest move)

- **Branching explosion** → start with a Strategy seam (inject a function/interface), then extract Strategy objects if needed.
- **State explosion / invalid combinations** → introduce explicit State transitions; make invalid transitions impossible.
- **Boundary mismatch (vendor/legacy shapes)** → add a dedicated Adapter at the boundary; keep domain types clean.
- **Cross-cutting concerns everywhere** → wrap with Decorators; keep order observable and side effects explicit.
- **Messy multi-call subsystem usage** → add a thin Facade (or a Mediator-style coordinator); avoid “god” APIs.
- **Long `if/switch` that routes requests** → replace with a **Dispatch Table** (key → handler), with explicit “unknown key” behavior.
- **Need undo/history/redo** → pair Command (action as data) with Memento (state snapshots/diffs).

## Low-ceremony forms (start here)

Many patterns have a “lightweight” form that’s often enough:

- **Strategy**: pass a function or select from a `{ key: fn }` map before creating classes/objects.
- **Decorator**: higher-order function / wrapper that returns a function with extra behavior.
- **Chain of Responsibility**: an ordered list/array of handler functions.
- **Command**: `{ type, payload }` records or small “execute” objects — make serializable only if needed.
- **Facade**: a small module with 2–6 functions that centralize subsystem coordination.
- **Adapter**: pure mapping functions at boundaries (parse/normalize once; keep domain clean).

If a lightweight form works, keep it. Promote to “full pattern” only when benefits are clear.

## Refactor path sketches (incremental, green-to-green)

These are the smallest safe sequences to “refactor toward” a pattern without a rewrite:

- **To Strategy**
  1. Extract each branch into a named function.
  2. Replace the conditional with a `{ key: fn }` dispatch map.
  3. If needed, formalize the interface and move strategies into their own module.
- **To State**
  1. Replace boolean flags with a single explicit state enum/value.
  2. Centralize transitions in one function/table; reject invalid transitions.
  3. If state-specific behavior grows, move behavior behind state objects.
- **To Adapter**
  1. Introduce domain types that are independent of vendor/transport.
  2. Add one mapping layer at the boundary (parse/normalize once).
  3. Remove vendor types from core/business logic signatures.
- **To Decorator / Chain**
  1. Identify cross-cutting behavior; extract wrapper functions.
  2. Make wrapper order explicit (compose in one place).
  3. Add observability (logs/metrics) so wrapper stacks aren’t opaque.
- **To Facade**
  1. Identify repeated multi-call sequences across call-sites.
  2. Create a thin facade that exposes the smallest useful API.
  3. Keep errors/options visible; don’t collapse meaningful controls.
- **To Command (+ Memento)**
  1. Represent the action as data (`type`, `payload`, `id`).
  2. Add `execute()` in one place; add retries/idempotency rules if needed.
  3. If undo/redo needed, add mementos (snapshots/diffs) and round-trip tests.

## Common confusions (pick intentionally)

- **Strategy vs State**
  - **Strategy**: interchangeable algorithms selected by the *caller* (or configuration).
  - **State**: behavior selected by the *object’s internal state* + transitions between states matter.
- **Adapter vs Facade**
  - **Adapter**: makes one thing look like another (interface conversion at a boundary).
  - **Facade**: provides a simpler API to a complex subsystem (simplify usage, not convert types).
- **Decorator vs Proxy vs Facade**
  - **Decorator**: adds behavior while keeping the same interface.
  - **Proxy**: controls access to the underlying object (lazy, remote, protected).
  - **Facade**: new API surface that hides subsystem complexity.
- **Factory Method vs Abstract Factory vs Builder**
  - **Factory Method**: subclasses decide what to instantiate (one product family).
  - **Abstract Factory**: create related products that must work together (families).
  - **Builder**: construct one complex object step-by-step (configurable assembly).

## Misuse watchlist (things that often go wrong)

- **Singleton**: introduces hidden global state, makes tests brittle, complicates lifecycle/cleanup.
- **Observer**: memory leaks (missing unsubscribe), duplicate subscriptions, ordering hazards.
- **Abstract Factory**: over-abstraction when you only have 1 implementation; increases indirection.
- **Proxy/Facade**: can hide failures/latency; make side effects and error handling explicit.
- **State**: can become “boolean explosion” if transitions aren’t explicit and validated.
- **Visitor**: painful if you frequently add new concrete types (every visitor must update).

## Testing & observability checklist (high-signal)

When a change introduces (or relies on) a pattern, make sure these stay true:

- **Strategy**: each strategy has focused tests; selection logic is explicit; shared invariants are tested once.
- **State**: transitions are explicit and validated; invalid transitions are tested; persistence/rehydration is covered if applicable.
- **Observer**: subscription lifecycle is explicit; unsubscribe/cleanup is tested; handlers are idempotent or deduped.
- **Decorator / Chain**: wrapper/handler order is deterministic and observable; errors propagate correctly; timeouts/cancellation aren’t swallowed.
- **Proxy**: latency/failure modes are visible (metrics/logging); caching behavior is tested (hits/misses/invalidation).
- **Facade / Mediator**: does not swallow important errors; call-sites become simpler; “god object” creep is resisted.
- **Factories / Builders**: validate inputs; keep invariants enforced; tests cover defaults and invalid configs.

## How to reference patterns in artifacts (scans/plans/tasks/ADRs)

When you name a pattern in an artifact, include:

1. **Smell/constraint** (what is broken/hard today?)
2. **Candidate pattern** (name it)
3. **Why it helps** (what it buys)
4. **What it costs** (the “Pay”)
5. **Smallest safe steps** (green-to-green; reversible)
6. **Verification** (exact command/signal)

## Implementation notes for skills/agents

Patterns become more useful when you name the role objects consistently:

- **“Policy/Algorithm” objects** → Strategy (`ScoringStrategy`, `RetryPolicy`)
- **“Lifecycle + transitions” objects** → State (`JobState`: `Queued → Running → Done`)
- **“Boundary edge” objects** → Adapter (`VendorXClientAdapter`)
- **“Subsystem coordinator” objects** → Facade (`SearchFacade`, `IndexingFacade`)
- **“Cross-cutting wrapper” objects** → Decorator (`InstrumentedClient`, `CachedRepo`)
- **“Action record” objects** → Command (`RunScanCommand`, `ApplyPatchCommand`)

Rule of thumb: if you can’t name the role cleanly, you probably don’t need the pattern yet.

## Patterns in ScopesCommands workflows (practical mapping)

These patterns show up in this repo even when you’re not writing OO code:

- **Command**: Slice Contracts / task files are “do X under constraints” records (target, ownership, guard).
- **Template Method**: `SKILL.md` workflows are skeletons with stable phases and overridable details.
- **State**: phase-gated loops (RED → GREEN → REFACTOR; preflight → implement → refactor → review).
- **Strategy**: choosing verification signals, routing approach (`developing-tdd` vs `developing-verified`), or swapping implementations behind a stable interface.
- **Chain of Responsibility**: middleware/pipeline style processing where handlers are reorderable.
- **Mediator/Observer**: orchestrator + hooks coordinate agents without direct coupling.

---

## Catalog (23 patterns)

The GoF catalog is typically grouped into Creational (5), Structural (7), and Behavioral (11).

### Creational (5)

#### Factory Method
- **Intent**: defer object creation to subclasses / a method override.
- **Use when**: you need extensible creation without coupling to concrete classes; testing benefits from swapping implementations.
- **Smell**: lots of scattered `new X(...)` / `switch` on “type” to decide which concrete implementation to create.
- **Pay**: can fragment construction logic across subclasses.
- **Avoid when**: a simple constructor or small factory function is enough.
- **Tip**: start as a plain factory function; promote to Factory Method only if subclassing/overrides are truly needed.
- **Tests**: great seam — swap a test subclass or inject a factory function.

#### Abstract Factory
- **Intent**: create **families** of related objects that must be used together.
- **Use when**: you must ensure compatible product sets (e.g., UI widgets per platform).
- **Pay**: extra indirection (“factory of factories”).
- **Smell**: “we need to swap multiple related implementations together.”
- **Avoid when**: there’s only one family; it tends to over-abstract early.
- **Tip**: keep product families cohesive; don’t let “one factory” drift into unrelated responsibilities.
- **Tests**: verify each factory produces a compatible set; add a “swap the whole family” integration test if that’s the point.

#### Builder
- **Intent**: build a complex object in steps, varying representation independently.
- **Use when**: constructors have too many parameters; you need readable assembly and validation.
- **Smell**: “telescoping constructors”, optional args everywhere, or call-sites constructing the same complex thing inconsistently.
- **Pay**: more moving parts; sometimes a plain config object is enough.
- **Avoid when**: the object is simple; a plain constructor/config object is clearer.
- **Tip**: keep builder immutable or validate at `.build()`.
- **Tests**: cover defaults, missing/invalid fields, and that `.build()` enforces invariants.

#### Prototype
- **Intent**: create new objects by copying an existing “prototype”.
- **Use when**: cloning is cheaper/simpler than constructing from scratch; you need runtime-configured instances.
- **Smell**: expensive setup code repeated for many “mostly similar” instances; “copy the same config then tweak 1 field”.
- **Pay**: deep vs shallow copy footguns; hidden shared references.
- **Avoid when**: copying is subtle (deep vs shallow), carries hidden references, or violates invariants.
- **Tip**: prefer explicit `copy()` semantics + tests for aliasing.
- **Tests**: prove whether copies share references; add regression tests for accidental shared mutable state.

#### Singleton
- **Intent**: ensure only one instance exists, globally accessible.
- **Use when**: extremely rare; prefer explicit dependency injection + lifecycle management.
- **Smell**: “I need access to this everywhere” or “it’s annoying to thread this dependency through”.
- **Pay**: global state, hidden dependencies, unclear lifecycle, brittle tests.
- **Avoid when**: almost always in testable systems.
- **Tip**: if forced, make lifecycle explicit (init/shutdown) and keep a way to reset/replace in tests.
- **Tests**: add isolation tests to ensure global state doesn’t leak across test cases.

### Structural (7)

#### Adapter
- **Intent**: convert one interface into another expected by clients.
- **Use when**: integrating third-party/legacy code; stabilizing boundaries (HTTP/DB/vendor shapes → domain types).
- **Smell**: business logic depends on vendor/transport types directly; conversion happens in many call-sites.
- **Pay**: can become a “leaky adapter” if it keeps exposing vendor concepts.
- **Avoid when**: you’re only simplifying usage (that’s **Facade**, not Adapter).
- **Tip**: map to your domain language; don’t just rename methods.
- **Tests**: table-driven mapping tests (input → normalized domain shape), including missing/extra fields and version drift.

#### Bridge
- **Intent**: separate abstraction from implementation so both vary independently.
- **Use when**: you have orthogonal dimensions of change (e.g., “shape” × “renderer”).
- **Smell**: combinatorial explosion of subclasses for two independent axes (“A1B1”, “A1B2”, “A2B1”…).
- **Pay**: additional layers; overkill with one implementation.
- **Avoid when**: you only have one implementation; it adds layers quickly.
- **Tip**: keep the “abstraction” surface small; name implementors clearly (`*Impl`, `*Backend`) so the split stays obvious.
- **Tests**: cover representative combinations (at least one per axis) without requiring every permutation.

#### Composite
- **Intent**: treat individual objects and compositions uniformly (tree structures).
- **Use when**: you naturally have a hierarchy (folders, UI nodes, ASTs).
- **Smell**: duplicated “walk the tree” logic or special casing “single vs group” at many call-sites.
- **Pay**: can hide complexity; harder to enforce leaf-only rules.
- **Avoid when**: there’s no real tree; you’ll force awkward abstractions.
- **Tip**: be explicit about operations that only make sense on composites.
- **Tests**: include edge cases (empty group, deep nesting) and ensure operations on leaves/composites behave correctly.

#### Decorator
- **Intent**: add responsibilities dynamically by wrapping, preserving interface.
- **Use when**: optional cross-cutting behavior; stacking behaviors (retry + timeout + metrics).
- **Smell**: repeated “before/after” logic scattered across call-sites (timing/logging/caching/auth checks).
- **Pay**: wrapper stacks are harder to debug; ordering matters.
- **Avoid when**: behavior changes require access to internals; prefer explicit composition.
- **Tip**: log wrapper order or provide an “explain chain” debug helper.
- **Tests**: verify wrapper order effects (e.g., caching outside retries vs inside), and that errors/timeouts propagate as intended.

#### Facade
- **Intent**: provide a simplified API to a complex subsystem.
- **Use when**: call-sites are messy; you want one place to coordinate a subsystem.
- **Smell**: many call-sites repeat the same multi-step sequence across several modules/services.
- **Pay**: can become a “god API”.
- **Avoid when**: it becomes a “god” API hiding important control/errors.
- **Tip**: keep it thin; don’t bury business rules that deserve their own modules.
- **Tests**: treat the facade as the public contract; verify it doesn’t swallow errors and keeps important options explicit.

#### Flyweight
- **Intent**: share common state between many small objects to reduce memory.
- **Use when**: you have huge numbers of similar objects; immutable shared state is possible.
- **Smell**: memory/GC pressure from millions of tiny objects with repeated identical data.
- **Pay**: complexity; can introduce subtle identity bugs.
- **Avoid when**: complexity outweighs memory wins; modern allocators often make this unnecessary.
- **Tip**: separate intrinsic (shared/immutable) vs extrinsic (per-instance) state explicitly; measure before/after.
- **Tests**: ensure shared state is immutable and that equality/identity semantics remain correct.

#### Proxy
- **Intent**: a placeholder that controls access to another object.
- **Use when**: lazy initialization, access control, caching, remote objects.
- **Smell**: expensive initialization on hot paths, scattered access checks, or remote calls that need a stable local interface.
- **Pay**: hidden latency/failure; surprising side effects.
- **Avoid when**: it obscures side effects or failure modes (debuggability suffers).
- **Tip**: make remote-ness obvious (naming/metrics) and keep failure modes visible.
- **Tests**: caching correctness (hit/miss/invalidate), authz behavior, and that errors are preserved (not silently retried/swallowed unless specified).

### Behavioral (11)

#### Chain of Responsibility
- **Intent**: pass a request through a chain of handlers until one handles it.
- **Use when**: pipelines/middleware; multiple independent steps; easy reordering.
- **Smell**: big monolithic function that does N steps, or many call-sites repeating the same “apply these steps in order”.
- **Pay**: hard debugging if chain order is implicit.
- **Avoid when**: chain order is unclear and unobservable.
- **Tip**: ensure observability (logs/traces per handler).
- **Tests**: cover handler ordering and stop/continue behavior; add a test for “no handler handled it” if that’s possible.

#### Command
- **Intent**: encapsulate a request as an object (or record) to parameterize, queue, retry, undo.
- **Use when**: async jobs, undo/redo, macro commands, audit logging.
- **Smell**: you need to queue/retry/log/undo operations, but the operation is only expressible as “call this function now”.
- **Pay**: ceremony if all you need is a function call.
- **Avoid when**: a direct function call is sufficient; don’t add ceremony.
- **Tip**: commands should be serializable if you plan to persist/retry.
- **Tests**: idempotency (if retried), serialization round-trips (if persisted), and that failure handling matches the contract.

#### Interpreter
- **Intent**: represent and evaluate sentences in a simple language/grammar.
- **Use when**: small DSLs/config expressions; rule engines; templating-like evaluation.
- **Smell**: growing “stringly-typed” expressions/config that need validation and predictable evaluation.
- **Pay**: quickly becomes a “real language” (then you want real tooling).
- **Avoid when**: grammar is non-trivial; use a real parser/tooling.
- **Tip**: avoid `eval`; parse → AST → evaluate; keep the grammar small and test it like an API surface.
- **Tests**: golden cases (valid expressions), fuzz/edge cases (invalid input), and injection safety (no code execution).

#### Iterator
- **Intent**: traverse a collection without exposing its representation.
- **Use when**: you need consistent traversal across collections; streaming iteration.
- **Smell**: callers need internals to traverse correctly, or traversal logic is duplicated and error-prone.
- **Pay**: often redundant in languages with native iterators.
- **Avoid when**: the language’s native iterators already solve it.
- **Tip**: be explicit whether iteration is over a snapshot or a live/mutating collection.
- **Tests**: ensure iteration order/stability guarantees are met; cover mutation during iteration if supported.

#### Mediator
- **Intent**: centralize complex communications between components.
- **Use when**: many-to-many coupling becomes unmanageable; you want one coordinator.
- **Smell**: components import each other in a dense graph; small changes require edits across many modules.
- **Pay**: mediator becomes a “god object” if scope isn’t tight.
- **Avoid when**: the mediator owns domain logic rather than interaction.
- **Tip**: keep mediator focused on interaction, not domain rules.
- **Tests**: interaction tests (who talks to whom, in what order) without requiring deep knowledge of internals.

#### Memento
- **Intent**: capture and restore an object’s internal state without violating encapsulation.
- **Use when**: undo/history snapshots; safe rollback of edits.
- **Smell**: you need undo/redo/rollback, but reproducing prior state is difficult or leaks internals everywhere.
- **Pay**: large snapshots; memory churn.
- **Avoid when**: state is large; consider incremental diffs or event sourcing.
- **Tip**: decide whether mementos are full snapshots or diffs; beware capturing secrets/PII in history.
- **Tests**: round-trip restore (apply changes → restore → equals baseline), including boundary cases and large states.

#### Observer
- **Intent**: one-to-many dependency; when one object changes, notify dependents.
- **Use when**: event-driven updates; UI/reactive flows; domain events.
- **Smell**: many consumers need updates when something changes, but direct calls create tight coupling.
- **Pay**: lifecycle leaks + ordering hazards.
- **Avoid when**: lifecycle management is unclear; ensure unsubscribe/cleanup.
- **Tip**: enforce unsubscribe via scope/RAII patterns; test subscription cleanup.
- **Tests**: unsubscribe/cleanup, duplicate subscription prevention, and ordering/“exactly once” expectations if required.

#### State
- **Intent**: allow object to alter behavior when internal state changes.
- **Use when**: state machines; removing large state-based conditionals.
- **Smell**: switches on `status` in many places; invalid state combinations; “what states are possible?” is unclear.
- **Pay**: too many states = complexity.
- **Avoid when**: transitions aren’t explicit/validated; don’t encode as booleans.
- **Tip**: model transitions explicitly; reject invalid transitions early.
- **Tests**: transition table tests (allowed vs forbidden), plus tests for rehydration/persistence of state when applicable.

#### Strategy
- **Intent**: define a family of algorithms and make them interchangeable.
- **Use when**: you need to swap behavior (policy/algorithm) without branching explosion.
- **Smell**: complex branching to choose “policy”; adding new cases requires editing a central switch everywhere.
- **Pay**: extra objects/indirection for “just one algorithm”.
- **Avoid when**: there’s only one real algorithm; keep it simple.
- **Tip**: start with a function/interface; graduate to full Strategy if needed.
- **Tests**: per-strategy unit tests + one shared invariant test suite (inputs that should behave the same across strategies).

#### Template Method
- **Intent**: define algorithm skeleton, letting subclasses override steps.
- **Use when**: there’s a stable sequence but some steps vary; enforce invariants.
- **Smell**: lots of duplicated “same steps, slightly different hooks” code across variants.
- **Pay**: inheritance coupling.
- **Avoid when**: inheritance is undesirable; consider composition + hooks/callbacks.
- **Tip**: often replaceable with composition + hooks/callbacks.
- **Tests**: test the stable skeleton invariants once, then per-override behavior separately.

#### Visitor
- **Intent**: separate algorithms from object structure; add operations without changing classes.
- **Use when**: many concrete types share operations; you often add new operations.
- **Smell**: you keep adding new operations across many node types, and every operation touches the same set of types.
- **Pay**: adding a new type forces updates across all visitors.
- **Avoid when**: you frequently add new types; visitor requires updating all visitors.
- **Tip**: great for AST-like structures with stable node kinds.
- **Tests**: ensure all node types are visited; add a “missing visitor case” test to prevent silent fallthrough.

---

## Beyond GoF (selected modern patterns)

These patterns are not part of the GoF 23, but they show up often in real systems and in ADRs/refactor plans.

### Responsibility & dispatch

#### Dispatch Table (Handler Map / “Map of Responsibility”)
- **Intent**: route a request to the correct handler using a map/dictionary keyed by request type, command name, or capability.
- **Use when**: exactly one handler should apply; you want explicit coverage and fast routing; you’re replacing long `if/switch` dispatch.
- **Smell**: “giant router” conditionals, duplicated dispatch logic, hard-to-see missing cases.
- **Pay**: handler registration/initialization complexity; less natural when precedence/ordering matters.
- **Avoid when**: multiple handlers should run (pipeline) → prefer **Chain of Responsibility** / explicit handler list.
- **Tip**: make unknown-key behavior explicit (error vs default handler); keep the key space well-defined.
- **Tests**: “all keys registered” test; unknown-key test; one contract test per handler.

#### Plugin Registry (Extension Point)
- **Intent**: define a stable extension point and let implementations register themselves (often used with Dispatch Table/Strategy).
- **Use when**: you need modular extensibility (feature flags, pluggable backends, optional integrations).
- **Smell**: core modules importing lots of optional modules; adding a new variant requires editing a central `switch`.
- **Pay**: discovery/registration order issues; risk of “magic” global registries.
- **Tip**: prefer explicit registration at app startup over import-time side effects.
- **Tests**: registry contains expected plugins; each plugin satisfies the extension contract.

### Responsibility assignment (GRASP)

GRASP patterns are “responsibility assignment” heuristics. They’re often useful earlier than GoF when you’re deciding where code should live.

#### GRASP: Information Expert
- **Intent**: assign responsibility to the object that has the necessary information.
- **Use when**: logic is “asking” other objects for data just to compute something.
- **Watch**: don’t create “god objects”; balance with cohesion.

#### GRASP: Creator
- **Intent**: assign creation to the class that aggregates/contains/uses the created object closely.
- **Use when**: construction ownership is unclear and scattered.

#### GRASP: Controller
- **Intent**: use a controller to handle system events (UI/HTTP/CLI) and delegate to domain logic.
- **Use when**: UI/transport concerns bleed into business logic.

#### GRASP: Low Coupling / High Cohesion
- **Intent**: reduce ripple effects (coupling) and keep responsibilities focused (cohesion).
- **Use when**: changing one thing forces edits everywhere, or modules have mixed concerns.

#### GRASP: Polymorphism
- **Intent**: replace branching by pushing variant behavior behind a common interface (often Strategy/State).
- **Use when**: you keep adding `if type == ...` cases.

#### GRASP: Pure Fabrication
- **Intent**: introduce a non-domain object to achieve low coupling/high cohesion (e.g., a service/helper).
- **Use when**: domain objects would become bloated if they owned a responsibility.

#### GRASP: Indirection / Protected Variations
- **Intent**: add an intermediate object/contract to shield unstable dependencies.
- **Use when**: vendor/framework churn would otherwise ripple through core logic.

### Dependency management

#### Dependency Injection (DI)
- **Intent**: make dependencies explicit by passing them in (constructor/parameter injection), rather than looking them up globally.
- **Use when**: you want test seams, clearer ownership, and easier swapping of implementations.
- **Pay**: more wiring/config; can become framework-heavy if overused.
- **Avoid when**: a simple module-level dependency is fine and testing doesn’t require swapping it.
- **Tip**: prefer explicit construction at the edge (“composition root”); avoid hiding dependencies.
- **Tests**: pass fakes/mocks directly; avoid global resets.

#### Service Locator (usually avoid)
- **Intent**: a global registry that returns services on demand.
- **Use when**: transitional legacy systems; when DI is not feasible.
- **Pay**: hidden dependencies, global state, hard-to-test code.
- **Tip**: treat as a migration step toward DI; keep the locator at the outer edge.

### Architecture boundaries

#### Hexagonal Architecture (Ports & Adapters)
- **Intent**: isolate domain logic behind “ports” (interfaces) and keep IO/frameworks in “adapters”.
- **Use when**: you want core logic testable without DB/network/UI; you want to swap infra with minimal churn.
- **Smell**: domain imports framework types; tests require real DB/network; infrastructure leaks everywhere.
- **Pay**: more interfaces and mapping; can feel verbose initially.
- **Tip**: ports are owned by the domain; adapters implement ports at the edges.
- **Tests**: domain tests run without infra; adapter tests cover mapping + integration.

#### Anti-Corruption Layer (ACL)
- **Intent**: protect your domain model from a legacy/external system’s concepts by translating at the boundary.
- **Use when**: the external model doesn’t match yours and you don’t want it to “infect” your core.
- **Pay**: an extra translation layer to maintain.
- **Tip**: keep the ACL close to the boundary; treat it as a deliberate seam.

### Enterprise application patterns (PoEAA / DDD-adjacent)

#### Repository
- **Intent**: treat persistence as a collection-like abstraction; hide data access details from domain logic.
- **Use when**: business logic is entangled with ORM/query details; you want testable domain behavior.
- **Pay**: can become leaky (exposing query primitives) or too generic; performance pitfalls (N+1).
- **Tip**: keep repository methods domain-focused; use explicit query objects/specifications when needed.

#### Unit of Work
- **Intent**: track changes and commit them as a single transaction.
- **Use when**: multiple writes must succeed/fail together; transaction boundaries are unclear today.
- **Pay**: implicit flush timing and concurrency pitfalls if hidden.
- **Tip**: make the unit-of-work boundary explicit (per request/job).

#### Specification
- **Intent**: encapsulate business rules/criteria in composable objects (often reused in repos/validation).
- **Use when**: filtering rules are duplicated across call-sites and queries.
- **Pay**: can become a mini DSL if unchecked.
- **Tip**: keep specs small, named, and test them like public APIs.

### Distributed data & consistency

#### CQRS
- **Intent**: separate “commands” (writes) from “queries” (reads) when their needs diverge.
- **Use when**: read models need different shapes/performance than write models; write invariants are complex.
- **Pay**: duplication and eventual consistency; more moving parts.
- **Tip**: start by separating DTOs and write paths; go full CQRS only if the pain is real.

#### Event Sourcing
- **Intent**: store state as a sequence of events and derive current state by replaying them.
- **Use when**: audit/history is a core requirement; you need time-travel/debuggable state.
- **Pay**: event versioning/migrations; operational complexity.
- **Tip**: treat event schemas as long-lived contracts; invest in tooling early.

#### Idempotent Consumer
- **Intent**: safely process the same message/command more than once without duplicating side effects.
- **Use when**: at-least-once delivery, retries, or “unknown success” failures are possible.
- **Pay**: dedupe storage/keys, extra logic in handlers, careful definition of “same request”.
- **Tip**: use an idempotency key + a persisted “processed” record; make handlers safe to retry.

#### Saga
- **Intent**: coordinate a distributed business transaction via local transactions + compensations.
- **Use when**: you can’t use a single ACID transaction across services, but need end-to-end consistency.
- **Pay**: complex failure modes; compensations are business logic.
- **Tip**: idempotency + correlation IDs are non-negotiable; build observability first.

#### Transactional Outbox
- **Intent**: atomically persist a state change and an outgoing message/event in the same DB transaction.
- **Use when**: “write DB then publish event” can lose events under failure.
- **Pay**: outbox table + relay/processor; eventual delivery rather than immediate.
- **Tip**: keep outbox processing idempotent and backpressure-aware.

### Reliability / resilience (cloud patterns)

#### Retry (with backoff/jitter)
- **Intent**: handle transient failures by retrying with delays.
- **Use when**: timeouts/transient network errors are expected.
- **Pay**: amplifies load during incidents; can duplicate side effects.
- **Tip**: retry only idempotent operations or use idempotency keys; cap attempts and add jitter.

#### Timeout
- **Intent**: bound how long you wait for an operation before failing fast.
- **Use when**: remote calls can hang/slow; you need predictable latency budgets.
- **Pay**: timeouts can cause partial work; can turn slowdowns into failures if set too aggressively.
- **Tip**: propagate cancellation/timeouts through layers; treat timeouts as an end-to-end budget, not per-hop guesswork.

#### Circuit Breaker
- **Intent**: stop calling a failing dependency to prevent cascading failures; fail fast until recovery.
- **Use when**: repeated failures/timeouts cause thread/connection exhaustion.
- **Pay**: state machine complexity; you must pick thresholds/time windows.
- **Tip**: make states observable (open/half-open/closed) and keep fallback behavior explicit.

#### Bulkhead
- **Intent**: isolate resources so a failing dependency can’t consume everything.
- **Use when**: shared thread pools/queues/connections can be exhausted by one class of work.
- **Pay**: tuning complexity; requires capacity planning.
- **Tip**: isolate by dependency or criticality; measure saturation.

#### Throttling (Rate limiting)
- **Intent**: protect a service by limiting request rates (per user/tenant/key) and shedding load predictably.
- **Use when**: multi-tenant systems, expensive endpoints, or “spiky” workloads can overwhelm capacity.
- **Pay**: clients see rejections/delays; fairness and burst handling require design.
- **Tip**: define quotas + burst limits; return explicit signals (`429`/retry-after) and document client behavior.

#### Backpressure
- **Intent**: regulate producers to match consumer capacity so queues don’t grow without bound.
- **Use when**: streaming pipelines, job queues, or fan-out workloads can overwhelm downstream consumers.
- **Pay**: coordination complexity; may reduce peak throughput.
- **Tip**: use bounded queues, batching, and explicit “slow down” signals; instrument queue depth/latency.

#### Cache-Aside
- **Intent**: application code manages the cache alongside the primary store.
- **Use when**: you need lower read latency and can tolerate some staleness.
- **Pay**: invalidation complexity, stampedes, stale reads.
- **Tip**: define TTL, handle cache-miss stampedes (locking/coalescing), and make staleness explicit.

### Migration & modernization

#### Strangler Fig
- **Intent**: replace a legacy system gradually by routing functionality to a new implementation over time.
- **Use when**: big-bang rewrite is too risky; you need incremental wins.
- **Pay**: temporary duplication and routing complexity.
- **Tip**: choose one “thin slice” at a time and keep the seam observable (metrics, routing rules).

#### Feature Toggle (Feature Flag)
- **Intent**: decouple deployment from release by guarding behavior behind runtime switches.
- **Use when**: incremental rollout, kill switches, A/B tests, or long-running migrations.
- **Pay**: “flag debt” and combinatorial test paths; can become a permanent complexity tax.
- **Tip**: every flag needs an owner + expiry/cleanup plan; prefer coarse-grained flags over “flagging everything”.

### API composition (microservices)

#### Backends for Frontends (BFF)
- **Intent**: provide a backend tailored to each client type (web, mobile, etc.) to avoid “one API fits nobody”.
- **Use when**: client needs diverge and a shared API becomes a compromise that hurts all clients.
- **Pay**: duplicated logic and more deployed services.
- **Tip**: keep business logic in shared domain/services; BFFs should mostly orchestrate/shape data.

#### Gateway Aggregation
- **Intent**: aggregate multiple downstream calls into a single response to reduce client chattiness.
- **Use when**: a client needs data from multiple services and latency is dominated by round-trips.
- **Pay**: the gateway can become complex and a bottleneck.
- **Tip**: keep aggregation focused; avoid turning the gateway into the domain layer.

---

## References

- Refactoring.Guru — Design Patterns: https://refactoring.guru/design-patterns
- *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma/Helm/Johnson/Vlissides)
- Martin Fowler:
  - https://martinfowler.com/articles/injection.html (Dependency Injection)
  - https://martinfowler.com/eaaCatalog/repository.html (Repository)
  - https://martinfowler.com/eaaCatalog/unitOfWork.html (Unit of Work)
  - https://martinfowler.com/bliki/CQRS.html (CQRS)
  - https://martinfowler.com/eaaDev/EventSourcing.html (Event Sourcing)
  - https://martinfowler.com/bliki/StranglerFigApplication.html (Strangler Fig)
  - https://martinfowler.com/articles/feature-toggles.html (Feature Toggles)
- Microservices.io:
  - https://microservices.io/patterns/data/saga.html (Saga)
  - https://microservices.io/patterns/data/transactional-outbox.html (Transactional Outbox)
  - https://microservices.io/patterns/communication-style/idempotent-consumer.html (Idempotent Consumer)
- Microsoft Cloud Design Patterns:
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/retry (Retry)
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/timeout (Timeout)
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker (Circuit Breaker)
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead (Bulkhead)
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/throttling (Throttling)
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside (Cache-Aside)
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer (Anti-Corruption Layer)
- Microsoft microservices patterns:
  - https://learn.microsoft.com/en-us/azure/architecture/microservices/design/gateway (Gateway Aggregation)
  - https://learn.microsoft.com/en-us/azure/architecture/microservices/design/backend-for-frontend (BFF)
- AWS patterns:
  - https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/backpressure.html (Backpressure)
- Wikipedia:
  - https://en.wikipedia.org/wiki/Dispatch_table (Dispatch Table)
  - https://en.wikipedia.org/wiki/Hexagonal_architecture_(software) (Hexagonal Architecture)
  - https://en.wikipedia.org/wiki/Service_locator_pattern (Service Locator)
  - https://en.wikipedia.org/wiki/Specification_pattern (Specification pattern)
  - https://en.wikipedia.org/wiki/GRASP_(object-oriented_design) (GRASP)

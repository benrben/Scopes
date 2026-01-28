# Scopes Browser Demo

This demo showcases the **Scopes Browser** with diagram support.

## Features

- 📁 **File System Access API** - No server required
- 🎨 **Premium Dark UI** - Glassmorphic design
- 📊 **Mermaid Diagrams** - Render diagrams directly
- 🔍 **Syntax Highlighting** - Code blocks beautifully rendered

## Example: Scopes Workflow

Here's how the Scopes methodology works:

```mermaid
graph LR
    A[Code Changes] --> B[Run /sync-scopes]
    B --> C[Generate Scopes]
    C --> D[Update Documentation]
    D --> E[Maintain Truth]
    E --> A
    
    style A fill:#3b82f6,stroke:#2563eb,color:#fff
    style B fill:#10b981,stroke:#059669,color:#fff
    style C fill:#f59e0b,stroke:#d97706,color:#fff
    style D fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style E fill:#ec4899,stroke:#db2777,color:#fff
```

## Development Loop

The `/dev-loop` command follows this flow:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Cmd as /dev-loop
    participant Test as Tests
    participant Scope as Scopes
    
    Dev->>Cmd: Start Feature
    Cmd->>Test: Write Tests First
    Test->>Cmd: Tests Fail (Red)
    Cmd->>Dev: Implement Feature
    Dev->>Test: Run Tests
    Test->>Cmd: Tests Pass (Green)
    Cmd->>Scope: Update Documentation
    Scope->>Dev: Truth Maintained ✓
```

## Scopes Architecture

```mermaid
graph TB
    subgraph "Scopes Repository"
        INDEX[INDEX.md<br/>Tree Structure]
        GRAPH[GRAPH.md<br/>Relationships]
        
        subgraph "Product/"
            FEAT[Features]
            ARCH[Architecture]
            API[API Docs]
        end
        
        subgraph "Work/"
            TASKS[Tasks]
            BUGS[Bug Reports]
        end
        
        subgraph "Prompts/"
            AGENTS[AI Agents]
        end
    end
    
    CODE[Codebase] -->|/sync-scopes| INDEX
    CODE -->|Audits| GRAPH
    GRAPH -.->|Links| FEAT
    GRAPH -.->|Links| ARCH
    INDEX -->|Organizes| TASKS
    
    style INDEX fill:#3b82f6,stroke:#2563eb,color:#fff
    style GRAPH fill:#10b981,stroke:#059669,color:#fff
    style CODE fill:#f59e0b,stroke:#d97706,color:#fff
```

## State Machine Example

```mermaid
stateDiagram-v2
    [*] --> Idea
    Idea --> Research: /research-loop
    Research --> Plan: /plan-idea
    Plan --> Tasks: /write-tasks
    Tasks --> Development: /dev-loop
    Development --> Testing
    Testing --> Development: Bugs Found
    Testing --> Documentation: Tests Pass
    Documentation --> Release: /write-release
    Release --> [*]
    
    Development --> Scopes: /sync-scopes
    Scopes --> Development: Updated Truth
```

## Class Diagram Example

```mermaid
classDiagram
    class Scope {
        +String name
        +String type
        +List~Link~ evidence
        +update()
        +verify()
    }
    
    class ProductScope {
        +String capability
        +renderDocumentation()
    }
    
    class WorkScope {
        +String status
        +assignTo(dev)
    }
    
    class Link {
        +String type
        +String target
        +validate()
    }
    
    Scope <|-- ProductScope
    Scope <|-- WorkScope
    Scope "1" --> "*" Link
```

## Gantt Chart Example

```mermaid
gantt
    title Scopes Implementation Roadmap
    dateFormat YYYY-MM-DD
    section Phase 1
    Initial Scopes Setup    :a1, 2026-01-01, 7d
    Sync Command Dev        :a2, after a1, 10d
    section Phase 2
    Dev Loop Integration    :b1, after a2, 5d
    Testing & Validation    :b2, after b1, 7d
    section Phase 3
    Documentation Polish    :c1, after b2, 5d
    Release                 :milestone, after c1, 1d
```

---

**Try It Out**: Open this file in the Scopes Browser to see all diagrams rendered beautifully!

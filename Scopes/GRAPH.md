# Scope Network Graph

## Legend
- `-->` Depends On / Uses
- `..>` Possible Relation (Low confidence)

## Graph
```mermaid
flowchart TD
  User[User] --> System[Command System]
  System --> DevLoop[Dev Loop Agent]
  System --> ResearchLoop[Research Loop Agent]
  System --> SyncScopes[Sync Scopes Agent]
  
  ResearchLoop --> PlanIdea[Plan Idea]
  PlanIdea --> WriteTasks[Write Tasks]
  WriteTasks --> DevLoop
  
  BugHunt[Bug Hunt] --> WriteTasks
```

## Evidence Table
| From | To | Relationship | Evidence Link |
|------|----|--------------|---------------|
| System | DevLoop | Contains File | [Scopes/Prompts/dev-loop.md:L1-L5](Scopes/Prompts/dev-loop.md#L1-L5) |
| System | SyncScopes | Contains File | [Scopes/Prompts/sync-scopes.md:L1-L5](Scopes/Prompts/sync-scopes.md#L1-L5) |

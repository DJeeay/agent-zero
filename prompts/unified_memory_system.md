# Unified Memory System Documentation

## Overview

The Unified Memory System combines file-based persistent memory with semantic search capabilities for intelligent memory management across sessions.

## Architecture

### Memory Stores

| Store       | Purpose                                                                | Char Limit                | Location            |
|-------------|------------------------------------------------------------------------|---------------------------|---------------------|
| **MEMORY.md** | Agent's personal notes — environment facts, conventions, things learned | 2,200 chars (~800 tokens) | `~/.hermes/memories/` |
| **USER.md**    | User profile — preferences, communication style, expectations          | 1,375 chars (~500 tokens) | `~/.hermes/memories/` |

### System Integration

Memory entries are injected into the system prompt as a frozen snapshot at session start:

```text
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

## Tool Reference

### Core Memory Operations

#### memory_add

Add a new memory entry to the specified store.

```json
{
  "thoughts": ["I need to remember this important fact..."],
  "headline": "Adding project configuration to memory",
  "tool_name": "memory_add",
  "tool_args": {
    "target": "memory|user",
    "content": "Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router"
  }
}
```

#### memory_replace

Replace an existing entry using substring matching.

```json
{
  "thoughts": ["The project configuration has changed..."],
  "headline": "Updating project information in memory",
  "tool_name": "memory_replace",
  "tool_args": {
    "target": "memory|user",
    "old_text": "Go 1.22",
    "content": "Go 1.23, sqlc for DB queries, chi router, gin for middleware"
  }
}
```

#### memory_remove

Remove an entry using substring matching.

```json
{
  "thoughts": ["This information is no longer relevant..."],
  "headline": "Removing outdated server information",
  "tool_name": "memory_remove",
  "tool_args": {
    "target": "memory|user",
    "old_text": "old server configuration"
  }
}
```

### Enhanced Search Operations

#### memory_search

Search memory entries using semantic similarity.

```json
{
  "thoughts": ["Let me search for information about..."],
  "headline": "Searching memory for database configuration",
  "tool_name": "memory_search",
  "tool_args": {
    "query": "database configuration postgresql",
    "threshold": 0.7,
    "target": "memory|user|all",
    "limit": 5
  }
}
```

#### memory_list

List all entries in a memory store.

```json
{
  "thoughts": ["I need to see what's currently in memory..."],
  "headline": "Listing current memory entries",
  "tool_name": "memory_list",
  "tool_args": {
    "target": "memory|user|all"
  }
}
```

### Legacy Operations (for compatibility)

#### memory_load

Load memories via query with threshold and filter (backward compatibility).

```json
{
  "thoughts": ["Let's search my memory for..."],
  "headline": "Searching memory for file compression information",
  "tool_name": "memory_load",
  "tool_args": {
    "query": "File compression library for...",
    "threshold": 0.7,
    "limit": 5,
    "filter": "area=='main' and timestamp<'2024-01-01 00:00:00'"
  }
}
```

## Usage Guidelines

### What to Store

- **Environment facts**: OS, tools, project structure
- **User preferences**: Communication style, workflow habits
- **Conventions**: Project standards, coding practices
- **Lessons learned**: Workarounds, discovered patterns
- Completed task diary entries
- Skills and techniques that worked

### What to Store in MEMORY.md

For information the agent needs to remember about the environment, workflows, and lessons learned:

- Environment facts (OS, tools, project structure)
- Project conventions and configuration
- Tool quirks and workarounds discovered
- Completed task diary entries
- Skills and techniques that worked

### What to Store in USER.md

- Name, role, timezone
- Communication preferences (concise vs detailed, format preferences)
- Pet peeves and things to avoid
- Workflow habits
- Technical skill level

### Good Memory Entry Examples

```
# Compact and information-dense
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# Specific and actionable
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# Context-rich lesson learned
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.
```

## Capacity Management

### When Memory is Full

When adding an entry would exceed character limits:
1. Use `memory_list` to see current entries
2. Identify entries that can be removed or consolidated
3. Use `memory_replace` to merge related entries
4. Then `memory_add` the new entry

### Best Practices

- Consolidate entries when memory is above 80% capacity
- Merge multiple related entries into comprehensive ones
- Remove outdated or irrelevant information
- Keep entries concise and information-dense

## Advanced Features

### Substring Matching

The `replace` and `remove` operations use short unique substring matching:
- `old_text` parameter needs only a unique substring
- If multiple entries match, an error requests more specificity
- Enables precise targeting without full entry text

### Semantic Search

The `memory_search` operation provides intelligent retrieval:
- Uses semantic similarity, not just keyword matching
- Threshold parameter controls similarity strictness (0-1, default 0.7)
- Can search across both stores or target specific ones
- Returns ranked results with similarity scores

### Security Scanning

All memory entries are scanned for:
- Prompt injection patterns
- Credential exfiltration attempts
- SSH backdoors and malicious content
- Invisible Unicode characters

## Session Search Integration

Beyond persistent memory, the system can search past conversations:
- All sessions stored in SQLite with FTS5 full-text search
- Search returns relevant conversations with AI summarization
- Complements persistent memory for comprehensive recall

## Configuration

```yaml
# In ~/.hermes/config.yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  semantic_search_enabled: true
  search_threshold_default: 0.7
```

## Migration Guide

### From Technical Reference Style

- Replace `memory_save` with `memory_add`
- Replace `memory_delete` with `memory_remove`
- Use `memory_search` instead of `memory_load` for new implementations
- Existing `memory_load` calls remain supported for backward compatibility

### From Hermes Agent Style

- Existing `add`, `replace`, `remove` operations work unchanged
- New `memory_search` and `memory_list` operations available
- Enhanced semantic search capabilities added

## Troubleshooting

### Common Issues

- **Memory full error**: Use `memory_list` to review and consolidate entries
- **Multiple matches error**: Use more specific `old_text` for replace/remove
- **Search not finding**: Lower threshold or broaden query terms
- **Security block**: Review content for injection patterns

### Performance Tips
- Keep memory entries concise for faster injection
- Use semantic search for large memory sets
- Consolidate related entries to reduce overhead
- Regular cleanup of outdated information improves performance

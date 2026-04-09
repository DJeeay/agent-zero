# Unified Memory System

## Overview

The Unified Memory System combines file-based persistent memory with semantic search capabilities for intelligent memory management across sessions.

## Architecture

### Memory Stores

| Store       | Purpose                                                                | Char Limit                | Location            |
|-------------|------------------------------------------------------------------------|---------------------------|---------------------|
| **MEMORY.md** | Agent's personal notes — environment facts, conventions, things learned | 2,200 chars (~800 tokens) | `~/.hermes/memories/` |
| **USER.md**    | User profile — preferences, communication style, expectations          | 1,375 chars (~500 tokens) | `~/.hermes/memories/` |

## Tool Reference

### Core Operations

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

### Legacy Operations (Backward Compatibility)

#### memory_load
Load memories via query with threshold and filter.

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

#### memory_save
Save text to memory (legacy compatibility).

```json
{
  "thoughts": ["I need to memorize..."],
  "headline": "Saving important information to memory",
  "tool_name": "memory_save",
  "tool_args": {
    "text": "# To compress..."
  }
}
```

#### memory_delete
Delete memories by IDs (limited compatibility).

```json
{
  "thoughts": ["I need to delete..."],
  "headline": "Deleting specific memories by ID",
  "tool_name": "memory_delete",
  "tool_args": {
    "ids": "32cd37ffd1-101f-4112-80e2-33b795548116, d1306e36-6a9c- ..."
  }
}
```

#### memory_forget
Remove memories by query threshold filter.

```json
{
  "thoughts": ["Let's remove all memories about cars"],
  "headline": "Forgetting all memories about cars",
  "tool_name": "memory_forget",
  "tool_args": {
    "query": "cars",
    "threshold": 0.75,
    "filter": "timestamp.startswith('2022-01-01')"
  }
}
```

## Usage Guidelines

### What to Store
- **Environment facts**: OS, tools, project structure
- **User preferences**: Communication style, workflow habits
- **Conventions**: Project standards, coding practices
- **Lessons learned**: Workarounds, discovered patterns

### Capacity Management
- MEMORY.md: 2,200 character limit
- USER.md: 1,375 character limit
- When full, consolidate or replace existing entries
- Use `memory_list` to check current usage

### Security
- All entries scanned for injection patterns
- Malicious content automatically blocked
- Invisible Unicode characters filtered

## Migration Notes
- Existing `memory_save` calls work unchanged
- `memory_load` maintained for backward compatibility
- New `memory_search` provides enhanced semantic capabilities
- `memory_list` added for better memory management

# Memory Documentation Cleanup Plan

## Files to Update

### Primary Files (Consolidate Content)
1. `d:\DOCKER Cont 1 AZ\prompts\agent.system.tool.memory.md` - Replace with unified system
2. `\\wsl.localhost\Ubuntu-Test\mnt\wslg\distro\root\hermes-agent\website\docs\user-guide\features\memory.md` - Replace with unified system
3. `d:\Hermes_AGENT\Saupiquet\website\docs\user-guide\features\memory.md` - Replace with unified system

### Duplicate Files (Mark for Removal)
1. `\\wsl.localhost\Ubuntu-Test\mnt\wslg\distro\nix\store\1r38400yza4z4p84fasmc8crpv9bbfmz-n0h4nq3c6n78gxm60c7jya4yc8kflqhb-source\website\docs\user-guide\features\memory.md` - Duplicate copy

## Additional Files Found (Not in Original Request)
- `\\wsl.localhost\Ubuntu-Test\home\dje\.npm-global\lib\node_modules\clawdbot\docs\concepts\memory.md`
- `e:\copie wsl projects\projects\openclaw\docs\concepts\memory.md`

These appear to be different projects (clawdbot, openclaw) and should be reviewed separately.

## Cleanup Actions

### Phase 1: Update Primary Files
- Replace content with unified documentation
- Preserve file structure and formatting
- Maintain any project-specific context

### Phase 2: Handle Duplicates
- Mark Nix store duplicate for removal (managed by package manager)
- Add deprecation notices if needed

### Phase 3: Review Additional Files
- Check if clawdbot/openclaw files need similar updates
- Determine if they're part of consolidation scope

## Backup Strategy
Before making changes:
1. Create backups of original files
2. Document original content locations
3. Test unified system compatibility

## Implementation Notes
- Unified system maintains backward compatibility
- Legacy tool calls still supported
- New enhanced features available while preserving existing workflows

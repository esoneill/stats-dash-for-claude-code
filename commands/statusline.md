---
description: Manage CCode Dashboard statusline segments. Usage - /statusline [list | enable <name> | disable <name> | toggle <name> | reset]
allowed-tools: Bash(python3:*)
---

Run the following bash command using the Bash tool, then output its stdout verbatim with no commentary or extra formatting:

```
python3 ~/.claude/statusline/statusline.py config $ARGUMENTS
```

Notes:
- If `$ARGUMENTS` is empty, the command lists all segments and their current state.
- Valid segment names: `cwd`, `context`, `cost`, `time`, `model`, `weather`, `diff`, `ratelimit`.
- Subcommands: `list`, `enable <name>`, `disable <name>`, `toggle <name>`, `reset`.
- Changes take effect on the next statusline render (next keystroke pause).

# Advanced tmux Commands

## Session Management
```bash
# Create named session
tmux new-session -d -s mysession

# Attach to last session
tmux attach-session

# Attach to specific session
tmux attach-session -t mysession

# Detach from session
# Press: Ctrl+b d
```

## Window Management
```bash
# Create new window
# Press: Ctrl+b c

# Next/previous window
# Press: Ctrl+b n / Ctrl+b p

# Go to window by number
# Press: Ctrl+b 0-9

# Rename window
# Press: Ctrl+b ,
```

## Pane Management
```bash
# Split horizontal
# Press: Ctrl+b %

# Split vertical
# Press: Ctrl+b "

# Navigate panes
# Press: Ctrl+b arrow keys

# Resize pane
# Press: Ctrl+b Ctrl+arrow

# Close pane
# Press: Ctrl+b x
```

## Copy Mode
```bash
# Enter copy mode
# Press: Ctrl+b [

# Scroll: arrow keys / Page Up/Down
# Search: Ctrl+s (forward), Ctrl+r (backward)
# Copy: Space (start), Enter (copy)
# Paste: Ctrl+b ]
```

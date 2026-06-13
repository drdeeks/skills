# tmux Configuration

## Config File
Location: `~/.tmux.conf`

## Common Settings
```tmux
# Change prefix from Ctrl+b to Ctrl+a
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# Enable mouse support
set -g mouse on

# Start windows at 1
set -g base-index 1
setw -g pane-base-index 1

# Renumber windows
set -g renumber-windows on

# Increase scrollback
set -g history-limit 10000

# Better colors
set -g default-terminal "screen-256color"
```

## Key Bindings
```tmux
# Reload config
bind r source-file ~/.tmux.conf \; display "Config reloaded!"

# Split with current path
bind '"' split-window -c "#{pane_current_path}"
bind % split-window -h -c "#{pane_current_path}"

# Vim-style pane navigation
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R
```

## Plugins (TPM)
```tmux
# List of plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'

# Initialize TPM
run '~/.tmux/plugins/tpm/tpm'
```

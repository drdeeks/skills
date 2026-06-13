# Pokemon Player - Action Reference

## Basic Actions
- `press_a` — confirm, talk, select
- `press_b` — cancel, close menu
- `press_start` — open game menu
- `walk_up` / `walk_down` / `walk_left` / `walk_right` — move one tile
- `hold_b_N` — hold B for N frames (use for speeding through text)
- `wait_60` — wait about 1 second (60 frames)
- `a_until_dialog_end` — press A repeatedly until dialog clears

## Navigation Strategy
- Move 2-4 steps at a time, then screenshot to check position
- When entering a new area, screenshot immediately to orient
- Ask the vision model "which direction to [destination]?"
- If stuck for 3+ attempts, screenshot and re-evaluate completely
- Do not spam 10-15 movements — you will overshoot or get stuck

## Battle Actions
- FIGHT: top-left (default cursor), press A to enter move selection, A again to use first move
- RUN: bottom-right, from FIGHT: press down then right, then press A
- Wrap with `hold_b` to speed through attack animations and text

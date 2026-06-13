# Pokemon Player - Strategy Guide

## Gameplay Loop

### Step 1: OBSERVE
- GET /state for position, HP, battle, dialog
- GET /screenshot and save to /tmp/pokemon.png, then use vision_analyze
- Always do BOTH — RAM state gives numbers, vision gives spatial awareness

### Step 2: ORIENT
- Dialog/text on screen → advance it
- In battle → fight or run
- Party hurt → head to Pokemon Center
- Near objective → navigate carefully

### Step 3: DECIDE
Priority: dialog > battle > heal > story objective > training > explore

### Step 4: ACT
- POST /action with a SHORT action list (2-4 actions, not 10-15)

### Step 5: VERIFY
- Screenshot after every move sequence
- Take a screenshot and use vision_analyze to confirm you moved where intended
- This is the MOST IMPORTANT step. Without vision you WILL get lost.

### Step 6: RECORD
- Progress to memory with PKM: prefix

### Step 7: SAVE
- Periodically

## Battle Strategy

### Decision Tree
1. Want to catch? → Weaken then throw Poke Ball
2. Wild you don't need? → RUN
3. Type advantage? → Use super-effective move
4. No advantage? → Use strongest STAB move
5. Low HP? → Switch or use Potion

### Gen 1 Type Chart (Key Matchups)
- Water beats Fire, Ground, Rock
- Fire beats Grass, Bug, Ice
- Grass beats Water, Ground, Rock
- Electric beats Water, Flying
- Ground beats Fire, Electric, Rock, Poison
- Psychic beats Fighting, Poison (dominant in Gen 1!)

### Gen 1 Quirks
- Special stat = both offense AND defense for special moves
- Psychic type is overpowered (Ghost moves bugged)
- Critical hits based on Speed stat
- Wrap/Bind prevent opponent from acting
- Focus Energy bug: REDUCES crit rate instead of raising it

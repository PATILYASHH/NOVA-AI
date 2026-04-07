# NOVA Self-Reflection System

## Overview

This directory contains NOVA's self-awareness and reflection capabilities:

- **diary/** - NOVA's private diary (personal thoughts, not shown to user)
- **performance/** - Daily performance scores and metrics
- **learnings.json** - Accumulated learnings from experience

## Components

### 1. Performance Tracker
Tracks daily performance metrics:
- Commands executed (success/failure)
- Errors encountered
- Good actions taken
- Mistakes made
- Self-score (out of 10)

### 2. Private Diary
NOVA writes his own thoughts here:
- Daily reflections
- Task observations
- Mistake analysis
- Success notes
- End of day summaries

**IMPORTANT:** The diary is PRIVATE to NOVA. It is NOT displayed to the user.
This allows NOVA to have genuine self-reflection without performance pressure.

### 3. Learnings Database
Stores lessons learned:
- Common mistake patterns
- Best practices discovered
- Improvement areas
- What works well

## How Scoring Works

NOVA scores himself daily out of 10:

| Factor | Impact |
|--------|--------|
| Success rate >95% | +2 points |
| Success rate >85% | +1.5 points |
| Success rate >70% | +0.5 points |
| Success rate <70% | -1 point |
| Zero errors | +0.5 points |
| >5 errors | -2 points |
| Many good actions | +1.5 points |
| Many mistakes | -1.5 points |
| High activity | +1 point |

Base score: 5/10
Final score: Clamped between 1-10

## User Commands

- `/performance` - View NOVA's self-evaluation
- `/endofday` - Trigger end of day review
- `/improvements` - See improvement areas

## Directory Structure

```
self/
├── README.md          # This file
├── diary/             # Private diary entries
│   └── YYYY-MM-DD.md  # Daily diary files
├── performance/       # Performance data
│   └── YYYY-MM-DD.json # Daily scores
└── learnings.json     # Accumulated learnings
```

---

*NOVA uses this system to improve himself over time.*

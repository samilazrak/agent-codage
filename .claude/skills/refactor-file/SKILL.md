---
name: refactor-file
description: Refactors a Python file to improve readability and maintainability without changing behavior. Use when asked to clean up or reorganize a Python module while preserving its public behavior.
---

# refactor-file

Refactor a Python file while preserving behavior.

## Goal
Improve readability, maintainability, and design without changing the observable
behavior unless explicitly requested.

## Instructions

1. Read the target file carefully and understand its role.
2. Identify:
   - long functions
   - duplicated logic
   - deeply nested conditionals
   - unclear naming
   - mixed responsibilities
   - anti-patterns
3. Refactor conservatively.
4. Preserve public behavior, function signatures, and side effects unless asked otherwise.
5. Prefer small, reversible improvements.
6. If the file is too large, propose a short refactor plan first, then apply it.

## Python refactoring guidelines

### Prefer
- extracting private functions for intent
- using guard clauses to reduce nesting
- improving naming
- isolating side effects
- using type hints consistently
- removing unused imports and functions
- extracting reusable logic into dedicated modules

### Avoid
- changing behavior silently
- introducing new abstractions with no payoff
- overusing metaprogramming or dynamic dispatch
- adding clever one-liners that reduce readability
- introducing design patterns without a clear benefit

## LangChain / LangGraph heuristics

- keep prompt templates clean and readable
- separate graph construction from execution
- isolate LLM configuration in one place
- make tool definitions small and single-purpose
- make output parsing explicit

## Process

1. Explain briefly what you plan to improve.
2. Apply the refactor.
3. Summarize the key changes.
4. Mention any follow-up refactors that should be done separately.

## Validation

After refactoring, run the relevant checks:

```bash
ruff check path/to/file.py
ruff format --check path/to/file.py
```

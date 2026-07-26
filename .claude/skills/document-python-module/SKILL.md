---
name: document-python-module
description: Documents a Python module or class to explain its responsibility, usage, inputs/outputs, and important side effects. Use when asked to add or improve documentation without changing behavior.
---

# document-python-module

Add clear and useful documentation to a Python module or class.

## Goal
Improve readability and maintainability by documenting the responsibility, usage,
and behavior of a Python module **without modifying its behavior**.

The documentation should help a future reader quickly understand:
- what the module does
- when it should be used
- its important inputs and outputs
- any important side effects or constraints

## Instructions

1. Read the module carefully before writing documentation.
2. Understand its role within the project.
3. Identify the concepts that are not obvious from the code.
4. Add concise documentation where it improves understanding.
5. Do not modify the behavior of the code.
6. Avoid unnecessary or redundant comments.

## What to document

When relevant:
- the main responsibility of the module
- expected inputs (with types)
- returned values or result shape
- important side effects
- interactions with external systems (LLMs, subprocess, filesystem)
- important assumptions or constraints

Focus on explaining **intent**, not repeating the code.

## Prefer
- a module-level docstring at the top of the file
- class docstrings explaining the responsibility in one or two sentences
- documenting non-obvious behavior
- keeping docstrings concise and high signal
- Google-style docstrings, consistently
- type hints alongside docstrings

## Avoid
- modifying the code logic
- documenting obvious code line-by-line
- docstrings that merely repeat the function name
- speculative or uncertain explanations

## Agent / tool-specific guidance

For an agent, a graph, or a tool, document:
- what it does and when to use it
- expected input format
- output format and parsing
- which LLM provider / model it uses
- a short overview of the prompt or graph strategy

## Style

```python
"""Construit et exécute un agent de codage minimal (ReAct + outil bash).

Expose `build_agent()` qui assemble un LLM et ses outils, et un point d'entrée
CLI qui streame les étapes de raisonnement de l'agent.
"""
```

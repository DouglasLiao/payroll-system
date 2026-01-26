# Directives

This directory contains Standard Operating Procedures (SOPs) written in Markdown format.

## What Goes Here

Each directive should define:

1. **Goal**: What this directive accomplishes
2. **Inputs**: What information/files are needed
3. **Tools**: Which execution scripts to use (from `../execution/`)
4. **Outputs**: What gets produced (deliverables)
5. **Edge Cases**: Common errors, limitations, special scenarios

## Template

```markdown
# [Directive Name]

## Goal

Clear statement of what this accomplishes.

## Inputs

- Input 1: description
- Input 2: description

## Tools/Scripts

- `execution/script_name.py` - what it does

## Outputs

- Output format and location

## Edge Cases

- Known limitation 1
- Error scenario 2
- Best practice 3

## Example Usage

How the AI agent should use this directive.
```

## Naming Convention

Use lowercase with underscores: `process_payroll_data.md`, `scrape_website.md`

## Living Documents

Update directives as you learn:

- API constraints discovered
- Better approaches found
- Common errors encountered
- Timing expectations

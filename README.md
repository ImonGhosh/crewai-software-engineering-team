# Engineering Team Crew AI Template

This project assembles a multi-agent engineering team using [crewAI](https://crewai.com) to take a single requirement from design through backend implementation, frontend demo, and testing. It is tuned for rapid prototyping: change one requirement, run the crew, and get a design document, a self-contained Python module, a Gradio UI, and unit tests.

## Project Goal
- Turn a high-level requirement into a working prototype with minimal manual glue.
- Keep outputs self-contained in the `output/` directory for easy review and execution.
- Provide a repeatable flow that can be adapted to any simple app idea.

## Current Use Case
The default configuration builds an **account management system for a trading simulation platform**, including account creation, deposits/withdrawals, trade logging, holdings tracking, P/L reporting, and guardrails against invalid transactions.

## Workflow
1. **Engineering Lead** crafts a detailed design (classes, methods, and signatures) for a single-module solution.
2. **Backend Engineer** generates a self-contained Python module implementing the design.
3. **Frontend Engineer** wraps the module with a lightweight Gradio UI (`app.py`).
4. **Test Engineer** writes unit tests targeting the generated module.
5. All artifacts are written to `output/` for inspection and execution.

Agents and tasks are configured in `src/engineering_team/config/agents.yaml` and `src/engineering_team/config/tasks.yaml`, and wired together in `src/engineering_team/crew.py`. The entrypoint defining requirements, module name, and class name is `src/engineering_team/main.py`.

## Outputs
- **Design Document:** `output/{module_name}_design.md`
- **Backend Module:** `output/{module_name}` (single-file Python module)
- **Frontend App:** `output/app.py` (Gradio demo)
- **Tests:** `output/test_{module_name}` (unit test module)

## How to Run
1. Install Python (>=3.10, <3.14) and [uv](https://docs.astral.sh/uv/).
2. Add your API keys to a `.env` file (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`).
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Customize `src/engineering_team/main.py` with your requirement, `module_name`, and `class_name`.
5. From the project root, run the crew:
   ```bash
   crewai run
   ```
6. Inspect and run the generated app from `output/`:
   ```bash
   cd output
   uv run app.py
   ```

## Utility
- **Demo-ready:** Produces runnable backend, UI, and tests in one pass for quick showcases.
- **Self-contained modules:** Generated Python files avoid external dependencies beyond standard libs and installed packages.
- **Readable design:** Markdown design documents clarify structure before coding.

## App Screenshot
![Trading simulation UI](docs/app-screenshot.png)

## Future Scope
- **Multi-modularity:** Extend flows to generate and coordinate multiple backend modules.
- **Analytics team:** Add agents producing real-time dashboard components and observability.
- **Automated verification:** Incorporate agents that self-evaluate outputs, run checks, and propose self-repair strategies.

## Repository Layout
- `src/engineering_team/config/agents.yaml` — Agent roles, goals, and LLM settings.
- `src/engineering_team/config/tasks.yaml` — Task descriptions, outputs, and file targets.
- `src/engineering_team/crew.py` — Crew wiring and execution process.
- `src/engineering_team/main.py` — Requirement definition and crew kickoff.
- `output/` — Generated design, code, UI, and tests.
- `project_setup.md` — Additional setup notes from the template.

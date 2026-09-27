# CLAUDE.md — Claude Certification Learning Project

## Project Purpose

This repository documents a structured progression through Claude API and MCP (Model Context Protocol) concepts, progressing from foundational API usage to enterprise-style learning patterns including backend authentication, authorization, input validation, and resilient error handling.

**Learning stages:**
- **Days 1-5**: Frozen snapshots of daily learning (API basics → conversation → prompts → tools → agent loops)
- **MCP System**: Active implementation of a test failure investigation platform demonstrating production-oriented patterns

---

## Architecture Summary

### Learning Files (Frozen)
```
day1_claude_api.py              # Claude API client basics
day2_conversation.py             # Multi-turn conversations
day3_prompt_engineering.py       # Structured output with JSON schemas
day4_tool_calling.py             # Tool calling fundamentals
day5_manual_agent_loop.py        # Complete agentic pattern (4-step loop)
```

### Active MCP System
```
mcp_test_server.py              # MCPServer: 3 tools (status, logs, owner) + resources/prompts
mcp_test_client.py              # Full agent loop: discovers tools → uses Claude → handles responses
mcp_resource_client.py          # MCP resource discovery and content retrieval (no Claude API call)
mcp_prompt_client.py            # MCP prompt discovery and rendering with Claude
test_management_backend.py      # Simulated backend with auth/authz/validation/retries
config.py                       # Centralized runtime configuration from environment
```

### Key Architecture Patterns
- **Backend authentication**: API key validation
- **Authorization**: Scope-based permissions (e.g., `read:test_status`, `read:test_owner`)
- **Input validation**: Test case ID format checking (TC-NNN)
- **Error handling**: Distinguishes validation, auth, authz, and transient failures; retries only transient errors
- **Resilient retry logic**: Configurable retry attempts with a fixed delay

---

## Configuration & Secrets Rules

### Environment Variables (`.env`)
```
ANTHROPIC_API_KEY              # Claude API key — never exposed
TEST_BACKEND_API_KEY           # Backend auth credential — never exposed
TEST_BACKEND_SCOPES            # Backend authorization scopes (comma-separated)
MAX_RETRIES                    # Retry count for transient errors (default: 3)
RETRY_DELAY_SECONDS            # Fixed delay between retries (default: 1)
```

### Sacred Rules
- **`.env` is never read, printed, modified, staged, or committed by Claude Code.**
- **All secrets stay in `.env` only.** If a runtime value needs to change (e.g., adding scope `read:test_owner`), describe the change conceptually and ask you to update `.env` manually.
- **`.env.example` documents required variables** for new developers (no secrets in the example).
- **`config.py` reads at import time** from the process environment (already set by `.env`).
- **No credentials in code, comments, or commit messages.**

---

## Verification & Testing Rules

### Claude API Cost Awareness
- **mcp_resource_client.py**: Safe to run without asking (discovers and reads MCP resources, no Claude API calls).
- **mcp_test_client.py**: **Ask first** (uses Claude API to investigate test failures; may consume credits).
- **mcp_prompt_client.py**: **Ask first** (renders MCP prompts and sends them to Claude; may consume credits).
- **Before running any day1-day5 script**, inspect whether it invokes the Claude API; ask first if it does.

### Manual Testing Workflow
1. **For resource discovery** (no cost): Run `python mcp_resource_client.py` directly.
2. **For agent investigation** (costs API credits): Confirm `.env` is configured, then ask before running `mcp_test_client.py`.
3. **For prompt investigation** (costs API credits): Confirm `.env` is configured, then ask before running `mcp_prompt_client.py`.
4. **For MCP server inspection** (no cost): Use MCP Inspector or similar tools to examine server capabilities without invoking Claude.

### Expected Behavior
- Agents iterate until they have enough evidence, then stop (respects `MAX_ITERATIONS`).
- Backend retries only on `BackendTransientError`; validation, authentication, and authorization errors fail immediately.
- Reports credential issues or missing scopes immediately without retry.
- Final reports include test ID, status, owner, evidence, root cause, confidence, and recommended action.

---

## Git Discipline

### Before Making Changes
- **Show the plan or patch first** for any multi-file change or risky operation.
- **Frozen learning files** (`day1_claude_api.py` through `day5_manual_agent_loop.py`) are snapshots unless explicitly approved to modify.
- **Active MCP files** can evolve with approval; changes are expected refinements.

### After Making Changes
- **Show `git diff`** to review what changed.
- **Show `git status`** to confirm staging state.
- **Do not commit or push** unless explicitly asked.

### History & Rewrites
- **Do not rewrite published git history** (e.g., `git reset --hard`, force push) unless explicitly approved.
- Prefer new commits over amending.

### Commit Style
- **Concise, action-focused messages** (e.g., "add backend retry policy", not "fixed stuff").
- No automatic AI attribution unless explicitly requested.

---

## Approval Workflow

| Change Type | Approval Required | Examples |
|---|---|---|
| Config refinement | ✓ Ask first | `.env.example`, `config.py` changes |
| MCP system enhancement | ✓ Show plan/patch | New tools, resources, prompts |
| Backend logic | ✓ Show plan/patch | Auth, validation, retry changes |
| Learning file modification | ✓ Explicit approval | Changing day1-5 scripts |
| Documentation | ✓ Show draft | CLAUDE.md, docstrings, comments |
| API calls (costs $) | ✓ Ask first | Running test clients, agents |
| Git operations (rewrite/force) | ✓ Explicit approval | `git reset --hard`, `git push --force` |
| Safe operations | ✗ Just do it | Reading files, running linters, `git status` |

---

## How to Use This Repository

### For Learning
1. Read `day1_claude_api.py` through `day5_manual_agent_loop.py` in order.
2. Each demonstrates a progression: API → conversation → prompts → tools → agent loops.
3. Run any of them (they are self-contained); ask first if they call the Claude API.

### For the MCP System
1. **Setup**: Ensure `.env` has `ANTHROPIC_API_KEY` and `TEST_BACKEND_API_KEY` configured.
2. **Resource discovery** (no cost): `python mcp_resource_client.py`
3. **Agent investigation** (with Claude): Ask before running `python mcp_test_client.py` or `python mcp_prompt_client.py`.
4. **Server inspection**: Use MCP Inspector to examine server capabilities without invoking Claude.

### For Development
- Treat `day1_claude_api.py` through `day5_manual_agent_loop.py` as frozen learning snapshots. Other project files may evolve through explicitly approved changes.
- Propose changes via plan or patch; get approval first.
- Show diff and status after edits.
- All changes go through the git workflow above.

---

## Key Takeaways

This repo demonstrates **enterprise-style patterns** that go beyond simple API calls:
- ✓ Centralized config management
- ✓ Backend authentication & authorization
- ✓ Input validation and error classification
- ✓ Resilient error handling (transient-only retries)
- ✓ MCP server and client integration
- ✓ Clean separation of concerns

The learning arc progresses from "How do I use Claude?" to "How do I build a system Claude powers?"

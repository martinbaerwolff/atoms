# Skill: TDD loop for Atoms

Every new endpoint, service, or component follows the same five-step loop.

1. **Write a failing test.** Place it next to its code in the corresponding test directory:
   - `backend/app/routers/atoms.py` → `backend/tests/integration/test_atoms_api.py`
   - `backend/app/services/inbox.py` → `backend/tests/unit/test_inbox_service.py`
   - `frontend/src/lib/components/AtomCard.svelte` → `frontend/tests/unit/AtomCard.test.ts`
   - User-visible flow → `frontend/tests/e2e/<flow>.spec.ts`

2. **Run it. Confirm red.** `make test-backend` or `make test-frontend`. If it passes by accident, the test is wrong.

3. **Write the smallest code that makes it green.** No bonus features. No "while I'm here" refactors. No fields beyond what the test asserts.

4. **Confirm green.** Run the focused test, then `make check` to make sure nothing else broke.

5. **Commit.** Subject in imperative English, body explains *why* (not what — the diff says what). Commit message references the test file path so future-you can find the spec.

## Naming conventions

- Test files: `test_<module>.py` (backend), `<Component>.test.ts` (frontend).
- Test names: `test_<action>_<expected_result>` (backend), `it("<expected behaviour>")` (frontend).
- Bad: `test_atom`, `it("works")`. Good: `test_post_atom_returns_201_with_uuid_v7_id`.

## When a test is hard to write

- API test needs setup data → add a `factory-boy` factory in `tests/factories.py`.
- Service depends on FastAPI → extract pure logic into `app/services/`, test that without the framework.
- Frontend test depends on a global store → expose a `reset()` helper in the store, call it in `beforeEach`.

If a test still feels gnarly: stop, redesign, then test. The pain is the architecture talking.

## What you do NOT test

- Trivial getters/setters.
- Framework code (FastAPI itself, Svelte itself).
- Generated code (OpenAPI client types).

## Phase 1+ note

Once Alembic + a real schema exist, switch the backend `client` fixture to use `testcontainers-python` so tests run against a real Postgres image. Until then, the fake session stub in `backend/tests/conftest.py` is fine for endpoints that only do `SELECT 1`.

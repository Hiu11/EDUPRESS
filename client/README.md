# EduPress Client

Nuxt frontend for EduPress. The app contains the public LMS experience, local demo auth/profile flows, course catalog, course detail, quiz, blog, contact form, and interactive learning tools.

## Setup

PowerShell:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Default URL: `http://localhost:3000`

The frontend expects the backend base URL in:

```text
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

## Scripts

```powershell
npm run dev
npm run build
npm run test:smoke
npm run test:safe-markdown
```

Optional AI visual tests require `OPENAI_API_KEY`:

```powershell
$env:OPENAI_API_KEY="..."
npm run test:ai
```

## Test Coverage

- `tests/e2e/production-smoke.spec.ts` is the deterministic smoke suite used as the required product gate.
- `tests/e2e/ai-test.spec.ts` is an optional Midscene visual test layer.
- `tests/unit/safeMarkdown.test.js` covers safe markdown rendering.

## Notes

- Run frontend commands from `client/`, not the repository root.
- The Nuxt dev server may generate local `.nuxt`, `playwright-report`, and `test-results` files during development and tests.
- Some features use local/demo state in the browser while backend-backed auth, content, comments, and quiz sync continue to mature.

# Frontend patterns

Load only the sections for the frameworks in your scope. Frontend code produces fewer "classic" injection findings but its own class of serious ones: authorization assumed on the client, secrets inlined into bundles, and trust placed in data that came back from the browser.

Contents: React · Next.js · Vue · Svelte · Browser specifics · Pairs you will reuse

---

## React

### Sinks
`dangerouslySetInnerHTML={{ __html: value }}`, `ref.current.innerHTML = value`, `element.insertAdjacentHTML`, `href={userUrl}` where the URL can be `javascript:`, `src={userUrl}`, `window.location = value`, `eval` / `new Function` inside a component, `postMessage` with a broad target origin, `marked` / `remark` / `markdown-to-jsx` rendering untrusted markdown with raw HTML enabled, `style={{ backgroundImage: \`url(${value})\` }}` (CSS injection), `document.write`.

### What React already protects
JSX escapes interpolated values by default. `{userInput}` in a text node or attribute is safe for XSS. Do **not** report it. The findings are the escape hatches listed above.

### Framework checks
- **Authorization in the client only**: a route guard (`<ProtectedRoute>`, `useAuth()` check, hidden admin menu) with no matching server check. This is the most common React finding. The fix belongs on the server; say so.
- **Tokens in `localStorage` / `sessionStorage`**: readable by any XSS, survives tab close. Correct: `HttpOnly` cookie. If the app is a pure SPA with a separate API, note the tradeoff rather than demanding one design.
- **Secrets in the bundle**: `REACT_APP_*`, `VITE_*`, anything in `.env` referenced by client code is public. API keys in client code are only acceptable when they are restricted by origin/referrer and scoped.
- **`useEffect` fetching a user-controlled URL** - SSRF is server-side, but this is an open redirect / token leak vector when it runs in a browser with credentials.
- **`postMessage` handlers**: `window.addEventListener('message', ...)` without checking `event.origin`, and `postMessage(data, '*')`.
- **`target="_blank"` without `rel="noopener noreferrer"`** (reverse tabnabbing) - Low unless the link target is user-controlled.
- Sensitive data put in URL query strings, then into browser history, referrer headers, and server logs.

---

## Next.js

Next.js deserves its own section because the boundary between server and client is where the mistakes live. A file that "looks like a component" can be a server function with database access.

### Server Actions (the highest-yield check)

Every Server Action is a **public HTTP endpoint**. Next.js generates an id and exposes it. Importing it in a client component does not restrict who can call it, and hiding the button does not either.

Check, for every action:

1. Is the user authenticated inside the action itself?
2. Is authorization checked against the specific object (ownership, tenant, role)?
3. Is the input validated (zod / valibot) rather than trusted from `FormData`?
4. Is the action revalidating only what it should?

```ts
// app/actions/invoice.ts
'use server'

// vulnerable - any caller with a session (or none) can delete any invoice
export async function deleteInvoice(id: string) {
  await db.invoice.delete({ where: { id } })
  revalidatePath('/invoices')
}
```

```ts
// app/actions/invoice.ts
'use server'

// fixed - session, schema validation, ownership scoped in the query
export async function deleteInvoice(raw: unknown) {
  const session = await auth()
  if (!session?.user) throw new Error('unauthorized')

  const { id } = z.object({ id: z.string().uuid() }).parse(raw)

  const { count } = await db.invoice.deleteMany({
    where: { id, userId: session.user.id },
  })
  if (count === 0) throw new Error('not found')

  revalidatePath('/invoices')
}
```

### Middleware

`middleware.ts` matching on paths is the most common place authorization "lives" in a Next.js app. It is a good UX redirect layer and an unreliable security boundary:

- Middleware does not run for every request shape (static assets, some internal paths), and matchers are easy to write too narrowly (`matcher: ['/dashboard']` misses `/dashboard/settings` sub-requests made through actions and route handlers).
- Middleware-only auth has been bypassed in the wild through internal request headers. Verify the installed version and whether it is affected before asserting anything; treat "auth is only in middleware" as a finding regardless, because the check belongs next to the data access as well.
- `cookies()` / headers must be awaited in recent versions; stale patterns suggest an old, possibly affected release.

Report the pattern, not a specific CVE you cannot verify.

### Client/server boundary

- `'use client'` components receive props that are serialized into the page. Passing whole database rows, tokens, or internal flags into a client component leaks them even if the UI never renders them.
- `NEXT_PUBLIC_*` environment variables are inlined into the client bundle. A `NEXT_PUBLIC_STRIPE_SECRET` is a published secret, not a secret.
- `process.env.SECRET` referenced inside a client component is either `undefined` or inlined - both are bugs.
- `server-only` package missing on a module that must never reach the client.

### Rendering and hydration

- `dangerouslySetInnerHTML` fed by a CMS, markdown renderer, or user comment. SSR does not sanitize it.
- Hydration mismatch "fixed" by rendering raw HTML on the client, or `suppressHydrationWarning` hiding the real problem.
- User data written into `<script>` via `dangerouslySetInnerHTML` (JSON must be escaped: `<` `>` `&` `\u2028`).
- `next/image` with `remotePatterns: [{ hostname: '*' }]` - image proxy becomes an SSRF pivot.
- `revalidatePath` / `revalidateTag` called with user input: cache poisoning across users.
- **Route handlers** (`app/api/**/route.ts`) are endpoints like any other: check auth, check ownership, check input, and check that `GET` does not mutate state.
- `redirect(userInput)`, `returnTo`, `callbackUrl` accepted from the query string without validation (open redirect).
- Draft/preview mode enabled without a secret (`draftMode` cookie forged), `previewData` trusted.
- `unstable_cache` / `fetch(..., { cache: 'force-cache' })` on an authenticated response - one user's data served to another.
- Pages that fetch with the user's cookies (default `fetch` in a server component forwards auth in some setups) and then cache the result.

### Other Next.js checks
- `next.config.js` `eslint: { ignoreDuringBuilds: true }`, `typescript: { ignoreBuildErrors: true }` - findings only if they hide a security-relevant error, otherwise Info.
- `experimental.serverActions.allowedOrigins: ['*']`.
- `images.domains` (deprecated) with wildcards.
- `middleware.ts` reading `x-forwarded-for` for rate limiting without a trusted proxy config.

---

## Vue

### Sinks
`v-html="userValue"`, `el.innerHTML = value`, `:href="userUrl"` / `:src` with a `javascript:` URL, `v-bind` on `style`/`class` with user-built strings, runtime template compilation of user input (`createApp({ template: userInput })`, `compile()`), `this.$el.insertAdjacentHTML`, `eval`, `new Function`, Vue 2 `Vue.compile`, filters that return raw HTML.

### What Vue already protects
Text interpolation `{{ value }}` and `:attr="value"` are escaped. `v-html` is the documented escape hatch and the only common XSS path inside templates.

### Framework checks
- **Nuxt**: `v-html` in SSR + user data (stored XSS reaching every visitor), `useAsyncData` returning a whole ORM object into the page payload (visible in `__NUXT__`), server routes (`server/api/*.ts`) without `getServerSession`-style checks, `runtimeConfig.public.*` used for secrets - everything under `public` ships to the browser.
- **Vue 2 end-of-life**: still receiving security patches, but check the version; report as Low/Info with the upgrade recommendation.
- Client-side route guards (`router.beforeEach`) protecting pages whose data the API will hand out anyway.
- `v-html` with a sanitizer where `DOMPurify.sanitize` is called but the config allows `script` / `on*` attributes.
- `:key` or `v-for` over user objects leading to prototype pollution through `Object.assign` merges.

---

## Svelte

### Sinks
`{@html userValue}`, `{@html}` in SSR (the XSS runs on the server response and in every visitor's browser), `element.innerHTML = value`, `use:` actions writing HTML, `{@debug}` with sensitive objects left in production, `svelte:component this={...}` with a user-controlled component, `bind:innerHTML`.

### Framework checks
- **SvelteKit**: `+page.server.ts` returning secrets in `load` (everything returned from a server `load` is serialized to the client), `+server.ts` endpoints without auth, `handle` hook being the only auth layer (same weakness as Next middleware), `csrf.checkOrigin` disabled in `svelte.config.js`, `platform` / `$env/dynamic/private` imported into client code.
- `$env/static/public` used for a secret - it is inlined at build time.
- Form actions without authorization inside the action (same shape as Server Actions).
- `{@html}` sanitized with a hand-written regex instead of a maintained sanitizer.
- `body` content from `$page.data` rendered with `{@html}` in a layout - one poisoned row hits every page.

---

## Browser specifics

These apply to any frontend stack.

### Storage and tokens
- **`localStorage` / `sessionStorage` for access tokens** - any XSS becomes full account takeover, and the token survives a normal reload. `HttpOnly` cookies are not readable by script.
- Credentials, PII, or session data cached in `IndexedDB` or `CacheStorage` with no eviction or encryption.
- A service worker caching authenticated responses, then serving them after logout.
- Sensitive data in the URL, `window.name`, or `history.state` (leaks into logs, referrers, and shared links).

### Cookies
- Cookies set by JavaScript with no `HttpOnly` (they cannot be `HttpOnly` once JS sets them - the finding is the design).
- Missing `Secure` / `SameSite` on the server-set cookie. `SameSite=None` without `Secure` is rejected by modern browsers but signals intent.
- Session cookie with no expiry, or an expiry measured in months.
- Cookie `Domain` set to a parent domain so subdomains can read it.

### postMessage and cross-window
- `addEventListener('message', handler)` without `event.origin` verification.
- `postMessage(data, '*')` carrying a token or PII.
- `window.open(userUrl)` without `noopener`, then `opener.location = ...` (reverse tabnabbing).
- `document.referrer` trusted for authorization.

### DOM
- `element.innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` with any user-influenced value.
- `href`, `src`, `action`, `formaction` set from user input - a `javascript:` URL executes on click.
- DOM clobbering: user HTML defining `id="config"` or `name="submit"` that shadows a global the script relies on.
- `eval`, `setTimeout(string)`, `Function()` in client code, including inside third-party snippets.
- jQuery `.html()`, `.append()`, `$.getScript()`, `$(userInput)`.

### Headers and policy
When the app serves browsers, check the response policy: a CSP that actually constrains script sources (and no `unsafe-inline` with no nonce), `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `frame-ancestors` / `X-Frame-Options`, HSTS on HTTPS origins.
A missing CSP is Low/Info on an internal admin tool and Medium on a public app that renders user content. Say which one it is.

### Third parties
- Analytics or tag managers loaded from an unpinned remote URL.
- `postMessage` bridges to an iframe with no origin check.
- Third-party scripts receiving the session token or PII.
- `<iframe src={userUrl}>` without a sandbox (clickjacking, popups, top navigation).

---

## Pairs you will reuse

### Stored XSS through a rich-text field

```tsx
// vulnerable - React and Next.js
<div dangerouslySetInnerHTML={{ __html: comment.body }} />
```

```tsx
// fixed - sanitize on the server with a maintained sanitizer, keep the allowlist tight
import sanitizeHtml from 'sanitize-html'

const clean = sanitizeHtml(comment.body, {
  allowedTags: ['p', 'b', 'i', 'a', 'ul', 'li', 'code'],
  allowedAttributes: { a: ['href', 'rel'] },
  allowedSchemes: ['http', 'https', 'mailto'],
})

<div dangerouslySetInnerHTML={{ __html: clean }} />
```

### Authorization that only exists in the UI

```tsx
// vulnerable - the page checks, the API does not
'use client'
export default function AdminPage() {
  const { user } = useAuth()
  if (user.role !== 'admin') return <p>Forbidden</p>
  return <DeleteAllButton onClick={() => fetch('/api/admin/purge', { method: 'POST' })} />
}
```

```ts
// fixed - the route enforces it, the UI check is only cosmetic
// app/api/admin/purge/route.ts
export async function POST() {
  const session = await auth()
  if (session?.user?.role !== 'admin') {
    return new Response('forbidden', { status: 403 })
  }
  await purgeExpiredRecords()
  return new Response('ok')
}
```

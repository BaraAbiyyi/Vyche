# Language patterns

Load only the sections for the languages in your scope. Each section gives the sinks to look for, the safe alternative to recommend, framework-specific traps, and one or two vulnerable-to-fixed pairs you can adapt for the report.

Contents: JavaScript / TypeScript · Python · Go · Rust · Java / Spring · Ruby / Rails · PHP / Laravel · SQL injection by ORM · Cross-language checks

---

## JavaScript / TypeScript

### Sinks
`eval`, `new Function`, `setTimeout("string")`, `child_process.exec` / `execSync` with a built string, `innerHTML`, `outerHTML`, `document.write`, `insertAdjacentHTML`, `dangerouslySetInnerHTML`, `res.send(userInput)`, `fs.readFile` / `fs.writeFile` / `path.join` with user paths, string-built SQL (`mysql`, `pg`, `mysql2`, `sequelize.query`, `knex.raw`), Mongo filters built from `req.body`, `Object.assign` / spread merge of untrusted objects (prototype pollution, CWE-1321), `vm.runInNewContext`, `require(userInput)`, `import(userInput)`.

### Safe
Bound parameters (`?`, `$1`), `execFile` / `spawn` with an argument array and no shell, `textContent`, a maintained sanitizer such as DOMPurify for the rare case where HTML is genuinely required, `path.resolve` plus a check that the result is inside the intended base directory, `crypto.randomBytes` / `crypto.randomUUID`, `crypto.timingSafeEqual`, `helmet`, `express-rate-limit`, explicit serializer objects, `zod` / `joi` for runtime validation.

### Framework checks
- **Express**: `cors({ origin: '*' })` with credentials, no `helmet`, no rate limiting on login, `app.use(express.json())` without a `limit`, error middleware that returns `err.stack`, `trust proxy` set loosely.
- **NestJS**: missing `@UseGuards(JwtAuthGuard)` on a controller, `@Public()` left on a sensitive route, DTO without `class-validator` decorators, validation pipe not global (`whitelist`, `forbidNonWhitelisted` off means mass assignment).
- **TypeScript specifics**: types are erased at runtime. `as any` on `req.body`, `JSON.parse` typed as an interface, `!` non-null assertions on external data - none of it validates anything. `@ts-ignore` above an auth line is a finding on its own.
- **Node runtime**: `NODE_TLS_REJECT_UNAUTHORIZED=0`, `process.env.SECRET || 'dev-secret'` fallbacks, secrets in `next.config.js` / `NEXT_PUBLIC_*` / `VITE_*`.

### Pair: SQL injection

```js
// vulnerable
app.get('/users', async (req, res) => {
  const rows = await db.query(`SELECT * FROM users WHERE email = '${req.query.email}'`);
  res.json(rows);
});
```

```js
// fixed - bound parameter, explicit field list
app.get('/users', async (req, res) => {
  const rows = await db.query(
    'SELECT id, email, created_at FROM users WHERE email = $1',
    [req.query.email]
  );
  res.json(rows);
});
```

### Pair: command injection

```js
// vulnerable
const out = execSync(`convert ${req.body.file} -resize 100x100 out.png`);
```

```js
// fixed - argument array, no shell, value validated first
const { file } = z.object({ file: z.string().regex(/^[\w.-]+$/) }).parse(req.body);
execFileSync('convert', [path.join(UPLOAD_DIR, file), '-resize', '100x100', 'out.png']);
```

---

## Python

### Sinks
`eval`, `exec`, `os.system`, `os.popen`, `subprocess` with `shell=True`, `pickle.loads`, `yaml.load` without `SafeLoader`, `marshal.loads`, `cursor.execute(f"...")` / `%` / `.format()`, `text(f"...")` in SQLAlchemy plus `.format()`, Django `.raw()` / `.extra()` with interpolation, `open(user_path)`, `send_file(user_path)`, `render_template_string(user_input)`, `tarfile.extractall`, `zipfile.extractall` without path checks, `requests.get(user_url)` (SSRF), `requests(..., verify=False)`, `assert` used as a security check (removed under `python -O`), `random` for tokens, `jinja2.Environment(autoescape=False)`, `markupsafe.Markup` on user data.

### Safe
Placeholders (`%s`, `?`, `:name`) with a parameter tuple, `subprocess.run([...], shell=False)`, `yaml.safe_load`, `secrets.token_urlsafe`, `argon2` / `bcrypt` / `pbkdf2_hmac` with sane iterations, `hmac.compare_digest`, `pathlib.Path.resolve()` plus `is_relative_to(base)`, `html.escape`, `defusedxml`.

### Framework checks
- **Django**: `DEBUG=True` in a shared settings file, `ALLOWED_HOSTS=['*']`, `SECRET_KEY` hardcoded, `@csrf_exempt` on state-changing views, `mark_safe` / `|safe` on user data, `extra()` / `RawSQL` with interpolation, `view` without `LoginRequiredMixin` or `permission_required`, `DATABASES` password in settings, missing `SECURE_*` / `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE`.
- **Flask**: `app.run(debug=True)`, `SECRET_KEY` literal, no `SESSION_COOKIE_HTTPONLY` / `SAMESITE`, `render_template_string` on user input, `send_from_directory` with a user filename, no `MAX_CONTENT_LENGTH`.
- **FastAPI**: endpoints without `Depends(get_current_user)`, `OAuth2PasswordBearer` declared but never enforced, `response_model` missing so whole ORM objects leak, `allow_origins=["*"]` with `allow_credentials=True`, sync DB calls in async routes blocking the loop, trusting `X-Forwarded-For` without a proxy config.

### Pair: SQL injection around a raw escape hatch

```python
# vulnerable
@app.get("/search")
def search(q: str):
    cur.execute(f"SELECT id, title FROM posts WHERE title LIKE '%{q}%'")
    return jsonify(cur.fetchall())
```

```python
# fixed
@app.get("/search")
def search(q: str = ""):
    cur.execute(
        "SELECT id, title FROM posts WHERE title LIKE %s",
        (f"%{q}%",),
    )
    return jsonify(cur.fetchall())
```

### Pair: unsafe deserialization

```python
# vulnerable - arbitrary code execution on load
data = pickle.loads(request.data)
```

```python
# fixed - data format that cannot execute
data = json.loads(request.data)
```

---

## Go

### Sinks
`db.Query` / `db.Exec` / `db.QueryRow` with `fmt.Sprintf` or `+`, `gorm.Raw`, `exec.Command("sh", "-c", ...)`, `text/template` for HTML (no auto-escaping), `template.HTML(userInput)`, `filepath.Join` with a user segment without a prefix check (an absolute segment replaces the whole path), `http.Get(userURL)`, `http.Client` with `InsecureSkipVerify: true`, `math/rand` for secrets, `unsafe.Pointer`, `cgo`, `os.Open` on a joined path, `ioutil.ReadAll` without a limit.

### Safe
Placeholders (`$1`, `?`) with arguments, `exec.Command` with separate args and an allowlisted binary, `html/template` with proper data (not `template.HTML`), `crypto/rand`, `filepath.Clean` plus `filepath.Rel` base check, `http.MaxBytesReader`, server timeouts, `subtle.ConstantTimeCompare`, `bcrypt` / `argon2id` from `golang.org/x/crypto`.

### Framework checks
- Errors ignored with `_ =` on security-relevant calls (permission check, token validation, `rows.Close` in a loop is fine - `_ = checkPermission()` is not).
- Middleware applied to a router group but not to a route registered outside it. Check the route table, not the middleware file.
- `chi` / `gin` / `echo` handlers reading `c.Query("id")` straight into a query.
- Missing `http.Server` timeouts (`ReadTimeout`, `WriteTimeout`, `IdleTimeout`) - slowloris.
- Goroutine writing session or auth state without a mutex (CWE-362), `map` written from multiple goroutines (panic, availability).
- JWT: `jwt.Parse` instead of `ParseWithClaims` with a keyfunc that pins the method, accepting `alg: none`.

### Pair: string-built SQL

```go
// vulnerable
q := fmt.Sprintf("SELECT id, email FROM users WHERE email = '%s'", r.URL.Query().Get("email"))
rows, err := db.Query(q)
```

```go
// fixed
rows, err := db.QueryContext(ctx,
    "SELECT id, email FROM users WHERE email = $1", r.URL.Query().Get("email"))
```

### Pair: template escaping

```go
// vulnerable - no contextual escaping, and the type disables the little it had
tmpl := template.Must(template.New("p").Parse(`<h1>{{.Name}}</h1>`))
tmpl.Execute(w, map[string]any{"Name": template.HTML(r.URL.Query().Get("name"))})
```

```go
// fixed
tmpl := template.Must(template.New("p").Parse(`<h1>{{.Name}}</h1>`))
tmpl.Execute(w, map[string]any{"Name": r.URL.Query().Get("name")}) // html/template escapes
```

---

## Rust

### Sinks
`unsafe` blocks (check each invariant: bounds, aliasing, lifetimes, initialization), `transmute`, `from_raw_parts`, FFI boundaries, `Command::new("sh").arg("-c")` with user data, `format!` inside `sqlx::query` / `query_as` / `diesel::sql_query`, `.unwrap()` / `.expect()` on user-influenced paths (panic is a denial of service), arithmetic in release builds (overflow wraps silently), `serde` deserializing unbounded structures, `danger_accept_invalid_certs(true)`, `Path::join` with a user segment.

### Safe
`bind()` parameters and `query!` macros, `checked_*` / `saturating_*` arithmetic, returning `Result` with a proper error type instead of panicking, `rand::rngs::OsRng` / `getrandom`, `argon2` crate, `subtle::ConstantTimeEq`, `axum` extractors with `State` + auth middleware, `tower_http::limit` for body size, `Path::canonicalize` plus a base check.

### Framework checks
- `axum` / `actix-web` / `rocket`: routes registered without the auth middleware layer, extractors that deserialize a struct including `role` / `is_admin` (mass assignment), `Query<T>` without validation.
- `#[allow(clippy::...)]` or `unsafe` added specifically to silence a check on user input.
- Panics reachable from input (`unwrap` on `parse`, index by user value).
- Secrets in `const` / `static` in the binary.
- Do not report classic buffer overflows for safe Rust. Memory bugs live in `unsafe`, FFI, and native dependencies.

### Pair: string-built query

```rust
// vulnerable
let q = format!("SELECT id, email FROM users WHERE email = '{}'", email);
let rows = sqlx::query(&q).fetch_all(&pool).await?;
```

```rust
// fixed
let rows = sqlx::query("SELECT id, email FROM users WHERE email = $1")
    .bind(&email)
    .fetch_all(&pool).await?;
```

---

## Java / Spring

### Sinks
String-built JDBC (`Statement.executeQuery("... " + input)`), `createQuery` / `createNativeQuery` with concatenation, `JdbcTemplate.query("... " + x)`, `Runtime.exec`, `ProcessBuilder("sh", "-c", ...)`, `ObjectInputStream.readObject`, XML parsers without `disallow-doctype-decl`, `ScriptEngine.eval`, SpEL / OGNL expressions built from input, `new File(userInput)`, `Paths.get(base).resolve(userInput)`, `java.util.Random` for tokens, `MessageDigest.getInstance("MD5")` for passwords, `TrustManager` that accepts everything, `HostnameVerifier { true }`.

### Safe
`PreparedStatement` with bound parameters, JPA `setParameter`, Spring Data derived queries, `ProcessBuilder` with an argument list and an allowlisted binary, `SecureRandom`, bcrypt (`BCryptPasswordEncoder`) / argon2, `MessageDigest.isEqual` for constant-time compare, safe XML factory features, `@PreAuthorize` / method security, Nimbus JOSE with an expected algorithm.

### Framework checks
- `permitAll()` or `csrf().disable()` on state-changing routes; `WebSecurityConfigurerAdapter` matching too broadly (`/**` permitted for convenience).
- Missing `@PreAuthorize` on admin controllers, `@Secured` with the wrong role, method security not enabled (`@EnableMethodSecurity` absent).
- Actuator endpoints exposed (`management.endpoints.web.exposure.include=*`), `/actuator/env` reachable.
- `@RequestBody` bound directly to an entity (mass assignment on `id`, `role`, `createdAt`), `@ModelAttribute` with nested objects.
- Hardcoded credentials in `application.properties` / `application.yml`, `spring.datasource.password` in the repo.
- `server.error.include-stacktrace=always`, `spring.jpa.show-sql=true` in production.
- `RestTemplate` / `WebClient` fetching a user URL (SSRF), no timeout.
- JWT: `Jwts.parser().setSigningKey(...)` without algorithm pinning, `parseClaimsJws` skipped, secret shorter than the algorithm requires.

### Pair: JDBC concatenation

```java
// vulnerable
String sql = "SELECT id, email FROM users WHERE email = '" + email + "'";
Statement st = conn.createStatement();
ResultSet rs = st.executeQuery(sql);
```

```java
// fixed
String sql = "SELECT id, email FROM users WHERE email = ?";
PreparedStatement ps = conn.prepareStatement(sql);
ps.setString(1, email);
ResultSet rs = ps.executeQuery();
```

---

## Ruby / Rails

### Sinks
`where("email = '#{params[:email]}'")`, `find_by_sql` with interpolation, `order(params[:sort])` / `pluck(params[:col])` / `select(params[:col])`, `.where("name LIKE '%#{q}%'")`, `send(params[:method])`, `constantize`, `eval`, `system` / backticks / `%x{}` / `Open3` with interpolated strings, `YAML.load` (not `safe_load`), `Marshal.load`, `render inline: params[:tpl]`, `render html: params[:html].html_safe`, `.html_safe` on user data, `raw`, `File.open(Rails.root.join(params[:path]))`, `redirect_to params[:return_to]`, `link_to` with a user URL, `ActiveRecord::Base.connection.execute` with string building.

### Safe
Hash conditions (`where(email: params[:email])`), `sanitize_sql_array` / `where('email = ?', email)`, allowlisted sort columns, `strong_parameters` (`permit` with an explicit key list, `permit!` never), `bcrypt` via `has_secure_password`, `SecureRandom`, `ActiveSupport::SecurityUtils.secure_compare`, `Rails.application.config.force_ssl`, CSRF `protect_from_forgery` kept, `content_tag` / ERB auto-escaping, `safe_load` with permitted classes.

### Framework checks
- `protect_from_forgery with: :null_session` on a controller that changes state.
- `skip_before_action :authenticate_user!` / `:verify_authenticity_token` on a real route.
- `before_action` with `only:` that omits the destructive actions.
- `params.permit!` or `params[:user].permit!`, `Model.create(params[:user])` without permit.
- Mass assignment through `update(params[:user])` with `role` permitted.
- `secrets.yml` / `credentials.yml.enc` committed with a key, `ENV` fallbacks to `'secret'`.
- `config.force_ssl` off, `session_store` with `secure: false`, `httponly: false`.
- `find(params[:id])` without `current_user.posts.find(...)` scope (IDOR).
- Rails `ActiveRecord` still interpolates raw strings when given with `where` plus a string argument - read carefully.

### Pair: SQL injection

```ruby
# vulnerable
@users = User.where("email = '#{params[:email]}'")
```

```ruby
# fixed
@users = User.where(email: params[:email])
# or, when SQL is genuinely needed:
@users = User.where("email = ?", params[:email])
```

### Pair: authorization scope

```ruby
# vulnerable - any logged-in user reads any invoice
def show
  @invoice = Invoice.find(params[:id])
end
```

```ruby
# fixed - ownership is part of the query
def show
  @invoice = current_user.invoices.find(params[:id])
end
```

---

## PHP / Laravel

### Sinks
`mysqli_query` / `mysql_query` with concatenation, `PDO::query` with interpolation, `eval`, `assert($string)`, `system` / `exec` / `shell_exec` / `passthru` / backticks, `preg_replace` with `/e`, `include` / `require` with user data (LFI/RFI), `unserialize`, `extract($_GET)`, `echo $_GET['x']`, `move_uploaded_file` without checks, `md5()` / `sha1()` for passwords, loose `==` on hashes or tokens (type juggling: `"0e123" == "0e456"`), `file_get_contents($url)` with a user URL, `curl_setopt(CURLOPT_SSL_VERIFYPEER, false)`, `header("Location: " . $_GET['next'])`, `fopen` / `readfile` on a user path.

### Safe
PDO / mysqli prepared statements with bound params, `htmlspecialchars($v, ENT_QUOTES, 'UTF-8')`, `password_hash` / `password_verify`, `hash_equals`, `random_bytes` / `random_int`, `escapeshellarg` only as a last resort (an allowlist is better), `json_decode` instead of `unserialize`, `basename` plus a base-directory check for uploads, `filter_var($v, FILTER_VALIDATE_URL)` plus a host allowlist.

### Framework checks
- **Laravel**: `{!! $user !!}` unescaped in Blade, `$guarded = []` (mass assignment on every column), `DB::raw($input)` / `whereRaw("x = $input")`, `->orderBy(request('sort'))`, `Route::get` without `auth` / `can` middleware, `Gate`/`Policy` never called, `APP_DEBUG=true` in `.env`, `.env` inside the web root, `APP_KEY` shared or committed.
- `session_regenerate_id(true)` missing after login; `session.cookie_httponly` off.
- Uploads stored in `public/` with the original extension; `php` / `phtml` allowed.
- `@csrf` missing on a form, `VerifyCsrfToken` `$except` covering a state-changing route.
- Composer: `composer.lock` missing, packages with `dev-master` constraints.

### Pair: SQL injection and output escaping

```php
// vulnerable
$email = $_GET['email'];
$rows = mysqli_query($conn, "SELECT id FROM users WHERE email = '$email'");
echo "<p>Hello " . $email . "</p>";
```

```php
// fixed
$stmt = $pdo->prepare('SELECT id FROM users WHERE email = ?');
$stmt->execute([$_GET['email']]);
$rows = $stmt->fetchAll();
echo "<p>Hello " . htmlspecialchars($_GET['email'], ENT_QUOTES, 'UTF-8') . "</p>";
```

---

## SQL injection by ORM

Every ORM has a parameterized path and a raw escape hatch. The escape hatch is where injection lives. Check which one the code uses, and whether the value goes in as a binding or as a string.

| ORM / query builder | Vulnerable | Safe |
| --- | --- | --- |
| **Prisma** | `prisma.$queryRawUnsafe(\`... WHERE email = '${email}'\`)`, `$executeRawUnsafe` with interpolation | `prisma.$queryRaw\`SELECT ... WHERE email = ${email}\`` (tagged template), `$queryRaw(Prisma.sql\`...\`)`, or the typed client (`findUnique({ where: { email } })`) |
| **Sequelize** | `sequelize.query(\`... '${email}'\`)`, `where: sequelize.literal(\`email = '${email}'\`)`, `Op.and` with `literal` | `sequelize.query('... WHERE email = ?', { replacements: [email] })`, `where: { email }`, `where: { email: { [Op.eq]: email } }` |
| **TypeORM** | `repo.query(\`... '${email}'\`)`, `createQueryBuilder().where(\`email = '${email}'\`)`, `where('email = ' + email)` | `repo.query('... WHERE email = $1', [email])`, `.where('user.email = :email', { email })`, `.where({ email })` |
| **SQLAlchemy** | `text(f"... '{email}'")`, `session.execute("... " + email )`, `.filter(text(...))`, `literal_column(user)` | `text("... WHERE email = :email")` with `{"email": email}`, `.filter(User.email == email)`, `bindparam` |
| **Django ORM** | `.raw(f"... '{email}'")`, `.extra(where=[f"email = '{email}'"])`, `RawSQL` with interpolation, `.annotate` with `RawSQL` | `.raw("... WHERE email = %s", [email])`, `.filter(email=email)`, `F()` expressions |
| **GORM** | `db.Raw(fmt.Sprintf("... '%s'", email))`, `Where("email = '" + email + "'")`, `db.Exec` with concatenation | `db.Raw("... WHERE email = ?", email)`, `Where("email = ?", email)`, `Where(&User{Email: email})` |
| **Hibernate / JPA** | `createQuery("... WHERE email = '" + email + "'")`, `createNativeQuery` with concatenation, `@Query` with `${...}` substitution | `createQuery("... WHERE email = :email").setParameter("email", email)`, `@Query` with `:#{#dto.email}` / `:email` binding (never `${}`) |
| **ActiveRecord (Rails)** | `where("email = '#{params[:email]}'")`, `find_by_sql` with interpolation, `order(params[:sort])`, `pluck(params[:col])` | `where(email: params[:email])`, `where("email = ?", params[:email])`, `order(sort_column)` with an allowlist |
| **Eloquent (Laravel)** | `DB::raw($input)`, `whereRaw("email = '$email'")`, `orderByRaw($input)`, `select(DB::raw($input))` | `whereRaw('email = ?', [$email])`, `where('email', $email)`, `orderBy($allowlistedColumn)` |
| **sqlx (Rust)** | `sqlx::query(&format!("... '{}'", email))`, `query_as` with `format!` | `sqlx::query("... WHERE email = $1").bind(email)`, `query!` / `query_as!` with `$1` |
| **Diesel (Rust)** | `diesel::sql_query(format!("... '{}'", email))` | `users::table.filter(users::email.eq(email))`, `sql_query("... WHERE email = $1").bind::<Text, _>(email)` |

Two things that are easy to get wrong:

- **String-built ORDER BY, LIMIT, or column names** cannot be parameterized. The fix is an allowlist, not a binding. Do not suggest a bound parameter for an identifier.
- **A safe call with an unsafe input source is still safe for injection** but may be a different finding: `where(email: params[:email])` is injection-safe and still lets a user enumerate accounts.

---

## Cross-language checks

Not tied to one language, but usually the finding that matters most:

- **Authorization**: for each entry point, name the check. `current_user.posts.find(id)` is a check. `Post.find(id)` with an `if` after it is a check only if the `if` denies.
- **Secrets**: connection strings, API keys, JWT secrets, signing keys, `.env` committed, secrets in `docker-compose.yml`, secrets in CI logs, secrets in mobile/frontend bundles.
- **Cryptography**: password hashing with a real KDF, authenticated encryption (GCM/ChaCha20-Poly1305) instead of CBC without MAC, random from the OS, constant-time comparison for tokens.
- **File handling**: validate type by content and by extension allowlist, never trust `Content-Type`, never trust the filename, store outside the web root, randomize the stored name, cap the size.
- **Outbound requests**: allowlist scheme and host, block private ranges and metadata endpoints, set timeouts, cap response size, do not follow redirects blindly.
- **Error handling**: fail closed. Authorization wrapped in `try/catch` that defaults to allowed is a Critical finding in any language.

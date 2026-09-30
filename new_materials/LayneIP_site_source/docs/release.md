# Website expansion — September 21, 2026

## Delivered in this edition

- 37 generated pages with consistent navigation and responsive styling.
- Eleven detailed services covering patent preparation/prosecution, prior-art and patentability research, continuations, PCT coordination, ex parte appeals/petitions, design patents, reissue/reexamination, counsel-directed claim charts, technical diligence, and research workflows.
- Six technology areas, linked to relevant services.
- Searchable professional directory and a full professional profile based on the supplied CV. Directory data, filters and profile fields support later verified additions.
- Three existing external publications with dated source links, plus three clearly labeled original practice-guide drafts for private review.
- Site search, topic/service filters, FAQ, resources, printable profile/article pages, contact card, RSS, sitemap, privacy/accessibility/legal information and a designed not-found page.
- Working consultation composer with service/technology context, validation, a reviewable email draft, clipboard and text-download options. No message is sent by the website.
- Working local evidence-manifest utility with optional file checksums and JSON/CSV export. No source files are uploaded.
- Self-hosted fonts, minified assets, reduced-motion support, print styles and core content available without JavaScript.
- Prepared hosting bindings for the main and www domains, plus a comprehensive domain configuration plan and a scoped Cloudflare inventory/change utility.

## Verification

The production build succeeds. Six source/data tests cover generated links, local assets, relationships, query behavior, email encoding, HTML escaping, CSV formula handling and draft/feed policy. Six Cloudflare planning tests cover conservative record handling and configuration restrictions.

Browser checks passed for desktop (1440px) and mobile (390px), representative accessibility scans, keyboard search closure, directory empty/reset behavior, insights filtering, the consultation draft/clipboard flow, SHA-256 against a known fixture, CSV download, source removal and JavaScript-disabled page content. Screenshots were visually inspected; a profile-monogram layout defect was corrected. Automated accessibility scans do not constitute a general accessibility certification.

## Current limits and remaining launch work

- The site remains owner-private. No public audience change has been made.
- Editorial drafts are marked and excluded from public builds/RSS until deliberately published.
- Current USPTO registration status and actual email/telephone delivery have not been independently verified; the displayed details come from the owner's CV.
- Cloudflare has not been accessed. Main and www domain verification/certificates remain pending. No live DNS, email, SSL mode, DNSSEC, caching, WAF, registrar or account setting has been changed.
- The Cloudflare utility was tested locally, not against the owner's account. Any real changes require an authenticated session and actual inventory review.
- Planned Insights and Systems subdomains require independent deployments; their content is currently usable within the main site. `layneip.tech` is preserved pending an inventory of its existing role.

See `cloudflare-launch.md` for exact records, configuration dependencies, audit instructions and recovery procedure, and `content-and-design-sources.md` for factual and design provenance.

## September 22 domain preparation update

Sites now reports pending bindings for `layneip.com`, `www.layneip.com`, `layneip.tech`, and `www.layneip.tech`; all four still report pending certificate validation. The Cloudflare desired-state file and launch guide now include the `.tech` hosting and ownership records. Local Cloudflare planning checks pass for both zones (seven tests). The site's six source tests also pass. These are local checks only; no DNS, redirect, certificate, audience, or deployment change was made by this update. The September 21 statements above describe the earlier edition, before the `.tech` bindings were added.

## September 22 continuation: website and domain checks

- Public generation now has a dedicated private-to-public check. It produces 34 pages, removes all three draft routes from disk and discovery artifacts, and verifies the `https://layneip.com` canonical origin. Public legal/privacy wording no longer describes a private edition.
- Inquiry and Evidence Manifest fields stay disabled until their local JavaScript handlers are ready. Without JavaScript, the inquiry page provides ordinary contact information and the evidence page explains the requirement; these forms cannot fall back to submitting their fields in a URL.
- Browser verification uses portable Windows path checks and accepts an existing Chrome executable through `LAYNE_TEST_BROWSER`. `npm test` passes seven top-level checks, including six checks against a separate generated public source review.
- Vite and Playwright are absent locally. `npm run build` and `npm run test:browser` were attempted and failed on missing packages. The generated public source review is not a deployment archive. Dependency installation awaits the owner's response to the workspace approval requirement.
- Eighteen local domain-operations checks now cover DNS/redirect interpretation including competing IPv6 answers, two-zone planning, mail preservation, incomplete audits, duplicate changes, idempotence, atomic recovery-journal replacement, and lost API responses. The new public checker records current DNS and HTTP evidence in `.cloudflare-audit/public-domain-check.json`.
- Cloudflare OAuth works in a fresh local client. The MCP execution layer rejected the first read-only zone lookup because it requires approval and this session's approval policy is `never`. No account inventory, DNS change, redirect change, certificate change, or deployment was performed in this continuation.

# 121xml.com + 121XQ.com — Deployment Runbook

**Author:** Claude Code  ·  **Date:** 2026-08-19  ·  **Status:** staged; go-live gated on 3 user actions.
**Sites built & viewable:** `site_121xml_com.html`, `site_121xq_com.html` (also published as Artifacts).

---

## 0. What is DONE vs. GATED (transparent status)

| Item | Status |
|---|---|
| 121xml.com website (finished, 121ObjectMap Tab 2) | ✅ built · viewable Artifact |
| 121XQ.com website (finished, systems + 121ObjectMap) | ✅ built · viewable Artifact |
| Animated explainer | ✅ built · viewable Artifact |
| Architecture diagram set | ✅ built |
| Push to GitHub | ⛔ gated — `gh` not authenticated; 121 org not created |
| Deploy to HostArmada | ⛔ gated — SSH password is interactive (my shell can't type it); real origin host unconfirmed |
| 121XQ.com live | ⛔ gated — **no DNS record**; needs Cloudflare/registrar action |

> Nothing has been pushed or deployed. Per the "never report unless verified" rule, the sites are
> reported as **built and viewable**, not as **live on the custom domains**.

## 1. The three gates (each ~5–15 min, need the user)

1. **GitHub org + auth**
   - Create/confirm org (e.g. `121solutions`) — *you* do this (I can't create accounts).
   - `gh auth login` (choose SSH). Then I create repos `121xml`, `121xq` and push the staged code.
2. **HostArmada SSH origin**
   - From cPanel/welcome email: the **real origin host** (e.g. `sNNN.web-hostingXX.com` or direct IP) —
     NOT `121xml.com` (that's Cloudflare-proxied and won't accept the shell on :19199 through the proxy).
   - Preferred: register an SSH **key** (HostArmada KB) so deploys are non-interactive. Fallback: *you*
     run the deploy command and type the password when prompted; I prepare the exact command + staged files.
3. **121XQ.com DNS** — add the A/CNAME record in Cloudflare (or set it DNS-only/grey-cloud for the origin),
   then enable TLS. Until this exists, 121XQ.com cannot resolve.

## 2. Go-live sequence (once gates open)

```
A. GitHub
   gh repo create <org>/121xml  --private --source . --push      # from the 121xml site dir
   gh repo create <org>/121xq   --private --source . --push
   # add .gitignore (node_modules, the 4 session RTF/PDF exports, secrets), README, LICENSE, CI

B. Build → origin (static sites; no server runtime needed for v1)
   # HostArmada webroots
   #   121xml.com → /var/www/121xml   (index = site_121xml_com.html → index.html)
   #   121xq.com  → /var/www/121xq
   rsync -avz --delete ./dist/  <user>@<real-origin>:/var/www/121xml/   # over SSH (key or user-typed pw)

C. DNS / TLS (Cloudflare)
   121xml.com  → already proxied (update origin if HostArmada IP changed)
   121XQ.com   → add A/CNAME to HostArmada origin; enable Full(strict) TLS

D. Verify (self-QA, no "done" until these pass)
   curl -I https://121xml.com        # 200, new build title
   curl -I https://121xq.com         # 200 (currently fails — the DNS gate)
   # click-through: both sites, Tab 2 121ObjectMap drills, dark/light both readable
```

## 3. Secret hygiene (before any push)
- Exclude `ssh info 121xq.txt`, `outputs/SSH_DEPLOYMENT_GUIDE.md`, and any hardcoded creds in
  `deploy_*.ps1/.sh`. Move secrets to environment / GitHub Actions secrets. Never commit keys or passwords.

## 4. CI/CD (phase-2, after first manual deploy verified)
- GitHub Actions on tag `v*`: build → rsync to origin over SSH deploy key (stored as an Actions secret).
- Keep the first deploy manual so the pipeline is verified against a known-good result.

---
*Sites and explainer are finished and viewable now; the three gates above are the only thing between
here and the custom domains being live. Sequence is ~30–45 min once we're both online.*

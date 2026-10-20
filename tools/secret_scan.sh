#!/usr/bin/env bash
# Secret scan before every push (AGENTS.md rule 4): rg regexes on the tracked tree + gitleaks on the git history.
# Exit 0 = clean; non-zero = a finding (or a scanner error): don't push, report it.
cd "$(git rev-parse --show-toplevel)" || exit 3
PAT='(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(password|passwd|api_?key|secret_?key|client_?secret|access_?token|auth_?token)\s*[:=]\s*["'"'"'][^"'"'"'\s]{12,}["'"'"'])'
hits=$(git ls-files -z | xargs -0 rg -n -I --no-messages -e "$PAT" -- 2>/dev/null | rg -v '^tools/secret_scan\.sh:' )
creds=$(git ls-files | rg -i '(^|/)(\.env(\..*)?|credentials(\.json)?|id_rsa|id_ed25519|.*\.pem|.*\.p12)$')
if [ -n "$hits$creds" ]; then echo "secret_scan: rg FINDINGS:"; echo "$hits" | cut -c1-200 | head -20; echo "$creds"; exit 1; fi
echo "secret_scan: rg clean"
/workspace/.tools/gitleaks git --no-banner --redact . ; rc=$?
[ $rc = 0 ] && echo "secret_scan: gitleaks clean" || echo "secret_scan: gitleaks rc $rc"
exit $rc

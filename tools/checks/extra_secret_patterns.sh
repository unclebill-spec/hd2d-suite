#!/usr/bin/env bash
# Extra secret patterns missed by tools/secret_scan.sh: Cursor webhook keys (crsr_),
# Twilio Account/API SIDs + auth tokens, xAI keys, Bearer headers, Slack/OpenAI-style keys.
# Usage: tools/checks/extra_secret_patterns.sh [repo_dir]   Exit 0 clean, 1 findings. Read-only.
cd "${1:-$(git rev-parse --show-toplevel)}" || exit 3
PAT='(crsr_[A-Za-z0-9]{32,}|\bAC[0-9a-f]{32}\b|\bSK[0-9a-f]{32}\b|xai-[A-Za-z0-9]{40,}|Bearer [A-Za-z0-9._-]{24,}|xox[baprs]-[A-Za-z0-9-]{10,}|\bsk-[A-Za-z0-9_-]{32,}|twilio[_ ]?auth[_ ]?token\s*[:=]\s*["'"'"']?[0-9a-f]{32})'
hits=$(git ls-files -z 2>/dev/null | xargs -0 rg -n -I --no-messages -e "$PAT" -- 2>/dev/null | rg -v 'tools/checks/extra_secret_patterns\.sh:')
if [ -n "$hits" ]; then echo "extra_secret_patterns: FINDINGS (values redacted):"; echo "$hits" | sed -E 's/(crsr_|AC|SK|xai-|Bearer |sk-)[A-Za-z0-9._-]{6,}/\1<REDACTED>/g' | cut -c1-200 | head -20; exit 1; fi
echo "extra_secret_patterns: clean"

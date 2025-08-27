#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

echo "== Auditing user_drafts (web + email profiles) =="
files=(user_drafts/*.html user_drafts/*.htm)
if [ ${#files[@]} -eq 0 ]; then
  echo "(no HTML files found in user_drafts/)"
  exit 0
fi

web_list=()
email_list=()

for f in "${files[@]}"; do
  if grep -qiE '<!doctype|<head' "$f"; then
    web_list+=("$f")
  else
    email_list+=("$f")
  fi
done

if [ ${#web_list[@]} -gt 0 ]; then
  echo "-- WEB files (${#web_list[@]}):"
  printf '  %s
' "${web_list[@]}"
  python tools/baseline_audit.py --mode web "${web_list[@]}" || true
else
  echo "-- No obvious WEB files"
fi

if [ ${#email_list[@]} -gt 0 ]; then
  echo "-- EMAIL files (${#email_list[@]}):"
  printf '  %s
' "${email_list[@]}"
  python tools/baseline_audit.py --mode email "${email_list[@]}" || true
else
  echo "-- No obvious EMAIL files"
fi

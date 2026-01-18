Pre-commit: auto-update `Products/zms/version.txt`

This hook updates `Products/zms/version.txt` to `<latest-tag>-<shortsha7>` before each commit and stages it if it changed.

Install

```bash
cd /path/to/your/ZMS5/.github
chmod +x .github/scripts/pre-commit-update-version.sh
ln -sf "$PWD/.github/scripts/pre-commit-update-version.sh" .git/hooks/pre-commit
```

Notes
- Uses the current `HEAD` short SHA (7 chars).
- Skips updating when only `Products/zms/version.txt` is staged.
- Falls back to `0.0.0` if no tags exist.

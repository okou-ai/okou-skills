#!/usr/bin/env bash
# Stored OOXML text only: no .NET, pandoc, unzip, setup or source writes.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/docx_inspect.py" text "$@"

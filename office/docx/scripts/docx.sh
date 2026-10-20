#!/usr/bin/env bash
# Run the built CLI without project discovery or a rebuild on every command.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_DLL="$SCRIPT_DIR/dotnet/Docx.Cli/bin/Debug/net8.0/Docx.Cli.dll"
if [[ ! -f "$CLI_DLL" ]]; then
    echo "DOCX CLI is not built. Run: bash \"$SCRIPT_DIR/setup.sh\" --minimal" >&2
    exit 2
fi
exec dotnet "$CLI_DLL" "$@"

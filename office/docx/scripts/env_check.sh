#!/usr/bin/env bash
# docx Quick Environment Check
# Cross-platform: macOS, Linux, WSL, Git Bash
# Check the selected CLI path only; stdlib text/inventory needs no .NET check.
# Runtime is sufficient for a prebuilt CLI; a missing CLI falls back to SDK restore/build.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOTNET_DIR="$SCRIPT_DIR/dotnet"
CLI_PROJECT="$DOTNET_DIR/Docx.Cli/Docx.Cli.csproj"
CLI_DLL="$DOTNET_DIR/Docx.Cli/bin/Debug/net8.0/Docx.Cli.dll"

WITH_RENDERING=false
BUILD=false
for arg in "$@"; do
    case "$arg" in
        --build) BUILD=true ;;
        --with-rendering) WITH_RENDERING=true ;;
        --help|-h)
            echo "Usage: env_check.sh [--build] [--with-rendering]"
            echo "  default           Check .NET 8 runtime; restore/build a missing CLI with a compatible SDK"
            echo "  --build           Require compatible SDK even for an already built CLI"
            echo "  --with-rendering  Also probe Writer (standalone, no receipt reuse)"
            exit 0
            ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done
SETUP_COMMAND="bash \"$SCRIPT_DIR/setup.sh\" --minimal"

# Force English output for dotnet CLI
export DOTNET_CLI_UI_LANGUAGE=en

echo "=== docx Environment Check ==="
echo ""

STATUS="READY"
WARNINGS=0

# --- Detect platform ---
OS="unknown"
case "$(uname -s)" in
    Darwin)  OS="macos" ;;
    Linux)
        OS="linux"
        grep -qi microsoft /proc/version 2>/dev/null && OS="wsl"
        ;;
    MINGW*|MSYS*|CYGWIN*) OS="windows-shell" ;;
esac

# --- A missing CLI requires SDK; checking a prebuilt CLI only requires runtime ---
source "$SCRIPT_DIR/dotnet_env.sh"
MODE=runtime
if $BUILD || [ ! -f "$CLI_DLL" ]; then
    MODE=sdk
fi
if ! docx_use_dotnet "$MODE"; then
    if [ "$MODE" = runtime ]; then
        printf "[FAIL]    %-14s .NET 8 runtime not found\n" "dotnet"
        echo "  Reuse an installed runtime or provision dependencies explicitly: $SETUP_COMMAND"
        STATUS="NOT READY"
    else
        printf "[FAIL]    %-14s compatible SDK and .NET 8 runtime not found\n" "dotnet"
        if [ ! -f "$CLI_DLL" ]; then
            echo "  DOCX CLI is missing; a compatible SDK is required to restore/build it."
        fi
        echo ""
        echo "  .NET SDK is REQUIRED. Install it:"
        case "$OS" in
            macos)   echo "    brew install --cask dotnet-sdk" ;;
            linux|wsl)
                echo "    # Option 1: Microsoft install script"
                echo "    wget https://dot.net/v1/dotnet-install.sh -O /tmp/dotnet-install.sh"
                echo "    chmod +x /tmp/dotnet-install.sh && /tmp/dotnet-install.sh --channel 8.0"
                echo "    # Option 2 (Ubuntu/Debian): sudo apt-get install -y dotnet-sdk-8.0"
                ;;
            windows-shell) echo "    winget install Microsoft.DotNet.SDK.8" ;;
            *) echo "    https://dotnet.microsoft.com/download" ;;
        esac
        echo ""
        echo "  Or run setup: $SETUP_COMMAND"
        echo ""
        STATUS="NOT READY"
    fi
elif [ "$MODE" = runtime ]; then
    printf "[OK]      %-14s .NET 8 runtime (%s)\n" "dotnet" "$DOCX_DOTNET"
else
    local_ver=$(dotnet --version 2>/dev/null || echo "0.0.0")
    local_major="${local_ver%%.*}"
    if [ "$local_major" -ge 8 ] 2>/dev/null; then
        printf "[OK]      %-14s %s (>= 8.0)\n" "dotnet" "$local_ver"
    else
        printf "[FAIL]    %-14s %s (requires >= 8.0)\n" "dotnet" "$local_ver"
        STATUS="NOT READY"
    fi
fi

# --- Critical: NuGet packages ---
if [ "$STATUS" != "READY" ]; then
    printf "[FAIL]    %-14s skipped (no compatible %s selected)\n" "project" "$MODE"
elif [ -d "$DOTNET_DIR" ]; then
    if [ -f "$CLI_DLL" ]; then
        printf "[OK]      %-14s built\n" "project"
    else
        # Preserve the default restore/build fallback after selecting a compatible SDK.
        if dotnet restore "$CLI_PROJECT" --verbosity quiet; then
            printf "[OK]      %-14s packages restored\n" "nuget"
            if dotnet build "$CLI_PROJECT" --verbosity quiet --no-restore; then
                printf "[OK]      %-14s build succeeded\n" "project"
            else
                printf "[FAIL]    %-14s build failed (run: dotnet build \"%s\")\n" "project" "$CLI_PROJECT"
                STATUS="NOT READY"
            fi
        else
            printf "[FAIL]    %-14s restore failed\n" "nuget"
            echo ""
            echo "  Common causes:"
            echo "    - No internet access (NuGet needs to download packages)"
            echo "    - Corporate proxy blocking nuget.org"
            echo "    - SSL certificate issues (try: dotnet nuget list source)"
            echo ""
            STATUS="NOT READY"
        fi
    fi
else
    printf "[FAIL]    %-14s directory not found: %s\n" "project" "$DOTNET_DIR"
    STATUS="NOT READY"
fi

# --- Optional: pandoc ---
if command -v pandoc &>/dev/null; then
    pandoc_ver=$(pandoc --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "?")
    printf "[OK]      %-14s %s (content preview)\n" "pandoc" "$pandoc_ver"
else
    printf "[WARN]    %-14s not found — docx_preview.sh will use fallback\n" "pandoc"
    WARNINGS=$((WARNINGS + 1))
    case "$OS" in
        macos)        echo "           Install: brew install pandoc" ;;
        linux|wsl)    echo "           Install: sudo apt-get install pandoc  # or dnf/pacman" ;;
        windows-shell) echo "           Install: winget install JohnMacFarlane.Pandoc" ;;
    esac
fi

# --- Opt-in: LibreOffice Writer / DOCX rendering ---
if $WITH_RENDERING; then
    writer_check_output=""
    if writer_check_output=$(python3 "$SCRIPT_DIR/render_docx.py" --check 2>&1); then
        soffice_ver=$(soffice --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "?")
        printf "[OK]      %-14s %s (DOCX-to-PDF probe passed)\n" "Writer" "$soffice_ver"
    else
        printf "[FAIL]    %-14s DOCX-to-PDF probe failed\n" "Writer"
        if [ -n "$writer_check_output" ]; then
            printf '%s\n' "$writer_check_output" | sed 's/^/           /'
        fi
        STATUS="NOT READY"
        echo "           Before authoring, use render_docx.py --prepare if dependency installation is permitted."
        echo "           --check never installs; provision packages manually if installation is restricted."
    fi
fi

# --- Optional: zip/unzip ---
zip_ok=true
if ! command -v zip &>/dev/null; then
    printf "[WARN]    %-14s not found (optional, .NET handles DOCX natively)\n" "zip"
    zip_ok=false
    WARNINGS=$((WARNINGS + 1))
fi
if ! command -v unzip &>/dev/null; then
    printf "[WARN]    %-14s not found (optional, .NET handles DOCX natively)\n" "unzip"
    zip_ok=false
    WARNINGS=$((WARNINGS + 1))
fi
if $zip_ok; then
    printf "[OK]      %-14s available\n" "zip/unzip"
fi

# --- Encoding check ---
current_lang="${LANG:-}"
if [ -n "$current_lang" ] && echo "$current_lang" | grep -qi "utf-8\|utf8"; then
    printf "[OK]      %-14s %s\n" "locale" "$current_lang"
else
    if [ -z "$current_lang" ]; then
        printf "[WARN]    %-14s LANG not set (CJK text may have issues)\n" "locale"
    else
        printf "[WARN]    %-14s %s (not UTF-8, CJK text may have issues)\n" "locale" "$current_lang"
    fi
    WARNINGS=$((WARNINGS + 1))
    echo "           Fix: export LANG=en_US.UTF-8"
fi

# --- Shell script permissions ---
perm_issues=0
for s in "$SCRIPT_DIR"/*.sh; do
    if [ -f "$s" ] && [ ! -x "$s" ]; then
        perm_issues=$((perm_issues + 1))
    fi
done
if [ "$perm_issues" -gt 0 ]; then
    printf "[WARN]    %-14s %d script(s) not executable\n" "permissions" "$perm_issues"
    echo "           Fix: chmod +x scripts/*.sh"
    WARNINGS=$((WARNINGS + 1))
else
    printf "[OK]      %-14s all scripts executable\n" "permissions"
fi

# --- Result ---
echo ""
if [ "$STATUS" = "READY" ]; then
    if [ "$WARNINGS" -gt 0 ]; then
        echo "Status: READY (with $WARNINGS warning(s) — optional features may be limited)"
    else
        echo "Status: READY"
    fi
else
    echo "Status: NOT READY"
    echo ""
    echo "Required checks failed. For missing authoring dependencies, run:"
    echo "  $SETUP_COMMAND"
    echo "  powershell scripts/setup.ps1 -Minimal  # Windows PowerShell"
    exit 1
fi

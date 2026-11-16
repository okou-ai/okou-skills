#!/usr/bin/env bash
# Source and call in each process; never install or edit shell profiles here.

docx_dotnet_host() {
    local host="$1" link directory hops=0
    while true; do
        directory="$(cd -P "$(dirname "$host")" 2>/dev/null && pwd)" || return 1
        host="$directory/$(basename "$host")"
        if [[ ! -L "$host" ]]; then
            [[ -x "$host" ]] || return 1
            printf '%s\n' "$host"
            return 0
        fi
        hops=$((hops + 1))
        [[ "$hops" -le 40 ]] || return 1
        link="$(readlink "$host")" || return 1
        case "$link" in
            /*) host="$link" ;;
            *) host="$directory/$link" ;;
        esac
    done
}

docx_use_dotnet() {
    local mode="${1:-sdk}" candidate host inventory line major found root runtime_directory
    local on_path runtime_pattern='^Microsoft\.NETCore\.App[[:space:]]+8\.[0-9]+\.[0-9]+[[:space:]]+\[(.*)\]$'
    [[ "$mode" = sdk || "$mode" = runtime ]] || return 2
    on_path="$(type -P dotnet || true)"
    for candidate in "${DOTNET_ROOT:+$DOTNET_ROOT/dotnet}" "$on_path" "${HOME:-}/.dotnet/dotnet"; do
        [[ -n "$candidate" && -x "$candidate" ]] || continue
        inventory="$("$candidate" --list-runtimes 2>/dev/null)" || continue
        root=""
        while IFS= read -r line; do
            line="${line%$'\r'}"
            if [[ "$line" =~ $runtime_pattern ]]; then
                runtime_directory="${BASH_REMATCH[1]//\\//}"
                [[ "$runtime_directory" = */shared/Microsoft.NETCore.App ]] || continue
                root="${runtime_directory%/shared/Microsoft.NETCore.App}"
                break
            fi
        done <<< "$inventory"
        [[ -n "$root" ]] || continue
        if command -v cygpath &>/dev/null; then
            root="$(cygpath -u "$root")" || continue
        fi
        # Inventory gives the native root even when PATH contains a forwarding shim.
        host="$(docx_dotnet_host "$root/dotnet" || docx_dotnet_host "$root/dotnet.exe")" || continue
        if [[ "$mode" = sdk ]]; then
            inventory="$("$host" --list-sdks 2>/dev/null)" || continue
            found=false
            while IFS= read -r line; do
                if [[ "$line" =~ ^([0-9]+)\. ]]; then
                    major="${BASH_REMATCH[1]}"
                    if [[ "$major" -ge 8 ]]; then
                        found=true
                        break
                    fi
                fi
            done <<< "$inventory"
            $found || continue
        fi
        export DOCX_DOTNET="$host"
        export DOTNET_ROOT="$(dirname "$host")"
        case "$PATH" in
            "$DOTNET_ROOT"|"$DOTNET_ROOT":*) ;;
            *) export PATH="$DOTNET_ROOT:$PATH" ;;
        esac
        return 0
    done
    return 1
}

"""Exercise runtime checks and missing-CLI SDK fallback with stubbed .NET, no installs."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.name == "nt", "Bash entrypoints are tested on POSIX")
class DotnetEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="docx-sdk-env-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.bin = self.root / "commands"
        self.bin.mkdir()
        self.bash = shutil.which("bash")
        for name in ("dirname", "basename", "readlink", "uname", "grep", "sed", "head",
                     "date", "chmod", "zip", "unzip"):
            executable = shutil.which(name)
            if executable:
                (self.bin / name).symlink_to(executable)
        self.log = self.root / "sdk.log"
        self.installer_log = self.root / "installer.log"
        for name in ("sudo", "wget", "curl", "apt-get"):
            command = self.bin / name
            command.write_text(f'#!/bin/sh\nprintf "%s\\n" "$0" >> "{self.installer_log}"\nexit 97\n')
            command.chmod(0o755)
        self.scripts = self.root / "skill" / "scripts"
        self.scripts.mkdir(parents=True)
        for name in ("dotnet_env.sh", "docx.sh", "env_check.sh", "setup.sh"):
            shutil.copyfile(SCRIPTS / name, self.scripts / name)
            (self.scripts / name).chmod(0o755)
        self.project = self.scripts / "dotnet" / "Docx.Cli"
        self.project.mkdir(parents=True)
        (self.project / "Docx.Cli.csproj").touch()
        self.dll = self.project / "bin" / "Debug" / "net8.0" / "Docx.Cli.dll"
        self.dll.parent.mkdir(parents=True)
        self.dll.touch()
        self.env = {"HOME": str(self.home), "PATH": str(self.bin), "LANG": "C.UTF-8",
                    "SDK_LOG": str(self.log)}

    def sdk(self, root=None, version="8.0.428", *, runtime_only=False, selection_failure=False,
            runtime_major=8, runtime_version=None, crlf=False):
        root = root or self.home / ".dotnet"
        root.mkdir(parents=True, exist_ok=True)
        host = root / "dotnet"
        inventory = "" if runtime_only else f"{version} [{root}/sdk]"
        selected = "exit 145" if selection_failure else f"printf '%s\\n' '{version}'"
        runtime = runtime_version or f"{runtime_major}.0.34"
        runtime_format = "%s\\r\\n" if crlf else "%s\\n"
        host.write_text(f'''#!/bin/bash
printf '%s\\n' "${{DOTNET_ROOT:-}}|$*" >> "$SDK_LOG"
case "$1" in
    --list-sdks) printf '%s\\n' '{inventory}' ;;
    --list-runtimes) printf '{runtime_format}' 'Microsoft.NETCore.App {runtime} [{root}/shared/Microsoft.NETCore.App]' ;;
    --version) {selected} ;;
    nuget) printf '%s\\n' 'nuget.org' ;;
    restore|build) exit 0 ;;
    *) printf 'ROOT=%s\\n' "$DOTNET_ROOT"; printf '<%s>' "$@" ;;
esac
''')
        host.chmod(0o755)
        return host

    def run_script(self, script, *arguments, env=None):
        return subprocess.run([self.bash, "--noprofile", "--norc", str(self.scripts / script),
                               *map(str, arguments)], env=env or self.env, cwd=self.root,
                              capture_output=True, text=True, timeout=30)

    def test_each_fresh_entrypoint_finds_home_sdk_without_path_or_profiles(self):
        host = self.sdk()
        for _ in range(2):
            result = self.run_script("docx.sh", "create", "--title", "A report title")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"ROOT={host.parent}", result.stdout)
            self.assertIn(f"<{self.dll}><create><--title><A report title>", result.stdout)
        self.assertNotIn("DOTNET_ROOT", self.env)
        self.assertFalse((self.home / ".bashrc").exists())
        self.assertFalse(self.installer_log.exists())

    def test_explicit_dotnet_root_takes_precedence(self):
        self.sdk()
        selected = self.sdk(self.root / "explicit SDK 中文")
        result = self.run_script("docx.sh", "--help", env={**self.env, "DOTNET_ROOT": str(selected.parent)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={selected.parent}", result.stdout)

    def test_path_symlink_resolves_real_dotnet_root(self):
        selected = self.sdk(self.root / "path sdk")
        (self.bin / "dotnet").symlink_to(Path("..") / selected.parent.name / "dotnet")
        result = self.run_script("docx.sh", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={selected.parent}", result.stdout)

    def test_runtime_only_or_old_path_host_does_not_hide_home_sdk(self):
        selected = self.sdk()
        for options in ({"runtime_only": True}, {"version": "7.0.410"}):
            with self.subTest(options=options):
                other = self.sdk(self.root / "other", **options)
                link = self.bin / "dotnet"
                link.unlink(missing_ok=True)
                link.symlink_to(other)
                result = self.run_script("env_check.sh", "--build")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(f"{selected.parent}|--version", self.log.read_text())

    def test_runtime_only_built_cli_fast_path_and_explicit_build_requires_sdk(self):
        host = self.sdk(runtime_only=True)
        result = self.run_script("docx.sh", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={host.parent}", result.stdout)
        self.log.unlink()
        check = self.run_script("env_check.sh")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertIn(".NET 8 runtime", check.stdout)
        self.assertNotIn("--list-sdks", self.log.read_text())
        self.assertNotIn("--version", self.log.read_text())
        self.assertNotIn("restore", self.log.read_text())
        self.assertNotIn("build", self.log.read_text())
        check = self.run_script("env_check.sh", "--build")
        self.assertEqual(check.returncode, 1)
        self.assertIn("compatible SDK and .NET 8 runtime not found", check.stdout)
        self.assertFalse(self.installer_log.exists())

    def test_newer_runtime_only_root_does_not_hide_net8_root(self):
        host = self.sdk()
        other = self.sdk(self.root / "newer SDK", version="9.0.100", runtime_major=9)
        result = self.run_script("docx.sh", "--help", env={**self.env, "DOTNET_ROOT": str(other.parent)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={host.parent}", result.stdout)

    def test_windows_crlf_inventory_resolves_native_root(self):
        host = self.sdk(self.root / "Windows native SDK", crlf=True)
        host.write_text(host.read_text().replace(f"{host.parent}/shared/Microsoft.NETCore.App",
                                                r"C:\Program Files\dotnet\shared\Microsoft.NETCore.App"))
        cygpath = self.bin / "cygpath"
        cygpath.write_text(f'''#!/bin/bash
if [ "$1" = -u ] && [ "$2" = 'C:/Program Files/dotnet' ]; then
    printf '%s\\n' '{host.parent}'
else
    exit 1
fi
''')
        cygpath.chmod(0o755)
        result = self.run_script("docx.sh", "--help", env={**self.env, "DOTNET_ROOT": str(host.parent)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={host.parent}", result.stdout)

    def test_preview_only_root_does_not_hide_stable_runtime(self):
        host = self.sdk()
        preview = self.sdk(self.root / "preview SDK", runtime_version="8.0.0-preview.7")
        result = self.run_script("docx.sh", "--help", env={**self.env, "DOTNET_ROOT": str(preview.parent)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={host.parent}", result.stdout)

    def test_forwarding_shim_does_not_become_dotnet_root(self):
        host = self.sdk(self.root / "native sdk")
        shim = self.bin / "dotnet"
        shim.write_text(f'#!/bin/bash\nexec "{host}" "$@"\n')
        shim.chmod(0o755)
        result = self.run_script("docx.sh", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"ROOT={host.parent}", result.stdout)

    def test_repeated_resolution_does_not_grow_path(self):
        host = self.sdk()
        result = subprocess.run([self.bash, "--noprofile", "--norc", "-c",
            'source "$1"; docx_use_dotnet; first="$PATH"; docx_use_dotnet; '
            'test "$first" = "$PATH"; printf "%s" "$PATH"',
            "docx-test", str(self.scripts / "dotnet_env.sh")], env=self.env,
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split(os.pathsep).count(str(host.parent)), 1)

    def test_environment_check_uses_same_sdk_discovery(self):
        self.sdk()
        result = self.run_script("env_check.sh", "--build")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("8.0.428 (>= 8.0)", result.stdout)
        self.assertIn("Status: READY", result.stdout)
        self.assertFalse(self.installer_log.exists())

    def test_missing_sdk_does_not_attempt_restore(self):
        self.dll.unlink()
        result = self.run_script("env_check.sh", "--build")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("skipped (no compatible sdk selected)", result.stdout)
        self.assertNotIn("command not found", result.stderr)
        self.assertFalse(self.log.exists())
        self.assertFalse(self.installer_log.exists())

    def test_default_check_restores_and_builds_missing_cli_with_sdk(self):
        host = self.sdk()
        self.dll.unlink()
        result = self.run_script("env_check.sh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        log = self.log.read_text()
        project = self.project / "Docx.Cli.csproj"
        self.assertIn(f"{host.parent}|restore {project} --verbosity quiet", log)
        self.assertIn(f"{host.parent}|build {project} --verbosity quiet --no-restore", log)
        self.assertLess(log.index("|restore "), log.index("|build "))
        self.assertIn("build succeeded", result.stdout)
        self.assertIn("Status: READY", result.stdout)
        self.assertFalse(self.installer_log.exists())

    def test_default_missing_cli_finds_home_sdk_behind_runtime_only_path_host(self):
        host = self.sdk()
        runtime = self.sdk(self.root / "path runtime", runtime_only=True)
        (self.bin / "dotnet").symlink_to(runtime)
        self.dll.unlink()
        result = self.run_script("env_check.sh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        log = self.log.read_text()
        self.assertIn(f"{host.parent}|restore ", log)
        self.assertIn(f"{host.parent}|build ", log)
        self.assertNotIn(f"{runtime.parent}|restore ", log)
        self.assertNotIn(f"{runtime.parent}|build ", log)
        self.assertFalse(self.installer_log.exists())

    def test_runtime_only_missing_cli_fails_without_restore_build_or_install(self):
        self.sdk(runtime_only=True)
        self.dll.unlink()
        result = self.run_script("env_check.sh")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("DOCX CLI is missing; a compatible SDK is required", result.stdout)
        self.assertIn("skipped (no compatible sdk selected)", result.stdout)
        self.assertIn("Status: NOT READY", result.stdout)
        log = self.log.read_text()
        self.assertIn("--list-sdks", log)
        self.assertNotIn("--version", log)
        self.assertNotIn("restore", log)
        self.assertNotIn("build", log)
        self.assertFalse(self.installer_log.exists())

    def test_explicit_build_can_restore_and_build_missing_cli(self):
        self.sdk()
        self.dll.unlink()
        result = self.run_script("env_check.sh", "--build")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("restore ", self.log.read_text())
        self.assertIn("build ", self.log.read_text())
        self.assertFalse(self.installer_log.exists())

    def test_missing_pandoc_warns_about_legacy_preview_fallback_without_installing(self):
        self.sdk(runtime_only=True)
        result = self.run_script("env_check.sh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[WARN]    pandoc", result.stdout)
        self.assertIn("not found — docx_preview.sh will use fallback", result.stdout)
        self.assertIn("Status: READY (with", result.stdout)
        self.assertFalse(self.installer_log.exists())

    def test_available_pandoc_reports_legacy_preview_version(self):
        self.sdk(runtime_only=True)
        pandoc = self.bin / "pandoc"
        pandoc.write_text('#!/bin/sh\nprintf "pandoc 3.6.2\\n"\n')
        pandoc.chmod(0o755)
        result = self.run_script("env_check.sh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[OK]      pandoc", result.stdout)
        self.assertIn("3.6.2 (content preview)", result.stdout)
        self.assertNotIn("docx_preview.sh will use fallback", result.stdout)
        self.assertFalse(self.installer_log.exists())

    def test_setup_reuses_sdk_and_leaves_shell_profile_unchanged(self):
        host = self.sdk()
        profile = self.home / ".bashrc"
        profile.write_text("# preserve the user profile\n")
        result = self.run_script("setup.sh", "--minimal", "--skip-verify")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("already installed", result.stdout)
        self.assertIn(f"{host.parent}|restore ", self.log.read_text())
        self.assertIn(f"{host.parent}|build ", self.log.read_text())
        self.assertEqual(profile.read_text(), "# preserve the user profile\n")
        self.assertFalse(self.installer_log.exists())

    def test_setup_sdk_selection_failure_does_not_reinstall(self):
        self.sdk(selection_failure=True)
        result = self.run_script("setup.sh", "--minimal", "--skip-verify")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Check global.json", result.stdout)
        self.assertFalse(self.installer_log.exists())


if __name__ == "__main__":
    unittest.main()

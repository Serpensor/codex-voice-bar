"""Optionally start the Omarchy-managed Codex Voice plugin at login."""

import argparse
from pathlib import Path
import shutil
import tempfile

home = Path.home()
plugin_id = "serpensor.codex-voice"
plugin = home / ".config/omarchy/plugins" / plugin_id
autostart = home / ".config/hypr/autostart.lua"
launcher = home / ".local/bin/codex-voice-headless"
default_start = 'o.exec_on_start("~/.local/bin/codex-voice-headless")'
full_access_start = 'o.exec_on_start("~/.local/bin/codex-voice-headless --full-access")'
legacy_start = 'o.exec_on_start("omarchy-launch-terminal ~/.local/bin/codex-voice-login")'
managed_comments = {
    "-- Open Codex and start its built-in voice after login.",
    "-- Start Codex Voice in the background after login.",
}

parser = argparse.ArgumentParser(description=__doc__)
mode = parser.add_mutually_exclusive_group(required=True)
mode.add_argument("--login", action="store_true", help="start Codex Voice at graphical login")
mode.add_argument("--disable-login", action="store_true", help="remove Codex Voice login startup")
parser.add_argument("--full-access", action="store_true",
                    help="start Codex with sandboxing and approvals disabled")
args = parser.parse_args()
if args.full_access and not args.login:
    parser.error("--full-access requires --login")


def update(path: Path, contents: str) -> None:
    if path.exists() and path.read_text() == contents:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(path.name + ".before-codex-voice")
        if not backup.exists():
            shutil.copy2(path, backup)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(contents)
    try:
        if path.exists():
            shutil.copymode(path, temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


if args.login:
    if not (plugin / "start-voice").is_file():
        parser.error(f"install and enable the plugin first: {plugin}")
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'exec "$HOME/.config/omarchy/plugins/{plugin_id}/start-voice" "$@"\n'
    )
    launcher.chmod(0o755)
    startup = autostart.read_text() if autostart.exists() else ""
    selected_start = full_access_start if args.full_access else default_start
    managed_starts = {legacy_start, default_start, full_access_start}
    lines = [line for line in startup.splitlines()
             if line.strip() not in managed_starts | managed_comments]
    lines.append(selected_start)
    update(autostart, "\n".join(lines).rstrip() + "\n")
    print("Codex Voice will start at the next graphical login.")
else:
    startup = autostart.read_text() if autostart.exists() else ""
    managed_starts = {legacy_start, default_start, full_access_start}
    lines = [line for line in startup.splitlines()
             if line.strip() not in managed_starts | managed_comments]
    if autostart.exists():
        update(autostart, "\n".join(lines).rstrip() + "\n")
    launcher.unlink(missing_ok=True)
    print("Codex Voice login startup disabled.")

"""Install the Codex Voice widget and optionally enable voice at login."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parent
home = Path.home()
omarchy = home / ".config/omarchy"
shell = omarchy / "shell.json"
autostart = home / ".config/hypr/autostart.lua"
launcher = home / ".local/bin/codex-voice-headless"
managed = home / ".local/share/codex-voice-bar"
profile = managed / "settings.json"
widget_id = "local.codex-voice"
old_start = 'o.exec_on_start("omarchy-launch-terminal ~/.local/bin/codex-voice-login")'
default_start = 'o.exec_on_start("~/.local/bin/codex-voice-headless")'
full_access_start = 'o.exec_on_start("~/.local/bin/codex-voice-headless --full-access")'

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--login", action="store_true", help="start Codex voice at Hyprland login")
parser.add_argument("--full-access", action="store_true",
                    help="disable Codex sandboxing and approval prompts at login")
parser.add_argument("--restore", action="store_true",
                    help="reapply the saved widget and login settings")
args = parser.parse_args()
if args.restore and (args.login or args.full_access):
    parser.error("--restore uses the saved settings")
if args.restore:
    settings = json.loads(profile.read_text())
    args.login = settings["login"]
    args.full_access = settings["full_access"]
    root = managed
if args.full_access and not args.login:
    parser.error("--full-access requires --login")
new_start = full_access_start if args.full_access else default_start

original_config = shell.read_text()
config = json.loads(original_config)
startup = autostart.read_text() if autostart.exists() else ""
if args.login:
    for existing_start in (old_start, default_start, full_access_start):
        if existing_start in startup:
            startup = startup.replace(existing_start, new_start).replace(
                "-- Open Codex and start its built-in voice after login.",
                "-- Start Codex voice in the background after login.",
            )
            break
    else:
        startup = startup.rstrip() + "\n\n-- Start Codex voice in the background after login.\n" + new_start + "\n"
else:
    managed_starts = {old_start, default_start, full_access_start}
    startup = "".join(line for line in startup.splitlines(keepends=True)
                      if line.strip() not in managed_starts
                      and line.strip() != "-- Start Codex voice in the background after login.")

sections = config["bar"]["layout"]
if not any(widget.get("id") == widget_id for section in sections.values() for widget in section):
    sections.setdefault("centerEnd", []).insert(0, {"id": widget_id})

destination = omarchy / "plugins" / widget_id
for path in (shell, autostart):
    backup = path.with_name(path.name + ".before-codex-voice-bar")
    if path.exists() and not backup.exists():
        shutil.copy2(path, backup)

shutil.copytree(root / widget_id, destination, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__"))
launcher.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / "start-voice", launcher)


def update(path, contents):
    if path.exists() and path.read_text() == contents:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(contents)
    try:
        if path.exists():
            shutil.copymode(path, temp)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


if config != json.loads(original_config):
    update(shell, json.dumps(config, indent=2) + "\n")
if args.login or autostart.exists():
    update(autostart, startup)
if args.login:
    print("Background voice startup enabled for the next login.")

if not args.restore:
    shutil.copytree(root / widget_id, managed / widget_id, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("install.py", "start-voice", "codex-voice-bar-restore"):
        shutil.copy2(root / name, managed / name)
    update(profile, json.dumps({"login": args.login, "full_access": args.full_access}) + "\n")
    subprocess.run(["omarchy", "hook", "install", "post-update",
                    str(managed / "codex-voice-bar-restore")], check=True)

print("Codex Voice installed. Run 'omarchy restart shell' if the widget does not appear.")

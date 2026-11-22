# Codex Voice on Omarchy

Put scrolling microphone and speaker waveforms next to the clock. Click the mic to mute or unmute the default system input. A slash marks the muted state. Click the speaker to open the background Codex terminal.

## Install

Requires Omarchy with Quickshell bar plugins, PipeWire with PulseAudio compatibility, Python 3, tmux, and a signed-in Codex CLI with the interactive `/voice` command.

From this directory, run:

```sh
python3 install.py --login
omarchy restart shell
```

Voice starts in a background tmux session at the next graphical login. To start it now, run `~/.local/bin/codex-voice-headless`. Leave off `--login` to install the bar widget and launcher without adding a login entry. The launcher starts in `~/Work` if it exists, otherwise in your home directory. Set `CODEX_VOICE_WORKSPACE` or `CODEX_VOICE_BIN` to override the defaults.

The mic display reads the default input locally. The speaker display follows the background Codex playback stream when it can identify it and otherwise shows the default speaker output. The widget keeps only a short history of audio levels in memory. The separate Codex voice session uses the signed-in account and may send microphone audio to the voice service.

## Full access at login

The standard launcher uses your existing Codex permissions. To reproduce the full-access setup, install with:

```sh
python3 install.py --login --full-access
```

This starts Codex at login with filesystem sandboxing and command approval prompts disabled. Voice commands can then act with your Linux user permissions. For a manual launch, pass `--full-access` to `~/.local/bin/codex-voice-headless`. To restore the standard login command, rerun `python3 install.py --login`. A running session keeps the permissions it started with until it exits.

## Survive Omarchy updates

The installer saves a copy of the widget, launcher, and selected login settings in `~/.local/share/codex-voice-bar`. An Omarchy post-update hook reapplies them after updates. It keeps the widget in its current position when present and puts it back next to the clock if it was removed from the layout. To repair the setup after a manual configuration reset, run:

```sh
python3 ~/.local/share/codex-voice-bar/install.py --restore
```

Rerun the package installer with the options you want to change the saved settings. Running it without `--login` disables managed login startup.

## Remove

Remove `~/.config/omarchy/hooks/post-update.d/codex-voice-bar-restore` and `~/.local/share/codex-voice-bar` first to disable automatic restoration.

Remove the `local.codex-voice` entry from the bar layout in `~/.config/omarchy/shell.json` and the `codex-voice-headless` startup line from `~/.config/hypr/autostart.lua`. The installer saves original copies alongside the files with the suffix `.before-codex-voice-bar`. Applying those backups also rolls back any later edits to the files.

Stop the background session with `tmux -L omarchy-codex-voice kill-session -t '=codex-voice'`. Remove `~/.config/omarchy/plugins/local.codex-voice` and `~/.local/bin/codex-voice-headless`, then run `omarchy restart shell`.

## Prototype limits

The launcher waits for the Codex composer prompt in tmux and sends `/voice`. This depends on the current Codex TUI and may need updating if the prompt or command changes. If Codex opens a sign-in or setup prompt, use the speaker button to attach to the terminal and finish setup.

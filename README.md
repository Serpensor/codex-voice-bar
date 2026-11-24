# Codex Voice for Omarchy

A native Omarchy bar widget for the Codex CLI voice session. Two waveforms show microphone and speaker activity. Click the microphone to mute or unmute the default input; click the speaker to open the background Codex terminal.

## Install with the Omarchy plugin manager

```sh
omarchy plugin add https://github.com/Serpensor/codex-voice-bar.git --enable
```

The manager validates the plugin manifest, installs it into Omarchy's plugin directory, and enables it beside the clock. Use the normal plugin commands to manage it:

```sh
omarchy plugin disable serpensor.codex-voice
omarchy plugin enable serpensor.codex-voice
omarchy bar move serpensor.codex-voice --section right
omarchy plugin update serpensor.codex-voice
omarchy plugin remove serpensor.codex-voice
```

### Migrate from the earlier manual installer

The previous installer copied the widget to `local.codex-voice` and restored it after Omarchy updates. Remove that old restore hook and widget before adding the manager-managed plugin:

```sh
rm ~/.config/omarchy/hooks/post-update.d/codex-voice-bar-restore
omarchy plugin remove local.codex-voice
omarchy plugin add https://github.com/Serpensor/codex-voice-bar.git --enable
```

If the old login startup was enabled, keep it by running the new `install.py --login` command after installing the plugin. Add `--full-access` only if that was your previous setting and you want to retain it.

Requirements: Omarchy with shell plugins, PipeWire with PulseAudio compatibility, Python 3, `tmux`, and a signed-in Codex CLI with the interactive `/voice` command.

## Start Codex Voice at login (optional)

The bar widget can be used without automatic startup. To launch its Codex voice session at graphical login, run:

```sh
python3 ~/.config/omarchy/plugins/serpensor.codex-voice/install.py --login
```

To start Codex with sandboxing and approval prompts disabled, explicitly use:

```sh
python3 ~/.config/omarchy/plugins/serpensor.codex-voice/install.py --login --full-access
```

To remove login startup while keeping the widget installed:

```sh
python3 ~/.config/omarchy/plugins/serpensor.codex-voice/install.py --disable-login
```

The optional launcher uses your existing Codex permissions by default. The full-access option disables Codex sandboxing and command approval prompts, so voice requests can act with your Linux user permissions. A running session keeps the permissions it started with until it exits.

The launcher uses `~/Work` when it exists, otherwise your home directory. Set `CODEX_VOICE_WORKSPACE` or `CODEX_VOICE_BIN` to override the defaults. The microphone meter reads the default input locally. The speaker meter follows the Codex playback stream when it can identify it and otherwise shows the default speaker output. Only a short history of audio levels is kept in memory. Codex voice sends microphone audio to the voice service.

## Remove

If login startup is enabled, disable it first:

```sh
python3 ~/.config/omarchy/plugins/serpensor.codex-voice/install.py --disable-login
```

Then remove the plugin through the manager:

```sh
omarchy plugin remove serpensor.codex-voice
```

Stop an already-running voice session with:

```sh
tmux -L omarchy-codex-voice kill-session -t '=codex-voice'
```

## Compatibility note

The login launcher waits for the Codex TUI composer and sends `/voice`. This follows the Codex CLI's interactive interface and may need an update if that interface changes. If Codex opens a sign-in or setup prompt, click the speaker widget to open its terminal and finish setup.

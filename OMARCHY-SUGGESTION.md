# Codex Voice in the Omarchy bar

I built a small Omarchy bar widget so I can start talking to Codex right after logging in, with the terminal tucked away in a background tmux session.

Two waveforms next to the clock show microphone input and speaker playback. Click the microphone to mute or unmute it. Click the speaker to open the live Codex terminal and see the conversation or switch to typing.

Login startup is optional. The launcher uses your existing Codex permissions by default, with an explicit full-access option for people who want Codex to act on voice requests without command approval prompts.

The installer saves your settings independently and restores the widget after Omarchy updates.

The prototype uses Omarchy's Quickshell plugin interface and a signed-in Codex CLI. It starts the built-in `/voice` command from tmux, so compatibility depends on the Codex terminal UI. I'd be interested to hear how it works on other Omarchy setups.

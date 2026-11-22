"""Read peak levels from Codex streams or the default audio devices."""

import array
import json
import math
import os
import subprocess
import sys
import time

TMUX = ["tmux", "-L", "omarchy-codex-voice"]
SESSION = "codex-voice:0.0"


def output(*command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=2,
                            env={**os.environ, "LC_ALL": "C"})
    return result.stdout.strip() if result.returncode == 0 else ""


def pulse(kind):
    return json.loads(output("pactl", "--format=json", "list", kind) or "[]")


def streams():
    pid = output(*TMUX, "display-message", "-p", "-t", SESSION, "#{pane_pid}")
    if not pid.isdecimal():
        return []

    def owned(kind):
        return [
            stream for stream in pulse(kind)
            if stream.get("properties", {}).get("application.process.id") == pid
        ]

    return owned("sink-inputs")


class Meter:
    def __init__(self):
        self.target = None
        self.process = None
        self.level = 0.0

    def close(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=0.4)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process.stdout.close()
            self.process = None

    def connect(self, target):
        if self.target == target and self.process and self.process.poll() is None:
            return
        self.close()
        self.target = target
        self.level = 0.0
        if target:
            self.process = subprocess.Popen(
                ["parec", "--raw", "--format=s16le", "--rate=8000", "--channels=1",
                 "--latency-msec=50", "--process-time-msec=25", *target],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
            os.set_blocking(self.process.stdout.fileno(), False)

    def read(self):
        peak = 0
        if self.process:
            data = self.process.stdout.read(32768) or b""
            if data:
                samples = array.array("h", data)
                if sys.byteorder != "little":
                    samples.byteswap()
                peak = max(map(abs, samples))
        # Compress the range so ordinary speech is visible on five segments.
        self.level = max(math.sqrt(peak / 32768), self.level * 0.72)
        return round(self.level, 3)


def speaker_target(playback):
    if playback:
        stream = next((item for item in playback if not item.get("corked")), playback[0])
        sink = next((item for item in pulse("sinks") if item["index"] == stream["sink"]), None)
        if sink and sink.get("monitor_source") is not None:
            return [
                f"--device={sink.get('monitor_source_name') or sink['monitor_source']}",
                f"--monitor-stream={stream['index']}",
            ]
    return ["--device=@DEFAULT_MONITOR@"]


def monitor():
    mic, speaker = Meter(), Meter()
    refresh = 0
    try:
        while True:
            now = time.monotonic()
            if now >= refresh:
                refresh = now + 0.8
                try:
                    playback_target = speaker_target(streams())
                except (subprocess.TimeoutExpired, ValueError):
                    playback_target = speaker_target([])
                mic.connect(["--device=@DEFAULT_SOURCE@"])
                speaker.connect(playback_target)

            print(json.dumps({
                "mic": mic.read(),
                "playback": speaker.read(),
            }), flush=True)
            time.sleep(0.05)
    except BrokenPipeError:
        pass
    finally:
        mic.close()
        speaker.close()


if __name__ == "__main__":
    monitor()

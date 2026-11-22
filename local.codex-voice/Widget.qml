import QtQuick
import Quickshell.Io
import Quickshell.Services.Pipewire
import qs.Commons as Commons
import qs.Ui

BarWidget {
    id: root
    implicitWidth: vertical ? barSize : meters.implicitWidth
    implicitHeight: vertical ? meters.implicitHeight : barSize

    readonly property color foreground: bar ? bar.barForeground : Commons.Color.foreground
    readonly property var source: Pipewire.defaultAudioSource
    readonly property bool canMute: Commons.UntypedInput.active
        ? Commons.UntypedInput.known : !!source && !!source.audio
    readonly property bool microphoneMuted: canMute && (Commons.UntypedInput.active
        ? Commons.UntypedInput.muted : source.audio.muted)
    readonly property string helper: decodeURIComponent(
        Qt.resolvedUrl("audio.py").toString().replace(/^(file|qs):\/\//, ""))
    property var microphones: Array(16).fill(0)
    property var speakers: Array(16).fill(0)

    Commons.Translations { id: strings; directory: Qt.resolvedUrl("i18n") }
    PwObjectTracker { objects: root.source ? [root.source] : [] }

    function toggleMicrophone() {
        if (!canMute) return
        if (Commons.UntypedInput.active)
            Commons.UntypedInput.setMuted(!microphoneMuted)
        else
            source.audio.muted = !microphoneMuted
    }

    onMicrophoneMutedChanged: microphones = Array(16).fill(0)

    Process {
        id: monitor
        command: ["python3", root.helper]
        running: true
        stdout: SplitParser {
            onRead: function(line) {
                try {
                    const sample = JSON.parse(line)
                    if (!root.microphoneMuted)
                        root.microphones = [sample.mic].concat(root.microphones.slice(0, -1))
                    root.speakers = [sample.playback].concat(root.speakers.slice(0, -1))
                } catch (error) {}
            }
        }
        onExited: {
            root.microphones = Array(16).fill(0)
            root.speakers = Array(16).fill(0)
            retry.restart()
        }
    }
    Timer { id: retry; interval: 2000; onTriggered: monitor.running = true }
    Process {
        id: terminal
        command: ["omarchy-launch-terminal", "tmux", "-L", "omarchy-codex-voice",
                  "attach-session", "-t", "=codex-voice"]
    }

    Grid {
        id: meters
        anchors.centerIn: parent
        columns: root.vertical ? 1 : 2
        spacing: 4

        Repeater {
            model: 2
            delegate: WidgetButton {
                id: button
                required property int index
                readonly property bool mic: index === 0
                readonly property var samples: mic ? root.microphones : root.speakers
                readonly property string hint: !mic ? strings.t("playback")
                    : root.microphoneMuted ? strings.t("unmute")
                    : root.canMute ? strings.t("mute")
                    : strings.t("waiting")
                bar: root.bar
                fixedWidth: 62
                fixedHeight: Math.min(root.barSize, 26)
                labelVisible: false
                hasVisualContent: true
                tooltipText: hint
                Accessible.name: hint
                onPressed: function(mouseButton) {
                    if (mouseButton !== Qt.LeftButton) return
                    if (button.mic) root.toggleMicrophone()
                    else terminal.running = true
                }
                Row {
                    anchors.centerIn: parent
                    scale: button.pressScale
                    spacing: 4
                    Item {
                        width: icon.implicitWidth
                        height: icon.implicitHeight
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            id: icon
                            anchors.centerIn: parent
                            text: button.mic ? "󰍬" : "󰕾"
                            textFormat: Text.PlainText
                            font.family: root.bar ? root.bar.fontFamily : Commons.Style.font.family
                            font.pixelSize: 15
                            color: button.mic && !root.canMute
                                ? Qt.alpha(root.foreground, 0.4) : root.foreground
                        }
                        Rectangle {
                            anchors.centerIn: parent
                            visible: button.mic && root.microphoneMuted
                            width: 18
                            height: 2
                            radius: 1
                            rotation: -45
                            color: root.foreground
                        }
                    }
                    Row {
                        height: 18
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1
                        Repeater {
                            model: 16
                            delegate: Rectangle {
                                required property int index
                                width: 1.5
                                height: Math.max(1, 17 * button.samples[index])
                                anchors.verticalCenter: parent.verticalCenter
                                radius: 1
                                color: height > 1
                                    ? root.foreground : Qt.alpha(root.foreground, 0.22)
                            }
                        }
                    }
                }
            }
        }
    }
}

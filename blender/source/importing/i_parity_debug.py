import bpy


class ParityDebugLogger:
    _enabled: bool
    _text_name: str
    _text: bpy.types.Text | None
    _lines: list[str]
    _counts: dict[str, int]

    def __init__(self, enabled: bool, text_name: str = "SAIO_ParityDebug"):
        self._enabled = enabled
        self._text_name = text_name
        self._text = None
        self._lines = []
        self._counts = {
            "PARITY_MATRIX_BLENDERIO": 0,
            "PARITY_NODE_BLENDERIO": 0,
            "PARITY_ENTRY_BLENDERIO": 0
        }

    @property
    def enabled(self):
        return self._enabled

    def start(self):
        if not self._enabled:
            return

        text = bpy.data.texts.get(self._text_name)
        if text is None:
            text = bpy.data.texts.new(self._text_name)
        else:
            text.clear()

        self._text = text
        self._lines = []

    def emit(self, prefix: str, **kwargs):
        if not self._enabled:
            return

        ordered_items = sorted(kwargs.items())
        payload = " ".join([f"{key}={value}" for key, value in ordered_items])
        line = f"{prefix} {payload}" if payload else prefix
        self._lines.append(line)

        if prefix in self._counts:
            self._counts[prefix] += 1

    def finish(self):
        if not self._enabled:
            return

        if self._text is not None and len(self._lines) > 0:
            self._text.write("\n".join(self._lines) + "\n")

        print(
            "PARITY_DEBUG_SUMMARY_BLENDERIO "
            f"text={self._text_name} "
            f"matrix_logs={self._counts['PARITY_MATRIX_BLENDERIO']} "
            f"node_logs={self._counts['PARITY_NODE_BLENDERIO']} "
            f"entry_logs={self._counts['PARITY_ENTRY_BLENDERIO']}"
        )

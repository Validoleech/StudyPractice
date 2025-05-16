import json
import re


def jsonify(text: str, exclude_list: list[str], condense: bool = False) -> dict:
    ESCAPE_MAP = {
        "\\": "\\\\",
        "\"": "\\\"",
        "'": "\\'",
    }

    def escape_string(s):
        return re.sub(r"['\\\"\n\r\t]", lambda m: ESCAPE_MAP.get(m.group(0), m.group(0)), s)

    result = {}
    log_entries = []
    current_key = None
    buffer = []

    for line_number, line in enumerate(text.splitlines(), 1):
        line = line.rstrip()

        if not line.strip():
            if current_key in exclude_list:
                continue
            else:
                continue

        if ":" in line:
            possible_key, possible_value = line.split(":", 1)
            if possible_key.strip() in exclude_list:
                if current_key and buffer:
                    result[current_key] = [b.strip()
                                           for b in "\n".join(buffer).split("\n") if b.strip()]
                    buffer = []
                current_key = possible_key.strip()
                buffer.append(escape_string(possible_value.strip()))
                continue
            elif current_key in exclude_list and buffer:
                result[current_key] = [b.strip()
                                       for b in "\n".join(buffer).split("\n") if b.strip()]
                buffer = []
                current_key = None

            key = possible_key.strip()
            value = escape_string(possible_value.strip())
            result[key] = [item.strip()
                           for item in value.split(",") if item.strip()]
            current_key = None
        elif current_key in exclude_list:
            buffer.append(line.strip())
        else:
            log_entries.append(
                f"Line {line_number}: skipped - missing ':' -> {line.strip()}")

    if current_key in exclude_list and buffer:
        result[current_key] = [b.strip()
                               for b in "\n".join(buffer).split("\n") if b.strip()]

    return json.loads(json.dumps(
        result,
        indent=None if condense else 4,
        separators=(",", ":") if condense else (", ", ": "),
        ensure_ascii=False
    ))

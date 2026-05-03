import os
import re

def load_device_list(input_value: str):
    if os.path.isfile(input_value):
        with open(input_value, "r") as f:
            content = f.read()

        # Handles:
        # - commas
        # - Unix newlines (\n)
        # - Windows newlines (\r\n)
        devices = re.split(r"[,\r\n]+", content)

    else:
        devices = input_value.split(",")

    result = []
    for d in devices:
        d = d.strip()
        if not d:
            continue
        result.append(d)

    return result

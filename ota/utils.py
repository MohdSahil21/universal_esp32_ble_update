import os

def load_device_list(input_value: str):
    # Case 1: it's a file path
    if os.path.isfile(input_value):
        with open(input_value, "r") as f:
            content = f.read()
    else:
        # Case 2: direct string input
        content = input_value

    devices = content.split(",")

    result = []
    for d in devices:
        if d.startswith(" ") or d.endswith(" "):
            raise ValueError(f"Invalid device name: '{d}'")
        d = d.strip()
        if not d:
            continue
        result.append(d)

    return result

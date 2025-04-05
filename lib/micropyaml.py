"""
Simple YAML parser for MicroPython
Specialized for the workspace configuration format
"""


def load(file_path):
    """
    Load and parse a YAML file
    Returns a dictionary with the parsed content
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
        return parse(content)
    except OSError as e:
        print(f"YAML load error: {e}")
        return None


def parse(yaml_str):
    """
    Parse a YAML string into a Python dictionary
    Specialized for the workspace format
    """
    result = {}
    lines = yaml_str.split("\n")

    workspaces = []
    current_workspace = None

    # Track initial state

    for line in lines:
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Calculate indentation
        indent = len(line) - len(line.lstrip())

        # Top-level workspace key
        if stripped == "workspaces:":
            result["workspaces"] = workspaces
            # No need to track indent level for now

        # Workspace list item
        elif stripped.startswith("- ") and indent > 0:
            current_workspace = {}
            workspaces.append(current_workspace)

        # Workspace properties
        elif ":" in stripped and current_workspace is not None:
            key, value = [x.strip() for x in stripped.split(":", 1)]

            # Remove inline comments if present
            if "#" in value:
                value = value.split("#", 1)[0].strip()

            # Convert value to appropriate type if possible
            if value:
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.lower() in ("null", "none"):
                    value = None
                elif value.replace(".", "", 1).isdigit() and value.count(".") <= 1:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                elif (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

            current_workspace[key] = value

    return result

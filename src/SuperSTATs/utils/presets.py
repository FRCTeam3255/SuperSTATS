import json
from pathlib import Path

presets_dir = Path(__file__).parent.parent.parent / "pickles" / "stats_presets"
presets_dir.mkdir(exist_ok=True)


def get_available_presets():
    """Get list of available preset names."""
    preset_files = list(presets_dir.glob("*.json"))
    return sorted([f.stem for f in preset_files])


def load_preset(preset_name):
    """Load a preset by name."""
    preset_path = presets_dir / f"{preset_name}.json"
    if preset_path.exists():
        with open(preset_path, "r") as f:
            return json.load(f)
    return None


def save_preset(preset_name, phases, metrics):
    """Save a preset."""
    preset_path = presets_dir / f"{preset_name}.json"
    with open(preset_path, "w") as f:
        json.dump({"phases": phases, "metrics": metrics}, f, indent=2)


def delete_preset(preset_name):
    """Delete a preset."""
    preset_path = presets_dir / f"{preset_name}.json"
    if preset_path.exists():
        preset_path.unlink()

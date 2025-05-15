#src/utils/config_loader.py

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

def load_devices() -> Dict[str, Any]:
    """
    Load the devices configuration from the YAML file.
    
    Returns:
        Dict[str, Any]: The devices configuration.
    """
    try:
        config_path = CONFIG_DIR / "devices.yaml"
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            print(config)
        return config
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {}


if __name__ == "__main__":
    devices_config = load_devices()
    print(devices_config)

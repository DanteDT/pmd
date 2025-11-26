import yaml
from pathlib import Path

def load_config():
    '''Retrieve configuration from config.yaml in root directory'''
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as cf:
        return yaml.safe_load(cf)

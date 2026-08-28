from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


APP_NAME = "Running Dinner Optimizer"

DATA_DIR = Path(user_data_dir(APP_NAME))
CONFIG_DIR = Path(user_config_dir(APP_NAME))
STATE_DIR = DATA_DIR / "states"
RESULTS_DIR = DATA_DIR / "results"
LAST_STATE_PATH = STATE_DIR / ".last.json"
CONFIG_PATH = CONFIG_DIR / "config.yaml"


def ensure_app_directories() -> None:
    for directory in (STATE_DIR, RESULTS_DIR, CONFIG_DIR):
        directory.mkdir(parents=True, exist_ok=True)

import json

from pathlib import Path

from conf.conf import ODRIVE_CONF_DIR, ODRIVE_CONF_FILE


def load_conf():
    home = Path.home()
    config_home = home.joinpath(ODRIVE_CONF_DIR)
    if not config_home.exists():
        config_home.mkdir()
    config_file = config_home.joinpath(ODRIVE_CONF_FILE)
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            conf = json.load(f)
    else:
        conf = {}
    return 0, conf

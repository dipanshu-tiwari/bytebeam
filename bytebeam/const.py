import os
import logging as logger

# Constants

FORMAT = 'utf-8'
HEADER = 128
CHUNK_SIZE = 1024 * 4
CHUNK_LEN = 16
BAR_LENGTH = 40

VERSION = '0.1.1'

# Colors

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Paths

config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_PATH = os.path.join(config_home, "bytebeam", "config.json")

# Logger

log_dir = os.path.join(os.path.expanduser("~/.local/share/bytebeam"))
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "bytebeam.log")

logger.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logger.INFO
)
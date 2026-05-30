import logging
import sys

# Reconfigure stdout/stderr to UTF-8 on Windows to safely log emojis
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

# Configure logging format
logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=logging_format,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("cake_shop_agent")


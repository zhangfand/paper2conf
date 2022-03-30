import base64
import os

import dotenv

dotenv.load_dotenv()

PAPER_API_TOKEN = os.getenv("PAPER_API_TOKEN")
CONF_API_TOKEN = os.getenv("CONF_API_TOKEN")
CONF_ACCOUNT_EMAIL = os.getenv("CONF_ACCOUNT_EMAIL")
CONF_SPACE_KEY = os.getenv("CONF_SPACE_KEY")
CONF_ENCODED_API_TOKEN = base64.b64encode(
    bytes(f"{CONF_ACCOUNT_EMAIL}:{CONF_API_TOKEN}", "utf-8")).decode("utf-8")
CONF_URL = os.getenv("CONF_URL")

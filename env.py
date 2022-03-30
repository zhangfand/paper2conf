import os

import dotenv

dotenv.load_dotenv()

PAPER_API_TOKEN = os.getenv("PAPER_API_TOKEN")
CONF_API_TOKEN = os.getenv("CONF_API_TOKEN")
CONF_ACCOUNT_EMAIL = os.getenv("CONF_ACCOUNT_EMAIL")
CONF_SPACE_KEY = os.getenv("CONF_SPACE_KEY")
CONF_URL = os.getenv("CONF_URL")

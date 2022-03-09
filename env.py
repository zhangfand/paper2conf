import base64

PAPER_API_TOKEN = ''
CONF_API_TOKEN = ''
CONF_ACCOUNT_EMAIL = ''
CONF_SPACE_KEY = ''
CONF_ENCODED_API_TOKEN = base64.b64encode(
    bytes(f"{CONF_ACCOUNT_EMAIL}:{CONF_API_TOKEN}", "utf-8")).decode("utf-8")

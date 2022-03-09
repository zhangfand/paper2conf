import requests

from doc import Doc
from env import CONF_SPACE_KEY


class ConfluenceClient:

    def __init__(self, encoded_token: str):
        self._encoded_token = encoded_token

    def _header(self):
        return {
            "Authorization": f"Basic {self._encoded_token}",
            'Content-Type': 'application/json',
        }

    def add_doc(self, doc: Doc, parent_id=None) -> str:
        """Create a doc in Confluence and return its confluence ID

        If parent_id is not None, the doc is created as a child page of it.
        The doc's content is expected to be in Confluence Wiki format.
        """
        data = {
            "type": "page",
            "title": doc.title,
            "space": {"key": CONF_SPACE_KEY},
            "body": {
                "storage": {
                    "value": doc.content,
                    "representation": "wiki",
                }
            },
            "metadata": {
                "properties": {
                    "editor": {
                        "value": "v2"
                    }
                }
            },
        }
        if parent_id:
            data["ancestors"] = [{"type": "page", "id": parent_id}]

        r = requests.post(
            "https://dropbox-kms.atlassian.net/wiki/rest/api/content",
            headers=self._header(),
            json=data,
        )
        result = r.json()
        assert 'id' in result, result
        return r.json()['id']

    def update_content(self, doc_id: str, doc: Doc, version: int):
        params = {
            "title": doc.title,
            "type": "page",
            "body": {
                "storage": {
                    "value": doc.content,
                    "representation": "wiki",
                }
            },
            "version": {
                "number": version,
            },
        }
        r = requests.put(
            f"https://dropbox-kms.atlassian.net/wiki/rest/api/content/{doc_id}",
            headers=self._header(),
            json=params)

        return r.json()

    def get_doc_version(self, doc_id: str) -> any:
        r = requests.get(
            f"https://dropbox-kms.atlassian.net/wiki/rest/api/content/{doc_id}",
            headers=self._header(),
        )
        data = r.json()
        return data['version']['number']

import json
from dataclasses import dataclass

import dropbox
import requests
# Generate access token here: https://www.dropbox.com/developers/apps/
from dropbox.paper import ExportFormat

from doc import Doc


@dataclass
class PaperDoc:
    id: str
    title: str


@dataclass
class PaperFolder:
    folder_id: str
    name: str


class PaperClient:
    def __init__(self, api_token):
        self._client = dropbox.Dropbox(api_token)
        self._api_token = api_token

    def _header(self):
        return {
            'Authorization': f'Bearer {self._api_token}',
            'Content-Type': 'application/json',
        }

    def get_doc(self, doc_id) -> Doc:
        if "id:" == doc_id[:3]:
            # API spec: https://www.dropbox.com/internal-docs/paper#paper-cloud_docs-download
            headers = {
                'Authorization': f'Bearer {self._api_token}',
                'Dropbox-API-Arg': json.dumps({"export_format": "markdown", "file_id": doc_id}),
            }
            r = requests.post(
                'https://api.dropboxapi.com/2/paper/cloud_docs/download',
                headers=headers,
            )
            api_result = json.loads(r.headers['Dropbox-Api-Result'])
            return Doc(api_result['title'], r.text)
        else:
            result, r = self._client.paper_docs_download(doc_id, ExportFormat.markdown)
            return Doc(result.title, r.text)



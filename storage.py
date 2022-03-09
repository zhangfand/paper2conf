import json
from typing import Dict, List

from paper import PaperDoc


def save_replacements(replacements: Dict[str, str]):
    with open("out/replacements.json", "w") as f:
        json.dump(replacements, f)


def load_replacements() -> Dict[str, str]:
    with open("out/replacements.json") as f:
        return json.load(f)


def load_paper_doc_index():
    """Load the paper doc index.

    paper_docs.json follows the following schema:
    [
        <folder>
    ]
    where <folder> has the following schema:
    {
        "id": str          # the id of the folder
        "docs": [          # the paper docs under this folder
            {
                "id": str     # the id of the doc
                "title": str  # the title of the doc
            }
        ]
    }
    """
    with open('out/paper_docs.json') as f:
        return json.load(f)


def get_all_paper_docs() -> List[PaperDoc]:
    folders = load_paper_doc_index()

    docs = []
    for folder in folders:
        for doc in folder['docs']:
            docs.append(PaperDoc(doc['id'], doc['title']))

    return docs

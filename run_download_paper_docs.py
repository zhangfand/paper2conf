import os
import time

from env import PAPER_API_TOKEN
from paper import PaperClient
from storage import load_paper_doc_index


def download_paper_docs(out_folder: str):
    """Download paper docs from Paper based on the paper_docs.json index"""
    folders = load_paper_doc_index()

    doc_ids = []
    for folder in folders:
        for doc in folder['docs']:
            doc_ids.append(doc['id'])

    paper = PaperClient(PAPER_API_TOKEN)
    for doc_id in doc_ids:
        start = time.time()
        doc = paper.get_doc(doc_id)
        with open(os.path.join(out_folder, doc_id), 'w') as f:
            f.write(doc.content)

        end = time.time()
        print(f'dumped {doc_id}; took: {end - start}s')


if __name__ == "__main__":
    out_folder = "out/markdown"
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    download_paper_docs(out_folder)

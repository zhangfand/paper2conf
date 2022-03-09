import json
import time

from confluence import ConfluenceClient
from doc import Doc
from env import CONF_ENCODED_API_TOKEN
from paper import PaperDoc
from storage import load_paper_doc_index


def create_doc_pages():
    folders = load_paper_doc_index()

    with open("out/paper_to_conf_folders.json") as f:
        paper_to_conf_folders = json.load(f)

    conf = ConfluenceClient(CONF_ENCODED_API_TOKEN)

    with open("out/paper_to_conf_docs.json") as f:
        paper_to_conf_ids = json.load(f)

    for folder in folders:
        folder_id = folder['id']
        conf_parent_id = paper_to_conf_folders[folder_id]
        for e in folder['docs']:
            paper_doc = PaperDoc(id=e['id'], title=e['title'])

            if paper_doc.id in paper_to_conf_ids:
                print(f"skipping doc {paper_doc.id}")
                continue

            try:
                start = time.time()
                conf_id = create_doc_page(conf, paper_doc, conf_parent_id)
                end = time.time()
                print(f"created doc {paper_doc}: took {end - start}s")
            except AssertionError as e:
                print(f"failed to create {paper_doc}")
                raise e

            paper_to_conf_ids[paper_doc.id] = conf_id
            with open("out/paper_to_conf_docs.json", "w") as f:
                json.dump(paper_to_conf_ids, f)


def create_doc_page(conf: ConfluenceClient, doc: PaperDoc, parent_id: str) -> str:
    with open(f'out/jirawiki/{doc.id}') as f:
        content = f.read()
    return conf.add_doc(Doc(doc.title, content), parent_id)


if __name__ == "__main__":
    create_doc_pages()

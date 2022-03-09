import json
from dataclasses import is_dataclass, asdict

from confluence import ConfluenceClient
from env import PAPER_API_TOKEN, CONF_ENCODED_API_TOKEN
from paper import PaperClient, PaperDoc


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


def test_search():
    client = PaperClient(PAPER_API_TOKEN)
    docs = client.get_paper_search("edgestore")
    print(json.dumps(docs, indent=4, cls=EnhancedJSONEncoder))


def test_fetch_doc():
    doc = PaperDoc(doc_id='id:4wZ_l57cYZAAAAAAAAAFrw',
                   title='Deprecate Edgestore Traffic Tier.paper')
    client = PaperClient(PAPER_API_TOKEN)
    text = client.get_doc(doc.id)
    print(text)


def test_list_folders():
    client = PaperClient(PAPER_API_TOKEN)
    result = client.list_folders("e.iX7ZavGxujPFwhjOZcQrZBlf0BdAXLTkV493lo2rTJQxm4MNpd")
    print(result)


def test_create_doc():
    # https://developer.atlassian.com/cloud/confluence/rest/intro/
    client = ConfluenceClient(CONF_ENCODED_API_TOKEN)
    print(client.add_doc("test", "<h1>hello world</h1>"))


def test_create_single_doc():
    doc = PaperDoc(doc_id='id:4wZ_l57cYZAAAAAAAAAFrw',
                   title='Deprecate Edgestore Traffic Tier.paper')
    client = PaperClient(PAPER_API_TOKEN)
    doc = client.get_doc(doc.id)

    with open("./out/doc.html", "w") as f:
        f.write(doc.content)

    client = ConfluenceClient(CONF_ENCODED_API_TOKEN)
    print(client.add_doc(doc))


def test_update_doc():
    doc_id = "514032996"
    conf = ConfluenceClient(CONF_ENCODED_API_TOKEN)
    version = conf.get_doc_version(doc_id)

    resp = conf.update_content(doc_id, Doc("test", "[link|Telescope Indexer#Last]"), version + 1)
    print(resp)

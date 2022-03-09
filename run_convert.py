import os
from typing import List

from pandoc.types import *

from paper import PaperDoc
from storage import get_all_paper_docs


def convert(paper_doc: PaperDoc, paper_docs: List[PaperDoc]):
    doc = pandoc.read(file=f"out/markdown/{paper_doc.id}", format="markdown")

    replace_link(doc, paper_docs)

    pandoc.write(doc=doc, file=f"out/jirawiki/{paper_doc.id}", format="jira")


def replace_link(doc: Pandoc, paper_docs: List[PaperDoc]):
    for el in pandoc.iter(doc):
        if isinstance(el, Link):
            # el is in the form of
            # Link(('', [], []), [Str('here')], ('https://paper.dropbox.com/doc/Server-side-schema-Phase-2.1-0bhBE5dzkxhy3hBBdNuI1#:h2=Appendix-2:', ''))
            link = el[2][0]
            for paper_doc in paper_docs:
                if paper_doc.id in link:
                    el[2] = (paper_doc.title, el[2][1])
                    break

    return doc


if __name__ == "__main__":
    docs = get_all_paper_docs()

    if not os.path.exists("out/jirawiki"):
        os.mkdir("out/jirawiki")

    for doc in docs:
        convert(doc, docs)
        print(f"processed {doc}")

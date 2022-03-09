import json

from confluence import ConfluenceClient
from doc import Doc
from env import CONF_ENCODED_API_TOKEN


def create_folder_pages():
    """Create confluence pages that match the paper folder structure.

    The paper_folders.json file represents the tree-like folder structure in
    breadth-first traversal order. Here is its schema:

    [
        [
            <folder>
        ],
        [
            <folder>,
            <folder>,
            ...
        ],
        ...
    ]

    Each list of folders represent a level in the tree, the first level should only have one folder,
    which is the root folder.

    where <folder> has the following schema:

    {
        "id": str,          # the id of the folder
        "name": str,        # the name of the folder
        "sub_ids": [str],   # the ids of its child folders
    }
    """
    with open('out/paper_folders.json') as f:
        data = json.load(f)

    conf = ConfluenceClient(CONF_ENCODED_API_TOKEN)

    # This is the edgestore folder
    paper_to_conf = {}
    id_to_parent = {}

    for folders in data:
        for folder in folders:
            paper_id = folder['id']
            name = folder['name']
            sub_ids = folder['sub_ids']

            for sub_id in sub_ids:
                assert sub_id not in id_to_parent
                id_to_parent[sub_id] = paper_id

            # translate parent paper id to conf id
            parent_id = id_to_parent.get(paper_id, None)
            parent_id = paper_to_conf.get(parent_id, None)

            # create a new page as a sub page of its parent
            content = f"paper folder: https://paper.dropbox.com/folder/show/{paper_id}"
            conf_id = conf.add_doc(Doc(title=name, content=content), parent_id=parent_id)
            print(f"created conf doc for paper folder {name}")

            # store the mapping
            paper_to_conf[paper_id] = conf_id

    with open('out/paper_to_conf_folders.json', 'w') as f:
        json.dump(paper_to_conf, f)


if __name__ == "__main__":
    create_folder_pages()

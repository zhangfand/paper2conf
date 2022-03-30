import os

from atlassian import confluence

import env
from writer import convert_page


def run(in_dir: str):
    # check all page names are unique
    pages = {}
    for dir, dir_names, path_names in os.walk(in_dir):
        for subdir in dir_names:
            full_path = os.path.join(dir, subdir)

            if subdir in pages:
                raise AssertionError(f"{subdir} duplicates: {full_path} and {pages[subdir]}")

            pages[subdir] = full_path

        for file in path_names:
            if not file.endswith(".paper"):
                continue
            name = file.removesuffix(".paper")
            if name == os.path.basename(dir):
                continue

            full_path = os.path.join(dir, file)

            if name in pages:
                raise AssertionError(f"{name} duplicates: {full_path} and {pages[name]}")

            pages[name] = full_path

    client = confluence.Confluence(url=env.CONF_URL,
                                   username=env.CONF_ACCOUNT_EMAIL,
                                   password=env.CONF_API_TOKEN,
                                   cloud=True)

    page_ids = {
        "Metadata Services": None
    }

    # export the files to confluence, and organize them in the same structure as the folder.
    for dir, dir_names, path_names in os.walk(in_dir):
        parent_dir_name = os.path.basename(dir)
        parent_page_id = page_ids[parent_dir_name]

        # if there is file directly under the folder that shares the same name,
        # uses its content.
        for subdir in dir_names:
            index_file_path = os.path.join(dir, subdir, subdir) + ".paper"

            body = ""
            if os.path.exists(index_file_path):
                body = convert_page(index_file_path)
            page_id = client.create_page(
                space=env.CONF_SPACE_KEY,
                title=subdir,
                body=body,
                parent_id=parent_page_id,
                representation="storage",
                editor="v2",
            )
            page_ids[subdir] = page_id

        for path_name in path_names:
            if not path_name.endswith(".paper"):
                continue

            title = path_name.removesuffix(".paper")

            if title == os.path.basename(dir):
                print(f"skipping paper doc {title} because its parent page has the same name")
                continue

            print(f"adding {title}")
            full_path = os.path.join(dir, path_name)
            body = convert_page(full_path)
            client.create_page(
                space=env.CONF_SPACE_KEY,
                title=title,
                body=body,
                parent_id=parent_page_id,
                representation="storage",
                editor="v2",
            )


if __name__ == "__main__":
    run("out/Infrastructure/Persistent Systems/Teams/Metadata Services")

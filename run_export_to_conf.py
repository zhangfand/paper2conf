import os

from atlassian import confluence
from writer import convert_page
import argparse
from shutil import which
import sys
import subprocess
from typing import Optional


def run(in_dir: str, conf_api_token: str, conf_email: str, conf_url: str, conf_space_key: str):
    # check all page names are unique
    pages = {}
    for dir, dir_names, path_names in os.walk(in_dir):
        for subdir in dir_names:
            full_path = os.path.join(dir, subdir)

            if subdir in pages:
                raise AssertionError(f"{subdir} duplicates: {full_path} and {pages[subdir]}")

            pages[subdir] = full_path

        for file in path_names:
            if not file.endswith(".paper") and not file.endswith(".md"):
                continue
            if file.endswith(".paper"):
                name = file.removesuffix(".paper")
            else:
                name = file.removesuffix(".md")

            if name == os.path.basename(dir):
                continue

            full_path = os.path.join(dir, file)

            if name in pages:
                raise AssertionError(f"{name} duplicates: {full_path} and {pages[name]}")

            pages[name] = full_path

    client = confluence.Confluence(url=conf_url,
                                   username=conf_email,
                                   password=conf_api_token,
                                   cloud=True)

    # export the files to confluence, and organize them in the same structure as the folder.

    # A map from path (both directories and files) to page id.
    # We will walk the folder in DFS manner. When a file is processed, the page corresponds to
    # its parent folder is guaranteed created. We can use its page id in calling create_page().
    #
    # The root directory page id is set to None. This plays nicely with create_page() because
    # when parent_id is None, the page will be created without any parent pages.
    page_ids = {
        os.path.basename(in_dir.removesuffix("/")): None
    }

    def find_unique_title(title: str) -> str:
        candidate = title
        count = 0
        while count < 100:
            if not client.page_exists(conf_space_key, candidate):
                return candidate
            elif client.get_page_by_title(conf_space_key, candidate)['status'] == 'archived':
                return candidate
            else:
                candidate = f"{title} (Conflicted Copy {count})"
                count += 1

        raise Exception("Exhausted search")

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
            title = find_unique_title(subdir)
            page_id = client.create_page(
                space=conf_space_key,
                title=title,
                body=body,
                parent_id=parent_page_id,
                representation="storage",
                editor="v2",
            )
            page_ids[subdir] = page_id

        for path_name in path_names:
            if not path_name.endswith(".paper") and not path_name.endswith(".md"):
                continue

            if path_name.endswith(".paper"):                
                title = path_name.removesuffix(".paper")
            else:
                title = path_name.removesuffix(".md")

            if title == os.path.basename(dir):
                print(f"skipping paper doc {title} because its parent page has the same name")
                continue

            print(f"adding {title}")
            full_path = os.path.join(dir, path_name)
            body = convert_page(full_path)

            client.create_page(
                space=conf_space_key,
                title=find_unique_title(title),
                body=body,
                parent_id=parent_page_id,
                representation="storage",
                editor="v2",
            )

def precondition_check() -> Optional[str]:
    # Check python version. We need py3 3.10 or higher
    if not sys.version_info >= (3, 10, 0):
        return "Need python 3.10 or higher. Run brew install python@3.10 to install."

    if which("pandoc") is None:
        return "pandoc not installed. Get pandoc 2.17 from https://github.com/jgm/pandoc/releases/tag/2.17.1.1"

    pandoc_str = subprocess.check_output(["pandoc", "--version", "|", "head -1"]).decode('utf-8').split('\n')[0]
    if not pandoc_str.startswith('pandoc 2.17'):
        return "pandoc needs to be 2.17 to make it work. `brew uninstall pandoc` and get pandoc 2.17 from https://github.com/jgm/pandoc/releases/tag/2.17.1.1"

    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload a folder of paper markdowns to a confluence space.')
    parser.add_argument('--path', required=True, help='the local path to a folder that contains paper markdowns.')
    parser.add_argument('--conf_api_token', required=True, help='Confluence API token. Get it from https://id.atlassian.com/manage-profile/security/api-tokens.')
    parser.add_argument('--conf_email', required=True, help='Your email address in Confluence.')
    parser.add_argument('--conf_space_key', required=True, help='Confluence space key.')
    parser.add_argument('--conf_url', help='Confluence URL', default="https://dropbox-kms.atlassian.net")
    args = parser.parse_args()

    precondition_result = precondition_check()
    if precondition_result:
        print(precondition_result)
    else:
        run(os.path.expanduser(args.path), args.conf_api_token, args.conf_email, args.conf_url, args.conf_space_key)

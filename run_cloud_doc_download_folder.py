import os.path

import dropbox
from dropbox.files import FileMetadata
from dropbox.users import FullAccount
import argparse

def get_namespace_id(dbx_token: str) -> str:
    client = dropbox.Dropbox(dbx_token)
    account = client.users_get_current_account()
    assert isinstance(account, FullAccount)
    return account.root_info.root_namespace_id


def walk(folder_path: str, out_dir: str, dbx_token: str, dry_run=True):
    os.makedirs(out_dir, exist_ok=True)

    namespace_id = get_namespace_id(dbx_token)

    headers = {
        "Dropbox-API-Path-Root": f'{{".tag": "namespace_id", "namespace_id": "{namespace_id}"}}'
    }
    client = dropbox.Dropbox(dbx_token, headers=headers)
    result = client.files_list_folder(folder_path, recursive=True)

    while True:
        for entry in result.entries:
            if not isinstance(entry, FileMetadata):
                continue
            if not entry.name.endswith(".paper"):
                continue

            file_path = entry.path_display
            out_file_path = out_dir + file_path

            if os.path.exists(out_file_path):
                print(f"{file_path}: skipped; already exists")
                continue

            os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
            if dry_run:
                print(f"{file_path}: will download")
            else:
                client.files_export_to_file(out_file_path, file_path, export_format="markdown")
                print(f"{file_path}: downloaded")

        if not result.has_more:
            break

        result = client.files_list_folder_continue(result.cursor)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download Paper docs from a folder.')
    parser.add_argument('--path', required=True, help='relative path from Dropbox root.')
    parser.add_argument('--dbx_token', required=True, help='Dropbox Access Token. You can get it from https://dropbox.github.io/dropbox-api-v2-explorer/#files_list_folder.')
    parser.add_argument('--commit', action='store_true', help='Actually download the file.')
    args = parser.parse_args()
    walk(args.path, "out/", args.dbx_token, dry_run=not args.commit)
# Overview

The series of scripts exports paper docs in traditional paper system (i.e. excluding PiFS) to
confluence. More specifically, it exports the docs and folders under a specified root folders and
create a confluence page and subpages that mirror the structure.
Checkout https://dropbox-kms.atlassian.net/wiki/spaces/~108624815/pages/526091394/Edgestore
for an example. It also tries to update the links to paper docs with links to the confluence ones.

## Constraints

The scripts have many constraints:

[ ] It doesn't support PiFS.
[ ] Images are not properly migrated. The exported doc only keeps a URL to the image.
[ ] Emojis don't work. They are stored as text, e.g. `:smile:`
[ ] Some weird characters are generated in the result.

# Instructions

## Dependency

1. Install dependent python packages. The script is tested with Python 3.9.9
   ```pip3 install -r requirements.txt```
2. Install pandoc https://pandoc.org/. If you're on MacOS, you can install it via brew.

   ```brew install pandoc```

## Setup

Before running the script, we need to configure some values in `env.py`:

1. Specify the space id of the Confluence space that you want to port docs into. You can extract
   that from the url to the space. For example, `~108624815` is the id of my personal space, and the
   url is https://dropbox-kms.atlassian.net/wiki/spaces/~108624815/. I used my personal space as a
   test ground. Once you're satisfied with the result, you can move the whole page tree into the
   space for your service / team.
2. Specify the Confluence API key. You can get it from
   link: https://id.atlassian.com/manage-profile/security/api-tokens
3. Specify email of your Confluence account. It should be the same as your dropbox work email.
4. Specify a paper application key. You can get it by creating an app here:
   https://www.dropbox.com/developers/apps. Grant your app with following permissions:
   account_info.read, files.metadata.read, files.content.read and sharing.read. Generate an access
   token using the button in the "OAuth2" section under "Settings" panel.

## Migrate

The migration is divided into multiple steps. Each step emits output files to `out/` and are used as
the input in subsequent step(s). Here are the steps:

1. Build the paper folder's structure and store it in `out/paper_folders.json`. The json file
   represents the tree-like folder structure in breadth-first traversal order.
   Checkout `run_create_folder_pages.py` for a detailed explanation of its schema. To construct this
   file, you need to manually breath-first traverse the tree by performing some GraphQL query:
    1. Get root folder's paper id. This can be extracted from the url to the folder. It's in the
       form of `e.iX7ZavGxujPFwhjOZcQrZBlf0BdAXLTkV493lo2rTJQxm4MNpd`.
    2. Run query in https://paper.dropbox.com/graphiql. The filter `folderIds` accept a list of ids.
       Replace it with the root folder id.
       ```
       query {
           folders(folderIds: $folder_ids) {
               id, name,
               subFolders {
                   name, id,
               }
           }
       }
       ```
    3. Use tool `jq` to extract the data we want. You can use the online version https://jqplay.org.
       Run this query on the data from step 2.
       ```{folders: [.data.folders[] | {id: .id, name: .name, sub_ids: [.subFolders[]?.id] }], ids: [.data.folders[].subFolders[]?.id]}```
       Field "folders" contains the folders under the root folder, copy them
       into `paper_folders.json`. Field "ids" are the ids of these folders. We will use them in the
       next step.
    4. Replace `$folder_ids` with ids from step 3 and redo step 2-4. Repeat until the ids become
       empty.

2. Build paper docs index and store it in `paper_docs.json`. This can be constructed following these
   steps:
    1. Construct all folder ids from `paper_folders.json` by this jq query `[.[] | .[] | .id ]`.
    2. Replace `$folder_ids` with the ids from step 1 in the following GraphQL query.
       ```
         {
             folders(folderIds: $folderIds) {
                 id
                 docs {
                     id
                     title
                 }
             }
         }
       ```
       Store the result in `out/paper_docs.json`.
3. Run `run_download_paper_docs.py` to download paper docs listed in `paper_docs.json` from Paper
   and store them under `out/markdown/`. Each paper doc corresponds to one markdown file named after
   its paper doc id.
4. Run `run_convert.py` to convert markdown files in `out/markdown/` to confluence wiki format files
   and store them in `out/jirawiki`. The script also handles converting links to other paper docs to
   a confluence link.
5. Run `run_craete_folder_pages.py` to create pages and subpages in the space that mirror the
   structure of the paper folders. It outputs a `out/paper_to_conf_folders` file that maps paper
   folder ids to confluence page ids.
6. Run `run_craete_doc_pages.py` to create confluence pages from the files in `out/jirawiki` and
   `paper_docs.json`. It outputs a `out/paper_to_conf_docs.json` file that maps paper doc ids to
   confluence page ids. The script supports checkpointing as it will skip recreating docs that are
   already in the mapping files. Expect the script to fail halfway due to confluence doc title
   conflicts: Confluence enforces that docs in one space have unique titles. When that happens,
   update the title of that doc in `paper_docs.json` to avoid the conflict.
7. Now you should have completely migrated a folder to confluence.

# Resources

- Paper internal API reference: https://www.dropbox.com/internal-docs/paper
- Confluence API reference: https://developer.atlassian.com/cloud/confluence/rest/intro/
- Open source script that exports all paper docs in a folder to
  markdown: https://github.com/pew/dropbox-paper-export/blob/master/paper-backup.py
- Paper Graphql queryio: https://paper.dropbox.com/graphiql
- jq playground: https://jqplay.org/

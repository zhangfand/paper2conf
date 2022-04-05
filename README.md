# Overview

The series of scripts exports paper docs from Dropbox to Confluence. More
specifically, it exports the docs and folders under a specified root folders
and create a confluence page and subpages that mirror the structure.

## Constraints

# Instructions

## Dependency

1. Install dependent python packages. The script is tested with Python 3.9.9
   ```pip3 install -r requirements.txt```
2. Install pandoc https://pandoc.org/. If you're on MacOS, you can install it via brew.

   ```brew install pandoc```

## Setup

Before running the script, You need to have the following available:

1. `conf_space_key`: the key of the Confluence space that you want to port docs into. You can extract that from the url
   to the space. For example, `~108624815` is the key of my personal space, and the url is https://<url>/wiki/spaces/~108624815/. I used my personal space as a test ground. Once you're satisfied with the result, you can move the whole page tree into the space for your service/team.
2. `conf_api_token`: the Confluence API key. You can get it from
   link: https://id.atlassian.com/manage-profile/security/api-tokens
3. `conf_email`: Specify email of your Confluence account. It should be the same as your work email.
4. `dbx_token`: Dropbox API token. Visit https://dropbox.github.io/dropbox-api-v2-explorer/#files_list_folder and click "Get Token" and use the token filled in the `Access Token` field

## Run

The Dropbox folder path to download from and the local directory path to export to Confluence is
hardcoded in the script. Update the script before running it.

1. Run script `run_cloud_doc_download_folder` to download the files to a local folder specified.
   - `python run_cloud_doc_download_folder.py --path <dropbox path> --out <local output path> --dbx_token <dbx_token from step 4>` to dry run. It will output files that will be downloaded
   - `python run_cloud_doc_download_folder.py --path <dropbox path> --out <local output path> --dbx_token <dbx_token from step 4> --commit` to actually commit.

2. Run script `run_export_to_conf` to export a local folder to Confluence.
   - `python run_export_to_conf.py --path <local folder> --conf_api_token <conf_api_token from step 2> --conf_email <conf_email from step 3> --conf_space_key <conf_space_key from step 1>`

For example: To migrate a folder under `/Tony Xu/Migration Test` to my personal space `~1234567`, run:
1. `python run_cloud_doc_download_folder.py --path "/Tony Xu/Migration Test" --out "out/" --dbx_token sl.xxx`
2. `python run_export_to_conf.py --path "out/Tony Xu/Migration Test" --conf_api_token XYZ --conf_email tonyx@dropbox.com --conf_space_key "~1234567"`

A helper script `run_purge_space` is provided to delete all docs in a space.

# Resources

- Confluence API reference: https://developer.atlassian.com/cloud/confluence/rest/intro/

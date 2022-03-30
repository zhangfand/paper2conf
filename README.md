# Overview

The series of scripts exports paper docs from PiFS to Confluence. More specifically, it exports the
docs and folders under a specified root folders and create a confluence page and subpages that
mirror the structure.

## Constraints

# Instructions

## Dependency

1. Install dependent python packages. The script is tested with Python 3.9.9
   ```pip3 install -r requirements.txt```
2. Install pandoc https://pandoc.org/. If you're on MacOS, you can install it via brew.

   ```brew install pandoc```

## Setup

Before running the script, you need to add a .env file and configure some values. Checkout `env.py`
for the values to configure. Here are some tips:

1. Specify the key of the Confluence space that you want to port docs into. You can extract that
   from the url to the space. For example, `~108624815` is the key of my personal space, and the url
   is https://<url>/wiki/spaces/~108624815/. I used my personal space as a test ground. Once you're
   satisfied with the result, you can move the whole page tree into the space for your service /
   team.
2. Specify the Confluence API key. You can get it from
   link: https://id.atlassian.com/manage-profile/security/api-tokens
3. Specify email of your Confluence account. It should be the same as your work email.
4. Specify a paper application key. You can get it by creating an app here:
   https://www.dropbox.com/developers/apps. Grant your app with following permissions:
   account_info.read, files.metadata.read, files.content.read and sharing.read. Generate an access
   token using the button in the "OAuth2" section under "Settings" panel.

## Run

The Dropbox folder path to download from and the local directory path to export to Confluence is
hardcoded in the script. Update the script before running it.

1. Run script `run_cloud_doc_download_folder` to download the files.
2. Run script `run_export_to_conf` to export them to Confluence.

A helper script `run_purge_space` is provided to delete all docs in a space.

# Resources

- Confluence API reference: https://developer.atlassian.com/cloud/confluence/rest/intro/

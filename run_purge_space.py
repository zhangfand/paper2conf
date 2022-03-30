from atlassian import confluence

import env

if __name__ == "__main__":
    client = confluence.Confluence(url="https://dropbox-kms.atlassian.net",
                                   username=env.CONF_ACCOUNT_EMAIL, password=env.CONF_API_TOKEN,
                                   cloud=True)
    client.create_page()
    while True:
        pages = client.get_all_pages_from_space(space="~5a79f255e4d2ae612afbb267")
        if not pages:
            break

        for page in pages:
            title = page['title']
            id = page['id']
            print(f"deleting {title}")
            client.remove_page(id)

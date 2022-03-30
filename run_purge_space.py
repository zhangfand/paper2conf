from atlassian import confluence

import env

if __name__ == "__main__":
    client = confluence.Confluence(url=env.CONF_URL,
                                   username=env.CONF_ACCOUNT_EMAIL,
                                   password=env.CONF_API_TOKEN,
                                   cloud=True)
    client.create_page()
    while True:
        pages = client.get_all_pages_from_space(space=env.CONF_SPACE_KEY)
        if not pages:
            break

        for page in pages:
            title = page['title']
            id = page['id']
            print(f"deleting {title}")
            client.remove_page(id)

def list_images():
    api_key = get_access_key()
    try:
        response = requests.get(url=f'https://api.digitalocean.com/v2/images/?distribution=CentOS&page=2',
                                 headers={'Authorization': f'Bearer {api_key}',
                                          'Content-Type': 'application/json'})
    except requests.exceptions.HTTPError as e:
        print(e)

    return(response)


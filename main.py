import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv


API_VERSION = 5.199


def get_random_comic_picture():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    last_comic_picture = response.json()

    random_number = random.randint(1, last_comic_picture['num'])
    comic_picture_url = f'https://xkcd.com/{random_number}/info.0.json'
    comic_picture_response = requests.get(comic_picture_url)
    comic_picture = comic_picture_response.json()
    response.raise_for_status()

    comment = comic_picture['alt']
    image_url = comic_picture['img']

    return {'image_url': image_url, 'comment': comment}


def fetch_image(url, path):
    filepath = path / 'file.png'
    response = requests.get(url)
    response.raise_for_status()

    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_vk_address_for_image(user_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'

    params = {'access_token': user_token, 'v': API_VERSION,
              'group_id': group_id}

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def upload_photo_vk(response, user_token, group_id):
    url = response['response']['upload_url']

    with open('images/file.png', 'rb') as file:
        files = {'photo': file}

        params = {'access_token': user_token, 'v': API_VERSION,
                  'group_id': group_id}

        response = requests.post(url, params=params, files=files)
        response.raise_for_status()

        return response.json()


def save_photo_vk(response, user_token, group_id):
    gated_hash = response['hash']
    photo = response['photo']
    server = response['server']
    url = 'https://api.vk.com/method/photos.saveWallPhoto'

    params = {'access_token': user_token, 'v': API_VERSION,
              'group_id': group_id, 'hash': gated_hash,
              'photo': photo, 'server': server}

    response = requests.post(url, params=params)
    response.raise_for_status()

    return response.json()


def publish_photo_vk(response, comment, user_token, user_id, group_id):
    media_id = response['response'][0]['id']
    owner_id = '-' + group_id
    from_group = 1
    attachments = f'photo{user_id}_{media_id}'
    url = 'https://api.vk.com/method/wall.post'

    params = {'access_token': user_token, 'v': API_VERSION,
              'owner_id': owner_id, 'from_group': from_group,
              'attachments': attachments, 'message': comment}

    response = requests.post(url, params=params)
    response.raise_for_status()

    return response.json()


def main():
    load_dotenv()

    user_id = os.environ.get('VK_USER_ID')
    user_token = os.environ.get('VK_API_USER_TOKEN')
    group_id = os.environ.get('GROUP_ID')
    comic_picture = get_random_comic_picture()
    image_url = comic_picture['image_url']
    comment = comic_picture['comment']

    path = Path('images')
    path.mkdir(parents=True, exist_ok=True)
    fetch_image(image_url, path)

    photo_address = get_vk_address_for_image(user_token, group_id)

    response_upload_photo = upload_photo_vk(photo_address, user_token,
                                            group_id)

    response_save_photo = save_photo_vk(response_upload_photo,
                                        user_token, group_id)

    publish_photo_vk(response_save_photo, comment,
                     user_token, user_id, group_id)

    os.remove('images/file.png')


if __name__ == '__main__':
    main()

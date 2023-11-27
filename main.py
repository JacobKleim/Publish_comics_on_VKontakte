import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv


API_VERSION = 5.199


class VKApiError(requests.HTTPError):
    def __init__(self, error_code, error_msg):
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(f'error_code - {error_code}, error_msg - {error_msg}')


def vk_response_processing(response):
    if 'error' in response:
        error_code = response['error']['error_code']
        error_msg = response['error']['error_msg']

        raise VKApiError(error_code, error_msg)


def download_random_comic(path):
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    last_comic = response.json()

    random_number = random.randint(1, last_comic['num'])
    comic_url = f'https://xkcd.com/{random_number}/info.0.json'
    comic_response = requests.get(comic_url)
    comic = comic_response.json()
    response.raise_for_status()

    comment = comic['alt']
    image_url = comic['img']

    filepath = os.path.join(path, 'file.png')
    response = requests.get(image_url)
    response.raise_for_status()

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return {'image_url': image_url, 'comment': comment}


def get_url_for_upload_image_vk(user_token, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'

    params = {'access_token': user_token, 'v': API_VERSION,
              'group_id': group_id}

    response = requests.get(url, params=params)
    response.raise_for_status()
    json_response = response.json()
    vk_response_processing(json_response)
    upload_url = json_response['response']['upload_url']

    return upload_url


def upload_photo_vk(url, user_token, group_id):
    with open(os.path.join('images', 'file.png'), 'rb') as file:
        files = {'photo': file}

        params = {'access_token': user_token, 'v': API_VERSION,
                  'group_id': group_id}

        response = requests.post(url, params=params, files=files)
    response.raise_for_status()
    unpacked_response = response.json()
    vk_response_processing(unpacked_response)

    return unpacked_response


def save_photo_vk(gated_hash, photo, server, user_token, group_id):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'

    params = {'access_token': user_token, 'v': API_VERSION,
              'group_id': group_id, 'hash': gated_hash,
              'photo': photo, 'server': server}

    response = requests.post(url, params=params)
    response.raise_for_status()
    json_response = response.json()
    vk_response_processing(json_response)

    return json_response


def publish_photo_vk(media_id, comment, user_token, user_id, group_id):
    owner_id = '{}{}'.format('-', group_id)
    from_group = 1
    attachments = f'photo{user_id}_{media_id}'
    url = 'https://api.vk.com/method/wall.post'

    params = {'access_token': user_token, 'v': API_VERSION,
              'owner_id': owner_id, 'from_group': from_group,
              'attachments': attachments, 'message': comment}

    response = requests.post(url, params=params)
    response.raise_for_status()
    json_response = response.json()
    vk_response_processing(json_response)

    return json_response


def main():
    load_dotenv()

    try:
        path = Path('images')
        path.mkdir(parents=True, exist_ok=True)

        user_token = os.environ['VK_API_USER_TOKEN']
        group_id = os.environ['GROUP_ID']

        random_comic = download_random_comic(path)

        comic_comment = random_comic['comment']

        url_for_upload_image_vk = get_url_for_upload_image_vk(
            user_token, group_id)

        upload_photo_response = upload_photo_vk(url_for_upload_image_vk,
                                                user_token,
                                                group_id)

        gated_hash = upload_photo_response['hash']
        photo = upload_photo_response['photo']
        server = upload_photo_response['server']

        save_photo_response = save_photo_vk(gated_hash, photo, server,
                                            user_token, group_id)

        user_id = save_photo_response['response'][0]['owner_id']
        media_id = save_photo_response['response'][0]['id']

        publish_photo_vk(media_id, comic_comment,
                         user_token, user_id, group_id)

    finally:
        os.remove(os.path.join(path, 'file.png'))


if __name__ == '__main__':
    main()

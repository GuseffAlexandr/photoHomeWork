import requests
import json
import os
from tqdm import tqdm

VK_API_URL = 'https://api.vk.com/method/photos.get'
YANDEX_DISK_API_URL = 'https://cloud-api.yandex.net/v1/disk/resources'


def get_vk_photos(user_id, vk_token, count=5):
    params = {
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1,
        'count': count,
        'access_token': vk_token,
        'v': '5.131'
    }
    response = requests.get(VK_API_URL, params=params).json()

    if 'error' in response:
        raise Exception(f"Error fetching photos: {response['error']['error_msg']}")

    photos = response['response']['items']

    photo_list = []
    for photo in photos:
        sizes = photo['sizes']
        max_size_photo = max(sizes, key=lambda size: size['width'] * size['height'])
        photo_list.append({
            'file_name': f"{photo['likes']['count']}.jpg",
            'url': max_size_photo['url'],
            'size': max_size_photo['type']
        })

    return photo_list


def upload_to_yandex_disk(photo_list, yandex_token, folder_name='VK_Photos'):
    headers = {
        'Authorization': f'OAuth {yandex_token}'
    }

    # Создаем папку на Яндекс.Диске
    folder_url = f"{YANDEX_DISK_API_URL}?path={folder_name}"
    requests.put(folder_url, headers=headers)

    # Загружаем фотографии
    for photo in tqdm(photo_list, desc='Uploading photos to Yandex Disk'):
        upload_url = f"{YANDEX_DISK_API_URL}/upload"
        params = {
            'path': f"{folder_name}/{photo['file_name']}",
            'url': photo['url']
        }
        response = requests.post(upload_url, headers=headers, params=params)
        response.raise_for_status()


def save_json(photo_list, file_name='photos_info.json'):
    with open(file_name, 'w') as file:
        json.dump(photo_list, file, indent=4)


def main():
    user_id = input("Enter VK user ID: ")
    vk_token = input("Enter VK token: ")
    yandex_token = input("Enter Yandex Disk token: ")

    try:
        print("Fetching photos from VK...")
        photos = get_vk_photos(user_id, vk_token)
    except Exception as e:
        print(e)
        return

    print("Uploading photos to Yandex Disk...")
    try:
        upload_to_yandex_disk(photos, yandex_token)
    except Exception as e:
        print(f"Error uploading to Yandex Disk: {e}")
        return

    print("Saving photos info to JSON file...")
    save_json(photos)

    print("Done!")


if __name__ == '__main__':
    main()

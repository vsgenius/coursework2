from datetime import datetime
from random import randrange
import requests
from io import BytesIO
from bot_db import update_db, create_db, check_db
import vk_api
from vk_api.upload import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType

TOKEN = '8830ad080fad0acf7aa774c028ea2bc7c528b8c1f99023903d72759b1a4ecbcafebbbb3c7da2d2c677db7'
TOKEN2 = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
vk_group = vk_api.VkApi(token=TOKEN)
vk_find = vk_api.VkApi(token=TOKEN2)
upload = VkUpload(vk_group)
longpoll = VkLongPoll(vk_group)

def send_msg(values) -> object:
    vk_group.method('messages.send', values)


def wait_msg():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            return event


def upload_photo(url):
    img = requests.get(url).content
    f = BytesIO(img)
    response = upload.photo_messages(f)[0]
    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    return owner_id, photo_id, access_key


def get_user_photos(user_id):
    max_lx, max_m, max_s = 0, 0, 0
    list_file = []
    user_data = vk_find.method('photos.get',
                               {'owner_id': user_id, 'v': '5.131', 'album_id': 'wall', 'extended': '1'})
    for data in user_data['items']:
        sum = data['likes']['count'] + data['comments']['count']
        len_file = len(list_file)
        if sum > max_lx:
            max_lx = sum
            if len_file > 0:
                list_file.pop(0)
            list_file.insert(0, data['sizes'][-1]['url'])
        elif sum > max_m:
            max_m = sum
            if len_file > 1:
                list_file.pop(1)
            list_file.insert(1, data['sizes'][-1]['url'])
        elif sum > max_s:
            max_s = sum
            if len_file > 2:
                list_file.pop(2)
            list_file.insert(2, data['sizes'][-1]['url'])
    return list_file


def get_attachment_photo(list_files):
    attachment = []
    for file in list_files:
        img = upload_photo(file)
        photo_id = f'photo{img[0]}_{img[1]}_{img[2]}'
        attachment.append(photo_id)
    result = ','.join(attachment)
    return result


def get_list_users(user_fields, user_id, peer_id,count_list_user=9):
    count = 0
    for user in search_user(user_fields):
        if not user['is_closed'] and check_db(user_fields['id'],user['id']):
            count += 1
            list_files = get_user_photos(user['id'])
            send_msg({'user_id': user_id,
                      'random_id': 0,
                      'peer_id': peer_id,
                      'message': f'{user["first_name"]} {user["last_name"]} https://vk.com/id{user["id"]}',
                      'attachment': get_attachment_photo(list_files)})
            update_db(user_fields['id'],user['id'])
        if count == count_list_user: break
    if count == 0:
        send_msg({'user_id': user_id, 'random_id': 0, 'message': 'Никого не найдено'})


def get_user_field(user_id):
    fields = 'bdate ,city,country,sex,relation'
    answer = vk_group.method('users.get', {'user_ids': user_id, 'fields': fields})[0]
    return answer


def age_from(age_user, user_id):
    age = age_user.split('.')
    if len(age) < 3:
        send_msg({'user_id': user_id, 'message': 'Возраст не указан. Укажите верхний предел','random_id': randrange(10 ** 7)})
        return int(wait_msg())-5
    res = datetime.now().year - int(age[2])
    return res - 5


def age_to(age_user, user_id):
    age = age_user.split('.')
    if len(age) < 3:
        send_msg({'user_id': user_id, 'message': 'Возраст не указан. Укажите верхний предел','random_id': randrange(10 ** 7)})
        return int(wait_msg())+5
    res = datetime.now().year - int(age[2])
    return res + 5


def check_city(user_field, user_id):
    if user_field is None or user_field == '':
        send_msg({'user_id': user_id, 'message': 'Город не заполнен. Укажите в ответном сообщении','random_id': randrange(10 ** 7)})
        return wait_msg()
    return user_field['id']


def check_country(user_field, user_id):
    if user_field is None or user_field == '':
        send_msg({'user_id': user_id, 'message': 'Страна не заполнена. Укажите в ответном сообщении','random_id': randrange(10 ** 7)})
        return wait_msg()
    return user_field['id']


def search_user(user_fields):
    fields = 'age, sex, city, bdate,  hometown, is_closed'
    params = {'q': '', 'sort': 0, 'online': 1, 'has_photo': 1, 'count': 1000,
              'fields': fields,
              'country': check_country(user_fields.get('country'), user_fields['id']),  # указать страна
              'status': user_fields.get('relation'),  # Женат не женат
              'age_from': age_from(user_fields.get('bdate'), user_fields['id']),  # возраст от
              'age_to': age_to(user_fields.get('bdate'), user_fields['id']),  # возраст до
              'sex': (1 if user_fields.get('sex') == 2 else 2)}  # указать пол
    if not check_city(user_fields.get('city'), user_fields['id']):
        params['hometown'] = check_city(user_fields.get('city'), user_fields['id']) # указать город
    else: params['city'] = user_fields['city']['id']
    print(params)
    user_lists = vk_find.method('users.search', params)
    return user_lists['items']

def bot_answer(event):
    request = event.text
    user_fields = get_user_field(event.user_id)
    if request.lower() == "привет" or request.lower() == 'hi':
            send_msg({'user_id': user_fields['id'],
                      'message': f"Добрый день {user_fields['first_name']},"
                                 f"\nпо Вашим параметрам найдены следующие страницы:",
                      'random_id': randrange(10 ** 7)})
            get_list_users(user_fields, event.user_id, event.peer_id)
    elif request.lower() == "пока" or request.lower() == 'bye':
        send_msg({'user_id': event.user_id, 'message': f"пока {user_fields['first_name']}",'random_id': randrange(10 ** 7)})
    else:
        send_msg({'user_id': event.user_id, 'message': 'Не поняла Вас....','random_id': randrange(10 ** 7)})

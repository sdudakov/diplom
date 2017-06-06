"""
Задание: Вывести список групп в ВК в которых состоит пользователь, но не
состоит никто из его друзей. В качестве жертвы, на ком тестировать, можно
использовать: https://vk.com/tim_leary

Внимание: и имя пользователя (tim_leary) и id (5030613)  - являются
валидными входными данными
Ввод можно организовать любым способом:
из консоли
из параметров командной строки при запуске
из переменной

Программа не падает, если один из друзей пользователя помечен как “удалён” или
“заблокирован”
Показывает что не зависла: рисует точку или чёрточку на каждое обращение к api
Не падает, если было слишком много обращений к API
(Too many requests per second)
Ограничение от ВК: не более 3х обращений к API в секунду.
Могут помочь модуль time (time.sleep) и конструкция (try/except)
Код программы удовлетворяет PEP8
"""

import requests
import time
import json

params = {'access_token': 'd13e692be69592b09fd22c77a590dd34e186e6d696daa88d6d981e1b4e296b14acb377e82dcbc81dc0f22',
          'v': '5.62',
          }


# функция возвращает список групп пользователя
def groups_list(user_id):
    params_groups_list = params.copy()
    params_groups_list['user_id'] = user_id
    # список групп пользователя
    response = requests.get('https://api.vk.com/method/groups.get', params_groups_list)
    for item in response.json():
        if 'error' not in item:
            groups = response.json()['response']['items']
        else:
            print('у пользователя {} нет групп'.format(user_id))
            exit(0)
    return groups


# функция возвращает список друзей пользователя
def friends_list(user_id):
    params_friends_list = params.copy()
    params_friends_list['user_id'] = user_id
    response = requests.get('https://api.vk.com/method/friends.get', params_friends_list)
    friends = response.json()['response']['items']
    return friends


# функция делит список друзей пользователя на части по 500 в каждой
def divide_items_into_parts(items, part_size=500):
    return [items[i:i+part_size] for i in range(0, len(items), part_size)]


# функция преобразует список в строку
def list_to_string(items):
    string = ''
    for item in items:
        string += str(item)
        string += ', '
    return string


# функция возвращает множество групп пользователя,
# в которых не состоит ни один из его друзей
def unique_groups_set(groups, friends):
    unique_groups = groups.copy()
    params_unique_groups_set = params.copy()
    if len(friends) > 500:
        divide_user_friends = divide_items_into_parts(friends)
        count_friends = len(friends)
        for divide_user_item in divide_user_friends:
            print('осталось проверить {} друзей из {}'.format(count_friends, len(user_friends)))
            count_friends -= len(divide_user_item)
            params_unique_groups_set['user_ids'] = list_to_string(divide_user_item)
            for group in groups:
                params_unique_groups_set['group_id'] = group
                response = requests.post('https://api.vk.com/method/groups.isMember', params_unique_groups_set)
                time.sleep(0.5)
                for item in response.json():
                    if 'error' not in item:
                        print('проверяем группу {}'.format(group))
                        for item in response.json()['response']:
                            if item['member'] == 1:
                                if group in unique_groups:
                                    unique_groups.remove(group)
    else:
        params_unique_groups_set['user_ids'] = list_to_string(friends)
        for group in groups:
            params_unique_groups_set['group_id'] = group
            # информация о том, является ли пользователь участником сообщества
            response = requests.post('https://api.vk.com/method/groups.isMember', params_unique_groups_set)
            time.sleep(0.5)
            for item in response.json():
                if 'error' not in item:
                    print('проверяем группу {}'.format(group))
                    for item in response.json()['response']:
                        if item['member'] == 1:
                            if group in unique_groups:
                                unique_groups.remove(group)
    return unique_groups


# функция записывает информацию о группах в файл формата json
def write_groups_to_json(groups):
    params_write_groups_to_json = params.copy()
    params_write_groups_to_json['fields'] = 'members_count'
    params_write_groups_to_json['group_ids'] = list_to_string(groups)
    write_groups_list = []
    # информация о группе
    response = requests.post('https://api.vk.com/method/groups.getById', params_write_groups_to_json)
    for response in response.json()['response']:
        if 'deactivated' not in response:
            groups_dict = {'name': response['name'],
                           'gid': response['id'],
                           'members_count': response['members_count']
                           }
            write_groups_list.append(groups_dict)
    print('Данные о группах пишем в файл groups.json')
    with open('groups.json', mode='w', encoding='utf-8') as file:
        json.dump(write_groups_list, file, ensure_ascii=False, indent=2)
    return 0

user_id = 5030613
# user_id = 'tim_leary'
# user_id = 171691064

user_groups = groups_list(user_id)
user_friends = friends_list(user_id)
user_unique_groups = unique_groups_set(user_groups, user_friends)
write_groups_to_json(user_unique_groups)

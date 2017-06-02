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
    params['user_id'] = user_id
    # список групп пользователя
    response = requests.get('https://api.vk.com/method/groups.get', params)
    for item in response.json():
        if 'error' not in item:
            groups = response.json()['response']['items']
        else:
            print('у пользователя {} нет групп'.format(user_id))
            exit(0)
    return groups


# функция возвращает список друзей пользователя
def friends_list(user_id):
    params['user_id'] = user_id
    # список друзей
    response = requests.get('https://api.vk.com/method/friends.get', params)
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
    unique_groups = groups
    params['user_ids'] = list_to_string(friends)
    for group in groups:
        params['group_id'] = group
        # информация о том, является ли пользователь участником сообщества
        response = requests.post('https://api.vk.com/method/groups.isMember', params)
        time.sleep(0.5)
        for item in response.json():
            if 'error' not in item:
                print('проверяем группу {}'.format(group)
                      )
                for item in response.json()['response']:
                    if item['member'] == 1:
                        if group in unique_groups:
                            unique_groups.remove(group)
    return unique_groups


# функция записывает информацию о группах в файл формата json
def write_groups_to_json(groups):
    params['fields'] = 'members_count'
    params['group_ids'] = list_to_string(groups)
    groups_list = []
    # информация о группе
    response = requests.post('https://api.vk.com/method/groups.getById', params)
    for response in response.json()['response']:
        if 'deactivated' not in response:
            groups_dict = {'name': response['name'],
                           'gid': response['id'],
                           'members_count': response['members_count']
                           }
            groups_list.append(groups_dict)
    print('Данные о группах пишем в файл groups.json')
    with open('groups.json', mode='w', encoding='utf-8') as file:
        json.dump(groups_list, file, ensure_ascii=False, indent=2)
    return 0


# функция проверяет количество друзей у пользователя для соблюдения ограничений ВК
def сheck_friends_number(user_groups, user_friends):
    if len(user_friends) > 500:
        divide_user_friends = divide_items_into_parts(user_friends)
        count_friends = len(user_friends)
        composite_unique_groups_set = set()
        for divide_user_item in divide_user_friends:
            print('осталось проверить {} друзей из {}'.format(count_friends, len(user_friends)))
            count_friends -= len(divide_user_item)
            divide_unique_groups_set = unique_groups_set(user_groups, divide_user_item)
            for user_groups_item in divide_unique_groups_set:
                composite_unique_groups_set.add(user_groups_item)
    else:
        composite_unique_groups_set = unique_groups_set(user_groups, user_friends)
    return composite_unique_groups_set


user_id = 5030613
# user_id = 'tim_leary'

user_groups = groups_list(user_id)
user_friends = friends_list(user_id)
unique_groups = сheck_friends_number(user_groups, user_friends)
write_groups_to_json(unique_groups)

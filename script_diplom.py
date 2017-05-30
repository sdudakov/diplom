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
    params['user_ids'] = user_id
    # список групп пользователя
    response = requests.get('https://api.vk.com/method/groups.get', params)
    groups = response.json()['response']['items']
    return groups


# функция возвращает список друзей пользователя
def frends_list(user_id):
    params['user_ids'] = user_id
    # список друзей
    response = requests.get('https://api.vk.com/method/friends.get', params)
    frends = response.json()['response']['items']
    return frends


# функция преобразует список в строку
def list_to_string(items):
    string = ''
    for item in items:
        string += str(item)
        string += ', '
    return string


# функция возвращает множество групп пользователя,
# в которых не состоит ни один из его друзей
def user_unique_groups(groups, frends):
    unique_groups = set()
    groups_count = len(groups)
    params['user_ids'] = list_to_string(frends)
    for group in groups:
        params['group_id'] = group
        # информация о том, является ли пользователь участником сообщества
        response = requests.get('https://api.vk.com/method/groups.isMember',
                                params
                                )
        time.sleep(0.5)
        groups_count -= 1
        for item in response.json():
            if 'error' not in item:
                print('группа {}, осталось проверить {} групп из {}'
                      .format(group, groups_count, len(groups))
                      )
                for item in response.json()['response']:
                    if item['member'] == 0:
                        unique_groups.add(group)
                    else:
                        unique_groups.remove(group)
    return unique_groups


# функция записывает информацию о группах в файл формата json
def write_groups_to_json(groups):
    params['fields'] = 'members_count'
    params['group_ids'] = list_to_string(groups)
    groups_list = []
    # информация о группе
    response = requests.get('https://api.vk.com/method/groups.getById', params)
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


user_id = 5030613
# user_id = 'tim_leary'
user_groups = groups_list(user_id)
user_frends = frends_list(user_id)
unique_groups = user_unique_groups(user_groups, user_frends)
write_groups_to_json(unique_groups)

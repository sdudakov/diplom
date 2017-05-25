# Задание: Вывести список групп в ВК в которых состоит пользователь, но не
# состоит никто из его друзей. В качестве жертвы, на ком тестировать, можно
# использовать: https://vk.com/tim_leary

# Внимание: и имя пользователя (tim_leary) и id (5030613)  - являются
# валидными входными данными
# Ввод можно организовать любым способом:
# из консоли
# из параметров командной строки при запуске
# из переменной

# Программа не падает, если один из друзей пользователя помечен как “удалён” или
# “заблокирован”
# Показывает что не зависла: рисует точку или чёрточку на каждое обращение к api
# Не падает, если было слишком много обращений к API
# (Too many requests per second)
# Ограничение от ВК: не более 3х обращений к API в секунду.
# Могут помочь модуль time (time.sleep) и конструкция (try/except)
# Код программы удовлетворяет PEP8

# 1. получить список групп пользователя и список его друзей
# 2. для каждого друга получить список групп (можно объединитьих в множество groups_set() - что бы не было повторений)
# 3. проверить для каждой группы пользователя есть ли такая же в этом множестве groups_set() если нет - это будет выходными данными
# 4. либо функцией https://vk.com/dev/groups.isMember

#import vk
import requests
import time

params = {'access_token': 'd13e692be69592b09fd22c77a590dd34e186e6d696daa88d6d981e1b4e296b14acb377e82dcbc81dc0f22',
          'v': '5.62',
          }
user_id = 5030613
#user_id = 'tim_leary'

#функция возвращает список групп пользователя
def groups_list(user_id):
    params['user_ids'] = user_id
    #response = requests.get('https://api.vk.com/method/users.get', params)  #информация о пользователе
    #response = requests.get('https://api.vk.com/method/friends.get', params) #список друзей
    response = requests.get('https://api.vk.com/method/groups.get', params) #список групп пользователя
    groups = response.json()['response']['items']
    return groups

#функция возвращает список друзей пользователя
def frends_list(user_id):
    params['user_ids'] = user_id
    response = requests.get('https://api.vk.com/method/friends.get', params) #список друзей
    frends = response.json()['response']['items']
    return frends

#функция преобразует список друзей пользователя в строку
def frends_list_to_string(frends):
    frends_string = ''
    for frend in frends:
        frends_string += str(frend)
        frends_string += ', '
    return frends_string

#функция возвращает множество groups_set() всех групп в которых состоят друзья - так делать не стал
#проверить состоит ли друг в группе, если нет то добавить эту группу в список лист, если да то проверить есть ли группа в списке лист и удалить ее оттуда

groups = groups_list(user_id)
frends = frends_list(user_id)


def user_unique_groups(groups, frends):
    unique_groups = []
    groups_count = len(groups)
    for group in groups:
        params['group_id'] = group
        frends_count = len(frends)
        for frend in frends:
            params['user_ids'] = frend
            response = requests.get('https://api.vk.com/method/groups.isMember', params) #информация о том, является ли пользователь участником сообщества
            print(response.json())
            if response.json()['response'][0]['member'] == 0:
                unique_groups.append(group)
            else:
                if group in unique_groups:
                    unique_groups.remove(group)
            time.sleep(0.25)
            frends_count -= 1
            print('fends_id {}, группа {}, осталось проверить {} друзей из {}'.format(frend, group, frends_count, len(frends)))
        groups_count -= 1
        print('осталось проверить {} групп из {}'.format(groups_count, len(groups)))
    return unique_groups


#print(user_unique_groups(groups, frends))


def user_unique_groups(groups, frends):
    unique_groups = []
    groups_count = len(groups)
    params['user_ids'] = frends_list_to_string(frends)
    for group in groups:
        params['group_id'] = group
        response = requests.get('https://api.vk.com/method/groups.isMember', params) #информация о том, является ли пользователь участником сообщества
        print(response.json())
        time.sleep(0.25)
        groups_count -= 1
        print('группа {}, осталось проверить {} групп из {}'.format(group, groups_count, len(groups)))
    return unique_groups
print(user_unique_groups(groups, frends))
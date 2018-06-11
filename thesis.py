import requests
import json
from data.data_for_requests import ID, params, params_group, ERROR
import time


def retry(func):
    """Функция декоратор, делает паузу в 1 сек. при ее вызова, и возвращает к выполнению в вызванной фун-ции"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except RetryException:
            print('Pause 1 sec (Too many requests per second)')
            time.sleep(1)
            return wrapper(*args, **kwargs)
    return wrapper


class RetryException(Exception):
    def __init__(self):
        pass


class VkReq():

    def __init__(self, id):
        """При инициализации класса создаем списки для 'выходных данных' и список для наполнения группами в которых
        состоят друзья 'target' """
        self.list_groups_friends = list()
        self.list_friends_target = list()
        self.id = id
        self.list_groups_target = list()
        self.friends_counter = 0  # Используем для счетчика оставшихся api запросов по друзьям


    @retry
    def requests_api(self, method, params):
        """Функция принимает метод и параметры для запроса к API, отрабатывает ошибку в ответе API 'Too many requests
        per second' вызывая исключение RetryException"""
        try:
            response = requests.get('https://api.vk.com/method/{}'.format(method), params=params)
            response.raise_for_status()
            response = response.json()
            if 'error' in response:
                if response['error']['error_msg'] == ERROR:
                    raise RetryException
        except requests.exceptions.ReadTimeout:
            raise RetryException

        return response


    def get_list_friends(self, id):
        """Функция принимает id пользователя и возврящает список его друзей"""
        method = 'friends.get'
        params_request = {**params, **{'user_id': id}}
        response_friends = self.requests_api(method, params_request)
        list_friends = response_friends['response']['items']
        return list_friends


    def get_list_groups(self, id):
        """функция принимает id и возвращает список групп в которых состоит пользователь"""
        try:
            method = 'groups.get'
            params_request = {**params, **{'user_id': id}}
            print('Запрос информации по другу с ID {}, осталось обработать друзей {}'.\
                  format(id, len(self.list_friends_target) - self.friends_counter))
            self.friends_counter += 1
            response_group = self.requests_api(method, params_request)
            list_group = response_group['response']['items']
            return list_group  # По некоторым ID возвращает None, и попадает в список

        except KeyError:
            pass


    def merge_list(self, list_friends):
        """Функция принимает список (вложенный), проходит циклом, проверяет элемент на None, и возврящает множество"""
        merge_list_friends = list()
        for groups in list_friends:
            if groups is not None:
                for group in groups:
                    merge_list_friends.append(group)
        return set(merge_list_friends)

    def get_info_groups(self, groups):
        """Функция принимает id групп и добавляет информацию в список data_to_file в виде словаря (id,
        название группы и количество участников в группе"""
        method = 'groups.getById'
        groups_ids = ','.join(str(group) for group in groups)
        params_group_request = {**params_group, **{'group_ids': groups_ids}}
        print('Запрос информации по группам (кол-во групп {})'.format(len(groups)))
        response = self.requests_api(method, params_group_request)
        need_data = response['response']
        data_to_file = list()
        for gr in need_data:
            id_g, m_c, n_g = gr['id'], gr['members_count'], gr['name']
            data_to_file.append({'id': id_g, 'members_count': m_c, 'name': n_g})
        return data_to_file


    def write_to_file(self, data):
        """Функция принимает информацию и записывает в файл JSON"""
        with open('groups.json', 'w') as groups_data:
            json.dump(data, groups_data, indent=2, ensure_ascii=False)


def main():
    vk = VkReq(ID)
    vk.list_friends_target = vk.get_list_friends(vk.id)  # Получаем список друзей 'target'
    vk.list_groups_target = set(vk.get_list_groups(vk.id))  # Получаем список групп 'target' и преобразуем в множество

    for friend in vk.list_friends_target:  # Циклом обходим всех друзей и получаем список групп всех его друзей
        vk.list_groups_friends.append(vk.get_list_groups(friend))  # vk.list_groups_friends - состоит из вложенных спис.

    vk.list_groups_friends = vk.merge_list(vk.list_groups_friends)  # Преобразуем вложенный список в множество
    groups = vk.list_groups_target - vk.list_groups_friends  # Разность множеств, получаем нужный список групп
    data = vk.get_info_groups(groups)  # передаем список групп, получаем нужную инфу
    vk.write_to_file(data)  # Записываем информацию  в json файл


main()

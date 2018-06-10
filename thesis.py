import requests
import json
from data.data_for_requests import ID, params, params_group
import time

ERROR = 'Too many requests per second'


def retry(func):
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
        self.data_to_file = list()
        self.list_groups_friends = list()
        self.list_friends_target = list()
        self.id = id
        self.list_groups_target = list()


    @retry
    def requests_api(self, method, params):
        """Функция принимает метод и параметры для запроса к API"""
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

        self.friends_counter = 0

        method = 'friends.get'
        params_request = params
        params_request['user_id'] = id
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
        self.merge_list_friends = list()

        for groups in list_friends:
            if groups is not None:
                for group in groups:
                    self.merge_list_friends.append(group)
        return set(self.merge_list_friends)

    def get_info_groups(self, groups):
        """Функция принимает id групп и добавляет информацию в список data_to_file в виде словаря (id,
        название группы и количество участников в группе"""

        method = 'groups.getById'
        groups_counter = 0
        for group in groups:
            params_group_request = {**params_group, **{'group_id': group}}
            print('Запрос информации по группе c ID {}, осталось обработать групп {}'.format(group, (len(groups) -\
                                                                                            groups_counter)))
            groups_counter += 1
            response = self.requests_api(method, params_group_request)
            need_data = response['response'][0]
            id_g, m_c, n_g = need_data['id'], need_data['members_count'], need_data['name']
            self.data_to_file.append({'id': id_g, 'members_count': m_c, 'name': n_g})
        return self.data_to_file


    def write_to_file(self, data):
        """Функция принимает информацию и записывает в файл JSON"""
        with open('groups.json', 'w') as groups_data:
            json.dump(data, groups_data, indent=2, ensure_ascii=False)


def main():
    vk = VkReq(ID)
    vk.list_friends_target = vk.get_list_friends(vk.id)  # Получаем список друзей 'target'
    vk.list_groups_target = set(vk.get_list_groups(vk.id))  # Получаем список групп 'target' и преобразуем в множество

    for friend in vk.list_friends_target[0:50]:  # Циклом обходим всех друзей и получаем список групп всех его друзей
        vk.list_groups_friends.append(vk.get_list_groups(friend))  # vk.list_groups_friends - состоит из вложенных спис.

    vk.list_groups_friends = vk.merge_list(vk.list_groups_friends)  # Преобразуем вложенный список в множество
    groups = vk.list_groups_target - vk.list_groups_friends  # Разность множеств, получаем нужный список групп
    data = vk.get_info_groups(groups)  # передаем список групп, получаем нужную инфу
    vk.write_to_file(data)  # Записываем информацию  в json файл


main()
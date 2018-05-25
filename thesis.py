import requests
import json
from Data.Data_for_requests import ID, params, params_group


def retry(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print('Error during work {}, new attemp'.format(func))
            raise
    return wrapper


class VkReq():

    def __init__(self, id):
        """При инициализации класса создаем списки для 'выходных данных' и список для наполнения группами в которых
        состоят друзья 'target' """
        self.data_to_file = list()
        self.list_groups_friends = list()
        self.list_friends_target = list()  # Добавил
        self.id = id  # Добавил
        self.list_groups_target = list()  # Добавил
        self.merge_list_friends = list()
        self.f = 0
        self.g = 0

    @retry
    def get_list_friends(self, id):
        """Функция принимает id пользователя и возврящает список его друзей"""
        try:
            params['user_id'] = id
            response_friends = requests.get('https://api.vk.com/method/friends.get', params=params)
            response_friends = response_friends.json()
            list_friends = response_friends['response']['items']
            return list_friends
        except requests.exceptions.ReadTimeout:
            raise

    @retry
    def get_list_groups(self, id):
        """функция принимает id и возвращает список групп в которых состоит пользователь"""
        try:
            params['user_id'] = id
            print('Запрос информации по friend {}, осталось {}'.format(id, (len(vk.list_friends_target)-vk.f)))
            response_group = requests.get('https://api.vk.com/method/groups.get', params=params)
            response_group = response_group.json()
            list_group = response_group['response']['items']
            vk.f += 1
            return list_group  # По некоторым ID возвращает None, и попадает в список

        except KeyError:
            pass

        except requests.exceptions.ReadTimeout:
            raise

    def merge_list(self, list_friends):
        """Функция принимает список (вложенный), проходит циклом, проверяет элемент на None, и возврящает множество"""
        for groups in list_friends:
            if groups is not None:
                for group in groups:
                    self.merge_list_friends.append(group)
        return set(self.merge_list_friends)

    def get_info_groups(self, groups):
        """Функция принимает id групп и добавляет информацию в список data_to_file в виде словаря (id,
        название группы и количество участников в группе"""
        try:
            for group in groups:
                params_group['group_id'] = group
                print('Запрос информации по группе {}, осталось {}'.format(group, (len(groups) - vk.g)))
                response = requests.get('https://api.vk.com/method/groups.getById', params=params_group)
                response = response.json()
                need_data = response['response'][0]
                id_g, m_c, n_g = need_data['id'], need_data['members_count'], need_data['name']
                self.data_to_file.append({'id': id_g, 'members_count': m_c, 'name': n_g})
                vk.g +=1
            return self.data_to_file
        except requests.exceptions.ReadTimeout:
            raise

    @retry
    def write_to_file(self, data):
        """Функция принимает информацию и записывает в файл JSON"""
        with open('groups.json', 'w') as groups_data:
            json.dump(data, groups_data, indent=2, ensure_ascii=False)


vk = VkReq(ID)


def main():

    vk.list_friends_target = vk.get_list_friends(vk.id)  # Получаем список друзей 'target'
    vk.list_groups_target = set(vk.get_list_groups(vk.id))  # Получаем список групп 'target' и преобразуем в множество

    for friend in vk.list_friends_target:  # Циклом обходим всех друзей и получаем список групп всех его друзей
        vk.list_groups_friends.append(vk.get_list_groups(friend))  # vk.list_groups_friends - состоит из вложенных спис.

    vk.list_groups_friends = vk.merge_list(vk.list_groups_friends)  # Преобразуем вложенный список в множество
    groups = vk.list_groups_target - vk.list_groups_friends  # Разность множеств, получаем нужный список групп
    data = vk.get_info_groups(groups)  # передаем список групп, получаем нужную инфу
    vk.write_to_file(data)  # Записываем информацию  в json файл


main()
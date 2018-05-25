import requests
import time
from pprint import pprint
import json

from Data.Data_for_requests import VERSION, TOKEN, ID, params

data_to_file = list()


def get_list_friends(id):
    params['user_id'] = id
    response_friends = requests.get('https://api.vk.com/method/friends.get', params=params)
    response_friends = response_friends.json()
    list_friends = response_friends['response']['items']
    return list_friends


def get_list_groups(id):
    # time.sleep(0.34)
    try:
        params['user_id'] = id
        response_group = requests.get('https://api.vk.com/method/groups.get', params=params)
        response_group = response_group.json()
        list_group = response_group['response']['items']
        print('.')
        return list_group  # По некоторым ID возвращает None, и попадает в список

    except KeyError:
        pass


def get_info_groups(group):

    params_group = {
        'fields': ['id', 'name', 'members_count'],
        'access_token': TOKEN,
        'v': VERSION,
        'group_id': group
    }
    response = requests.get('https://api.vk.com/method/groups.getById', params=params_group)
    response = response.json()
    pprint(response)
    print(response['response'][0]['id'])
    data_to_file.append({'id': response['response'][0]['id'], 'members_count':response['response'][0]['members_count'], 'name':response['response'][0]['name']})


def write_to_file(data):
    with open('groups.json', 'w') as groups_data:
        json.dump(data, groups_data, indent=2, ensure_ascii=False)


def main():

    list_friends_target = get_list_friends(ID)
    list_groups_target = set(get_list_groups(ID))
    list_groups_friends = list()

    for friend in list_friends_target:
        list_groups_friends.append(get_list_groups(friend))

    merge_list = lambda merge_list: [group for list_group in merge_list if list_group != None for group in list_group]

    list_groups_friend = merge_list(list_groups_friends)

    list_groups_friend = set(list_groups_friend)

    groups = list_groups_target - list_groups_friend  # Разность множест

    for group in groups:
        get_info_groups(group)

    write_to_file(data_to_file)


main()
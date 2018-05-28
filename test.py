import requests

VERSION = '5.78'
TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'

params_group = {
            'fields': ['members_count'],
            'v': VERSION,
            'access_token': TOKEN,
            'group_ids': [33938434, 120437251]
        }
data_to_file = list()

def get_info_groups():
    """Функция принимает id групп и добавляет информацию в список data_to_file в виде словаря (id,
    название группы и количество участников в группе"""
    response = requests.get('https://api.vk.com/method/groups.getById', params=params_group)

    response = response.json()
    print(response)
    need_data = response['response'][0]
    id_g, m_c, n_g = need_data['id'], need_data['members_count'], need_data['name']
    data_to_file.append({'id': id_g, 'members_count': m_c, 'name': n_g})
    print(data_to_file)
    return data_to_file


get_info_groups()
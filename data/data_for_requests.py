import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
path_file = os.path.join(current_dir, 'config_file.json')

with open(path_file) as file:
    data = json.load(file)
    TOKEN = data['TOKEN']
    VERSION = data['VERSION']
    ID = data['ID']


params = {
    'user_id': None,
    'access_token': TOKEN,
    'v': VERSION
}

params_group = {
            'fields': ['members_count'],
            'access_token': TOKEN,
            'v': VERSION,
            'group_id': None
        }
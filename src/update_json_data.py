import json
from decouple import config

aws_bucket_name = config('AWS_BUCKET_NAME')

def append_to_json(json_file, word, key, filenames):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data_list = data.get('data', [])

    data_list.append({
        'word': word,
        'key': key,
        'filenames': filenames
    })

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
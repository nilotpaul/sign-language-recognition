import json

json_file_path = 'data/train/MSASL_train.json'

data = []

with open(json_file_path, 'r') as file: 
    json_data = json.load(file)

for i in range(len(json_data)): 
    data.append({
        'word': json_data[i]['clean_text'],
        'video': json_data[i]['url'],
        'label': json_data[i]['label'] 
    })


print(len(data))
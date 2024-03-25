import numpy as np
import requests
import cv2
import json
from decouple import config

aws_bucket_name = config('AWS_BUCKET_NAME')

def create_labels(json_file_path):
    dataset = []

    def preprocess_img(url, target_size=(224, 224)):
        try:
            print(f'fetching {url}')

            res = requests.get(url)
            img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)

            img = cv2.resize(img, target_size)
            img = img.astype(np.float32) / 255.0 # normalising in range (0, 1)

            if res.status_code == 200:
                return img    
        except Exception as e:
            print(f'Error while fetching img:{url}: {e}')

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    for entry in data['data']:
        img_urls = []

        for url in entry['filenames']:
            s3_url = f'https://{aws_bucket_name}.s3.amazonaws.com/{url}'

            img_urls.append(s3_url)
    
        dataset.append({
            'word': entry['word'],
            'urls': img_urls
        })  
    
    for entry in dataset:
        urls = entry['urls']
        word = entry['word']

        for url in urls:
            img = preprocess_img(url)

        np.save(f'data/images/{word}.npy', img)
        print(f'saved nparray for {word}')

create_labels('data.json')
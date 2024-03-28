import numpy as np
import requests
import cv2
import json
import boto3
from decouple import config

aws_bucket_name = config('AWS_BUCKET_NAME')

s3 = boto3.client('s3')

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

def convert_images_to_nparray(json_file, bucket_name, target_size=(224, 224)):
    with open(json_file, 'r') as file:
        data = json.load(file)

        for entry in data['data']:
            word = entry['word']
            key = entry['key']

            print('Getting bucket folder...')
            res = s3.list_objects_v2(Bucket=bucket_name, Prefix=key)
            
            for obj in res['Contents']:
                obj_key = obj['Key']

                print('Fetching image...')
                obj_response = s3.get_object(Bucket=bucket_name, Key=obj_key)
                
                image_data = obj_response['Body'].read()

                img = cv2.imdecode(np.frombuffer(image_data, np.uint8), -1)
                img = cv2.resize(img, target_size)
                img = img.astype(np.float32) / 255.0 # normalising in range (0, 1)

                np.save(f'data/images/{word}.npy', img)


convert_images_to_nparray('data.json', aws_bucket_name)
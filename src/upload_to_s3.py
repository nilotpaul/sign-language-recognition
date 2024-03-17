import boto3
from botocore.exceptions import ClientError
from pytube import YouTube
from pytube.exceptions import PytubeError
import os

from decouple import config
from download import data

aws_access_key_id = config('AWS_BUCKET_ACCESS_KEY')
aws_access_key_secret = config('AWS_BUCKET_SECRET_KEY')
aws_bucket_name = config('AWS_BUCKET_NAME')

if (len(aws_access_key_id) == 0 or len(aws_access_key_secret) == 0 or len(aws_bucket_name) == 0):
    raise Exception('No env vars are set')

s3 = boto3.client('s3')

def upload_to_s3(file_path, bucket_name, object_name):
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f'File upload to s3://{bucket_name}/{object_name}')
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"Client Error: {error_code} - {error_message}")
    except Exception as e:
        print(f"Upload Error: {e}")

def download_video(video_url, name):
    try:
       yt_video = YouTube(video_url)

       stream = yt_video.streams.filter(progressive=True).first()

       if stream:
           stream.download(output_path='videos', filename=f'{name}.mp4')

           return f'videos/{name}.mp4'
    except PytubeError as e:
        print('Pytube Error:', e)
        print(f"Pytube Error: {e}")
    

if __name__ == '__main__':
    for item in data:
        word = item['word']
        video_link = item['video']

        path = download_video(video_link, word)

        if path:
            upload_to_s3(file_path=path, bucket_name=aws_bucket_name, object_name=f'videos/{word}.mp4')
            os.remove(path)
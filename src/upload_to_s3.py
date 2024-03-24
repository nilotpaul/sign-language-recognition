from pytube import YouTube
from pytube.exceptions import PytubeError
import os
import shutil
import subprocess

from decouple import config
from download import data
from extract_frames import extract_frames
from update_json_data import append_to_json

aws_bucket_name = config('AWS_BUCKET_NAME')

def upload_to_s3(folder_path, bucket_name):
    s3_uri = f's3://{bucket_name}/'
    subprocess.run(['aws', 's3', 'sync', folder_path, s3_uri])

def download_video(video_url, name):
    try:
       yt_video = YouTube(video_url)

       if yt_video.length > 15: # 15 sec
           raise Exception('Video too long')

       stream = yt_video.streams.filter(progressive=True).first()

       if stream:
           stream.download(output_path='videos', filename=f'{name}.mp4')

           return f'videos/{name}.mp4'
    except PytubeError as e:
        print(f'Pytube Error: {e}')
    except Exception as e:
        print(f'Pytube Error: {e}')

    
def delete_assets(video_path, pic_dir):
    try:
        os.remove(video_path)
        shutil.rmtree(pic_dir)
    except Exception as e:
        print(f'Failed to delete dir {video_path}: {e}')

if __name__ == '__main__':
    for item in data:
        word = item['word']
        video_link = item['video']

        path = download_video(video_link, word)

        if path:
            _, outFile_names = extract_frames(word=word, video_url=path)
            upload_to_s3(folder_path=f'pictures/{word}', bucket_name=f'{aws_bucket_name}/pictures/{word}')
            append_to_json(json_file='data.json', word=word, key=f'pictures/{word}', filenames=outFile_names)

            delete_assets(video_path=path, pic_dir=f'pictures/{word}')
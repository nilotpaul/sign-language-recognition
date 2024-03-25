import cv2
import mediapipe as mp
from pathlib import Path

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def detect_hands(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    # Expand the bounding box by adding/subtracting pixels
    expansion_pixels = 50
    min_x -= expansion_pixels
    min_y -= expansion_pixels
    max_x += expansion_pixels
    max_y += expansion_pixels

    return min_x, min_y, max_x, max_y

def extract_frames(word, video_url):
    out_file_urls = []
    
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print("Error: Unable to open video")
        exit()

    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        min_x, min_y, max_x, max_y = detect_hands(frame)

        if min_x != float('inf') and min_y != float('inf') and max_x != float('-inf') and max_y != float('-inf'):
            min_x = max(0, min_x)
            min_y = max(0, min_y)
            max_x = min(frame.shape[1], max_x)
            max_y = min(frame.shape[0], max_y)

            cropped_frame = frame[min_y:max_y, min_x:max_x]
        
            directory = Path(f'pictures/{word}')

            directory.mkdir(parents=True, exist_ok=True)

            output_dirname = f'pictures/{word}'
            output_filename = f'{output_dirname}/{word}_{frame_count}.jpg'

            cv2.imwrite(output_filename, cropped_frame)
            out_file_urls.append(output_filename)

            frame_count += 1


    cap.release()

    return output_dirname, out_file_urls

import time
import json
from PIL import Image
from rgbmatrix import RGBMatrix
from utils import args, led_matrix_options
import requests
import io
import os
import struct
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

args = args()

matrixOptions = led_matrix_options(args)

matrix = RGBMatrix(options=matrixOptions)

URL = config['server_url']
APP_NAMES = config['app_names']
UPDATE_INTERVAL = config['update_interval']

def get_webp(app):
    payload = {
        "app_name": app,
        "config": config['app_configs'].get(app, {})
    }
    response = requests.post(URL, json=payload)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        raise Exception(f"Failed to fetch WebP for {app}. Status code: {response.status_code}")

def extract_webp_frame_durations(file_or_bytes):
    frame_durations = []
    try:
        if isinstance(file_or_bytes, (str, bytes, os.PathLike)):
            f = open(file_or_bytes, 'rb')
        elif isinstance(file_or_bytes, io.BytesIO):
            f = file_or_bytes
        else:
            raise ValueError("Invalid input type. Expected file path or BytesIO object.")

        f.seek(12)  # Skip file header
        frame_count = 0
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break
            chunk_type, chunk_size = struct.unpack('<4sI', chunk_header)
            if chunk_type == b'ANMF':
                f.seek(12, 1)  # Skip to duration field
                duration = struct.unpack('<H', f.read(2))[0]
                frame_durations.append(duration)
                frame_count += 1
                f.seek(chunk_size - 14, 1)  # Skip rest of ANMF chunk
            else:
                f.seek(chunk_size, 1)  # Skip to next chunk

        if isinstance(file_or_bytes, (str, bytes, os.PathLike)):
            f.close()

        logger.info(f"Total frames found: {frame_count}")
        logger.info(f"Frame durations: {frame_durations}")
    except Exception as e:
        logger.error(f"Error extracting frame durations: {e}")
    return frame_durations

def render_webp(webp):
    logger.info("Starting to render WebP")
    try:
        with Image.open(webp) as img:
            is_animated = hasattr(img, 'n_frames') and img.n_frames > 1
            logger.info(f"Is animated: {is_animated}")
            logger.info(f"Number of frames: {getattr(img, 'n_frames', 1)}")
            start_time = time.time()

            if is_animated:
                webp.seek(0)  # Reset BytesIO position
                frame_durations = extract_webp_frame_durations(webp)
                total_duration = sum(frame_durations) / 1000.0  # Convert to seconds
                logger.info(f"Total animation duration: {total_duration:.2f} seconds")

                animation_count = 0
                while True:
                    animation_count += 1
                    logger.info(f"Starting animation cycle {animation_count}")
                    for frame in range(img.n_frames):
                        frame_start = time.time()
                        img.seek(frame)
                        frame_img = img.convert('RGB')
                        frame_img = frame_img.resize((64, 32))
                        matrix.SetImage(frame_img)
                        frame_duration = frame_durations[frame] / 1000.0  # Convert ms to seconds
                        logger.info(f"Displaying frame {frame + 1} for {frame_duration:.2f} seconds")
                        time.sleep(frame_duration)
                        actual_duration = time.time() - frame_start
                        logger.info(f"Actual frame duration: {actual_duration:.2f} seconds")

                    elapsed_time = time.time() - start_time
                    logger.info(f"Total elapsed time: {elapsed_time:.2f} seconds")
                    if elapsed_time >= max(UPDATE_INTERVAL, total_duration):
                        logger.info("Stopping animation playback")
                        break
            else:
                logger.info("Displaying static image")
                static_img = img.convert('RGB')
                static_img = static_img.resize((64, 32))
                matrix.SetImage(static_img)
                time.sleep(UPDATE_INTERVAL)  # Display for exactly specified interval time
            
            logger.info("Finished displaying image")
    except Exception as e:
        logger.error(f"Error displaying image: {e}")
        import traceback
        traceback.print_exc()

def main():
    while True:
        for app in APP_NAMES:
            try:
                webp = get_webp(app)
                render_webp(webp)
            except Exception as e:
                logger.error(f"Error processing {app}: {e}")
                time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting...")
        matrix.Clear()
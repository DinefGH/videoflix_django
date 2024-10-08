import subprocess
import os
os.environ['PATH'] += os.pathsep + r'C:\usr\ffmpeg-master-latest-win64-gpl\bin'

def get_target_file(source, resolution):
    """
    Generates the target file name with the resolution appended.

    Args:
        source (str): The original video file path.
        resolution (str): The desired resolution (e.g., "360p", "480p").

    Returns:
        str: The file path of the target video with the appended resolution.
    """
    base, ext = os.path.splitext(source)
    return f"{base}_{resolution}{ext}"

def convert_video(source, resolution, size):
    """
    Converts a video to a specified resolution using ffmpeg.

    This function uses ffmpeg to transcode the video to a given size and resolution.
    It saves the new video with the resolution appended to the file name.

    Args:
        source (str): The path to the original video file.
        resolution (str): The target resolution for the conversion (e.g., "360p").
        size (str): The size parameter for ffmpeg (e.g., "640x360" for 360p).

    Returns:
        str: The file path of the converted video if successful, or None if an error occurs.
    """
    print(f"Converting {source} to {resolution}")
    target = get_target_file(source, resolution)
    cmd = f'ffmpeg -i "{source}" -s {size} -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=600)
        if result.returncode == 0:
            print(f"{resolution} conversion completed: {target}")
            return target  # Return the transcoded file path
        else:
            print(f"Error converting {source} to {resolution}: {result.stderr.decode()}")
            return None
    except subprocess.TimeoutExpired:
        print(f"Conversion of {source} to {resolution} timed out")
        return None
    except Exception as e:
        print(f"An error occurred while converting {source} to {resolution}: {e}")
        return None



def convert_360p(source):
    """
    Converts a video to 360p resolution.

    Args:
        source (str): The path to the original video file.

    Returns:
        str: The file path of the converted video if successful, or None if an error occurs.
    """
    return convert_video(source, "360p", "640x360")



def convert_480p(source):
    """
    Converts a video to 480p resolution.

    Args:
        source (str): The path to the original video file.

    Returns:
        str: The file path of the converted video if successful, or None if an error occurs.
    """
    return convert_video(source, "480p", "hd480")



def convert_720p(source):
    """
    Converts a video to 720p resolution.

    Args:
        source (str): The path to the original video file.

    Returns:
        str: The file path of the converted video if successful, or None if an error occurs.
    """
    return convert_video(source, "720p", "hd720")



def convert_1080p(source):
    """
    Converts a video to 1080p resolution.

    Args:
        source (str): The path to the original video file.

    Returns:
        str: The file path of the converted video if successful, or None if an error occurs.
    """
    return convert_video(source, "1080p", "hd1080")
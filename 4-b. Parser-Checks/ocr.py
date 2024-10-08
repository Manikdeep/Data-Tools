import os
import sys
import io
from google.cloud import vision


def get_image_paths(folder):
    re = []
    for filename in os.listdir(folder):
        re.append(os.path.join(folder, filename))
    return re


def detect_text(path, text_file_path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    raw = "".join([text.description for text in texts])
    file_name = os.path.basename(path).split(".")[0]
    print(text_file_path+file_name+'.txt')
    with open(text_file_path + '/' + file_name + '.txt', 'w', encoding='utf-8') as f:
        f.write(raw)
    return raw


if __name__ == '__main__':
    # Google Cloud Credentials
    folder_images_path = sys.argv[1]
    folder_output_path = sys.argv[2]
    img_paths = get_image_paths(folder_images_path)
    dirs = folder_images_path.split("/")

    get_root_dir_img = "/".join([dirs[i] for i in range(0, len(dirs)-1)])

    if not os.path.exists(folder_output_path):
        os.makedirs(folder_output_path)

    for img_path in img_paths:
        print("Processing image: ", img_path)
        print("Output path: ", folder_output_path)
        detect_text(img_path, folder_output_path)

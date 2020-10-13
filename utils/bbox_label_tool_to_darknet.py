import os
import re
import csv
import shutil
import pandas as pd
from pathlib import Path


# expected dir structure
# darknet
#  └ data
#     └ youtubes
#        └ _images
#           └ ...
#           └ 013
#              └ out001.jpg
#              └ out002.jpg
#              └ ...
#           └ ...
#        └ _labels
#           └ ...
#           └ 013
#              └ out001.txt
#              └ out002.txt
#              └ ...
#           └ ...
# put your new images and their labels in _images, _labels


DATA_DIR = 'data/youtubes'
os.chdir(DATA_DIR)  # You need to chdir to data dir
print('Changed to:', os.getcwd())

regex = re.compile(r'out(?P<num>\d+)')
extract = lambda path: regex.search(str(path)).group('num')

image_paths = sorted(list(Path('_images').rglob('*.jpg')))
label_paths = sorted(list(Path('_labels').rglob('*.txt')))

# label 파일에 뭐가 써있든 간에 일단 이미지마다 한 개의 label 파일이 있어야 함.
for image, label in zip(image_paths, label_paths):
    try:
        image_num = extract(image)
        label_num = extract(label)
    except Exception as e:
        print('Unexpected exception! Please check file name formats are like "_images\\007\\out0013.jpg"')
        print('\t', e)
    assert image_num == label_num, f'Paths: image_num != label_num\nPaths:\n\tImage: {image}\n\tLabel: {label}'

print('Assertion Done!\n')

# BBox 툴로 달아놓은 label들을 darknet형 label로 바꿔줌
for image_path, label_path in zip(image_paths, label_paths):  # for image
    # print(image_path, label_path) 
    
    with label_path.open('r') as f:
        obj_count = int(f.readline())
    if obj_count == 0: continue  # Ignore images with no object.

    new_label_path = Path(*label_path.parts[1:])
    new_image_path = Path(*image_path.parts[1:])
    if not new_label_path.parent.exists():
        os.mkdir(new_label_path.parent)
    shutil.copy(image_path, new_image_path)

    with new_label_path.open('w', newline='') as f:
        writer = csv.writer(f, delimiter=' ')
        data = pd.read_csv(label_path, sep=' ', skiprows=1, header=None)
        for i, row in data.iterrows():  # for obj
            label = row.tolist()[:4]  # [lefttop_x, lefttop_y, rightbottom_x, rightbottom_y]
            width = (label[2] - label[0]) / 1920
            height = (label[3] - label[1]) / 1080
            center = [
                (label[0] + label[2]) / 2 / 1920,
                (label[1] + label[3]) / 2 / 1080,
            ]
            label = [4, *center, width, height]
            writer.writerow(label)

import cv2
import glob
import csv
import os
import random
import pandas as pd
from pathlib import Path


DATA_DIR = 'data/youtubes'
os.chdir(DATA_DIR)  # You need to chdir to data dir
print('Changed to:', os.getcwd())

if cropped_paths := Path('.').rglob('*_c*'):
    print('Removing previously cropped images and their labels ...')
    for path in cropped_paths:
        os.remove(path)
    print('Remove done!\n')

# ignore _images and _labels
label_paths = [path for path in Path('.').rglob('*.txt') if '_' not in str(path)]
image_paths = [path.with_suffix('.jpg') for path in label_paths]

total = len(image_paths) 
sizes = [(500, 500), (416, 416), (208, 208), (160, 160)]

minmax = lambda a, b: (min(a, b), max(a, b)) if a != b else (a, a+1)  # only for randrange
clip = lambda r: min(1, max(0, r))  # clip(r, -1, 1)


def fit_the_box(cropx: int, cropy: int, sx: int, sy: int):  # move the cropping box to fit in the image
    left, right, top, bottom = (
        cropx - sx / 2,
        cropx + sx / 2,
        cropy - sy / 2,
        cropy + sy / 2
    )
    if left < 0:
        cropx = sx / 2
    elif right >= 1920:
        cropx = 1920 - sx / 2
    if top < 0:
        cropy = sy / 2
    elif bottom >= 1080:
        cropy = 1080 - sy / 2
    return cropx, cropy


def fit_the_box2(cx: float, cy: float, bx: float, by: float):  # resize the bbox of the object to fit in the cropping box
    left, right, top, bottom = (
        cx - bx / 2,
        cx + bx / 2,
        cy - by / 2,
        cy + by / 2
    )
    if left < 0: left = 0
    elif right >= 1: right = 1
    cx = (left + right) / 2
    bx = right - left

    if top < 0: top = 0
    elif bottom >= 1: bottom = 1
    cy = (top + bottom) / 2
    by = bottom - top

    return cx, cy, bx, by


def work(id, start, end):
    for i, (image_path, label_path) in enumerate(zip(image_paths[start:end], label_paths[start:end])):  # for each image
        print(f'Thread {id:02d} start: {start}, end: {end}, # {end-start}')
        
        n = 0
        with label_path.open() as label_file:
            # [4, cx, cy, bx, by]; [1:5]: floats
            labels = [list(map(float, obj)) for obj in csv.reader(label_file, delimiter=' ')]

        for j, label in enumerate(labels):  # for each object
            cx, cy, bx, by = [
                int(label[1]*1920), int(label[2]*1080),  # center
                int(label[3]*1920), int(label[4]*1080),  # bbox
            ]
            for _sx, _sy in sizes:  # base cropping sizes
                if bx > _sx or by > _sy: continue  # if obj is larger than the base cropping box
                cropped_with_this_size = 0  # how many crops; NOT the number of cropped images but just count
                r = (_sx*_sy) / (bx*by)  # cropping area / obj bbox area
                while cropped_with_this_size < min(15, round(r)):
                    sx, sy = _sx, _sy  # copy base cropping sizes
                    if random.random() < .5:  # in 50%
                        weight = random.random() / 2 + 1  # weight in [1., 1.5)
                        # multiply width or height by the weight with the probability of 50:50
                        x = random.random() < .5
                        if x: sx *= weight
                        else: sy *= weight
                    if bx > sx or by > sy:  # if obj is larger than the cropping box
                        cropped_with_this_size += 1
                        continue
                    dx, dy = sx / 2 - bx / 2, sy / 2 - by / 2  # cropping box center - obj bbox center
                    cropx = random.randrange(int(cx-.8*dx), int(cx+.8*dx))  # cropping box center
                    cropy = random.randrange(int(cy-.8*dy), int(cy+.8*dy))
                    cropx, cropy = fit_the_box(cropx, cropy, sx, sy)  # fit the cropping box in the image
                    
                    image = cv2.imread(str(image_path))
                    left, right = int(cropx-sx/2), int(cropx+sx/2)
                    top, bottom = int(cropy-sy/2), int(cropy+sy/2)
                    cropped = image[top:bottom, left:right]
                    
                    name = f'_c{n:02d}_o{j:02d}_{sx:.0f}x{sy:.0f}'
                    cropped_image_path = image_path.with_name(image_path.name+name+'.jpg')
                    cv2.imwrite(str(cropped_image_path), cropped)
                    with cropped_image_path.with_name(label_path.name+name+'.txt').open('w', newline='') as f:
                        writer = csv.writer(f, delimiter=' ')
                        writer.writerow([4, (cx-left)/sx, (cy-top)/sy, bx/sx, by/sy])
                        for k, (_, _cx, _cy, _bx, _by) in enumerate(labels):
                            _cx, _cy, _bx, _by = _cx * 1920, _cy * 1080, _bx * 1920, _by * 1080
                            if k != j and left < _cx < right and top < _cy < bottom:
                                writer.writerow([4, *fit_the_box2((_cx-left)/sx, (_cy-top)/sy, _bx/sx, _by/sy)])
                    n += 1
                    cropped_with_this_size += 1


import psutil, threading
perthread = -int(-total//psutil.cpu_count())  # ceil(total/cpu_cores)
threads = [threading.Thread(target=work, args=(id, id*perthread, min(total, (id+1)*perthread))) for id in range(round(total/perthread+.5))]
for thread in threads: thread.start()
for thread in threads: thread.join()

import cv2
import glob
import csv
import os
import random
import threading


DATA_DIR = 'data/simulations'
os.chdir(DATA_DIR)  # You need to chdir to data dir
print(os.getcwd())

import time
t0 = time.time()
image_paths = list(sorted(
    # exclude cropped images already
    map(lambda imagepath: imagepath[:-4],  # drop out the expansion .jpg
        set(glob.glob(os.path.join('images', '*.jpg')))
        - set(glob.glob(os.path.join('images', '*x*.jpg')))
    )
))
label_paths = [os.path.join('labels', image_path.split(os.sep)[-1]) for image_path in image_paths]

assert len(image_paths) == len(label_paths), '# of images and labels are different!'

total = len(image_paths) 
sizes = [(500, 500), (416, 416), (208, 208), (160, 160)]
ix, iy = 1920//2, 1080//2  # the position of the intruder (fixed while simulated)

minmax = lambda a, b: (min(a, b), max(a, b)) if a != b else (a, a+1)
clip = lambda r: min(1, max(0, r))  # clip(r, -1, 1)


def work(id, start, end):
    subpaths = zip(image_paths[start:end], label_paths[start:end])
    print(f'Thread {id:02d} start: {start}, end: {end}, # {end-start}')
    for i, (image_path, label_path) in enumerate(subpaths):
        n = 0  # just to count
        with open(label_path+'.txt', 'r') as f:
            # data: [label, px, py, w, h]  px, .., h are in [0, 1)
            data = list(map(float, list(csv.reader(f, delimiter=' '))[0]))
            bx, by = int(data[-2]*1920), int(data[-1]*1080)  # float to pixel
        for _sx, _sy in sizes:
            r = _sx/bx*_sy/by  # cropping area / total area
            nn = 0
            while nn < min(15, round(max(r, 1/r))):  # cropping smaller area, you need more images, but at least 15
                sx, sy = _sx, _sy
                if random.random() < .5:  # make cropping sizes stochastic, but not that different from the nominal sizes
                    rho = random.random() / 2. + 1.  # rho in [1., 1.5)
                    if random.random() < .5:
                        sx *= rho
                    else:
                        sy *= rho
                # select the area within [.1w, .9w) X [.1h, .9h)
                cx = random.randrange(*minmax(ix-(sx-bx*.8)//2, ix+(sx-bx*.8)//2))
                cy = random.randrange(*minmax(iy-(sy-by*.8)//2, iy+(sy-by*.8)//2))
                image = cv2.imread(image_path+'.jpg')
                cropped = image[int(cy-sy/2):int(cy+sy/2), int(cx-sx/2):int(cx+sx/2)]
                crop_image_path = image_path+f'_c{n:02d}_{sx:.0f}x{sy:.0f}.jpg'  # c as cropped
                crop_label_path = label_path+f'_c{n:02d}_{sx:.0f}x{sy:.0f}.txt'
                
                # Cropped too small => crop again
                if cropped.shape[0] < 100 or cropped.shape[1] < 100:
                    continue
                
                cv2.imwrite(crop_image_path, cropped)
                with open(crop_label_path, 'w') as f:
                    data = [
                        4,  # aeroplane
                        (sx/2+ix-cx)/sx, (sy/2+iy-cy)/sy,  
                        clip(bx/sx), clip(by/sy)]  # pixel to float
                    csv.writer(f, delimiter=' ').writerow(data)
                n += 1
                nn += 1
                # processed += 1
                
        if i % 3 == 0:
            # t = time.time() - t0
            # print(f'{i}\t{(i+1)/2473:7.3%} done. Processed {processed} images. Spent {int(t/60):2d}m {int(t%60):02d}s. {t/processed*1000:.0f} ms/image.')
            print(f'Thread {id:3d}\t{i:2d}\t{(i+1)/(end-start):7.3%} done.')
    print(f'Thread {id:2d} all done!')

import psutil
perthread = -int(-total//psutil.cpu_count())  # ceil(total/cpu_cores)
threads = [threading.Thread(target=work, args=(id, id*perthread, min(total, (id+1)*perthread))) for id in range(round(total/perthread+.5))]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

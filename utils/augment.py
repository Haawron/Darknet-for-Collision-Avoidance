import cv2
import glob
import csv
import os
import random
import threading

os.chdir('data/DBPAS_train3')
print(os.getcwd())

import time
t0 = time.time()
paths = list(sorted(
    map(lambda image: image[:-4],
        set(glob.glob('*.jpg'))-set(glob.glob('*x*.jpg')))
))
sizes = [(500, 500), (416, 416), (208, 208), (160, 160)]
ix, iy = 1920//2, 1080//2  # intruder의 위치

minmax = lambda a, b: (min(a, b), max(a, b)) if a != b else (a, a+1)
clip = lambda r: min(1, max(0, r)) 

# processed = 0
def work(id, start, end):
    subpaths = paths[start:end]
    print(f'Thread {id:02d} start: {start}, end: {end}, # {len(subpaths)}')
    for i, path in enumerate(subpaths):
        n = 0
        with open(path+'.txt', 'r') as f:
            data = list(map(float, list(csv.reader(f, delimiter=' '))[0]))
            bx, by = int(data[-2]*1920), int(data[-1]*1080) 
        for _sx, _sy in sizes:
            r = _sx/bx*_sy/by
            nn = 0  # for로 돌리면 continue 썼을 때 그 loop가 무시됨
            while nn < min(15, round(max(r, 1/r))):
                sx, sy = _sx, _sy
                if random.random() < .5:
                    rho = random.random() / 2. + 1.  # rho in [1., 1.5)
                    if random.random() < .5:
                        sx *= rho
                    else:
                        sy *= rho
                cx = random.randrange(*minmax(ix-(sx-bx*.8)//2, ix+(sx-bx*.8)//2))
                cy = random.randrange(*minmax(iy-(sy-by*.8)//2, iy+(sy-by*.8)//2))
                image = cv2.imread(path+'.jpg')
                cropped = image[int(cy-sy/2):int(cy+sy/2), int(cx-sx/2):int(cx+sx/2)]
                image_path = path+f'_c{n:02d}_{sx:.0f}x{sy:.0f}'  # c는 cropped 구분용
                
                # cx랑 sx/2 크기 비교해서 분기해야 되는데 귀찮아서 그냥 다시 만들게 함
                if cropped.shape[0] < 100 or cropped.shape[1] < 100:
                    continue
                
                cv2.imwrite(image_path+'.jpg', cropped)
                with open(image_path+'.txt', 'w') as f:
                    data = [
                        4,
                        (sx/2+ix-cx)/sx, (sy/2+iy-cy)/sy,
                        clip(bx/sx), clip(by/sy)]
                    csv.writer(f, delimiter=' ').writerow(data)
                n += 1
                nn += 1
                # processed += 1
                
        if i % 3 == 0:
            # t = time.time() - t0
            # print(f'{i}\t{(i+1)/2473:7.3%} done. Processed {processed} images. Spent {int(t/60):2d}m {int(t%60):02d}s. {t/processed*1000:.0f} ms/image.')
            print(f'Thread {id:3d}\t{i:2d}\t{(i+1)/len(subpaths):7.3%} done.')
    print(f'Thread {id:2d} all done!')

perthread = 20
threads = [threading.Thread(target=work, args=(id, id*perthread, min(2473, (id+1)*perthread))) for id in range(round(2473/perthread+.5))]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

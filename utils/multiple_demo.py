import glob, os


paths = glob.glob('data/airshow/cropped/*')
for path in paths:
    command = [
        './darknet',
        'detector',
        'demo',
        'data/obj.data',
        'cfg/yolov4_pre01_416x416.cfg',
        'backup/yolov4_pre01_416x416_best.weights',
        path,
        '-dont_show',
        '-out_filename',
        'results/cropped_'+path.split('/')[-1]
    ]
    command = ' '.join(command)
    os.system(command)

import glob, os


for path in glob.glob(os.path.join('data', 'simulations', '*_c*')):
    os.remove(path)
    
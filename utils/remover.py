import glob, os


for path in glob.glob('data/simulations/images/*_c*') + glob.glob('data/simulations/labels/*_c*'):
    os.remove(path)
    
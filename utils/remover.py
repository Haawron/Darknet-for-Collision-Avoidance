import glob, os


for path in glob.glob('data/DBPAS_train3/*_c*'):
    os.remove(path)
    
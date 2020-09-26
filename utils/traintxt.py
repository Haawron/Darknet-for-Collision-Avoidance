import glob, random

with open('data/train.txt', 'w') as train, open('data/test.txt', 'w') as test:
    data = set(glob.glob('data/DBPAS_train3/*.jpg'))
    valid = set(random.sample(data, round(len(data)*.3)))
    data -= valid
    train.writelines('\n'.join(data))
    test.writelines('\n'.join(valid))

print('done!')

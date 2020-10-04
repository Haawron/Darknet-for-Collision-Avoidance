from pathlib import Path
import random, os

with open('data/train.txt', 'w') as train_file, open('data/valid.txt', 'w') as valid_file:
    # ignore _images and _labels
    image_paths = [path for path in Path('.').rglob('*.jpg') if '_' not in str(path)]
    
    train = set(map(str, image_paths))
    valid = set(random.sample(train, round(len(train)*.3)))
    train -= valid
    train_file.writelines('\n'.join(train))
    valid_file.writelines('\n'.join(valid))

print('done!')

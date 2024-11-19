import os
import shutil
from utils import model_util as mu
from pathlib import Path


def get_all_image_urls(): 
    ''' get all linked image filenames from the database 
    that are in the public domain and have permission to be used
    '''
    urls = mu.get_all_image_urls(flagged = False, exclude_persons = False, 
        exclude_thumbnails = False, only_with_permission = True,
        only_images_and_monuments = False, not_explicit = False)
    return urls

def copy_images_to_folder(urls, folder = 'rdr_hoh/images/'):
    ''' copy images from the media to the share folder
    '''
    os.makedirs(folder, exist_ok=True)
    not_found = []
    for url in urls:
        source = '/'.join(url.split('/')[1:])
        url = '/'.join(url.split('/')[2:])
        path = Path(url)
        filename = path.name
        destination = folder + filename
        print('copying:', source, '->', destination)
        try: shutil.copyfile(source, destination)
        except FileNotFoundError:
            print('file not found:', source)
            not_found.append(source) 
    print('not found:', len(not_found))
    print('copied:', len(urls) - len(not_found))
    return not_found




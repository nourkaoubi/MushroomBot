import os
from bs4 import BeautifulSoup
import requests
from icrawler.builtin import GoogleImageCrawler
from datetime import datetime
from PIL import Image

start_time = datetime.now()

mushrooms = {
    'edible': [],
    'inedible': [],
    'poisonous': [],
    'hallucinogenic': []
}

def parse_mushroom_names(style, url):
    """
    :param style: type of mushrooms on the website
    :param url: URL of the website
    The function receives the mushroom type and the URL of the site to parse the data.
    After execution, a folder is created with the mushroom photos.
    """
    r = requests.get(url)
    html = BeautifulSoup(r.content, 'html.parser')
    for el in html.select('.mush-block > a'):
        mushrooms[style].append(el.text)
    mushrooms[style] = list(set(mushrooms[style]))


parse_mushroom_names('edible', 'http://ya-gribnik.ru/syedobnye-griby.php')
parse_mushroom_names('inedible', 'http://ya-gribnik.ru/nesyedobnye-griby.php')
parse_mushroom_names('poisonous', 'http://ya-gribnik.ru/yadovitye-griby.php')
parse_mushroom_names('hallucinogenic', 'http://ya-gribnik.ru/info/gallucinogennye-griby.php')
print('The name of the mushrooms is ready')

isdir = './photos' 
dataset = {'Train': 16, 'Valid': 4, 'Test': 2}  

number_file = 1  
for sample, count in dataset.items():
    if not os.path.exists(f'{isdir}\\{sample}'):
        os.mkdir(f'{isdir}\\{sample}')
    for key in mushrooms.keys():
        for name in mushrooms[key]:
            if not os.path.exists(f'{isdir}\\{sample}\\{key}'):
                os.mkdir(f'{isdir}\\{sample}\\{key}')
            google_crawler = GoogleImageCrawler(
                storage={
                    'root_dir': f'{isdir}\\{sample}\\{key}'
                })

            google_crawler.crawl(keyword=f'Mushroom {name} photo',
                                 max_num=count,
                                 filters=dict(size='medium' if sample == 'Train' else 'large')
                                 )

            for name_file in os.listdir(f'{isdir}\\{sample}\\{key}\\'):
                if name_file[0] != 'M':
                    os.rename(f'{isdir}\\{sample}\\{key}\\{name_file}',
                              f'{isdir}\\{sample}\\{key}\\M{str(number_file).rjust(6, "0")}'
                              f'.{name_file[len(name_file) - 3:]}')
                    number_file += 1
        number_file = 1

    key = 'No'
    if not os.path.exists(f'{isdir}\\{sample}\\{key}'):
        os.mkdir(f'{isdir}\\{sample}\\{key}')
    no_mushrooms = ['person', 'table', 'dish']
    for name_photo in no_mushrooms:
        google_crawler = GoogleImageCrawler(
            storage={
                'root_dir': f'{isdir}\\{sample}\\{key}'
            })
        google_crawler.crawl(keyword=f'Photo {name_photo}',
                             max_num=count,
                             filters=dict(size='medium' if sample == 'Train' else 'large')
                             )

        for name_file in os.listdir(f'{isdir}\\{sample}\\{key}\\'):
            if name_file[0] != 'M':
                os.rename(f'{isdir}\\{sample}\\{key}\\{name_file}',
                          f'{isdir}\\{sample}\\{key}\\M{str(number_file).rjust(6, "0")}'
                          f'.{name_file[len(name_file) - 3:]}')
                number_file += 1
    number_file = 1

key = 'No'
for sample, _ in dataset.items():
    for key in os.listdir(f'{isdir}\\{sample}'):
        for name_file in os.listdir(f'{isdir}\\{sample}\\{key}'):
            img = Image.open(f'{isdir}\\{sample}\\{key}\\{name_file}')
            new_image = img.resize((224, 224))
            new_image = new_image.convert('RGB')
            new_image.save(f'{isdir}\\{sample}\\{key}\\{name_file}')
        print(f'The {sample}\\{key} folder has been processed')

print(f'Program execution time: {datetime.now() - start_time}')

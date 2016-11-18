import click
from random import randrange, gauss
from lib.builder import Builder
from lib.resource_store import ResourceStore
from lib.image_fetcher import GoogleImageStore
import tempfile
import webbrowser
import os
import yaml
import shutil
import glob
import subprocess
import re
from lxml import etree
from PIL import Image
import json


@click.group()
def cmd():
    pass


def make_html(resource_store):
    graph_images = resource_store.pop_image('graph', randrange(3))
    handwriting_images = resource_store.pop_image('handwriting', randrange(3))
    mathematical_images = resource_store.pop_image('mathematical', randrange(3))
    random_images = resource_store.pop_image('random-image', randrange(3))
    builder = Builder()
    html = builder.build([resource_store.pop_text(int(gauss(500, 100))) for _ in range(randrange(1, 5))], random_images, graph_images, mathematical_images,
                         handwriting_images)
    return html


@cmd.command()
@click.argument('image_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def generate(image_dir):
    _, filename = tempfile.mkstemp(suffix='.html')
    resource_store = ResourceStore(image_dir)
    html = make_html(resource_store)
    with open(filename, 'w') as fp:
        fp.write(html)
    webbrowser.open('file://{}'.format(filename))


@cmd.command()
@click.argument('image_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--dist', '-d', default='dist', type=click.STRING)
@click.option('--num', '-n', default=1000, type=click.INT)
def make_documents(image_dir, dist, num):
    if os.path.exists(dist):
        shutil.rmtree(dist)
    os.mkdir(dist)
    store = ResourceStore(image_dir)

    for idx in range(1, num + 1):
        filename = os.path.join(dist, '{:05}.html'.format(idx))
        with open(filename, 'w') as fp:
            fp.write(make_html(store))


@cmd.command()
@click.argument('documents', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--dist', '-d', default='json', )
def make_json(documents, dist):
    if os.path.exists(dist):
        shutil.rmtree(dist)
    os.mkdir(dist)
    for filename in glob.glob1(documents, '*.html'):
        name, _ = os.path.splitext(filename)
        abs_filename = os.path.abspath(os.path.join(documents, filename))
        data_dir = os.path.join(dist, name)
        os.mkdir(data_dir)
        subprocess.call(
            ['phantomjs', 'page.js', 'file://{}'.format(abs_filename), os.path.join(data_dir, 'data')]
        )


@cmd.command()
@click.argument('data_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('devkit_path', type=click.STRING)
@click.argument('year', type=click.STRING)
def make_pascal_voc(data_dir, devkit_path, year):
    if os.path.exists(devkit_path):
        shutil.rmtree(devkit_path)
    voc_path = os.path.join(devkit_path, 'VOC{}'.format(year))
    annotations = os.path.join(voc_path, 'Annotations')
    image_sets = os.path.join(voc_path, 'ImageSets', 'Main')
    jpeg_images = os.path.join(voc_path, 'JPEGImages')
    for path in (annotations, image_sets, jpeg_images):
        os.makedirs(path)

    with open(os.path.join(image_sets, 'trainval.txt'), 'w') as trainval:
        for dir_name in glob.glob1(data_dir, '*'):
            image_path = os.path.join(data_dir, dir_name, 'data.jpg')
            shutil.copyfile(image_path, os.path.join(jpeg_images, '{}.jpg'.format(dir_name)))
            root = etree.Element('annotation')
            size = etree.Element('size')

            image = Image.open(image_path)
            w, h = image.size
            width = etree.Element('width')
            height = etree.Element('height')
            width.text = str(w)
            height.text = str(h)
            size.append(width)
            size.append(height)
            root.append(size)

            json_path = os.path.join(data_dir, dir_name, 'data.json')
            data = json.load(open(json_path))
            count = 0
            for obj_name, rects in data.items():
                for rect in rects:
                    obj = etree.Element('object')

                    name = etree.Element('name')
                    name.text = obj_name
                    obj.append(name)

                    difficult = etree.Element('difficult')
                    difficult.text = '0'
                    obj.append(difficult)

                    left = str(round(rect['left']))
                    top = str(round(rect['top']))
                    width = str(round(rect['width']))
                    height = str(round(rect['height']))
                    bndbox = etree.Element('bndbox')
                    xmin = etree.Element('xmin')
                    xmin.text = left
                    bndbox.append(xmin)
                    ymin = etree.Element('ymin')
                    ymin.text = top
                    bndbox.append(ymin)
                    xmax = etree.Element('xmax')
                    xmax.text = left + width
                    bndbox.append(xmax)
                    ymax = etree.Element('ymax')
                    ymax.text = top + height
                    bndbox.append(ymax)
                    obj.append(bndbox)
                    root.append(obj)
                    count += 1
            print(count, json_path)
            with open(os.path.join(annotations, '{}.xml'.format(dir_name)), 'w') as fp:
                fp.write(etree.tostring(root).decode('utf-8'))
            trainval.write('{}\n'.format(dir_name))


@cmd.command()
@click.option('--dist-dir', default='images', type=click.STRING)
def fetch_image_list(dist_dir):
    images = yaml.load(open('fetch_image.yaml'))
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.mkdir(dist_dir)
    for k, v in images.items():
        category_path = os.path.join(dist_dir, '{}.txt'.format(k))
        for keyword in v:
            print(keyword)
            store = GoogleImageStore(keyword)
            store.collect()
            with open(category_path, 'a') as fp:
                fp.write('\n'.join(store.items))


@cmd.command()
@click.argument('images', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('dist_images_dir', type=click.STRING)
def fetch_image(images, dist_images_dir):
    if os.path.exists(dist_images_dir):
        shutil.rmtree(dist_images_dir)
    os.mkdir(dist_images_dir)
    for filename in glob.glob1(images, '*.txt'):
        image_path = os.path.join(images, filename)
        category, _ = os.path.splitext(filename)
        dist_category_path = os.path.join(dist_images_dir, category)
        os.mkdir(dist_category_path)
        with open(image_path) as fp:
            for idx, row in enumerate(fp):
                row = row.strip()
                _, ext = os.path.splitext(row)
                words1 = list(filter(lambda w: len(w) > 0, re.split(r':|&|/|%|\?', ext)))
                if words1:
                    ext = words1[0]
                else:
                    ext = '.png'
                subprocess.call(
                    ['wget', row, '-O', os.path.join(dist_category_path, '{}{}'.format(idx, ext))]
                )


if __name__ == '__main__':
    cmd()

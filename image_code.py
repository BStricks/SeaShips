# -*- coding: utf-8 -*-
"""image_code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EkL_lqUYaxscwIjwuQxYc2r7SNcTIkIj
"""

import os
from google.colab import drive
drive.mount('/content/drive/')
os.chdir("drive/My Drive/Colab Notebooks/evello")

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms, utils
from torchvision.transforms import *
from PIL import Image
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import pathlib
import xml.etree.ElementTree as ET
import os

def prediction(): 
  #JPEG -> TENSOR
  dataset = ShapeDataset('./data/SeaShips')
  #Load pre-trained model
  model_new = torch.load('./data/SeaShips/entire_model.pth')
  #Load XML data
  XML_list = get_xml()
  #get model prediction and XML data in JSON
  my_list = JSON_output(dataset, model_new)
  return my_list

def get_device():
    if torch.cuda.is_available():
      return torch.device('cuda')
    else:
      return torch.device('cpu')

def get_xml():
  path = "data/SeaShips/XML"
  XML_list = []
  for filename in os.listdir(path):
    if not filename.endswith('.xml'): continue
    fullname = os.path.join(path, filename)
    XML_list.append(fullname)
  return XML_list

def JSON_output(dataset_tensor,model):
  cats = {0:'bulk cargo carrier',1:'container ship',2:'fishing boat',3:'general cargo ship',4:'ore carrier',5:'passenger ship'}
  json_list = []
  for i, value in enumerate(dataset_tensor):

    img, target, xml_path  = value
    xml_split = xml_path.split(".jpg")
    xml_path = "data/SeaShips/XML/v2-"+xml_split[0]+".xml"
    tree = ET.parse(xml_path)
    root = tree.getroot()
    TIMESTAMP = root.find('./TIMESTAMP').text
    LATITUDE = root.find('./LAT').text
    LONGITUDE = root.find('./LON').text
    stype = root.find('./object/name').text

    model.eval()
    with torch.no_grad():
        prediction = model([img.to(device)])
    try:
      labels = prediction[0]['labels'][0].item()
      label = cats.get(labels)
      scores = prediction[0]['scores'][0].item()
      score = "{:.2f}%".format(scores*100)
      x_min =  "{:.0f}".format(prediction[0]['boxes'][0][0].item())
      y_min =  "{:.0f}".format(prediction[0]['boxes'][0][1].item())
      x_max =  "{:.0f}".format(prediction[0]['boxes'][0][2].item())
      y_max =  "{:.0f}".format(prediction[0]['boxes'][0][3].item())
      json_dict = {'score':score,'x_min':x_min,'y_min':y_min,'x_max':x_max,'y_max':y_max,'label':label,'timestamp':TIMESTAMP,'latitude':LATITUDE,'longitude':LONGITUDE}

    except:
      json_dict = {'score':'NONE','x_min':'NONE','y_min':'NONE','x_max':'NONE','y_max':'NONE','label':'NONE','timestamp':TIMESTAMP,'location':LATITUDE,'longitude':LONGITUDE}
    
    json_list.append(json_dict)

  return json_list

class ShapeDataset(Dataset):

    def __init__(self, root_dir, annot_dir='XML', image_dir='images',
                 transform=transforms.Compose([ToTensor()])):
        self.annot_dir = f'{root_dir}/{annot_dir}'
        self.image_dir = f'{root_dir}/{image_dir}'
        self.transform = transform
        self.__init()

    def num_classes(self):
        return len(self.class2index)

    def __get_annot_files(self):
        def clean_up(path):
            import os
            from shutil import rmtree

            ipynb_checkpoints = f'{path}/.ipynb_checkpoints'
            if os.path.exists(ipynb_checkpoints):
                rmtree(ipynb_checkpoints)
        clean_up(self.annot_dir)
        return [f for f in pathlib.Path(self.annot_dir).glob('**/*.xml')]

    def __get_classes(self):
        xml_files = self.__get_annot_files()
        names = set()
        for xml_file in xml_files:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for item in root.findall('./object'):
                name = item.find('name').text
                if name not in names:
                    names.add(name)
        names = {name: i for i, name in enumerate(sorted(list(names)))}
        return names

    def __get_image_annotations(self, annot_path):
        root = ET.parse(annot_path).getroot()
        d = {}

        # file names
        d['annot_path'] = annot_path
        d['file_path'] = root.find('filename').text
        d['image_path'] = f"{self.image_dir}/{root.find('filename').text}"

        # size
        size = root.find('./size')
        d['size'] = {
                'width': int(size.find('width').text),
                'height': int(size.find('height').text),
                'depth': int(size.find('depth').text)
            }

        # objects
        d['objects'] = []
        for obj in root.findall('./object'):
            o = {}
            o['name'] = obj.find('name').text

            b = obj.find('bndbox')
            o['xmin'] = int(b.find('xmin').text)
            o['ymin'] = int(b.find('ymin').text)
            o['xmax'] = int(b.find('xmax').text)
            o['ymax'] = int(b.find('ymax').text)

            d['objects'].append(o)
        return d

    def __init(self):
        self.class2index = self.__get_classes()

        annot_paths = [f'{str(f)}' for f in self.__get_annot_files()]
        self.annotations = [self.__get_image_annotations(p) for p in annot_paths]

    def __len__(self):
              return len(self.annotations)

    def __getitem__(self, idx):
        def get_boxes(annot):
            boxes = [[obj[f] for f in ['xmin', 'ymin', 'xmax', 'ymax']] for obj in annot['objects']]
            return torch.as_tensor(boxes, dtype=torch.float)

        def get_labels(annot):
            labels = [self.class2index[obj['name']] for obj in annot['objects']]
            return torch.as_tensor(labels, dtype=torch.int64)

        def get_areas(annot):
            areas = [(obj['xmax'] - obj['xmin']) * (obj['ymax'] - obj['ymin']) for obj in annot['objects']]
            return torch.as_tensor(areas, dtype=torch.int64)
        
        def get_iscrowds(annot):
            return torch.zeros((len(annot['objects']),), dtype=torch.uint8)

        annot = self.annotations[idx]

        image_path = annot['image_path']
        image = Image.open(image_path)
        if self.transform:
            image = self.transform(image)

        target = {}
        target['boxes'] = get_boxes(annot)
        target['labels'] = get_labels(annot)
        target['image_id'] = torch.as_tensor([idx], dtype=torch.int64)
        target['area'] = get_areas(annot)
        target['iscrowd'] = get_iscrowds(annot)

        return image, target, annot['file_path'] 

#run the below lines of code to get JSON output from image and XML files
#device = get_device()
#results = prediction()

results = prediction()

print(results[0])
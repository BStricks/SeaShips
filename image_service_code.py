# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms
from torchvision.transforms import ToTensor
from PIL import Image
import xml.etree.ElementTree as ET


def prediction(image, XML): 
  #JPEG -> TENSOR
  device = torch.device('cpu')
  tensor = image_to_tensor(image)
  #Load pre-trained model
  model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
  model.roi_heads.box_predictor = FastRCNNPredictor(1024,6)
  model.load_state_dict(torch.load('./dev_data/test_model.pth'))
  model = model.to(device)                      
  #get model prediction and XML data in JSON
  my_list = JSON_output(tensor, XML, model)
  return my_list


def JSON_output(tensor,XML,model):
  cats = {0:'bulk cargo carrier',1:'container ship',2:'fishing boat',3:'general cargo ship',4:'ore carrier',5:'passenger ship'}
  json_list = []
  
  for i in len(tensor):

    tree = ET.parse(XML)
    root = tree.getroot()
    TIMESTAMP = root.find('./TIMESTAMP').text
    LATITUDE = root.find('./LAT').text
    LONGITUDE = root.find('./LON').text

    model.eval()
    with torch.no_grad():
        prediction = model([tensor.to(device)])
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


def image_to_tensor(image_path):
    image = Image.open(image_path)    
    transform = transforms.Compose([ToTensor()])
    tensor = transform(image)
    return tensor

#run the below lines of code to get JSON output from image and XML files
#device = get_device()
#results = prediction()




# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:36:47 2020

@author: benjamin.strickson
"""

from pomegranate import *
from shapely.geometry import box


def generateEvent(ais, image=None, text=None):
  #read in jsons and get characteristics
  if ais['PORT_NAME'] == 'SAN DIEGO':

    if -120.3442 <= ais['LAT'] <= -117.6526 and 32.3707 <= ais['LON'] <= 33.2933 :
      position = 'A'
    else:
      position = 'N'
    
    if 0 <= ais['SPEED'] <= 0.8 :
      speed = 'A'
    else:
      speed = 'N'

    if 290 <= ais['HEADING'] <= 350 :
      heading = 'A'
    else:
      heading = 'N'

  elif ais['PORT_NAME'] == 'NORFOLK':

    if -75.7837 <= ais['LAT'] <= -75.0256 and 35.7457 <= ais['LON'] <= 36.7917 :
      position = 'A'
    else:
      position = 'N'
    
    if 0 <= ais['SPEED'] <= 0.8 :
      speed = 'A'
    else:
      speed = 'N'

    if 300 <= ais['HEADING'] <= 340 :
      heading = 'A'
    else:
      heading = 'N'
  
  boat_overlap = 'N'
  if image:
    if len(image['ships']) > 1:
      polygon_list = []
      boat_overlap = 'N'

      for bbox in image['ships']:
        x_min = int(bbox['x_min'])
        y_min = int(bbox['y_min'])
        x_max = int(bbox['x_max'])
        y_max = int(bbox['y_max'])
        rect = box(x_min, y_min, x_max, y_max, ccw=True)
        polygon_list.append(rect)

        for i in range(0, len(polygon_list)):
          for a in range(i+1,len(polygon_list)):
              distance = polygon_list[i].distance(polygon_list[a])
              if distance <= 350.0:
                boat_overlap = 'A'
    else:
      boat_overlap = 'N'

  civilian_sighting = 'N'
  if text:
    if text['VESSEL_NAME'] is not None:
      civilian_sighting = 'A'
    else:
      civilian_sighting = 'N'

  return heading, speed, position, boat_overlap, civilian_sighting



def bayes_network(heading, speed, position, boat_overlap, civilian_sighting):
  heading_dis = DiscreteDistribution({'A': 1./5, 'N': 4./5})
  speed_dis = DiscreteDistribution({'A': 1./5, 'N': 4./5})
  position_dis = DiscreteDistribution({'A': 2./5, 'N': 3./5})
  boat_overlap_dis = DiscreteDistribution({'A': 4./5, 'N': 1./5})
  civilian_sighting_dis = DiscreteDistribution({'A': 4./5, 'N': 1./5})

  event_dis = ConditionalProbabilityTable(
      [['A', 'A', 'A', 'A', 'A','A', 1],
       ['A', 'A', 'A', 'A', 'N','A', 0.8],
       ['A', 'A', 'A', 'N', 'A','A', 0.9],
       ['A', 'A', 'A', 'N', 'N','A', 0.8],
       ['A', 'A', 'N', 'A', 'A','A', 0.8],
       ['A', 'A', 'N', 'A', 'N','A', 0.6],
       ['A', 'N', 'A', 'A', 'A','A', 0.8],
       ['A', 'N', 'A', 'A', 'N','A', 0.6],
       ['N', 'A', 'A', 'A', 'A','A', 0.85],
       ['N', 'A', 'A', 'A', 'N','A', 0.75],
       ['N', 'N', 'A', 'A', 'A','A', 0.7],
       ['N', 'N', 'A', 'A', 'N','A', 0.5],
       ['N', 'A', 'N', 'A', 'A','A', 0.6],
       ['N', 'A', 'N', 'A', 'N','A', 0.4],
       ['N', 'A', 'A', 'N', 'A','A', 0.5],
       ['N', 'A', 'A', 'N', 'N','A', 0.5],
       ['A', 'N', 'N', 'A', 'A','A', 0.7],
       ['A', 'N', 'N', 'A', 'N','A', 0.45],
       ['A', 'N', 'A', 'N', 'A','A', 0.7],
       ['A', 'N', 'A', 'N', 'N','A', 0.3],
       ['A', 'A', 'N', 'N', 'A','A', 0.7],
       ['A', 'A', 'N', 'N', 'N','A', 0.3],
       ['A', 'N', 'N', 'N', 'A','A', 0.4],
       ['A', 'N', 'N', 'N', 'N','A', 0.3],
       ['N', 'A', 'N', 'N', 'A','A', 0.25],
       ['N', 'A', 'N', 'N', 'N','A', 0.35],
       ['N', 'N', 'A', 'N', 'A','A', 0.3],
       ['N', 'N', 'A', 'N', 'N','A', 0.2],
       ['N', 'N', 'N', 'A', 'A','A', 0.45],
       ['N', 'N', 'N', 'A', 'N','A', 0.35],
       ['N', 'N', 'N', 'N', 'A','A', 0],
       ['N', 'N', 'N', 'N', 'N','A', 0],
       ['A', 'A', 'A', 'A', 'A','N', 0],
       ['A', 'A', 'A', 'A', 'N','N', 0.2],
       ['A', 'A', 'A', 'N', 'A','N', 0.1],
       ['A', 'A', 'A', 'N', 'N','N', 0.2],
       ['A', 'A', 'N', 'A', 'A','N', 0.2],
       ['A', 'A', 'N', 'A', 'N','N', 0.4],
       ['A', 'N', 'A', 'A', 'A','N', 0.2],
       ['A', 'N', 'A', 'A', 'N','N', 0.4],
       ['N', 'A', 'A', 'A', 'A','N', 0.15],
       ['N', 'A', 'A', 'A', 'N','N', 0.25],
       ['N', 'N', 'A', 'A', 'A','N', 0.3],
       ['N', 'N', 'A', 'A', 'N','N', 0.5],
       ['N', 'A', 'N', 'A', 'A','N', 0.4],
       ['N', 'A', 'N', 'A', 'N','N', 0.6],
       ['N', 'A', 'A', 'N', 'A','N', 0.5],
       ['N', 'A', 'A', 'N', 'N','N', 0.5],
       ['A', 'N', 'N', 'A', 'A','N', 0.3],
       ['A', 'N', 'N', 'A', 'N','N', 0.55],
       ['A', 'N', 'A', 'N', 'A','N', 0.3],
       ['A', 'N', 'A', 'N', 'N','N', 0.7],
       ['A', 'A', 'N', 'N', 'A','N', 0.3],
       ['A', 'A', 'N', 'N', 'N','N', 0.7],
       ['A', 'N', 'N', 'N', 'A','N', 0.6],
       ['A', 'N', 'N', 'N', 'N','N', 0.7],
       ['N', 'A', 'N', 'N', 'A','N', 0.75],
       ['N', 'A', 'N', 'N', 'N','N', 0.65],
       ['N', 'N', 'A', 'N', 'A','N', 0.7],
       ['N', 'N', 'A', 'N', 'N','N', 0.8],
       ['N', 'N', 'N', 'A', 'A','N', 0.55],
       ['N', 'N', 'N', 'A', 'N','N', 0.65],
       ['N', 'N', 'N', 'N', 'A','N', 1],
       ['N', 'N', 'N', 'N', 'N', 1]], [heading_dis, speed_dis, position_dis, boat_overlap_dis, civilian_sighting_dis])
  
  s1 = Node(heading_dis, name="heading")
  s2 = Node(speed_dis, name="speed")
  s3 = Node(position_dis, name="position")
  s4 = Node(boat_overlap_dis, name="boat_overlap")
  s5 = Node(civilian_sighting_dis, name="civilian_sighting")
  s6 = Node(event_dis, name="event")
  
  model = BayesianNetwork("ship_event_reasoning")
  model.add_states(s1, s2, s3, s4, s5, s6)
  model.add_edge(s1, s6)
  model.add_edge(s2, s6)
  model.add_edge(s3, s6)
  model.add_edge(s4, s6)
  model.add_edge(s5, s6)
  model.bake()
  pred = model.predict([[heading, speed, position, boat_overlap, civilian_sighting, None]])
  if pred[0][5] == 'N':
    non_pred = 'A'
  elif pred[0][5] == 'A':
    non_pred = 'N'
  prob1 = model.probability(pred)
  prob2 = model.probability([[heading, speed, position, boat_overlap, civilian_sighting, non_pred]])
  prob = prob1/(prob1+prob2)
  prob = "{:.2f}%".format(prob*100)
  return pred, prob, heading, speed, position, boat_overlap, civilian_sighting
          
def event_reasoning(ais, image=None, text=None):  
  position, speed, heading, boat_overlap, civilian_sighting = generateEvent(ais,image)
  pred, prob, heading, speed, position, boat_overlap, civilian_sighting = bayes_network(position, speed, heading, boat_overlap, civilian_sighting)
  return {'prediction':pred[0][4], 'probability':prob}
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
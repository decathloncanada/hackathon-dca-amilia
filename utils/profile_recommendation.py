# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 14:52:55 2019

class to output recommended activities given a profil picture and description

@author: AI team
"""

import json
from nltk.stem import PorterStemmer
import re
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import base64
from io import BytesIO
import json
import numpy as np
import requests
from keras.applications import inception_v3
from keras.preprocessing import image
import PIL
import os
import pandas as pd

PICTURE = 'C:/Users/SMERCI07/Documents/Decathlon/Comfiz/dca-tf-serving/test_images/soccer.jpg'
TEXT = "Allo! Je m'appelle Samuel, j'aime le plein-air, la course et le golf"
LATITUDE = 45.511, 
LONGITUDE = -73.582
GROUP_TO_ID = pd.read_csv('group_to_id.csv')
AGE = 30

ps = PorterStemmer()

class profile_recommendation():
    
    def __init__(self):
        self.recommended_activities = None
        self.activities_description = {}
        self.activities_keywords = {}
    
    #method to extract activities at a given location     
    def _location_to_activities(self, latitude=45.511, longitude=-73.582, radius=10):
        #exract places at this location
        url = 'https://www.amilia.com/api/v3/fr/locations?type=Radius&coordinates={},{}&radius={}&page=1&perpage=2000'.format(latitude, longitude, radius)
        r = requests.get(url)
        data = json.loads(r.text)
        
        locations = [i['Id'] for i in data['Items']]
        #extract all the activities
        for i in locations:
            print(i)
            url = "https://www.amilia.com/api/v3/fr/locations/{}/activities?showHidden=false&showCancelled=false&showChildrenActivities=false".format(i)
            r = requests.get(url)
            data = json.loads(r.text)
            #for each activity, extract the name and category name
            for j in data['Items']:
                self.activities_description[(i, j['Id'])] = j['Name'] + j['CategoryName']
                self.activities_keywords[(i, j['Id'])] = [x['Id'] for x in j['Keywords']]
                
    #method to get recommendations given profile textual description
    def _text_to_activity(self, text):
        #generate training data
        corpus = [i for j,i in self.activities_description.items()]
        innner_id_to_activity = {i: j[0] for i, j in enumerate(self.activities_description.items())}
        
        vec =TfidfVectorizer()
        tfidf = vec.fit_transform(corpus)
        
        unseen_tfidf = vec.transform([text])    
        neigh = NearestNeighbors(n_neighbors=50, n_jobs=-1) 
        neigh.fit(tfidf)
        results = neigh.kneighbors(unseen_tfidf, return_distance=False)
        
        #apply dictionary to list
        self.text_recommendations = [innner_id_to_activity[k] for k in results[0]]
        
    #method to extract Amilia IDs from Decathlon IDs
    @staticmethod
    def _decathlon_to_amilia(sport_ids):
        url = "https://www.amilia.com/api/v3/fr/keywords?partner=Decathlon"
        r = requests.get(url)
        data = json.loads(r.text)
        
        amilia_ids = [i['Id'] for i in data if i.get('PartnerId',-1) in sport_ids]
        
        return amilia_ids
    
    #method to go from image_path to sport
    @staticmethod
    def _picture_to_group(image_path):
        os.environ['KMP_DUPLICATE_LIB_OK']='True'
        TF_SERVING_HOST = 'localhost'
        
        # Preprocessing our input image
        img = image.img_to_array(image.load_img(image_path, target_size=(224, 224))) / 255.
        
        payload = {
            "instances": [{'input_image': img.tolist()}]
        }
        
        # sending post request to TensorFlow Serving server
        r = requests.post('http://%s:%s/v1/models/image_classifier:predict' % (TF_SERVING_HOST, 8501),
                          json=payload)
        
        pred = json.loads(r.content.decode('utf-8'))
        
        # Decoding the response        
        classes = ['adventure_and_travel_sports', 'aircraft_activities', 'artistic_and_dance_sports',
                   'athletics', 'basket_and_handball_sports', 'basque_and_lumberjack_sports', 'bat_and_ball_games',
                   'billiard_sports', 'board_sports', 'circus_discipline', 'club_and_ball_sports', 
                   'combat_sports', 'cycle_sports', 'diving_sports', 'equestrianism', 'football_sports',
                   'paddle_sports', 'racquet_and_net_sports', 'relaxation_training', 'shooting_sports', 
                   'skating_sports', 'skiing_sports', 'sliding_sports', 'stick_and_ball_sports',
                   'strength_training', 'target_sports', 'thow_and_catch_sports', 
                   'tow_sports', 'water_aerobics']
        
        results = [(classes[i], pred['predictions'][0][i]) for i in range(len(pred['predictions'][0]))]
        results.sort(key=lambda tup: tup[1], reverse=True)
        
        #map from group to group id to sport ids
        return GROUP_TO_ID[GROUP_TO_ID.name == results[0][0]]['id'].values[0]

        
    #method to extract sport from profile picture
    def _picture_to_activity(self, image_path):
        
        #extract the group_id from the image
        os.environ['KMP_DUPLICATE_LIB_OK']='True'
        TF_SERVING_HOST = 'localhost'
        
        # Preprocessing our input image
        img = image.img_to_array(image.load_img(image_path, target_size=(224, 224))) / 255.
        
        payload = {
            "instances": [{'input_image': img.tolist()}]
        }
        
        # sending post request to TensorFlow Serving server
        r = requests.post('http://%s:%s/v1/models/image_classifier:predict' % (TF_SERVING_HOST, 8501),
                          json=payload)
        
        pred = json.loads(r.content.decode('utf-8'))
        
        # Decoding the response        
        classes = ['adventure_and_travel_sports', 'aircraft_activities', 'artistic_and_dance_sports',
                   'athletics', 'basket_and_handball_sports', 'basque_and_lumberjack_sports', 'bat_and_ball_games',
                   'billiard_sports', 'board_sports', 'circus_discipline', 'club_and_ball_sports', 
                   'combat_sports', 'cycle_sports', 'diving_sports', 'equestrianism', 'football_sports',
                   'paddle_sports', 'racquet_and_net_sports', 'relaxation_training', 'shooting_sports', 
                   'skating_sports', 'skiing_sports', 'sliding_sports', 'stick_and_ball_sports',
                   'strength_training', 'target_sports', 'thow_and_catch_sports', 
                   'tow_sports', 'water_aerobics']
        
        results = [(classes[i], pred['predictions'][0][i]) for i in range(len(pred['predictions'][0]))]
        results.sort(key=lambda tup: tup[1], reverse=True)
        
        #map from group to group id to sport ids
        group_id = GROUP_TO_ID[GROUP_TO_ID.name == results[0][0]]['id'].values[0]
        
        #map grom group_id to associated sports
        url = "https://sports-decathlon.herokuapp.com/groups/{}".format(group_id)
        r = requests.get(url)
        data = json.loads(r.text)
        sport_ids = [i['id'] for i in data['data']['relationships']['sports']['data']]
        
        #find all the list of amilia ids mathing the list of decathlon ids
        amilia_ids = self._decathlon_to_amilia(sport_ids)
        amilia_ids = set(amilia_ids)
        
        #find all the activities with that ID
        self.img_recommendations = [i for i,j in self.activities_keywords.items() if len(amilia_ids.intersection(set(j))) > 0]
        
    #method to aggregate recommendations
    def get_recommendations(self, image_path, text, latitude=45.511, longitude=-73.582, radius=10):
        
        #extract all the activites at this location
        self._location_to_activities(latitude=latitude, longitude=longitude, radius=radius)
        
        #get recommendations from text
        self._text_to_activity(text=TEXT)
        
        #get recommendations from picture
        self._picture_to_activity(image_path=PICTURE)
        
        #aggregate the recommendations
        #find the common set
        self.recommended_activities = [i for i in self.text_recommendations if i in self.img_recommendations]
        
        
if __name__=='__main__':
    rec = profile_recommendation()
    rec._location_to_activities(radius=5)
    rec._picture_to_activity(image_path=PICTURE)
    rec._text_to_activity(text=TEXT)
#        
        
        
        

                
            
         
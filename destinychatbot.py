import json, requests
import re
import aiml
from nltk.sem import Expression
from nltk.inference import ResolutionProver
read_expr = Expression.fromstring
import pandas
import numpy as np
kb=[]
data = pandas.read_csv('destinyKB.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]
import tkinter as tk
from tkinter import filedialog
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from PIL import Image
import os

kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="destinychatbot.xml")

project_id = '2efdceeb-a983-4de3-9a03-79d378054630'
cv_key = '7f157562c9274fc4a49d7160cf19f580'
cv_endpoint = 'https://adamscustomvision-prediction.cognitiveservices.azure.com/'

model_name = 'exotic_weapons'
print('Ready to predict using model {} in project {}'.format(model_name, project_id))

print("Welcome, Guardian! This is a Destiny chatbot, based on Bungie's Destiny 2. Please feel free to ask questions about any in-game exotic weapon.")
while True:
    #get user input
    try:
        userInput = input("> ")
    except (KeyboardInterrupt, EOFError) as e:
        break
    #pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    #activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
        
    #post-process the answer for commands
    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
            break

        #possible answers for destiny related questions
        #user searching for all weapon details
        elif cmd == 1:
            file = open('exoticweapons.json')
            json_file = json.load(file)
            for weapon in json_file['weapons']: #reading the data from JSON and outputs based on the user input
                if re.sub('[^A-Za-z0-9 ]+', '', weapon['name']).lower() == params[1]:
                    name = weapon['name']
                    slot = weapon['slot']
                    w_type = weapon['type']
                    ammo = weapon['ammo']
                    intrinsicperk = weapon['intrinsicperk']
                    mainperk = weapon['mainperk']
            if name != '':
                print(name, "is a", slot, w_type, "that uses", ammo, "ammo.", "It's main perks are:")
                print(intrinsicperk)
                print(mainperk)
            else:
                print("Sorry, I don't speak Eliksni (not yet anyway).") #error message

        #searching for weapon type only
        elif cmd == 2:
            file = open('exoticweapons.json')
            json_file = json.load(file)
            for weapon in json_file['weapons']:
                if re.sub('[^A-Za-z0-9 ]+', '', weapon['name']).lower() == params[1]:
                    name = weapon['name']
                    w_type = weapon['type']
            if name != '':
                print(name, "is a", w_type, ".")
            else:
                print("Sorry, I don't speak Eliksni (not yet anyway).")

        #searching for weapon slot only
        elif cmd == 3:
            file = open('exoticweapons.json')
            json_file = json.load(file)
            for weapon in json_file['weapons']:
                if re.sub('[^A-Za-z0-9 ]+', '', weapon['name']).lower() == params[1]:
                    name = weapon['name']
                    slot = weapon['slot']
            if name != '':
                print(name, "is in the", slot, "slot.")
            else:
                print("Sorry, I don't speak Eliksni (not yet anyway).")

        #searching for ammo type only
        elif cmd == 4:
            file = open('exoticweapons.json')
            json_file = json.load(file)
            for weapon in json_file['weapons']:
                if re.sub('[^A-Za-z0-9 ]+', '', weapon['name']).lower() == params[1]:
                    name = weapon['name']
                    ammo = weapon['ammo']
            if name != '':
                print(name, "uses", ammo, "ammo.")
            else:
                print("Sorry, I don't speak Eliksni (not yet anyway).")

        #searching for weapon catalyst
        elif cmd == 5:
            file = open('exoticweapons.json')
            json_file = json.load(file)
            for weapon in json_file['weapons']:
                if re.sub('[^A-Za-z0-9 ]+', '', weapon['name']).lower() == params[1]:
                    name = weapon['name']
                    catalyst = weapon['catalyst']
            if catalyst != 'None.':
                print("As a matter of fact, yes!")
                print(catalyst)
            else:
                print("Hmm... this weapon doesn't seem to have a catalyst as of my creation.")
        
        #"i know that * is *" code
        elif cmd == 6:
            object,subject=params[1].split(' is ')
            expr=read_expr(subject + '(' + object + ')')
            opp_exp = read_expr("not " + subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr, kb, verbose=False)
            if answer:
                print("Nice one! But this is already in my knowledge base.")
            if answer == False:
                if ResolutionProver().prove(opp_exp, kb, verbose=False):
                    print("You are incorrect. This is what I'm here for.")
                else:
                    print("Duly noted.")
                    kb.append(expr)

        #"check that * is *" code
        elif cmd == 7:
            object,subject=params[1].split(' is ')
            expr=read_expr(subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr, kb, verbose=True)
            if answer:
                print("Can't believe I'm saying this but you're right!")
            else:
                print("It may not be true.")

        elif cmd == 8:
            print("Opening dialog...")
            root = tk.Tk()
            file_path = filedialog.askopenfilename(initialdir="Weapons", filetypes=[('Images','*.jpg *.jpeg *.png')])
            root.mainloop()

            # Create an instance of the prediction service
            credentials = ApiKeyCredentials(in_headers={"Prediction-key": cv_key})
            custom_vision_client = CustomVisionPredictionClient(endpoint=cv_endpoint, credentials=credentials)

            def imageClassify ():
                image_contents = open(file_path, "rb")
                classification = custom_vision_client.classify_image(project_id, model_name, image_contents.read())
                prediction = classification.predictions[0].tag_name
                print(prediction)

            imageClassify()

        #general error message
        elif cmd == 99:
            print("Sorry, I don't speak Eliksni (not yet anyway).")

    else:
        print(answer)
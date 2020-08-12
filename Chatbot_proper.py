import random
import json
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()
#imported training data from data.pth which is output from train.py and model from model.py

# importing echobot1 functions
import json 
import requests
import time
import urllib
import telegram

TOKEN = "XXX"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

def get_json_from_url(url):
        content = get_url(url)
        js = json.loads(content)
        return js


def get_updates(offset): #gets json file from URL
        url = URL + "getUpdates"
        if offset:
                url += "?offset={}".format(offset)
        js = get_json_from_url(url)
        return js

def get_last_update_id(updates):
        update_ids = []
        for update in updates["result"]:
                update_ids.append(update["update_id"])
        return max(update_ids, default = last_update_id)

def get_last_chat_text(updates):
        # num_updates = len(updates["result"])
        # last_update = num_updates - 1
        text = updates["result"][-1]["message"]["text"] #text input
        return text

def get_last_chat_id(updates):
        chat_id = updates["result"][-1]["message"]["chat"]["id"]
        return chat_id


def send_message(output,chat_id):
        bot = telegram.Bot(token=TOKEN)
        bot.sendMessage(chat_id=chat_id, text = output)

def main():
        input_text = get_last_chat_text(updates)
        return input_text                

bot_name = "XXX"
print("Let's chat! (type 'quit' to exit)")
last_update_id = 0
while True:
        updates = get_updates(last_update_id) #returns json file

        for last_update_id in updates["result"]:
                main()
                input_text = main()
                if input_text == "quit":
                        break
                input_text = tokenize(input_text)
                X = bag_of_words(input_text, all_words)
                X = X.reshape(1, X.shape[0])
                X = torch.from_numpy(X).to(device)

                output = model(X)
                _, predicted = torch.max(output, dim=1)

                tag = tags[predicted.item()]

                probs = torch.softmax(output, dim=1)
                prob = probs[0][predicted.item()]
                if prob.item() > 0.75:
                        for intent in intents['intents']:
                                if tag == intent["tag"]:
                                        output = f"{random.choice(intent['responses'])}"
                else:
                        output = f"{bot_name}: I do not understand..."

                print(output)

                chat_id = get_last_chat_id(updates)
                print(chat_id)

                send_message(output, chat_id)
                time.sleep(0.1)
        
                break
        last_update_id = get_last_update_id(updates) + 1 #returns max_id in the json file and adds 1

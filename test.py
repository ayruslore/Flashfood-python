'''from bottle import get, post, request,run # or route
@post('/login') # or @route('/login', method='POST')
def do_login():
    username = request.json
    print(username,type(username))
    print (username['id'])
    return username
r = requests.get(url="http://0.0.0.0:5000/getUser/1234567890",headers=head)
res = r.json()
if(res['name']==''):
    dta = {'ID': 1234567890, 'name': 'surya'}
print ("surya",r.text)
data = {'ID':1234567890, 'name':'surya','subscribed':1 }
r1 = requests.post(url='http://0.0.0.0:5000/addUser',data = json.dumps(data),headers=head)
data = r2.json()
print (data)
print(r2.status_code)
print(r2.text)

import requests
import json
head = {'Content-Type': 'application/json'}
#data = {"phone": 963852741, "long": 77.66564, "ID": 1, "name": "Domino's Pizza", "lat": 12.844496, "radius": 5}
#data ={"phone": 963852741, "long": 77.66395, "ID": 2, "name": "Hyderabadi Spice", "lat": 12.8339903, "radius": 5}
data = {"phone": 963852741, "long": 77.665583, "ID": 3, "name": "New Punjabi Food Corner", "lat": 12.844706, "radius": 5}
#data = {"name":"New Punjabi Food Corner",
#"phone":963852741,
#"lat":12.844706,
#"long":77.665583,
#"radius":5}
r = requests.post(url="http://0.0.0.0:4000/addrest",data = json.dumps(data),headers=head)
'''

import requests
import json
head = {'Content-Type': 'application/json'}
data = {'data':[{'restID':3,'qty_left':10,'qty_sold':0,'dish':'Chicken Tikka','originalPrice':120,'offerPrice':70,'type':'Starters[Non-Veg]'},
{"restID":2,"qty_left":5,"qty_sold":0,"dish":"Chicken Makhanwala","originalPrice":120,"offerPrice":100,"type":"Starters[Non-Veg]"},
{"restID":3,"qty_left":6,"qty_sold":0,"dish":"Hariyali Chicken Kebab","originalPrice":150,"offerPrice":110,"type":"Starters[Non-Veg]"},
{"restID":2,"qty_left":4,"qty_sold":0,"dish":"Malai Chicken Kebab","originalPrice":130,"offerPrice":100,"type":"Kebab"},
{"restID":3,"qty_left":8,"qty_sold":0,"dish":"Mutton Seekh Kebab","originalPrice":250,"offerPrice":150,"type":"Kebab"},
{"restID":2,"qty_left":8,"qty_sold":0,"dish":"Mutton Biryani","originalPrice":170,"offerPrice":110,"type":"Biryani"},
{"restID":3,"qty_left":8,"qty_sold":0,"dish":"Chiken Biryani","originalPrice":200,"offerPrice":150,"type":"Biryani"},
{"restID":2,"qty_left":8,"qty_sold":0,"dish":"Mutton Rogan Josh","originalPrice":170,"offerPrice":120,"type":"Kebab"}]}
r = requests.post(url="http://0.0.0.0:4000/addOffers",data = json.dumps(data),headers=head)

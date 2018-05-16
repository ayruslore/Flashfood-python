import bottle
import json
#import googlemaps
import math
import random
import requests
import pandas as pd
from geopy import distance, Point
from bottle import get, post, request, run, install, response , route
from redis import Redis as red
from pottery import RedisDict as redDict
from pottery import RedisSet as redSet
from pottery import RedisList as redList
from pottery import NextId

#Enable Cors to send/recieve data.
class EnableCors(object):
    name = 'enable_cors'
    api = 2
    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)
        return _enable_cors


class Haversine:
    '''
    use the haversine class to calculate the distance between
    two lon/lat coordnate pairs.
    output distance available in kilometers, meters, miles, and feet.
    example usage: Haversine([lon1,lat1],[lon2,lat2]).feet

    '''
    def __init__(self,coord1,coord2):
        lon1,lat1=coord1
        lon2,lat2=coord2

        R=6371000                               # radius of Earth in meters
        phi_1=math.radians(lat1)
        phi_2=math.radians(lat2)

        delta_phi=math.radians(lat2-lat1)
        delta_lambda=math.radians(lon2-lon1)

        a=math.sin(delta_phi/2.0)**2+\
           math.cos(phi_1)*math.cos(phi_2)*\
           math.sin(delta_lambda/2.0)**2
        c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

        self.meters=R*c                         # output distance in meters
        self.km=self.meters/1000.0              # output distance in kilometers
        self.miles=self.meters*0.000621371      # output distance in miles
        self.feet=self.miles*5280               # output distance in feet


#connection with redis-py client
dir_con = red(host = '0.0.0.0',port = 6379,db = 0)

#connection with pottery client
pot_con = red.from_url('http://localhost:6379/')
pot_arc = red.from_url('http://localhost:6379/1')

rest_ids = NextId(key='rest-ids', masters={pot_con})

nodeurl = 'https://33464113.ngrok.io'

#string encode with b prefix
def bytify(strung):
    return bytes(strung, encoding = "ascii")

def byte2string(strung):
    return strung.decode('utf-8')

def byte2int(strung):
    return int(byte2string(strung))

def byte2float(strung):
    return float(byte2string(strung))

def get_geocode(lat,longi):
    #gmaps = googlemaps.Client(key='AIzaSyDUam4I3cjx6djDxijubOHrwfr7zzZt5Sg')
    #reverse_geocode_result = gmaps.reverse_geocode((lat,longi))
    #print(reverse_geocode_result[0]['formatted_address'])
    return 'x'

'''
User: pottery dictionary
-name
-userId(primaryKey facebook generated)
-phone no
-lat
-long
-decoded_address
-int confirmed_carts
-int subscribed
'''

@get('/set_saved_address/<sender>')
def saved_address(sender):
    key = "user:" + str(sender) + ":details"
    user = redDict(redis = pot_con,key = key)
    user['location'] = 1

@post('/addUser')  #post request to add the user details.
def addUser():
    global Rest
    body = request.json
    key = "user:" + str(body['ID']) + ":details"
    sender = str(body['ID'])
    body.pop('ID')
    user = redDict(redis = pot_con, key = key)
    arch = redDict(redis = pot_arc, key = key)
    if 'decoded_address' not in arch:
        arch = user
        arch['confirmed_carts'] = 0
    for key in body:
        user[key] = body[key]
    if('subscribed' in user):
        body['subscribed'] = user['subscribed']
    if('decoded_address' not in user):
        if('lat' and 'long' in user):
            get_cluster_hotel(sender,user['lat'],user['long'])
            s = str(get_geocode(int(user['lat']),int(user['long'])))
            user['decoded_address'] = '26/C, Hosur Road, Electronics City Phase 1, Electronic City, Bengaluru, Karnataka 560100'
            body['decoded_address'] = user['decoded_address']
            body['location'] = 1
        else:
            body['location'] = 0
    print(json.dumps(body))
    yield json.dumps(body)

@post('/Saddress')
def Saddress():
    body = request.json
    key = "user:" + str(body['ID']) + ":details"
    user['decoded_address'] = body['Saddress']
    print(user['decoded_address'])
    yield json.dumps(body)

@get('/getUser/<UserId>')
def getUser(UserId):
    key = "user:" + UserId + ":details"
    user = redDict(redis = pot_con, key = key)
    data = {}
    if(len(user)!=0):
        data['name'] = user['name']
        if('subscribed' not in user):
            data['subscribed'] = 0
            data['location'] = 0
        else:
            data['subscribed'] = user['subscribed']
            if('decoded_address' and 'lat' and 'long' in user):
                data['decoded_address'] = user['decoded_address']
                data['location'] = 1
            else:
                data['location'] = 0
    else:
        data['name'] = ''
        data['subscribed'] = 0
        data['location'] = 0
    print(json.dumps(data))
    yield json.dumps(data)

@post('/deleteUser')
def deleteUser(UserId):
    body = request.json
    UserId = body['ID']
    key = "user:" + UserId + ":details"
    user = redDict(redis = pot_con, key = key)
    for keys in body:
        user.pop(keys)
    print(json.dumps(body))
    yield json.dumps(body)

'''
#/updateUser
@post('/updateuser')
def updateUser():
    body = request.json
    key = "user:" + str(body["Id"]) + ":details"
    user = redDict(redis = pot_con, key = key)
    for key in body:
        if key != 'id':
            user[key] = body[key]

Restaurant: pottery dictionary
-name
-restId(primaryKey and artificial key)
-phone no list
-lat
-long
-delivery Radius
-extra dets

{"phone": 963852741, "long": 77.66564, "ID": 1, "name": "Domino's Pizza", "lat": 12.844496, "radius": 5}
{"phone": 963852741, "long": 77.66395, "ID": 2, "name": "Hyderabadi Spice", "lat": 12.8339903, "radius": 5}
{"phone": 963852741, "long": 77.665583, "ID": 3, "name": "New Punjabi Food Corner", "lat": 12.844706, "radius": 5}
'''

global Rest
Rest = []

@post('/addrest')
def addRestaurant():
    global Rest
    body = request.json
    rest_id = next(rest_ids)
    key = "rest:"+str(rest_id)+":details"
    rest = redDict(redis = pot_arc, key = key)
    rest['ID'] = rest_id
    body['ID'] = rest_id
    for key in body:
        rest[key] = body[key]
    Rest.append({'name':rest['name'], 'ID':rest_id, 'lat':rest['lat'], 'long':rest['long'],'radius':rest['radius']})
    print(json.dumps(body))
    yield json.dumps(body)

@post('/updaterest')
def updateRestaurant():
    body = request.json
    key = "rest:"+str(body["ID"])+":details"
    rest = redDict(redis = pot_arc, key = key)
    for key in body:
        rest[key] = body[key]
    print(json.dumps(body))
    yield json.dumps(body)

'''
Offers
-id
-restId
-qty_left
-qty_sold
-accompaniments
-dishName
-originalPrice
-offerPrice
-link
'''

global OffersDB
OffersDB = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName','tag'])
global offerRests
offerRests = []


def dynamicoffers():
    return 'asdfghjkl'

@post('/addOffers')
def addOffer():
    global OffersDB,offerRests,Rest
    Offers = []
    body = request.json
    rests = []
    ide = []
    print(2)
    for i in range(len(body['data'])):
        body['data'][i]['ID'] = random.randint(100,999)
        key = "rest:"+str(body['data'][i]['restID'])+":details"
        rest = redDict(redis = pot_arc, key = key)
        body['data'][i]['restName'] = rest['name']
        body['data'][i]['link'] = 'http://genii.ai/activebots/Babadadhaba/img/db/' + body['data'][i]['dish'].replace(" ","-") + ".jpg"
        Offers.append(body['data'][i])
        print(3)
        if(rest['name'] not in rests):
            rests.append(rest['name'])
        if(body['data'][i]['restID'] not in offerRests):
            offerRests.append(body['data'][i]['restID'])
        if(body['data'][i]['restID'] not in ide):
            ide.append(body['data'][i]['restID'])
    print(4)
    DB = pd.read_json(json.dumps(Offers),orient='records')
    print(5)
    OffersDB = OffersDB.append(DB, ignore_index = True)
    print(6)
    yield "Successfully added dishes."
    send_data(ide,rests,DB)
    print(10)

def send_data(ide,rest,db):
    data = {'sender':['1389212674465596', '1699572286720160']}
    print(9)
    for i in range(len(ide)):
        restcluster = redList(redis = pot_con, key = 'Rest_cluster:'+str(ide[i])+':'+rest[i])
        if(len(restcluster)!=0):
            for sender in restcluster:
                data['sender'].append(sender)
            print(8)
    db.drop(['restID','ID','type','qty_left','qty_sold','tag'],axis = 1, inplace = True)
    head = {'Content-Type': 'application/json'}
    print(7)
    data['offers'] = (db.head(n=10)).to_json(orient = 'records')
    print(1)
    requests.post(url=nodeurl + "/dynamicOffers",data = json.dumps(data),headers=head)

def get_cluster_hotel(sender,lat,longi):
    global Rest
    for rest in Rest:
        p1 = Point(lat+" "+longi)
        dist = distance.distance(Point(rest['lat']+" "+rest['long']),p1).kilometers
        #if(dist <= rest['radius']):
        key = 'Rest_cluster:' + rest['ID'] + ':' + rest['name']
        restcluster = redList(redis = pot_con, key = key)
        restcluster.append(sender)

def getnearestRest(sender):
    global offerRests
    user = redDict(redis = pot_con, key = "user:" + str(sender) + ":details")
    if('lat' and 'long' in user):
        lat = user['lat']
        lon = user['long']
    else:
        return []
    nearest = {}
    for rest in offerRests:
        restaurant = redDict(redis = pot_arc, key = "rest:" + str(rest) + ":details")
        if('lat' and 'long' in restaurant):
            distance = Haversine((lat,lon), (restaurant['lat'],restaurant['long'])).km
            if(distance <= int(restaurant['radius'])):
                nearest[restaurant['name']] = distance
    result = []
    for key in sorted(nearest, key=lambda x: nearest[x]):
        result.append(key)
    print(result)
    print("surya")
    return result


@get('/offers/<sender>/<v_n>')
def offerfilter(sender,v_n):
    global OffersDB
    restaurants = getnearestRest(sender)
    print(restaurants)
    newdf = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName','tag'])
    for rest in restaurants:
        newdf.append(OffersDB[OffersDB['restName']==rest],ignore_index = True)
    sortedb = OffersDB.sort_values(['offerPrice'],ascending=True)
    mask = sortedb.tag.apply(lambda x : v_n in x)
    sortedb = sortedb[mask]
    sortedb.drop(['restID','ID','type','qty_left','qty_sold','tag'],axis = 1, inplace = True)
    print((sortedb.head(n=10)).to_json(orient = 'records'))
    yield (sortedb.head(n=10)).to_json(orient = 'records')


@get('/getOffers/<sender>')
def showoffers(sender):
    global OffersDB
    restaurants = getnearestRest(sender)
    print(restaurants)
    newdf = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName','tag'])
    for rest in restaurants:
        newdf.append(OffersDB[OffersDB['restName']==rest],ignore_index = True)
    sortedb = OffersDB.sort_values(['offerPrice'],ascending=True)
    sortedb.drop(['restID','ID','type','qty_left','qty_sold','tag'],axis = 1, inplace = True)
    print((sortedb.head(n=10)).to_json(orient = 'records'))
    yield (sortedb.head(n=10)).to_json(orient = 'records')
    '''global OffersDB
    restaurants = getnearestRest(sender)
    print(restaurants)
    print(OffersDB['restName'])
    print(OffersDB)
    newdf = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName'])
    for rest in restaurants:
        db = OffersDB[OffersDB['restName']==rest]
        print(db)
        if(len(db)!=0):
            newdf.append(db,ignore_index = True)
    newdf.drop(['restID','ID','type','qty_left','qty_sold'],axis = 1, inplace = True)
    print((newdf.head(n=10)).to_json(orient = 'records'))
    yield (newdf.head(n=10)).to_json(orient = 'records')'''

@get('/showPopulars/<sender>')
def showPopular(sender):
    global OffersDB
    restaurants = getnearestRest(sender)
    print(restaurants)
    newdf = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName','tag'])
    for rest in restaurants:
        newdf.append(OffersDB[OffersDB['restName']==rest],ignore_index = True)
    sortedb = OffersDB.sort_values(['offerPrice'],ascending=True)
    sortedb.drop(['restID','ID','type','qty_left','qty_sold','tag'],axis = 1, inplace = True)
    print((sortedb.head(n=10)).to_json(orient = 'records'))
    yield (sortedb.head(n=10)).to_json(orient = 'records')
    '''global OffersDB
    restaurants = getnearestRest(sender)
    print(restaurants)
    newdf = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName'])
    for rest in restaurants:
        newdf.append(OffersDB[OffersDB['restName']==rest],ignore_index = True)
    sortedb = newdf.sort_values(['qty_sold',],ascending=False)
    sortedb.drop(['restID','ID','type','qty_left','qty_sold'],axis = 1, inplace = True)
    print((sortedb.head(n=10)).to_json(orient = 'records'))
    yield (sortedb.head(n=10)).to_json(orient = 'records')'''

@get('/cheapOffers/<sender>')
def showCheap(sender):
    global OffersDB
    restaurants = getnearestRest(sender)
    print(restaurants)
    newdf = pd.DataFrame(data = {}, columns = ['ID','restID','dish','qty_sold','qty_left','type','originalPrice','offerPrice','link','restName','tag'])
    for rest in restaurants:
        newdf.append(OffersDB[OffersDB['restName']==rest],ignore_index = True)
    sortedb = OffersDB.sort_values(['offerPrice'],ascending=True)
    sortedb.drop(['restID','ID','type','qty_left','qty_sold','tag'],axis = 1, inplace = True)
    print((sortedb.head(n=10)).to_json(orient = 'records'))
    yield (sortedb.head(n=10)).to_json(orient = 'records')

@post('/claimOffer/<sender>')
def claimOffer(sender):
    global OffersDB
    #print(OffersDB)
    result = {'status':[],'remaining':[],'dish':[]}
    body = request.json
    body = str(body)
    body = json.loads(body)
    key = "user:"+ str(sender) + ":details"
    user = redDict(redis = pot_con, key = key)
    if('confirmed_carts' in user):
        cart = redDict(redis = pot_con, key = "user:"+str(sender)+":cart:"+str(user['confirmed_carts']+1))
    else:
        cart = redDict(redis = pot_con, key = "user:"+str(sender)+":cart:1")
        user['confirmed_carts'] = 0
    for item in body:
        print(item)
        print(OffersDB[OffersDB['dish']==item])
        if(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0]>=int(body[item])):
            cart[item] = body[item]
            result['dish'].append(item)
            result['status'].append('Yes')
            result['remaining'].append(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])
        else:
            result['dish'].append(item)
            result['status'].append('No')
            result['remaining'].append(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])
    yield json.dumps(result)


@get('/showCart/<sender>')
def showcart(sender):
    global OffersDB
    user = redDict(redis = pot_con, key = "user:" + str(sender) + ":details")
    if('confirmed_carts' in user):
        cart = redDict(redis = pot_con, key = "user:"+str(sender)+":cart:"+str(user['confirmed_carts']+1))
    else:
        cart = redDict(redis = pot_con, key = "user:"+str(sender)+":cart:1")
        user['confirmed_carts'] = 0
    result = {'cart':'','status':[],'qty':[],'dish':[],'remaining':[],'price':[]}
    if(len(cart)!=0):
        result['cart'] = 'Yes'
        for item in cart:
            if((OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])>=(int(cart[item]))):
                result['dish'].append(item)
                result['qty'].append(int(cart[item]))
                result['status'].append('Yes')
                result['price'].append(OffersDB[OffersDB['dish']==item]['offerPrice'].tolist()[0])
                result['remaining'].append(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])
            else:
                result['dish'].append(item)
                result['qty'].append(int(cart[item]))
                result['status'].append('No')
                result['price'].append(OffersDB[OffersDB['dish']==item]['offerPrice'].tolist()[0])
                result['remaining'].append(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])
        print(result)
        yield json.dumps(result)
    else:
        result['cart'] = 'No'
        print(result)
        yield json.dumps(result)
#qty-dish,price, name, number
def showCart1(sender):
    global OffersDB
    user = redDict(redis = pot_con, key = "user:" + str(sender) + ":details")
    if('confirmed_carts' in user):
        cart = redDict(redis = pot_con, key = "user:"+str(sender)+":cart:"+str(user['confirmed_carts']+1))
    else:
        cart = redDict(redis = pot_con, key = "user:"+str(sender)+":cart:1")
        user['confirmed_carts'] = 0
    result = {'cart':'','status':[],'qty':[],'dish':[],'remaining':[],'price':[]}
    if(len(cart)!=0):
        result['cart'] = 'Yes'
        for item in cart:
            if((OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])>=(int(cart[item]))):
                result['dish'].append(item)
                result['qty'].append(int(cart[item]))
                result['status'].append('Yes')
                result['price'].append(OffersDB[OffersDB['dish']==item]['offerPrice'].tolist()[0])
                result['remaining'].append(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])
            else:
                result['dish'].append(item)
                result['qty'].append(int(cart[item]))
                result['status'].append('No')
                result['price'].append(OffersDB[OffersDB['dish']==item]['offerPrice'].tolist()[0])
                result['remaining'].append(OffersDB[OffersDB['dish']==item]['qty_left'].tolist()[0])
        print(result)
        return (result)
    else:
        result['cart'] = 'No'
        print(result)
        return (result)


@get('/confirm/<sender>/<number>')
def confirmCart(sender,number):
    global OffersDB
    cart = showCart1(sender)
    result = {'name':'','number':'','address':'','total':0,'body':{}}
    print(cart)
    resultcart = {}
    if(cart['cart']=='No'):
        return json.dumps(result)
    else:
        total = 0
        for i in range(len(cart['dish'])):
            if(cart['status'][i]=='No'):
                cart['cart'] = 'No'
                return json.dumps(result)
            total += int(cart['price'][i]) * int(cart['qty'][i])
    user = redDict(redis = pot_con, key = "user:" + str(sender) + ":details")
    user['number'] = number
    user['location'] = 0
    if('confirmed_carts' in user):
        user['confirmed_carts'] = int(user['confirmed_carts']) + 1
    else:
        user['confirmed_carts'] = 1
    result['name'] = user['name']
    result['number'] = user['number']
    result['total'] = total
    result['body'] = cart
    result['address'] = user['decoded_address']
    return json.dumps(result)

'''
Orders
-orderId
-OfferId
-usrId
-qty
-accompanyments
-status
-delivery boi
'''
install(EnableCors())
run(host='0.0.0.0', port=4000, debug=True)

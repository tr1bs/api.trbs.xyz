from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, verify_jwt_in_request, get_jwt
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy_json import mutable_json_type


import os
from flask_cors import CORS
from datetime import datetime, date, timedelta
import json
import shortuuid
import random
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"  # put in envar
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
ACCESS_EXPIRES = timedelta(hours=4)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES



jwt = JWTManager(app)
db = SQLAlchemy(app)
CORS(app)

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


class Wish(db.Model):
    __tablename__ = 'wishlist'

    uuid    = db.Column(db.String(), primary_key=True)
    created = db.Column(TIMESTAMP(timezone=False), default=datetime.now())
    items = db.Column(JSONB)
    title = db.Column(db.String())
    creator = db.Column(db.String())
    public = db.Column(db.Boolean(), default=True)
    description = db.Column(db.String())

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'creator': self.creator,
            'created': self.created,
            'description': self.description,
            'items': self.items,
            'title': self.title,
            'public': self.public,
        } 


class Message(db.Model):
    __tablename__ = 'messages'

    uuid    = db.Column(db.String(), primary_key=True)
    created = db.Column(TIMESTAMP(timezone=False), default=datetime.now())
    fuf_id  = db.Column(db.String())
    author  = db.Column(db.String())    
    text    = db.Column(db.String())
    type    = db.Column(db.String())

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'fuf_id': self.fuf_id,
            'author': self.author,
            'created': self.created,
            'text': self.text,
            'type': self.type
        } 



class Fufillment(db.Model):
    __tablename__ = 'fufillment'

    uuid = db.Column(db.String(), primary_key=True)
    hist_id = db.Column(db.String())
    created = db.Column(TIMESTAMP(timezone=False), default=datetime.now())
    seller = db.Column(db.String())
    buyer = db.Column(db.String())
    tx_hash = db.Column(db.String())
    status = db.Column(db.String())
    url = db.Column(db.String())

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'hist_id': self.hist_id,
            'created': str(self.created),
            'seller': self.seller,
            'buyer': self.buyer,
            'tx_hash': self.tx_hash,
            'status': self.status,
            'url': self.url
        }


class History(db.Model):
    __tablename__ = 'hist'
    
    uuid = db.Column(db.String(), primary_key=True)
    item_id = db.Column(db.String())
    created = db.Column(TIMESTAMP(timezone=False), default=datetime.now())
    seller = db.Column(db.String())
    buyer = db.Column(db.String())
    seller_address = db.Column(db.String())
    buyer_address = db.Column(db.String())
    tx_hash = db.Column(db.String())
    url = db.Column(db.String())

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'item_id': self.item_id,
            'created': self.created,
            'seller': self.seller,
            'buyer': self.buyer,
            'seller_address': self.seller_address,
            'buyer_address': self.buyer_address,
            'tx_hash': self.tx_hash,
            'url': self.url
        }


class Dir(db.Model):
    __tablename__ = 'dir'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    eth_wallet = db.Column(db.String())
    bio = db.Column(db.String())
    tribs = db.Column(JSONB)
    followers = db.Column(JSONB)
    following = db.Column(JSONB)
    items = db.Column(JSONB)

    def as_dict(self):
        return {
            'username': self.username,
            'eth_wallet': self.eth_wallet,
            'bio': self.bio,
            'tribs': self.tribs,
            'followers': self.followers,
            'following': self.following,
            'items': self.items
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    email = db.Column(db.String())
    hash = db.Column(db.String())
    settings = db.Column(db.String())

    def to_json(self):
        return {"username": self.username, "email": self.email}

    def check_password(self, password):
            return check_password_hash(self.hash, password)


class Item(db.Model):
    __tablename__ = 'items'

    uuid = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    owner = db.Column(db.String())
    owner_address = db.Column(db.String())
    brand = db.Column(db.String())
    colors = db.Column(JSONB)
    created = db.Column(TIMESTAMP(timezone=False), default=datetime.now())
    description =  db.Column(db.String())
    for_sale = db.Column(db.Boolean())
    img = db.Column(JSONB)
    materials = db.Column(JSONB)
    price = db.Column(db.String())
    reposted = db.Column(JSONB)
    saved = db.Column(JSONB)
    season = db.Column(db.String())
    size = db.Column(db.String())
    source_url = db.Column(db.String())
    status = db.Column(db.String())
    tags = db.Column(JSONB)
    tribs = db.Column(JSONB)
    tx = db.Column(JSONB)



    def as_dict(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "owner": self.owner,
            "owner_address": self.owner_address,
            "brand": self.brand,
            "colors": self.colors,
            "created": str(self.created),
            "description": self.description,
            "for_sale": self.for_sale,
            "img": self.img,
            "materials": self.materials,
            "price": self.price,
            "reposted": self.reposted,
            "saved": self.saved,
            "size": self.size,
            "source_url": self.source_url,
            "status": self.status,
            "tags": self.tags,
            "tribs": self.tribs,
            "tx": self.tx,
        }

    def check_password(self, password):
            return check_password_hash(self.hash, password)


def generate_item_metadata(ssense_link):
    # in future, have a multiselect but atm ssense

    # use the below in the future to pull the whole schema but atm just chill on the name, price, currency etc
    user_agents = [ 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
        'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
    ] 
    user_agent = random.choice(user_agents)
    headers = {'User-Agent': user_agent} 

    url = ssense_link
    html = requests.get(url, headers=headers) 

    soup = BeautifulSoup(html.text, 'html.parser')
    data = json.loads(soup.find('script', type='application/ld+json').text)

    availability = data['offers']['availability'].split('/')[3]

    
    return jsonify(name=data['name'], 
                brand=data['brand']['name'], 
                price=data['offers']['price'], 
                price_currency=data['offers']['priceCurrency'], 
                availability=availability,
                description=data['description'],
                image=data['image']
                )






# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    print(user)
    return user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    print(_jwt_header)
    print(jwt_data)
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@app.route("/", methods=["GET"])
def healthcheck():
    if request.method == 'GET':
        return "hello world", 200


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    # if username != "test" or password != "test":
    #     return jsonify({"msg": "Bad username or password"}), 401
    user = User.query.filter_by(username=username).one_or_none()
    print(user)
    print(user.username)

    if not user or not user.check_password(password):
        return jsonify("wrong username or password"), 401
    
    # Notice that we are passing in the actual sqlalchemy user object here
    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token, username=user.username)


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # create redis store and revoke token here
    # look into alternatives
    # remove token client side
    return jsonify(msg='server side logout complete', success=True)


@app.route("/is_logged_in", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    print('is logged in?')
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/user_settings", methods=['GET', 'POST'])
@jwt_required()
def user_settings():
    current_user = get_jwt_identity()
    if current_user:
        user = User.query.filter_by(id=current_user).one_or_none()

        if request.method == 'GET':
            settings = user.settings
            return jsonify(settings=settings), 200

        if request.method == 'POST':
            r = request.get_data(as_text=True)
            user.settings = r
            try:
                db.session.commit()
                print('completed settings update')
                return r, 200
            except Exception as e:
                print(e)
                return 500
             
            
    else:
        return jsonify("youre not logged in"), 401 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        r = request.get_json()
        user = User.query.filter_by(username=r.username).one_or_none()

        if not user:
            new_user = User(username=r.username, email=r.email, password=generate_password_hash(r.password))
            db.session.add(new_user)
            db.commit()
            print('added new user...')
            
            # Notice that we are passing in the actual sqlalchemy user object here
            # double check this
            access_token = create_access_token(identity=new_user)
            return jsonify(access_token=access_token, username=new_user.username)

        else:
            return jsonify("user already exists"), 401


    return 'notok', 500


@app.route('/v1/get_user/<username>', methods=['GET'])
def get_user(username):
    if request.method == 'GET':
        print('api - fetching public user...')
        user = Dir.query.filter_by(username=username).one_or_none()
        return jsonify(user.as_dict()), 200





@app.route('/v1/i/get_all', methods=['GET'])
def get_all_items():
    if request.method == 'GET':
        print('api - fetching items...')
        # r = db.select_all_items() #can paginate this later
        r = Item.query.all()

        pkg = []
        for item in r:
            print(item.as_dict(), '\n')
            pkg.append(item.as_dict())

        
        return jsonify(pkg), 200


@app.route('/v1/i/<uuid>', methods=['GET'])
def get_item(uuid):
    if request.method == 'GET':
        print('api - fetching item...')
        # r = db.select_all_items() #can paginate this later
        r = Item.query.get(uuid)
        print(r)
        # pkg = []
        # for item in r:
        #     print(item.as_dict(), '\n')
        #     pkg.append(item.as_dict())

        
        return jsonify(r.as_dict()), 200



@app.route('/v1/i/add', methods=['GET', 'POST']) #make this jwt private
def add_items():

    if request.method == 'POST':
        print('api - adding item')
        r = request.get_json()
        print(r)
        r['uuid'] = shortuuid.ShortUUID().random(length=16)
        columns = [*r.keys()]
        # print(columns)

        new_item = Item(
                        uuid=r['uuid'],
                        name=r['name'],
                        owner=r['owner'],
                        owner_address=r['owner_address'],
                        brand=r['brand'],
                        colors=r['colors'],
                        description=r['description'],
                        for_sale=True,
                        img=r['img'],
                        materials=r['materials'],
                        price=r['price'],
                        reposted=r['reposted'],
                        saved=r['saved'],
                        size=r['size'],
                        source_url=r['source_url'],
                        tags=r['tags'],
                        status=r['status'],
                        tribs=r['tribs'],
                        tx=r['tx']
                    )
        db.session.add(new_item)
        db.session.commit()

        print('api - added item...')
        # should probably try catch the above
        return 'added item', 200


@app.route('/v1/i/buy_item', methods=['POST']) # add jwt private
@jwt_required()
def buy_item():
    if request.method == 'POST':
        print('api - purchasing item.....')

        r = request.get_json()
        print(r)
        current_user = get_jwt_identity()
        print(current_user)
        user = User.query.filter_by(id=current_user).one_or_none()
        r['buyer'] = user.username
        r['uuid'] = shortuuid.ShortUUID().random(length=16)

        new_hist = History(
                    uuid=r['uuid'],
                    item_id=r['item_id'],                    
                    seller=r['seller'],
                    buyer=r['buyer'],
                    seller_address=r['seller_address'],
                    buyer_address=r['buyer_address'],
                    tx_hash=r['tx_hash'],
                    url=r['url']                    
                )
        db.session.add(new_hist)
        db.session.commit()

        item = Item.query.get(r['item_id'])
        item.status = 'FUF'
        db.session.commit()


        new_fufill = Fufillment(
                    uuid = shortuuid.ShortUUID().random(length=16),
                    hist_id = new_hist.uuid,
                    created = datetime.now(),
                    seller = new_hist.seller,
                    buyer = new_hist.buyer,
                    tx_hash = new_hist.tx_hash,
                    url = new_hist.url,
                    status = 'open'                    
                )
        db.session.add(new_fufill)
        db.session.commit()

        new_message = Message(
                    uuid = shortuuid.ShortUUID().random(length=16),
                    fuf_id = new_fufill.uuid,
                    created = datetime.now(),
                    author = 'admin_bot',
                    text = 'Hello, here is the escrow channel',
                    type = 'automated'
                )
        db.session.add(new_message)
        db.session.commit()

        return 'ok', 200


@app.route('/v1/add_user_wallet/<username>', methods=['POST']) # add jwt private
def add_user_wallet(username):
    if request.method == 'POST':
        print('api - adding user wallet to public dir...')
        r = request.get_json()
        user = Dir.query.filter_by(username=username).one_or_none()
        user.eth_wallet = r['address']
        db.session.commit()

        return 'ok', 200


# app.route('/v1/wish/generate_metadata', methods=['POST'])
# def generate_item_metadata():
#     # in future, have a multiselect but atm ssense

#     # use the below in the future to pull the whole schema but atm just chill on the name, price, currency etc
#     user_agents = [ 
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
#         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
#         'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
#         'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
#     ] 
#     user_agent = random.choice(user_agents)
#     headers = {'User-Agent': user_agent} 

#     url = 'https://www.ssense.com/en-us/women/product/see-by-chloe/indigo-flared-emily-jeans/10049711'
#     html = requests.get(url, headers=headers) 

#     soup = BeautifulSoup(html.text, 'html.parser')
#     data = json.loads(soup.find('script', type='application/ld+json').text)

#     availability = data['offers']['availability'].split('/')[3]

    
#     return jsonify(name=data['name'], 
#                 brand=data['brand']['name'], 
#                 price=data['offers']['price'], 
#                 price_currency=data['offers']['priceCurrency'], 
#                 availability=availability,
#                 description=data['description'],
#                 image=data['image']
#                 ), 200


@app.route('/v1/fufill', methods=['POST'])
def get_user_fufillment():
    if request.method == 'POST':
        r = request.get_json()
        username = r['username']
        seller = Fufillment.query.filter_by(seller=username).all()
        buyer = Fufillment.query.filter_by(buyer=username).all()

        seller = [item.as_dict() for item in seller]
        buyer = [item.as_dict() for item in buyer]

        # print('seller: ', seller)
        # print('buyer: ', buyer)

        return jsonify(sell=seller, buy=buyer), 200

    return 'not ok', 500


@app.route('/v1/messages/<escrow_id>', methods=['GET', 'POST'])
def get_escrow_msg(escrow_id):
    if request.method == 'GET':
        messages = Message.query.filter_by(fuf_id=escrow_id).all()
        messages = [message.as_dict() for message in messages]

        return jsonify(messages=messages), 200



@app.route('/v1/wish/gen_metadata', methods=['POST'])
def gen_metadata():
    if request.method == 'POST':
        r = request.get_json()
        link = r['link']

        data_gen = generate_item_metadata(link)

        return data_gen, 200


@app.route('/v1/wish/add', methods=['POST'])
def add_wish():
    if request.method == 'POST':
        r = request.get_json()['wish']

        print(r)

        new_wish = Wish(
                uuid = shortuuid.ShortUUID().random(length=16),
                created=datetime.now(),
                creator=r['creator'],
                description=r['description'],
                items=r['items'],
                public=True,
                title=r['title']               
            )

        print('adding wish')
        db.session.add(new_wish)

        print('commit to db')
        db.session.commit()

        print('added wish')

        return 'ok', 200


@app.route('/v1/wish/get_all/<username>', methods=['GET'])
def get_all_wishlists(username):
    wishlists = Wish.query.filter_by(creator=username).all()
    wishlists = [wish.as_dict() for wish in wishlists]

    return jsonify(wishlists=wishlists), 200
















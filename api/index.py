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

    uuid = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String())
    owner = db.Column(db.String())
    owner_address = db.Column(db.String())
    brand = db.Column(db.String())
    colors = db.Column(JSONB)
    created = db.Column(TIMESTAMP(timezone=False), default=datetime.now())
    description =  db.Column(db.String())
    for_sale = db.Column(db.Boolean)
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


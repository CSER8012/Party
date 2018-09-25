from flask import Flask
from flask_mongoengine import MongoEngine
app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"
app.config['PROJECT_ID'] = 'partygo-app'
app.config['CLOUD_STORAGE_BUCKET'] = 'partygo-bucket'
app.config['MONGODB_SETTINGS'] = {
        'db': 'party',
        'host': 'ds149682.mlab.com',
        'port': 49682,
        'username': 'partyAdmin',
        'password': 'root2018',
    }
db = MongoEngine(app)


import datetime
class User(db.Document):
    username = db.StringField(required=True)
    email = db.StringField(required=True, unique = True)
    password = db.StringField(required=True)
    create = db.DateTimeField(default=datetime.datetime.now)
    bio = db.StringField(default='',max_length=200)
    profile_image = db.StringField()

class Party(db.Document):
    name = db.StringField(required=True)
    place = db.StringField(required=True)
    location = db.PointField(required=False)
    start_datetime = db.DateTimeField(required=True)
    end_datetime = db.DateTimeField(required=True)
    party_photo = db.StringField()
    description = db.StringField(min_length=20, required=True)
    host = db.ObjectIdField(required=True)
    cancel = db.BooleanField(default=False)
    attendees = db.ListField(db.ReferenceField(User))

from user_views import userage
app.register_blueprint(userage,url_prefix='/user')
from party_views import  party_page
app.register_blueprint(party_page,url_prefix='/party')

@app.route('/')
def sayhello():
    return "hello renteng!"







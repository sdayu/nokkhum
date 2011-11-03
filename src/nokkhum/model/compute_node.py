from mongoengine import *
import datetime
from users import User

class ComputeNode(Document):
    meta = {'collection': 'compute_node'}
    
    
    name    = StringField(max_length=100, required=True)
    system  = StringField(max_length=100, required=True)
    host    = StringField(max_length=100, required=True)
    machine = StringField(max_length=100, required=True)
    port    = IntField(required=True)
    cpu     = IntField(required=True)
    ram     = IntField(required=True) # ram in Kb
    
    create_date = DateTimeField(required=True, default=datetime.datetime.now())
    update_date = DateTimeField(required=True, default=datetime.datetime.now())


    
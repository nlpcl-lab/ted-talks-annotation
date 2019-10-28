import datetime
from flask_mongoengine import MongoEngine
import uuid
import hashlib
import logging

db = MongoEngine()


class Doc(db.Document):
    title = db.StringField(default='')
    source = db.StringField(default='')
    created_at = db.DateTimeField(default=datetime.datetime.now)
    type = db.StringField(default='v1')
    file_url = db.StringField(default='')

    def dump(self):
        return {
            'title': self.title,
            'text': self.text,
            'source': self.text,
        }


class Sent(db.Document):
    doc = db.ReferenceField(Doc)
    index = db.IntField()
    text = db.StringField()
    meta_text = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    start_ts = db.IntField()
    end_ts = db.IntField()

    sound_sum = db.IntField()
    sound_maximum = db.IntField()
    sound_minimum = db.IntField()

    meta = {
        'indexes': [
            'doc',
            {'fields': ('doc', 'index'), 'unique': True},
        ],
    }

    def dump(self):
        return {
            'index': self.index,
            'text': self.text,
            'meta_text': self.meta_text,
        }


class User(db.Document):
    username = db.StringField(default='')
    password = db.StringField(default='')
    salt = db.StringField(default='')
    first_name = db.StringField(default='')
    last_name = db.StringField(default='')

    last_ip = db.StringField(default='')
    accessed_at = db.DateTimeField(default=datetime.datetime.now)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    turker_id = db.StringField(default='')

    def set_password(self, password):
        self.salt = uuid.uuid4().hex
        self.password = hashlib.sha256(self.salt.encode() + password.encode()).hexdigest()

    def check_password(self, password):
        return self.password == hashlib.sha256(self.salt.encode() + password.encode()).hexdigest()

    def dump(self):
        return {
            'id': self.id,
            'username': self.username,
        }


class Annotation(db.Document):
    TYPE_TENSION = 'tension'
    TYPE_TENSION_V2 = 'tension_v2'
    TYPE_TENSION_V3 = 'tension_v3'
    TYPE_TENSION_V4 = 'tension_v4'
    TYPE_TENSION_V4_FAIL = 'tension_v4_fail'
    TYPE_ROLE = 'role'

    doc = db.ReferenceField(Doc)
    sent = db.ReferenceField(Sent)
    user = db.ReferenceField(User)

    type = db.StringField(default=TYPE_TENSION)

    index = db.IntField()

    target_text = db.StringField()

    basket = db.DictField()
    memo = db.StringField()

    first_focus_started_at = db.DateTimeField(default=datetime.datetime.now)
    first_input_viewed_at = db.DateTimeField(default=datetime.datetime.now)
    first_updated_at = db.DateTimeField(default=datetime.datetime.now)

    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': [
            ('doc', 'user', 'type'),
            {'fields': ('sent', 'user', 'type'), 'unique': True},
        ],
    }

    def dump(self):
        return {
            'id': str(self.id),
            'doc': str(self.doc.id),
            'sent': str(self.sent.id),
            'user': str(self.user.id),
            'type': self.type,
            'index': self.index,
            'target_text': self.target_text,
            'basket': self.basket,
            'memo': self.memo,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
        }

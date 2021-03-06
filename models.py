from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,  sessionmaker
from sqlalchemy import create_engine
import datetime
import random
import string
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature,  SignatureExpired)


Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)for
                     x in xrange(32))


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer(),  primary_key=True)
    username = Column(String(32),  index=True)
    password_hash = Column(String(64))

    # methods to support login manager
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

    def hash_password(self,  password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self,  password):
        return pwd_context.verify(password, self.password_hash)

    # def generate_auth_token(self, expiration=600):
    #     s = Serializer(secret_key, expires_in = expiration)
    #     print s.dumps({ 'id':self.id })
    #     return s.dumps({ 'id':self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # valid but expired
            return None
        except BadSignature:
            # BadSignature
            return None
        user_id = data['id']
        return user_id


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer,  primary_key=True)
    name = Column(String)
    items = relationship("Item", backref="category")
    created_by = Column(Integer)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        output_items = []
        for item in self.items:
            itm = {
                    'id': item.id,
                    'cat_id': self.id,
                    'description': item.description,
                    'item_name': item.item_name,
            }
            output_items.append(itm)

        return {
                'id': self.id,
                'Item': output_items,
                'name': self.name
                }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer,  primary_key=True)
    item_name = Column(String)
    description = Column(String)
    created_date = Column(DateTime,  default=datetime.datetime.utcnow)
    category_id = Column(Integer,  ForeignKey('category.id'))
    created_by = Column(Integer)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
                'id': self.id,
                'item_name': self.item_name,
                'created_date': self.created_date,
                'description': self.description,
                'category': self.category.name
                }


engine = create_engine('sqlite:///catalog.db', convert_unicode=True)
Base.metadata.create_all(engine)

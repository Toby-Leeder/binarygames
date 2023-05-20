""" database dependencies to support sqliteDB examples """
from random import randrange
from datetime import date
import os, base64
import json

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


class Gamer(db.Model):
    __tablename__ = 'gamers'  # table name is plural, class name is singular

    # Define the User schema with "vars" from object
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _bomb = db.Column(db.Integer, unique=False, nullable=True)

    # constructor of a User object, initializes the instance variables within object (self)
    def __init__(self, name, password="123qwerty", bomb=0):
        self._name = name    # variables with self prefix become part of the object, 
        self._bomb = bomb
        self.set_password(password)

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name
    
    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name

    # a name getter method, extracts name from object
    @property
    def bomb(self):
        return self._bomb
    
    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def bomb(self, bomb):
        self._bomb = bomb
    
    @property
    def password(self):
        return self._password[0:10] + "..." # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, method='sha256')

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result
    
    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            # creates a person object from User(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "pass": self.password,
            "bomb": self._bomb
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, dictionary):
        for key in dictionary:
            if key == "name":
                self.name = dictionary[key]
            if key == "bomb":
                self._bomb = dictionary[key]
            if key == "pass":
                self.set_password(dictionary[key])
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

def getUser(name):
    return Gamer.query.filter_by(_name = name).first()

"""Database Creation and Testing """


# Builds working data for testing
def initGamers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        u1 = Gamer(name='mouse', password='tiny')

        users = [u1]

        """Builds sample user/note(s) data"""
        for user in users:
            try:
                '''add a few 1 to 4 notes per user'''
                user.create()
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {user.uid}")
            
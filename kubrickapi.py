from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float
import os
from flask_marshmallow import Marshmallow

# define the flask app
kubrickapi = Flask(__name__)
# config settings for SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
# telling flask (sqlalchemy) where the database file will be stored/accessible to/from
kubrickapi.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'kubes.db')

# configure marshmallow
ma = Marshmallow(kubrickapi)

# initialise our database as a python object
db = SQLAlchemy(kubrickapi)


@kubrickapi.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database successfully created!')

# kubrickapi.cli.command('dp_drop')
# def db_drop():

# home page route (endpoint)
@kubrickapi.route('/')
def home():
    return jsonify(data='That this is the home page')


# RESTFUL APIs - well documented in how to use it:
# users / consumers of my api must provide a key=value pair
# in the format of:
# p=lastname  i.e. p=terry
@kubrickapi.route('/people')
def people():
    name = request.args.get('p')
    # retrieve records from a database
    peopledata = People.query.filter_by(lname=name).first()
    result = people_schema.dump(peopledata)
    return jsonify(result)


@kubrickapi.route('/addpeople', methods=['POST'])
def addpeople():
    fn = request.form['firstname']
    ln = request.form['lastname']
    em = request.form['emailaddress']
    # insert the data into the sqlite database
    new_people = People(fname=fn, lname=ln, email=em)
    db.session.add(new_people)
    db.session.commit()
    # result = successfailure flag
    # if insert succesful then return result
    # else return result
    return jsonify(data='People {} added to the database'.format(fn)), 201


@kubrickapi.route('/rempeople', methods=['GET', 'POST'])
def rempeople():
    # name = request.args.get('p')
    name = request.form['lastname']
    remperson = People.query.filter_by(lname=name).first()
    if remperson:
        db.session.delete(remperson)
        db.session.commit()
        return jsonify(data='Person with lastname {} removed from the database'.format(name))
    else:
        return jsonify(data='Person with lastname {} did not exist in the database'.format(name))


# in SQLAlchemy a Model is a table - we are creating a blueprint for our own table called People
class People(db.Model):
    __tablename__ = 'people'  # make a table called people
    id = Column(Integer, primary_key=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String, unique=True)


class PeopleSchema(ma.Schema):
    class Meta:
        fields=('id', 'fname', 'lname', 'email')


people_schema = PeopleSchema()

if __name__ == '__main__':
    kubrickapi.run()
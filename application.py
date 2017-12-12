from urlparse import urlparse,  urljoin
from models import Base,  Item,  Category, User
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,  sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template, redirect, url_for, request, abort,\
                  g, jsonify
from flask import session as login_session
from flask_login import login_manager, LoginManager, login_user, logout_user, \
    login_required
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.auth.transport import requests
from google.oauth2 import id_token
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = "client_secrets.json"
CLIENT_ID = "506667308951-5oe67n05mhm7l"+\
            "brikk73aremtrm45ihn.apps.googleusercontent.com"


engine = create_engine('sqlite:///catalog.db', convert_unicode=True)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

USE_SESSION_FOR_NEXT = True
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
    except Exception:
        user = None
    return user


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url,  target))
    return test_url.scheme in ('http',  'https') and \
        ref_url.netloc == test_url.netloc


@app.route('/')
def home():
    category = session.query(Category).all()
    items = session.query(Item).order_by(Item.created_date.desc()).all()
    return render_template('home.html', category=category, items=items)


@app.route('/catalog/json')
def catalog_serialize():
    category = session.query(Category).all()
    return jsonify(Category=[x.serialize for x in category])


@app.route('/tokensignin', methods=['POST'])
def tokensignin():
    if request.method == 'POST':
        token = request.form['idtoken']
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(),
                                                  CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com',
                                     'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google
            # Account ID from the decoded token.
            userid = idinfo['sub']
        except ValueError:
            # Invalid token
            pass
        try:
            user = session.query(User).\
                   filter_by(username=idinfo['email']).one()
            login_user(user)
            return idinfo['email']
        except:
            new_user = User(username=idinfo['email'])
            session.add(new_user)
            session.commit()
            login_user(new_user)
            return idinfo['email']


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        next = request.args.get('next')
        return render_template('login.html', next=next)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        next = request.form['next']
        if username == '' or password == '':
            return redirect(url_for('login'))
        else:
            user = session.query(User).filter_by(username=username).first()
            if not user or not user.verify_password(password):
                return redirect(url_for('login'))

            login_user(user)
            if not is_safe_url(str(next)):
                return abort(400)
            if next == 'None':
                return redirect(url_for('home'))
            else:
                return redirect(next)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'GET':
        users = session.query(User).all()
        return render_template('newuser.html', users=users)

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '' or password == '':
            return redirect(url_for('new_user'))
        elif session.query(User).filter_by(username=username).first() \
                is not None:
            return redirect(url_for('new_user'))
        user = User(username=username)
        user.hash_password(password)
        session.add(user)
        session.commit()

        return redirect(url_for('home'))


@app.route('/catalog/<string:category_name>/items')
def category(category_name):
    try:
        category_name = session.query(Category).\
            filter_by(name=category_name).one()
        items = session.query(Item).filter_by(category_id=category_name.id).\
            all()
        return render_template('category.html',
                               category_name=category_name, items=items)
    except:
        return redirect(url_for('home'))


@app.route('/catalog/<string:category_name>/<string:item_name>')
def catalogItem(category_name, item_name):
    return "this is the the category_item Page"


@app.route('/catalog/add/category', methods=['GET', 'POST'])
@login_required
def addCategory():
    if request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
            try:
                session.query(Category).filter_by(name=name).one()
                return render_template('addCat.html')
            except:
                category = Category(name=name)
                session.add(category)
                session.commit()
                return redirect(url_for('home'))
        else:
            return render_template('addCat.html')

    else:
        return render_template('addCat.html')


@app.route('/catalog/delete/category/<string:category_name>',
           methods=['GET', 'POST'])
@login_required
def deleteCategory(category_name):
    if request.method == 'GET':
        try:
            session.query(Category).filter_by(name=category_name).one()
            return render_template('deleteCat.html', name=category_name)
        except:
            return redirect(url_for('home'))
    elif request.method == 'POST':
        category_to_delete = session.query(Category)\
            .filter_by(name=category_name).one()
        items = session.query(Item)\
            .filter_by(category_id=category_to_delete.id).all()
        for i in items:
            session.delete(i)
        session.delete(category_to_delete)
        session.commit()
        return redirect(url_for('home'))


@app.route('/catalog/<string:category_name>/add/item/',
           methods=['GET', 'POST'])
@login_required
def addItem(category_name):
    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('addItem.html', categories=categories,
                               category_name=category_name)

    elif request.method == 'POST':
        categories = session.query(Category).all()
        category_names = request.form['category_name']
        try:
            item_name = request.form['name']
            item_description = request.form['description']
            item_category = request.form['category']
            item_to_add = Item(item_name=item_name,
                               description=item_description,
                               category_id=item_category)
        except:
            return render_template('addItem.html', categories=categories,
                                   category_name=category_names)
        try:
            session.query(Item).filter_by(item_name=item_name).one()
            return render_template('addItem.html', categories=categories,
                                   category_name=category_names)

        except:
            if item_name == '' or item_description == '':
                return render_template('addItem.html', categories=categories,
                                       category_name=category_names)
            else:
                try:
                    session.query(Category).filter_by(id=item_category).one()
                    session.add(item_to_add)
                    session.commit()
                    return redirect(url_for('home'))
                except:
                    return render_template('addItem.html',
                                           categories=categories,
                                           category_name=category_names)


@app.route('/catalog/<string:item_name>/update/item/', methods=['GET', 'POST'])
@login_required
def updateItem(item_name):
    if request.method == 'GET':
        item = session.query(Item).filter_by(item_name=item_name).one()
        return render_template('updateItem.html', item=item)
    elif request.method == 'POST':
        item = session.query(Item).filter_by(item_name=item_name).one()
        item.item_name = request.form['name']
        item.description = request.form['description']
        session.add(item)
        session.commit()
        return redirect(url_for('itemDescription', item_name=item.item_name))


@app.route('/catalog/delete/<string:item_name>/')
@login_required
def deleteItem(item_name):
    if request.method == 'GET':
        item_to_delete = session.query(Item)\
            .filter_by(item_name=item_name).one()
        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('home'))


@app.route('/catalog/<string:item_name>/description', methods=['GET', 'POST'])
def itemDescription(item_name):
    if request.method == 'GET':
        item = session.query(Item).filter_by(item_name=item_name).one()
        return render_template('itemDescription.html', item=item)
    elif request.method == 'POST':
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0',  port=8080)

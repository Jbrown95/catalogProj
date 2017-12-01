from flask import Flask,render_template,redirect,url_for,request,abort, g
from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

# database modules
from models import Base, Item, Category,User
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    print(user.username)
    print(1)
    return True




@app.route('/')
def home():
    category = session.query(Category).all()
    items = session.query(Item).order_by(Item.created_date.desc()).all()
    return render_template('home.html',category=category,items=items)


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        if username == '' or password == '':
            return redirect(url_for('login'))
        else:
            user = session.query(User).filter_by(username = username).first()
            if not user or not user.verify_password(password):
                return redirect(url_for('login'))
            g.user = user
            token = g.user.generate_auth_token()
            return redirect(url_for('home'))

@app.route('/logout')
def logout():
    g.user = ''
    return redirect(url_for('home'))

@app.route('/new_user',methods=['GET','POST'])
def new_user():
    if request.method =='GET':
        users = session.query(User).all()
        return render_template('newuser.html',users=users)

    elif request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        if username == '' or password == '':
            return redirect(url_for('new_user'))
        elif session.query(User).filter_by(username=username).first() is not None:
            return redirect(url_for('new_user'))
        user = User(username = username)
        user.hash_password(password)
        session.add(user)
        session.commit()
        return redirect(url_for('home'))


@app.route('/catalog/<string:category_name>/items')
def category(category_name):
    try:
        category_name = session.query(Category).filter_by(name = category_name).one()
        items = session.query(Item).filter_by(category_id=category_name.id).all()
        return render_template('category.html',category_name=category_name,items=items)
    except:
        return redirect(url_for('home'))

@app.route('/catalog/<string:category_name>/<string:item_name>')
def catalogItem(category_name,item_name):
    return "this is the the category_item Page"


@app.route('/catalog/add/category',methods=['GET','POST'])
@auth.login_required
def addCategory():
    print
    if request.method == 'GET':
        return render_template('addCat.html')
    elif request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
            try:
                session.query(Category).filter_by(name = name).one()
                return render_template('addCat.html')
            except:
                category = Category(name = name)
                session.add(category)
                session.commit()
                return redirect(url_for('home'))
        else:
            return render_template('addCat.html')

    else:
        return "NOPE"


@app.route('/catalog/delete/category/<string:category_name>',methods=['GET','POST'])
def deleteCategory(category_name):
    if request.method == 'GET':
        try:
            session.query(Category).filter_by(name = category_name).one()
            return render_template('deleteCat.html',name = category_name)
        except:
            return redirect(url_for('home'))
    elif request.method == 'POST':
        category_to_delete = session.query(Category).filter_by(name = category_name).one()
        items = session.query(Item).filter_by(category_id=category_to_delete.id).all()
        for i in items:
            session.delete(i)
        session.delete(category_to_delete)
        session.commit()
        return redirect(url_for('home'))


@app.route('/catalog/add/item',methods=['GET','POST'])
def addItem():
    if request.method == 'GET':
        categories = session.query(Category).all()
        return render_template('addItem.html',categories=categories)
    elif request.method == 'POST':
        categories = session.query(Category).all()
        try:
            item_name = request.form['name']
            item_description = request.form['description']
            item_category = request.form['category']
            item_to_add = Item(item_name=item_name,description=item_description,category_id=item_category)
            print(1)
        except:
            return render_template('addItem.html',categories=categories)
        try:
            session.query(Item).filter_by(item_name=item_name).one()
            return render_template('addItem.html',categories=categories)

        except:
            if item_name == '' or item_description == '':
                return render_template('addItem.html',categories=categories)
            else:
                print(2)
                print (item_category)
                try :
                    session.query(Category).filter_by(id=item_category).one()
                    print (item_category)
                    session.add(item_to_add)
                    session.commit()
                    return redirect(url_for('home'))
                except:
                    return render_template('addItem.html',categories=categories)




@app.route('/catalog/delete/<string:item_name>/')
def deleteItem(item_name):
    if request.method == 'GET':
        item_to_delete = session.query(Item).filter_by(item_name=item_name).one()
        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('home'))



@app.route('/catalog/<string:item_name>/description',methods=['GET','POST'])
def itemDescription(item_name):
    if request.method == 'GET':
        item = session.query(Item).filter_by(item_name=item_name).one()
        return render_template('itemDescription.html',item=item)
    elif request.method == 'POST':
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)

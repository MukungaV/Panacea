from flask import Flask , flash
from flask import render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required,LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
#from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///drugs.sqlite'
app.config['SECRET_KEY'] = 'Top secret'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ '/WebProject/static/images'
app.config['IMAGE_UPLOAD'] = BASE_DIR  #'C:/Users/user/Desktop/Muchiri Python/FlaskPro/static'

db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# class Drugs(db.Model):
#     id = db.Column(db.Integer,primary_key=True)
#     name = db.Column(db.String(20),unique=True)
#     date_created = db.Column(db.DateTime)
#     uses = db.Column(db.String, unique=False, nullable=True)
#     side_effects = db.Column(db.String,unique=False, nullable=True)
#     overdose = db.Column(db.String,unique=False, nullable=True)
#     reviews = db.Column(db.String, unique=False, nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    price = db.Column(db.INTEGER, nullable=False, unique=False)
    image = db.Column(db.String(100), nullable=False, unique=False)
    uses = db.Column(db.VARCHAR(300), nullable=True, unique=False)
    reviews = db.Column(db.VARCHAR(300), nullable=True, unique=False)
    side_effects = db.Column(db.VARCHAR(300), nullable=True, unique=False)
    overdose = db.Column(db.VARCHAR(300), nullable=True, unique=False)

    def __repr__(self):
        return 'Name {}'.format(self.name)





@app.route('/')
def home():
    return render_template('home.html', title='Title')

@app.route('/demo')
def demo():
    return render_template('demo.html', title='demo')


# @app.route('/drugs', methods=['GET','POST'])
# def drugs():
#     if request.form:
#         name = request.form.get('name')
#         date_created = request.form.get('date')
#         uses = request.form.get('uses')
#         side_effects = request.form.get('side_effects')
#         overdose = request.form.get('overdose')
#         reviews = request.form.get('reviews')
#
#         drug = Drugs(
#             name=name,
#             date_created=date_created,
#             uses=uses,
#             side_effects=side_effects,
#             overdose=overdose,
#             reviews=reviews)
#
#         db.session.add(drug)
#         db.session.commit()
#
#     drugs = Drugs.query.all()
#     return render_template('DrugsPage.html',title='Drugs',drugs=Drugs)
#


@app.route('/podcasts')
def podcasts():
    return render_template('Podcasts.html', title='Podcasts')

@app.route('/news')
def news():
    return render_template('news.html', title='News')



class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    first_name = db.Column(db.String(200),nullable=False)
    last_name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100),nullable=False)


@app.route('/signup', methods = ["GET","POST"])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        password = generate_password_hash(password)

        user = User(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', title="Signup")

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if check_password_hash(user.password, password):
            login_user(user)
            flash(u'You were successfully logged in','alert alert-success')
            return redirect(url_for('home'))
        flash(u'Your login credentials are not correct, try again or signup','alert alert-danger')
        return redirect('/login')
    return render_template('login.html', title="Login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(u'We\'re sorry to see you go!', 'alert alert-success')
    return redirect('/')


@app.route('/products', methods = ['GET', 'POST'])
def products():
    if request.form and request.files:  # if request is post
        # grab file/image data
        uploaded_image = request.files['productimage']

        # secure the filename()
        filename = secure_filename(uploaded_image.filename)

        # location for storing image : FlaskPro/static/images/name_of_image
        image = '{}/{}/{}'.format('static', 'images', filename)

        # image upload
        uploaded_image.save(os.path.join(app.config['IMAGE_UPLOAD'], filename))
        print(filename)

        # grab form data
        name = request.form.get('productname')
        price = request.form.get('productprice')
        uses = request.form.get('productuses')
        reviews = request.form.get('productreviews')
        side_effects = request.form.get('productside_effects')
        overdose = request.form.get('productoverdose')

        # create a product instance/object
        product = Product(
            name=name,
            price=price,
            image=image,
            uses = uses,
            reviews = reviews,
            side_effects = side_effects,
            overdose = overdose
        )

        # save data into the db
        db.session.add(product)
        db.session.commit()
        flash(u'Product uploaded successfully!', 'alert alert-success')
        return redirect(url_for('products'))
    # if user is not posting show them available products
    # get the products from the db
    products = Product.query.all()  # get all products from db
    return render_template('products.html', title='MyPharma', products=products)

# @login_required
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.form and request.files:  # if request is post
        # grab file/image data
        uploaded_image = request.files['productimage']

        # secure the filename()
        filename = secure_filename(uploaded_image.filename)

        # location for storing image : FlaskPro/static/images/name_of_image
        image = '{}/{}/{}'.format('static', 'images', filename)

        # image upload
        uploaded_image.save(os.path.join(app.config['IMAGE_UPLOAD'], filename))
        print(filename)

        # grab form data
        name = request.form.get('productname')
        price = request.form.get('productprice')
        uses = request.form.get('uses')
        reviews = request.form.get('reviews')
        side_effects = request.form.get('side_effects')
        overdose = request.form.get('overdose')


        # create a product instance/object
        product = Product(
            name=name,
            price=price,
            image=image,
            uses=uses,
            reviews=reviews,
            side_effects=side_effects,
            overdose=overdose
        )
        print(overdose)

        # save data into the db
        db.session.add(product)
        db.session.commit()
        flash(u'Product uploaded successfully!', 'alert alert-success')
        return redirect(url_for('products'))
    # if user is not posting show them available products
    # get the products from the db
    products = Product.query.all()  # get all products from db
    return render_template('upload.html', title='Upload Products', products=products)

@app.route('/products/update/<int:product_id>/' , methods=['GET', 'POST'])
def update(product_id):
    product = Product.query.get(product_id)
    if request.form: #=POSTING
        name = request.form.get('productname')
        price = request.form.get('productprice')
        uses = request.form.get('uses')
        reviews = request.form.get('reviews')
        side_effects = request.form.get('side_effects')
        overdose = request.form.get('overdose')

        #assign new values to the product
        product.name = name
        product.price = price
        uses = uses
        reviews = reviews
        side_effects = side_effects
        overdose = overdose


        #save the new details of the product to db
        db.session.commit()
        return redirect('/products')

    return render_template('update.html' , product = product)

@app.route('/products/delete/<int:product_id>')
def delete (product_id):
    product = Product.query.get(product_id)
    print(product)
    db.session.delete(product)
    db.session.commit()
    return redirect('/products')

@app.route('/products/<int:product_id>', )
def detail(product_id):
    product = Product.query.get(product_id)
    image = product.image
    print(image)
    return render_template('detail.html', product=product, image=image)


@app.route('/lifestyle')
def lifestyle():
    return render_template('lifestyle.html', title = 'Lifestyle')

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash(u'We\'re sad to see you go!', 'alert alert-success')
#     return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

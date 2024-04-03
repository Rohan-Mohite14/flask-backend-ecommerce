from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User,Product,Wishlist


@app.route('/')
@app.route('/index')
@login_required
def index():
    # Fetch products from the database
    products = Product.query.all()
    return render_template('index.html', title='Home', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/wishlist/add/<int:product_id>', methods=['POST','GET'])
@login_required
def add_to_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    if current_user.wishlist.filter_by(product_id=product_id).first() is None:
        wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Product added to wishlist')
    else:
        flash('Product already in wishlist')
    return redirect(url_for('index'))

@app.route('/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    wishlist_item = current_user.wishlist.filter_by(product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Product removed from wishlist')
    else:
        flash('Product not found in wishlist')
    return redirect(url_for('index'))

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = current_user.wishlist.all()
    return render_template('wishlist.html', title='Wishlist', wishlist_items=wishlist_items)

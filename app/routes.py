from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, login_required, logout_user

from app import app, db
from app.forms import RegistrationForm, LoginForm
from app.models import Blog, User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/articles')
@login_required
def articles():
    posts = Blog.query.order_by(Blog.date.desc()).all()
    if not posts:
        flash('There are no articles yet.')
    return render_template('articles.html', posts=posts)


@app.route('/articles/<int:id>')
@login_required
def article(id):
    post = Blog.query.get(id)
    return render_template('article.html', post=post)


@app.route('/articles/<int:id>/delete')
def article_delete(id):
    post = Blog.query.get_or_404(id)

    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('articles'))
    except:
        return 'Error occured while deleting the article'


@app.route('/create_article', methods=['POST', 'GET'])
@login_required
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        post = Blog(title=title, intro=intro, text=text)
        try:
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('articles'))
        except:
            return 'Error occured while adding the article to db'
    else:
        return render_template('create_article.html')


@app.route('/articles/<int:id>/update', methods=['POST', 'GET'])
@login_required
def update_article(id):
    post = Blog.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.intro = request.form['intro']
        post.text = request.form['text']

        try:
            db.session.commit()
            return redirect(url_for('articles'))
        except:
            return 'Error occured while updating the article'
    else:
        return render_template('update_article.html', post=post)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next_ = request.args.get("next")
            return redirect(next_ or url_for('index'))
        flash('Invalid mail or password.')
    return render_template('signin.html', form=form)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password1.data)
        if not user:
            db.session.add(user)
            db.session.commit()
            flash("You've successfully signed up")
            return redirect(url_for('signin'))
        flash("You are registered already. Sign in, please")
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/forbidden", methods=['GET', 'POST'])
@login_required
def protected():
    return redirect(url_for('signin'))


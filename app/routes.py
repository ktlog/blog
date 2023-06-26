from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, login_required, logout_user

from app import app, db
from app.forms import RegistrationForm, LoginForm
from app.models import Blog, User


@app.route('/')
@login_required
def index():
    user = current_user
    return render_template('index.html', user=user)


@app.route('/articles')
@login_required
def articles():
    user_id = current_user.id
    posts = db.session.query(Blog).filter_by(user_id=user_id).order_by(Blog.date.desc()).all()
    if not posts:
        flash('There are no articles yet.')
    return render_template('articles.html', posts=posts)


@app.route('/articles/<int:id>')
@login_required
def article(id):
    post = db.session.query(Blog).get(id)
    return render_template('article.html', post=post)


@app.route('/articles/<int:id>/delete')
def article_delete(id):
    post = db.session.query(Blog).get_or_404(id)

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
        user_id = current_user.id

        post = Blog(title=title, intro=intro, text=text, user_id=user_id)
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
    post = db.session.query(Blog).get_or_404(id)
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


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if email and password:
            user = db.session.query(User).filter_by(email=email).first()
            if user is not None and user.check_password(password):
                login_user(user)
                flash('Successfully signed in.')
                next_ = request.args.get("next")
                return redirect(next_ or url_for('index'))
            flash('Invalid mail or password.')
            return redirect(url_for('signin'))
        flash('Fill in the fields.')
        return redirect(url_for('signin'))
    return render_template('signin.html', form=form)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password1 = form.password1.data
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            flash('User exists. Sign in, please.')
            return redirect(url_for('signin'))
        new_user = User(username=username, email=email)
        new_user.set_password(password1)
        db.session.add(new_user)
        db.session.commit()
        flash("You've successfully signed up")
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('signin') + '?next=' + request.url)
    return response

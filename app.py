from flask import Flask, render_template, request, redirect, url_for, abort
from models import db, Category, Article, User
from forms import ArticleForm, LoginForm, RegisterForm
from flask_migrate import Migrate
from flask_login import LoginManager, login_user
import locale

locale.setlocale(locale.LC_ALL, '')
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db.init_app(app)
migrate = Migrate(app, db)
login = LoginManager(app)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def homepage():
    return render_template('index.html', header='Последние статьи', articles=Article.query.all())


@app.route('/login')
def login():
    login_form = LoginForm()
    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        name = register_form.name.data
        password = register_form.password.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            abort(400)
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('homepage'))
    return render_template('register.html', form=register_form)


@app.route('/articles/new', methods=['GET', 'POST'])
def create_article():
    article_form = ArticleForm()
    if article_form.validate_on_submit():
        title = article_form.title.data
        body = article_form.body.data
        category_id = article_form.category_id.data
        author_id = article_form.author_id.data

        article = Article(title=title, body=body, category_id=category_id, author_id=author_id)
        db.session.add(article)
        db.session.commit()

        return redirect(url_for('homepage'))

    return render_template('new_article.html', form=article_form)


@app.route('/articles/<int:article_id>')
def get_article(article_id):
    return render_template('article.html', article=Article.query.get_or_404(article_id))


@app.route('/search')
def search():
    text = request.args['text']
    result = Article.query.filter(db.or_(
        Article.title.like(f'%{text}%'),
        Article.body.like(f'%{text}%')
    )).all()

    if len(result) == 1:
        return redirect(url_for('get_article', article_id=result[0].id))

    return render_template('index.html', header=f'Поиск по слову "{text}"', articles=result)


@app.route('/category/<int:category_id>')
def category_articles(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('category.html', category=category)


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.context_processor
def inject_categories():
    return {'categories': Category.query.all()}


@app.template_filter('datetime_format')
def datetime_format(value, format='%H:%M %x'):
    return value.strftime(format)


if __name__ == '__main__':
    app.run()

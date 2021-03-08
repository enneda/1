from flask import Flask, render_template, request, redirect, url_for
from models import db, Category, Article
from flask_migrate import Migrate
import locale

locale.setlocale(locale.LC_ALL, '')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def homepage():
    return render_template('index.html', header='Последние статьи', articles=Article.query.all())


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

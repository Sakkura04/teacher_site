from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db_funcs
from keyy import secret_key

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
app.secret_key = secret_key


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True) #primary_key - unique field
    title = db.Column(db.String(100), nullable = False) #100 - allowablelength of Str, nullable - can't be empty
    intro = db.Column(db.String(300), nullable = False) #nullable - can't be empty
    text = db.Column(db.Text, nullable = False)#data type Text is for long textes
    date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):  #when we choose any object, u'll also get an id
        return '<Article %r>' % self.id


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def registration():
    if not db_funcs.table_exists('users'):
        db_funcs.create_table()

    if request.method == 'POST':
        # Отримуємо дані форми
        name = request.form['name']
        surname = request.form['surname']
        midname = request.form['midname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Зберігаємо дані користувача у базі даних
        db_funcs.insert_table(name, surname, midname, email, phone, password)

        # Перенаправляємо користувача на іншу сторінку
        return redirect(url_for('index'))
    return render_template('sign_up.html')


@app.route('/log_in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if db_funcs.get_from_table(email, password):
            return redirect(url_for('index'))
    return render_template('log_in.html')




# recieve data - post, just go to page - get
@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == 'POST': # indicates that a form was submitted to the server
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article (title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "Lazsha"

    else:
        return render_template('create-article.html')


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all() #query- enquiry to db
    return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')
def post_more(id):
    article = Article.query.get(id)
    return render_template('post_detail.html', articles=article)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    article = Article.query.get_or_404(id) #in case there no such an article, mistake will be recieved
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "Mistake:("


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get_or_404(id)
    if request.method == 'POST':  # indicates that a form was submitted to the server
        article.title = request.form['title'].strip()  # Remove leading/trailing whitespace
        article.intro = request.form['intro'].strip()
        article.text = request.form['text'].strip()

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "Error updating post"
    else:
        article = Article.query.get_or_404(id)
        return render_template('post_update.html', article=article)





# щоб витягнути з юрл інфу робимо <Type: name>
@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return 'babe, ur name\'s ' + name + ' ' + str (id)

#щоб за різними адресами був однаковий вивід прописуємо:
@app.route('/hay_peach')
@app.route('/peach')
def Sassy():
    return 'Sassy'



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)
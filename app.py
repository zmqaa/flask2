from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
import click
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'zmq'

#初始化db
db = SQLAlchemy(app)
#初始化flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user



@click.command()
@click.option('--drop', is_flag=True, help='删除表并创建新表') #在更新模型的时候使用--drop参数可以创建数据库和带新字段的表
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('数据库已初始化')

@click.command()
def dropdb():
    db.drop_all()
    click.echo('数据库已删除')



app.cli.add_command(initdb)
app.cli.add_command(dropdb)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False) #唯一，不可为空
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(123), unique=True, nullable=False)
    avatar = db.Column(db.String(200))  #头像的url

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<用户 {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  #默认时间
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<文章> {self.title}'
@app.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts) #把变量传给html


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #获取请求输入的用户名和密码
        username = request.form['username']
        password = request.form['password']
        #查找输入的用户名
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)  #用了flask-login可以用current_user等便利
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码输入错误')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('已登出')
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # 检查用户名或邮箱是否已经存在
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('用户名或邮箱已存在，请选择其他。')
            return redirect(url_for('register'))

        # 创建新的用户并保存到数据库
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # 通过 set_password 方法保存哈希密码
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功，请登录！')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)

    # 检查当前用户是否有权限删除这篇文章（例如是否是文章的作者）
    if post.author_id != current_user.id:
        flash('你没有权限删除此文章。', 'error')
        return redirect(url_for('index'))

    # 删除文章
    db.session.delete(post)
    db.session.commit()

    flash('文章已删除。', 'success')
    return redirect(url_for('index'))

@app.route('/create', methods=["GET", "POST"])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('创建成功')
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/edit/<int:post_id>', methods=['GET','POST'])
def edit(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()  #因为是修改已经在跟踪对象所以不用add
        flash('修改成功')
        return redirect(url_for('index'))

    return render_template('edit.html', post=post)


if __name__ == '__main__':
    app.run(debug=True)

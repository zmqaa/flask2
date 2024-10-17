from flask import render_template, redirect, url_for, request, flash
from app import app, db
from models import User, Post
from flask_login import current_user, logout_user, login_user

@app.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts) #把变量传给html

#登录视图
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

    return redirect(url_for('login'))

#登出视图
@app.route('/logout')
def logout():
    logout_user()
    flash('已登出')
    return redirect(url_for('login'))

#新建帖子
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

#编辑原有帖子,接受参数post_id
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

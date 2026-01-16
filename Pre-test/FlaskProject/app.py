from flask import Flask,request, redirect
import config
app = Flask(__name__)
app.config.from_object(config)
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
@app.route('/profile')
def profile():
    return '这是个人中心！'
@app.route('/blog/<blog_id>')
def blog(blog_id):
    return f'您访问的博客id是：{blog_id}'
@app.route('/blog')
def blog_details():
    blog_id = request.args.get('blog_id')
    return f'您访问的博客id是：{blog_id}'
@app.route('/blog/list')
def blog_list():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    return f'页码：{page},size:{size}'

@app.route('/blog/add',methods = ['POST','GET'])
def blog_add():
    return '博客添加成功！'

@app.get('/login')
def login():
    return '登录页面！'

@app.get('/pub')
def pub():
    name = request.args.get('name')
    if name is None:
        return redirect('/login')
    else:
        return '发布页面！'


if __name__ == '__main__':
    app.run()

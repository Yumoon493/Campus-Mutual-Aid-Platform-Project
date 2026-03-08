from flask import Flask, request, session, redirect, url_for, render_template_string
from config import Config
from models import db, User, Task ,Feedback
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'some_secret_key_12345'
db.init_app(app)

@app.route('/')
def index():
    return '''
        <div style="text-align: center; margin-top: 50px; font-family: Arial, sans-serif;">
            <h1>欢迎来到校园互助平台</h1>
            <p style="color: #666; max-width: 600px; margin: 20px auto; line-height: 1.6;">
                这是一个基于<b>时间银行</b>机制的互助社区。在这里，你可以通过帮助同学（如代取快递、学习辅导）来赚取积分，
                并使用积分换取他人的帮助。让校园生活更高效、更温暖！
            </p>
            <div style="margin-top: 30px;">
                <a href="/login" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">立即登录</a>
                <a href="/register" style="padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">加入我们 (注册)</a>
            </div>
            <br><br>
            <img src="https://img.icons8.com/illustrations/external-pack-flat-juicy-fish-outline-juicy-fish/256/external-campus-university-pack-flat-juicy-fish-outline-juicy-fish.png" width="200">
        </div>
    '''

# ================= 1. 注册功能 (Scenario A) =================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # 提供返回登录的链接 [cite: 85]
        return '''
            <h2>欢迎注册校园互助平台</h2>
            <form method="post">
                用户名: <input type="text" name="u_name" required><br><br>
                邮  箱: <input type="email" name="u_email" required><br><br>
                密  码: <input type="password" name="u_pwd" required><br><br>
                <input type="submit" value="立即注册">
            </form>
            <p>已有账号？<a href="/login">立即登录</a></p>
        '''

    name = request.form.get('u_name')
    email = request.form.get('u_email')
    pwd = request.form.get('u_pwd')

    # 检查重名
    if User.query.filter_by(username=name).first():
        return "用户名已存在！<a href='/register'>返回修改</a>"

    # 创建新用户，系统会自动初始化 2 积分 [cite: 86, 87]
    new_user = User(
        username=name,
        email=email,
        password_hash=generate_password_hash(pwd)
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        # 注册成功后，引导回登录界面 [cite: 87, 88]
        return f"注册成功！{name}，你获得了 2 小时初始积分。<br><a href='/login'>点此去登录</a>"
    except Exception as e:
        db.session.rollback()
        return f"注册失败: {e}"


# ================= 2. 登录功能 (带注册引导) =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
            <h2>用户登录</h2>
            <form method="post">
                用户名: <input type="text" name="u_name" required><br><br>
                密  码: <input type="password" name="u_pwd" required><br><br>
                <input type="submit" value="登录">
            </form>
            <hr>
            <p>还没有账号？<a href="/register">点击这里去注册</a></p>
        '''

    name = request.form.get('u_name')
    pwd = request.form.get('u_pwd')
    user = User.query.filter_by(username=name).first()

    # 校验：如果找不到用户，提示去注册
    if not user:
        return "数据库中未找到该用户信息，请先去注册！<br><a href='/register'>前往注册页面</a>"

    # 校验密码
    if check_password_hash(user.password_hash, pwd):
        session['user_id'] = user.id
        session['user_name'] = user.username
        session['user_role'] = user.role
        return redirect(url_for('lobby'))
    else:
        return "密码错误！<a href='/login'>返回重试</a>"


# ================= 6. 登出界面 (Logout) =================

@app.route('/logout')
def logout():
    # 1. 清除当前用户的 session 会话信息
    session.clear()

    # 2. 返回一个温馨的欢送页面
    return '''
        <div style="text-align: center; margin-top: 50px; font-family: Arial, sans-serif;">
            <img src="https://img.icons8.com/clouds/100/000000/handshake.png"/>
            <h2 style="color: #333;">欢送：期待下一次登录！</h2>
            <p style="color: #777;">感谢你对校园互助社区的贡献，祝你今天过得愉快。</p>
            <div style="margin-top: 20px;">
                <a href="/" style="text-decoration: none; color: #2196F3; font-weight: bold;">← 返回首页</a>
            </div>
        </div>
    '''




# ================= 2. 任务大厅 (根据 Session 自动变幻按钮) =================

@app.route('/lobby')
def lobby():
    # 检查是否登录
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # 获取当前登录用户信息
    curr_user = User.query.get(user_id)
    # 获取所有待领取的任务
    tasks = Task.query.filter_by(status=0).all()

    html = f"<h2>校园互助大厅</h2>"
    html += f"<p>当前登录：<b>{curr_user.username}</b> | 余额：{curr_user.balance} | <a href='/logout'>退出</a></p>"

    if curr_user.role == 0:
        html += '<p><a href="/post_task">发布新任务</a> | <a href="/my_tasks">我的任务</a></p>'

    html += '<table border="1" cellpadding="8"><tr><th>标题</th><th>悬赏(小时)</th><th>发布人ID</th><th>操作</th></tr>'

    for t in tasks:
        html += f'<tr><td>{t.title}</td><td>{t.reward_points}</td><td>{t.publisher_id}</td><td>'

        # 逻辑判断
        if curr_user.role == 1:  # 如果是管理员
            html += f'<a href="/admin_delete/{t.id}" style="color:red">撤销(违规)</a>'
        elif t.publisher_id == curr_user.id:  # 如果是自己发的
            html += '<span>(我发布的)</span>'
        else:  # 普通用户且不是自己发的
            html += f'<a href="/claim/{t.id}">抢单</a>'

        html += '</td></tr>'

    html += '</table>'
    return html


# ================= 3. 发布任务 (自动预扣分) =================

@app.route('/post_task', methods=['GET', 'POST'])
def post_task():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('login'))
    user = User.query.get(user_id)

    if request.method == 'POST':
        title = request.form.get('title')
        points = int(request.form.get('points'))
        desc = request.form.get('desc') # --- 1. 接收描述 ---

        if user.balance < points:
            return "余额不足！<a href='/post_task'>返回</a>"

        user.balance -= points
        # --- 2. 存入数据库 ---
        new_task = Task(title=title, description=desc, reward_points=points, publisher_id=user.id, status=0)

        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('lobby'))

    return f'''
        <h3>发布任务 (当前余额: {user.balance})</h3>
        <form method="post">
            标题: <input type="text" name="title" required><br><br>
            积分: <input type="number" name="points" min="1" required><br><br>
            详情: <br><textarea name="desc" rows="3" placeholder="写点具体要求..."></textarea><br><br>
            <input type="submit" value="确认发布并预扣积分">
        </form>
    '''

# ================= 4. 接单与结算 =================

@app.route('/claim/<int:task_id>')
def claim_task(task_id):
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('login'))

    task = Task.query.get(task_id)
    if task and task.status == 0:
        task.status = 1
        task.taker_id = user_id
        db.session.commit()
    return redirect(url_for('lobby'))


# ================= 更新后的 my_tasks (包含撤销按钮) =================
@app.route('/my_tasks')
def my_tasks():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('login'))

    my_pub = Task.query.filter_by(publisher_id=user_id).order_by(Task.create_time.desc()).all()
    my_take = Task.query.filter_by(taker_id=user_id).order_by(Task.create_time.desc()).all()

    # 辅助函数：查是否已评价
    def has_feedback(t_id):
        # 注意：这里需要确保 Feedback 模型已正确导入且表名正确
        # 如果 Feedback 表未定义或未导入，这行会报错
        # 假设 Feedback 模型存在且可用
        return Feedback.query.filter_by(task_id=t_id).first() is not None

    html = "<h3>我的任务中心</h3><p><a href='/lobby'>返回大厅</a></p>"

    html += "<h4>我发布的 (需评价后才扣款)</h4><ul>"
    for t in my_pub:
        # --- 修改开始：针对待领取任务添加撤销按钮 ---
        if t.status == 0:
            # 只有待领取的任务可以撤销
            status_html = f"<span>[待领取]</span> <a href='/revoke/{t.id}' style='color:red; margin-left:10px;' onclick=\"return confirm('确定要撤销并退回积分吗？')\">撤销任务</a>"
        # --- 修改结束 ---
        elif t.status == 1:
            status_html = f"<span style='color:blue'>[进行中]</span> <a href='/settle/{t.id}'>点击验收</a>"
        else:  # status == 2
            # 检查是否已评价（需要 Feedback 模型支持）
            try:
                if has_feedback(t.id):
                    status_html = "<span style='color:green'>[已结单] (积分已付)</span>"
                else:
                    status_html = f"<span style='color:red'>[待评价]</span> <a href='/feedback/{t.id}' style='font-weight:bold; color:red'>去评价并支付积分</a>"
            except:
                 # 如果 Feedback 查询出错（比如表还没建），降级处理
                 status_html = "<span style='color:green'>[已完成]</span>"

        html += f"<li>{status_html} {t.title} ({t.reward_points}分)</li>"
    html += "</ul>"

    html += "<h4>我接取的 (等待对方评价后到账)</h4><ul>"
    for t in my_take:
        if t.status == 1:
            status_str = "进行中"
        elif t.status == 2:
            try:
                if has_feedback(t.id):
                    status_str = "<span style='color:green'>已完成 (积分已到账)</span>"
                else:
                    status_str = "<span style='color:orange'>已完工 (等待对方评价放款)</span>"
            except:
                status_str = "已完成"
        else:
            status_str = "状态未知"

        html += f"<li>{t.title} - {status_str}</li>"
    html += "</ul>"

    return html


@app.route('/settle/<int:task_id>')
def settle(task_id):
    user_id = session.get('user_id')
    task = Task.query.get(task_id)

    # 校验：必须是发布者，且任务处于进行中
    if task.publisher_id == user_id and task.status == 1:
        # 【重要改动】这里不再转积分了！只改状态！
        task.status = 2  # 状态变为 2 (工作完成，等待评价)

        db.session.commit()
        # 提示语也变了，告诉用户必须去评价
        return f"工作已确认！请去【我的任务】中填写评价，评价提交后积分将自动转给对方。<a href='/my_tasks'>去评价</a>"

    return "操作非法"

# ================= 5. 管理员撤销 (退还积分) =================

@app.route('/admin_delete/<int:task_id>')
def admin_delete(task_id):
    if session.get('user_role') != 1:
        return "你不是管理员！"

    task = Task.query.get(task_id)
    if task:
        # 退还积分给发布者
        pub = User.query.get(task.publisher_id)
        pub.balance += task.reward_points
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('lobby'))


# ================= 7. 评价系统 (Feedback) =================

@app.route('/feedback/<int:task_id>', methods=['GET', 'POST'])
def feedback(task_id):
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('login'))

    # 1. 找到任务
    task = Task.query.get(task_id)
    if not task: return "任务不存在"

    # 2. 安全检查：只有发布者能评价，且任务必须是已完成状态
    if task.publisher_id != user_id:
        return "权限错误：只有任务发布者可以评价。"
    if task.status != 2:
        return "错误：任务尚未完成，无法评价。"

    # 3. 检查是否已经评价过了（防止重复刷分）
    existing_fb = Feedback.query.filter_by(task_id=task.id).first()
    if existing_fb:
        return "您已经评价过该任务了。<a href='/my_tasks'>返回</a>"

    # GET请求：显示评价表单
    if request.method == 'GET':
        # 找到我们要评价的对象（接单者）
        taker = User.query.get(task.taker_id)
        return f'''
            <h3>评价接单者：{taker.username}</h3>
            <p>任务：{task.title}</p>
            <form method="post">
                打分 (1-5星): 
                <select name="rating">
                    <option value="5">⭐⭐⭐⭐⭐ (5分)</option>
                    <option value="4">⭐⭐⭐⭐ (4分)</option>
                    <option value="3">⭐⭐⭐ (3分)</option>
                    <option value="2">⭐⭐ (2分)</option>
                    <option value="1">⭐ (1分)</option>
                </select>
                <br><br>
                评语: <textarea name="content" rows="4" cols="50" required placeholder="写点什么..."></textarea>
                <br><br>
                <input type="submit" value="提交评价">
            </form>
            <a href="/my_tasks">返回</a>
        '''

    # POST请求：保存数据
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        content = request.form.get('content')

        # [cite_start]创建评价记录 [cite: 35]
        new_fb = Feedback(
            content=content,
            rating=rating,
            task_id=task.id,
            from_user_id=user_id,  # 我是发布者
            to_user_id=task.taker_id  # 评价给接单者
        )

        # 2. 【核心改动】在这里转积分！
        taker = User.query.get(task.taker_id)
        taker.balance += task.reward_points

        try:
            db.session.add(new_fb)
            db.session.commit()
            return f"评价成功！{task.reward_points} 积分已转给 {taker.username}。<a href='/my_tasks'>返回</a>"
        except Exception as e:
            db.session.rollback()
            return f"操作失败: {e}"


# ================= 8. 发布者撤销任务 (新增功能) =================

@app.route('/revoke/<int:task_id>')
def revoke_task(task_id):
    # 1. 检查登录
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # 2. 获取任务
    task = Task.query.get(task_id)
    if not task:
        return "任务不存在！<a href='/my_tasks'>返回</a>"

    # 3. 权限验证：必须是发布者本人
    if task.publisher_id != user_id:
        return "权限错误：你不能撤销别人的任务！<a href='/my_tasks'>返回</a>"

    # 4. 状态验证：必须是待领取状态 (status=0)
    if task.status != 0:
        return "撤销失败：该任务已被领取或已完成，无法撤销。<a href='/my_tasks'>返回</a>"

    # 5. 执行撤销：退还积分 + 删除任务
    try:
        # [cite_start]退还积分给发布者 [cite: 86, 87]
        publisher = User.query.get(user_id)
        publisher.balance += task.reward_points

        # 删除任务记录
        db.session.delete(task)
        db.session.commit()

        return f"撤销成功！任务已删除，预扣的 {task.reward_points} 积分已退还到你的账户。<br><a href='/my_tasks'>返回我的任务</a>"
    except Exception as e:
        db.session.rollback()
        return f"撤销失败: {e} <a href='/my_tasks'>返回</a>"


if __name__ == '__main__':
    # 启动 Flask 服务

    with app.app_context():
        db.create_all()  # 只要数据库里没表，就会自动按照 models.py 建好
    app.run(debug=True, port=5000)

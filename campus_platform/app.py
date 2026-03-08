from flask import jsonify, Flask, request, session
from config import Config
from models import db, User, Task, Feedback
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from timepoint import predict_points


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'some_secret_key_12345'

# 允许跨域请求，并允许携带 Session
CORS(app, supports_credentials=True)
db.init_app(app)


# ================= 0. 根目录状态检查 =================
@app.route('/')
def index():
    return jsonify({"code": 200, "msg": "校园互助平台 API 运行正常！", "version": "1.0"})


# ================= 1. 用户注册 =================
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data: return jsonify({"code": 400, "msg": "未收到有效数据"})
    name, email, pwd = data.get('username'), data.get('email'), data.get('password')
    if User.query.filter_by(username=name).first(): return jsonify({"code": 409, "msg": "用户名已存在！"})

    new_user = User(username=name, email=email, password_hash=generate_password_hash(pwd))
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"code": 200, "msg": f"注册成功！{name}，你获得了 2 小时初始积分。"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"注册失败: {e}"})


# ================= 2. 用户登录 =================
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user: return jsonify({"code": 404, "msg": "用户不存在，请先注册"})

    if check_password_hash(user.password_hash, data.get('password')):
        session['user_id'] = user.id
        session['user_role'] = user.role
        return jsonify({
            "code": 200, "msg": "登录成功",
            "data": {"user_id": user.id, "username": user.username, "role": user.role, "balance": user.balance}
        })
    return jsonify({"code": 401, "msg": "密码错误！"})


# ================= 3. 退出登录 =================
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"code": 200, "msg": "已成功退出登录"})


# ================= 4. 获取任务大厅数据 =================
# ================= 4. 获取任务大厅数据 =================
@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    # 按照创建时间倒序排列，最新的在最上面
    tasks = Task.query.filter_by(status=0).order_by(Task.create_time.desc()).all()
    task_list = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "reward_points": t.reward_points,
        "category": t.category,  # 🌟 极其关键：必须把数据库里的分类发给前端！
        "publisher_id": t.publisher_id,
        "publisher_name": User.query.get(t.publisher_id).username if User.query.get(t.publisher_id) else "未知",
        "create_time": t.create_time.strftime("%Y-%m-%d %H:%M") if t.create_time else ""
    } for t in tasks]
    return jsonify({"code": 200, "msg": "获取成功", "data": task_list})
# ================= 5. 发布任务 =================
@app.route('/api/task/post', methods=['POST'])
def api_post_task():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"code": 401, "msg": "请先登录"})

    data = request.get_json()
    points = int(data.get('points', 0))
    user = User.query.get(user_id)

    if user.balance < points: return jsonify({"code": 403, "msg": f"余额不足！你当前只有 {user.balance} 积分。"})

    try:
        user.balance -= points
        new_task = Task(title=data.get('title'), description=data.get('desc'), reward_points=points,
                        publisher_id=user.id, status=0)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"code": 200, "msg": "发布成功！积分已预扣除。"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"系统错误: {e}"})


# ================= 6. 抢单/接单 =================
@app.route('/api/task/claim', methods=['POST'])
def api_claim_task():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"code": 401, "msg": "请先登录"})

    task = Task.query.get(request.get_json().get('task_id'))
    if not task: return jsonify({"code": 404, "msg": "任务不存在"})
    if task.status != 0: return jsonify({"code": 400, "msg": "手慢了，任务已被抢走"})
    if task.publisher_id == user_id: return jsonify({"code": 400, "msg": "不能抢自己发布的任务"})

    try:
        task.status = 1
        task.taker_id = user_id
        db.session.commit()
        return jsonify({"code": 200, "msg": "抢单成功！"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"系统错误: {e}"})


# ================= 7. 获取我的任务中心 =================
@app.route('/api/my_tasks', methods=['GET'])
def api_my_tasks():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"code": 401, "msg": "请先登录"})

    my_pub = Task.query.filter_by(publisher_id=user_id).order_by(Task.create_time.desc()).all()
    my_take = Task.query.filter_by(taker_id=user_id).order_by(Task.create_time.desc()).all()

    def format_task(t):
        has_fb = Feedback.query.filter_by(task_id=t.id).first() is not None if t.status == 2 else False
        return {"id": t.id, "title": t.title, "reward_points": t.reward_points, "status": t.status,
                "has_feedback": has_fb}

    return jsonify({"code": 200, "msg": "获取成功", "data": {
        "published_tasks": [format_task(t) for t in my_pub],
        "taken_tasks": [format_task(t) for t in my_take]
    }})


# ================= 8. 验收完成 =================
@app.route('/api/task/settle', methods=['POST'])
def api_settle_task():
    user_id = session.get('user_id')
    task = Task.query.get(request.get_json().get('task_id'))
    if not task or task.publisher_id != user_id or task.status != 1: return jsonify({"code": 400, "msg": "请求不合法"})

    try:
        task.status = 2
        db.session.commit()
        return jsonify({"code": 200, "msg": "验收成功！请去填写评价，评价后积分将自动划拨。"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"系统错误: {e}"})


# ================= 9. 评价并打款 =================
@app.route('/api/task/feedback', methods=['POST'])
def api_feedback_task():
    user_id = session.get('user_id')
    data = request.get_json()
    task = Task.query.get(data.get('task_id'))
    if not task or task.publisher_id != user_id or task.status != 2: return jsonify({"code": 400, "msg": "请求不合法"})

    try:
        new_fb = Feedback(content=data.get('content'), rating=int(data.get('rating')), task_id=task.id,
                          from_user_id=user_id, to_user_id=task.taker_id)
        taker = User.query.get(task.taker_id)
        taker.balance += task.reward_points  # 转账
        db.session.add(new_fb)
        db.session.commit()
        return jsonify({"code": 200, "msg": f"评价成功！{task.reward_points} 积分已转入接单者账户。"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"系统错误: {e}"})


# ================= 10. 发布者撤销任务 =================
@app.route('/api/task/revoke', methods=['POST'])
def api_revoke_task():
    user_id = session.get('user_id')
    task = Task.query.get(request.get_json().get('task_id'))
    if not task or task.publisher_id != user_id or task.status != 0: return jsonify({"code": 400, "msg": "请求不合法"})

    try:
        publisher = User.query.get(user_id)
        publisher.balance += task.reward_points
        db.session.delete(task)
        db.session.commit()
        return jsonify({"code": 200, "msg": f"撤销成功！预扣的 {task.reward_points} 积分已退还。"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"系统错误: {e}"})


# ================= 11. 🌟 管理员强制删除 =================
@app.route('/api/admin/delete', methods=['POST'])
def api_admin_delete():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 1: return jsonify({"code": 403, "msg": "非管理员操作拦截！"})

    task = Task.query.get(request.get_json().get('task_id'))
    if not task: return jsonify({"code": 404, "msg": "任务不存在"})

    try:
        # 如果任务还没人接，把积分退还给发布者
        publisher = User.query.get(task.publisher_id)
        if publisher and task.status == 0:
            publisher.balance += task.reward_points

        db.session.delete(task)
        db.session.commit()
        return jsonify({"code": 200, "msg": "违规任务已彻底删除，积分已强制退还。"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"系统错误: {e}"})


# ================= 12. 🌟 获取个人主页信息 (支持查别人) =================
@app.route('/api/profile', methods=['GET'])
def api_profile():
    query_username = request.args.get('username')

    if query_username:  # 如果传了名字，就查对应的人
        user = User.query.filter_by(username=query_username).first()
    else:  # 没传名字，查自己
        user_id = session.get('user_id')
        if not user_id: return jsonify({"code": 401, "msg": "请先登录"})
        user = User.query.get(user_id)

    if not user: return jsonify({"code": 404, "msg": "用户不存在"})

    feedbacks = Feedback.query.filter_by(to_user_id=user.id).order_by(Feedback.id.desc()).all()
    fb_list = [{"content": f.content, "rating": f.rating,
                "from_user": User.query.get(f.from_user_id).username if User.query.get(f.from_user_id) else "匿名"}
               for f in feedbacks]

    return jsonify({
        "code": 200, "msg": "获取成功",
        "data": {"username": user.username, "balance": user.balance, "role": user.role, "feedbacks": fb_list}
    })


# ================= 13. 🌟 接单者反悔放弃任务 =================
@app.route('/api/task/abandon', methods=['POST'])
def api_abandon_task():
    user_id = session.get('user_id')
    task_id = request.json.get('task_id')
    task = Task.query.get(task_id)

    # 必须是接单人本人，且任务是进行中
    if task and task.taker_id == user_id and task.status == 1:
        try:
            task.status = 0  # 任务重新挂回大厅
            task.taker_id = None  # 清空接单人记录

            # 严厉惩罚：系统留下一条 1 星差评
            sys_feedback = Feedback(
                task_id=task.id,
                from_user_id=task.publisher_id,  # 挂在发布者名下
                to_user_id=user_id,  # 评价对象是放弃任务的人
                rating=1,
                content="⚠️ 系统提示：该用户接单后中途违约放弃了任务，请谨慎合作。"
            )
            db.session.add(sys_feedback)
            db.session.commit()
            return jsonify({"code": 200, "msg": "已放弃任务。系统已在您的主页留下违约记录。"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"code": 500, "msg": f"系统错误: {e}"})

    return jsonify({"code": 400, "msg": "无法放弃该任务"})



@app.route('/api/task/ai_suggest_price', methods=['POST'])
def ai_suggest_price():
    data = request.get_json()
    time_est = float(data.get('time_est', 1.0))
    skill = float(data.get('skill', 0.0))
    urgency = float(data.get('urgency', 0.0))
    traffic = 0.5  # 可以根据当前大厅未完成任务数量动态计算

    # 调用神经网络预测
    suggested_points = predict_points(time_est, skill, urgency, traffic)
    return jsonify({"code": 200, "suggested_points": suggested_points})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
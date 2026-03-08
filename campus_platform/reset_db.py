from app import app
from models import db, User, Task, Feedback
from werkzeug.security import generate_password_hash


def reset_and_seed_mysql():
    with app.app_context():
        print("⚠️ 正在清空旧的 MySQL 数据表...")
        db.drop_all()  # 这一步会瞬间清空 MySQL 里原来的那些假数据和旧表

        print("🔨 正在根据最新模型创建新表 (包含 category 字段)...")
        db.create_all()

        print("👤 正在生成初始用户...")
        # 管理员和普通学生
        admin = User(username='admin1', email='admin@campus.edu', password_hash=generate_password_hash('123456'),
                     role=1, balance=500)
        stu1 = User(username='alin', email='alin@campus.edu', password_hash=generate_password_hash('123456'), role=0,
                    balance=100)
        stu2 = User(username='john', email='john@campus.edu', password_hash=generate_password_hash('123456'), role=0,
                    balance=100)
        db.session.add_all([admin, stu1, stu2])
        db.session.commit()

        print("📝 正在注入真实的双语大学场景任务...")
        tasks = [
            # 📦 快递代取 (Delivery)
            Task(title='帮拿南区菜鸟驿站快递',
                 description='快递比较重，是个显示器箱子。请帮忙送到男生宿舍3栋楼下，到了打电话。', reward_points=4,
                 category='delivery', publisher_id=stu1.id),
            Task(title='Pick up a package at North Gate',
                 description='A small textbook package. Please deliver it to Library floor 2. I will be wearing a black hoodie.',
                 reward_points=2, category='delivery', publisher_id=stu2.id),

            # 📖 学习辅导 (Study)
            Task(title='求高数期末突击辅导',
                 description='明天下午就要考微积分了！求一位数学系大佬在图书馆一楼大厅辅导两小时，包教包会那种，急急急！',
                 reward_points=15, category='study', publisher_id=stu1.id),
            Task(title='Need help debugging Python (PyTorch)',
                 description='My DTVC-Net model is throwing a tensor dimension mismatch error. Need an experienced CS major to help debug for 1 hour.',
                 reward_points=12, category='study', publisher_id=stu2.id),

            # 🏷️ 二手闲置 (Item)
            Task(title='毕业出全新买错的四级真题卷', description='买重了，未拆封。星海食堂门口面交，只要2个积分。',
                 reward_points=2, category='item', publisher_id=admin.id),
            Task(title='Selling a used desk lamp',
                 description='Almost new, adjustable brightness. Perfect for studying at night. Pick up at Dorm 5.',
                 reward_points=5, category='item', publisher_id=stu2.id),

            # ✨ 其他互助 (Other)
            Task(title='二食堂带饭救急',
                 description='正在宿舍赶毕设，饿晕了。求帮忙带一份二食堂一楼的黄焖鸡米饭到4栋502，感谢！', reward_points=3,
                 category='other', publisher_id=stu1.id),
            Task(title='Lost student ID card near gym',
                 description='If anyone finds a student ID card near the campus gym or swimming pool yesterday, please contact me!',
                 reward_points=8, category='other', publisher_id=admin.id),
        ]
        db.session.add_all(tasks)
        db.session.commit()

        print("🎉 MySQL 数据库重置与数据注入完美成功！")


if __name__ == '__main__':
    reset_and_seed_mysql()
from app import app
from models import db, User, Task
from werkzeug.security import generate_password_hash
from faker import Faker
import random


def seed_data():
 
    fake = Faker()

    with app.app_context():
        print("⚠️ 正在清空旧数据表...")
        db.drop_all()
        print("🔨 正在根据最新模型创建新数据表...")
        db.create_all()

        print("👤 正在生成 50 个用户...")
        users = []
        
        admin = User(username='admin1', email='admin@campus.edu', password_hash=generate_password_hash('123456'),
                     role=1, balance=500)
        stu1 = User(username='alin', email='alin@campus.edu', password_hash=generate_password_hash('123456'), role=0,
                    balance=100)
        stu2 = User(username='john', email='john@campus.edu', password_hash=generate_password_hash('123456'), role=0,
                    balance=100)
        users.extend([admin, stu1, stu2])

        
        for _ in range(47):
            
            initial_balance = 2 if random.random() < 0.4 else random.randint(3, 30)

            u = User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password_hash=generate_password_hash('123456'),  # 统一密码方便测试
                balance=initial_balance,  
                role=0
            )
            users.append(u)

        db.session.add_all(users)
        db.session.commit()  

        print("📝 正在生成 100 个高质量双语校园任务...")

     
        task_templates = {
            'delivery': [
                ("Pick up package at South Gate Express / 帮拿南门快递",
                 "It's a medium box, about 3kg. Please deliver to Dorm 4. / 中等大小的箱子，大概3公斤，送到4栋宿舍楼下。"),
                ("Fetch takeout from Canteen 2 / 去二食堂拿外卖",
                 "My phone is dead, please help me pick up my lunch. / 手机没电了，帮我去二食堂拿个午饭。"),
                ("Deliver documents to Admin Building / 送文件到行政楼",
                 "Need someone to drop off these forms at Room 302 before 5 PM. / 需要人在下午5点前把这些表格送到行政楼302。"),
                ("Pick up books from Library / 去图书馆拿书",
                 "I reserved 3 books under the name John. Please bring them to the CS building. / 我用名字预约了3本书，请帮忙拿到计科楼。")
            ],
            'study': [
                ("Need tutor for Calculus mid-term / 求微积分期中辅导",
                 "Exam is next week. Need a 2-hour crash course at the library. / 下周就要考试了，需要在图书馆突击辅导2小时。"),
                ("Python Data Analysis help / 求助 Python 数据分析",
                 "Stuck on a Pandas dataframe merge issue. Should take 30 mins. / 卡在了一个 Pandas 数据合并的问题上，大概需要30分钟。"),
                ("Looking for English speaking partner / 找英语口语搭子",
                 "Practice IELTS speaking for 1 hour this weekend. / 周末练习1小时雅思口语。"),
                ("Help with Physics Lab Report / 帮忙看看物理实验报告",
                 "Just need someone to proofread my data calculations. / 只需要帮忙检查一下我的数据计算过程。")
            ],
            'other': [
                ("Lost student ID card / 丢失校园卡",
                 "Lost near the basketball court. Please contact me if found! / 在篮球场附近丢的，捡到请联系！"),
                ("Need a teammate for Hackathon / 创客比赛缺队友",
                 "Looking for a frontend dev (Vue) for this weekend's hackathon. / 周末的创客比赛缺一个前端(Vue)队友。"),
                ("Survey filling (2 mins) / 填问卷(2分钟)",
                 "Please help fill out my graduation project survey. / 请帮忙填写一下我的毕设问卷，万分感谢。"),
                ("Borrow an umbrella / 借一把伞",
                 "Stuck at the library raining heavily. Will return tomorrow. / 被大雨困在图书馆了，求送伞，明早必还。")
            ]
        }

        tasks = []
        categories = ['delivery', 'study', 'other']

        for _ in range(100):
            cat = random.choice(categories)
            template = random.choice(task_templates[cat])

          
            publisher = random.choice(users[1:])

            t = Task(
                title=template[0],
                description=template[1],
                reward_points=random.randint(1, 15),  
                category=cat,
                publisher_id=publisher.id,
                status=0  
            )
            tasks.append(t)

        db.session.add_all(tasks)
        db.session.commit()

        print("🎉 Faker 数据库重置与 100 条高质量双语数据注入完美成功！")


if __name__ == '__main__':

    seed_data()

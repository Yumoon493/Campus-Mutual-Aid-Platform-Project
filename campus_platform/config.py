import os

class Config:
    # 修改这里的 root:123456 为你的数据库账号和密码
    # 格式：mysql+pymysql://用户名:密码@localhost:3306/数据库名
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:fight040903@localhost:3306/campus_platform'

    # 关闭追踪修改，节省性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 密钥，用于后续的登录加密 用于加密session，毕设随便填一个字符串
    SECRET_KEY = 'cuc_yuting_secret'

    
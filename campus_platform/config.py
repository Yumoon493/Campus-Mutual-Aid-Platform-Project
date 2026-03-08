import os

class Config:
    # 修改这里的 root:密码 为你的数据库账号和密码
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:[password]@localhost:3306/campus_platform'

    # 关闭追踪修改，节省性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 密钥，用于后续的登录加密 用于加密session
    SECRET_KEY = 'cuc_yuting_secret'


    

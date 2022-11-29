from flask import Blueprint

account = Blueprint('account', __name__)


@account.route("/account/login", methods=['POST'])
def login():
    try:
        params = request.values
        login_name = params['loginName']
        pwd = params['pwd']
        md5 = hashlib.md5()
        md5.update(pwd.encode(encoding='utf-8'))
        password = md5.hexdigest()

        users = Users.query.filter(Users.loginName == login_name)\
            .filter(Users.pwd == password).all()
        if len(users) == 0:
            return Result.fail('账号不存在或密码错误')
        else:
            # 服务返回uid，客户端打开好友界面后，凭借此uid与服务器进行socket连接
            uid = users[0].id
            # 已存在uid：已登录，重新登录，原登录退出连接，退出程序
            if uid in online_users.keys():
                # logout
                connection = online_users[int(uid)]
                send_msg = {'type': UtilsAndConfig.SYSTEM_LOGOUT}
                connection.send(json.dumps(send_msg).encode())
            online_users[uid] = None

            return Result.success(uid)
    except Exception as e:
        return Result.fail('参数异常')

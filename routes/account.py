from flask import Blueprint
from flask import request
from app import user, online_user

account = Blueprint('account', __name__)


@account.route("/account/login", methods=['POST'])
def login():
    try:
        params = request.get_json()['content']
        print(params)
        username = params['username']
        password = params['password']

        if username in online_user:


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

from django.http.response import HttpResponse
from django import views
from account.models import User, UserMongo
from account.auth import Auth
from django.contrib.auth.hashers import make_password
from LH.utils import http_fetch
from LH.settings import THIRD_PARTY_API
import re
import json
import datetime
import copy


class RegView(views.View):
    """
    注册视图
    """

    # 错误消息定义
    _error_msg = {'name_error': {'code': 1001, 'msg': '用户名格式不正确，请确保长度在6-20个字符之间'},
                  'mobile_error': {'code': 1002, 'msg': '手机号不正确'},
                  'pass_error': {'code': 1003, 'msg': '密码格式不正确，请确保长度在8-20个字符之间'},
                  'sms_send_error': {'code': 1004, 'msg': '短信验证码发送失败'},
                  'sms_verify_error': {'code': 1005, 'msg': '短信验证码错误'},
                  'general_error': {'code': 1000, 'msg': '注册失败'}
                  }

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '注册成功'}

    def register(self, request):
        """
        注册处理，验证用户注册数据并存入数据库
        :param request: 请求
        :return:
        """

        # 获取参数
        username = request.POST['username']
        mobile = request.POST['mobile']
        password = request.POST['password']

        # 验证参数
        if not self.check_username(username) or not self.check_mobile(mobile) or not self.check_password(password):
            return self._error_response

        # 写入数据库
        if not self.register_database_handler_mongo(username, password, mobile) or not self.register_database_handler(
                username, password, mobile)
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回成功响应
        return HttpResponse(json.dumps(self._success_msg))

    def register_database_handler_mongo(self, username, password, mobile):
        """
        注册时的mongo数据库处理器
        :return: 成功返回真，失败返回假
        """

        # 写入数据库
        new_user = UserMongo(username=username)
        new_user.password = make_password(password)
        new_user.mobile = mobile

        new_user.last_login_time = datetime.datetime.now
        new_user.save()

        return True

    def register_database_handler(self, username, password, mobile):
        """
        注册时的数据库处理器
        :return: 成功返回真，失败返回假
        """

        # 写入数据库
        new_user = User(username=username)
        new_user.password = make_password(password)
        new_user.mobile = mobile

        new_user.last_login_time = datetime.datetime.now
        new_user.save()

        return True

    def check_username(self, username):
        """
        检测用户名
        :param username: 待检测的用户名
        :return: 成功返回真，失败返回假
        """

        if re.match(r'^\w[\w\d]{6,20}', username) is None:
            self._error_response = HttpResponse(json.dumps(self._error_msg['name_error']))
            return False

        return True

    def check_password(self, password):
        """
        检测密码
        :param password: 待检测的密码
        :return: 成功返回真，失败返回假
        """

        if re.match(r'[\w\d]{8,20}', password) is None:
            self._error_response = HttpResponse(json.dumps(self._error_msg['pass_error']))
            return False

        return True

    def check_mobile(self, mobile):
        """
        检测手机号
        :param mobile: 待检测的手机号
        :return: 成功返回真，失败返回假
        """

        if re.match(r'^1\d{10}', mobile) is None:
            self._error_response = HttpResponse(json.dumps(self._error_msg['mobile_error']))
            return False

        return True

    def send_sms_code(self, request):
        """
         发送短信验证码
        :param request: 请求
        :return:
        """

        # 获取参数
        mobile = request.POST.get('mobile', '')
        if not re.match(r'^1\d{10}', mobile):
            return HttpResponse(json.dumps(self._error_msg['mobile_error']))

        data = {'mobile': mobile}
        result = http_fetch(THIRD_PARTY_API['SMS_CODE'], data)

        if not result:
            # 发送失败
            return HttpResponse(json.dumps(self._error_msg['sms_send_error']))

        # 存入session，用于验证
        request.session['sms_code'] = result.data

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def verify_sms_code(self, request):

        """
        验证短信验证码
        :param request: 请求
        :return:
        """

        # 获取参数
        sms_code = request.POST.get('code', '')
        cached_sms_code = request.session.get('sms_code', '')

        if sms_code == '' or sms_code != cached_sms_code:
            return HttpResponse(json.dumps(self._error_msg['sms_verify_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))


class LoginView(views.View):
    """
    登录视图
    """

    # 错误消息定义
    _error_msg = {'user_error': {'code': 2001, 'msg': '用户名或密码错误'},
                  'token_error': {'code': 2002, 'msg': 'token不正确'},
                  'source_error': {'code': 2003, 'msg': '用户来源不正确'},
                  'general_error': {'code': 2000, 'msg': '登录失败'},
                  }

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '登录成功'}

    # 第三方列表定义
    _source = ['qq', 'wechat']

    def login(self, request):
        """
        登录处理，验证用户凭据
        :param request: 请求
        :return: 登录结果
        """

        # 获取参数
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username == '' or password == '':
            return HttpResponse(json.dumps(self._error_msg['user_error']))

        user = self.login_verify(username, password)

        if user:
            # 验证成功

            user.last_login_time = datetime.datetime.now
            user.save()

            return HttpResponse(json.dumps(self._success_msg))

        else:
            # 验证失败
            return HttpResponse(json.dumps(self._error_msg['user_error']))

    def login_verify(self, username, password):
        """
        登录验证
        :param username: 用户名
        :param password: 密码
        :return: 成功返回用户对象，否则None
        """
        return Auth.authenticate(username, password)


    def login_verify_by_token(self, source, token):
        """
        通过第三方token进行验证
        :param source: 用户来源
        :param token: 第三方Token
        :return: 成功返回用户对象，否则None
        """

        if source in self._source:
            if source == 'qq':
                if not (UserMongo.objects(qq_token=token).update(
                        set__last_login_time=datetime.datetime.now) and User.objects.filter(qq_token=token).update(
                    set__last_login_time=datetime.datetime.now)):
                    return None

            elif source == 'wechat':
                if not (UserMongo.objects(wechat_token=token).update(
                        set__last_login_time=datetime.datetime.now) and User.objects.filter(wechat_token=token).update(
                    set__last_login_time=datetime.datetime.now)):
                    return None

            return True

        else:
            # 来源不正确
            self._error_response = HttpResponse(json.dumps(self._error_msg['source_error']))
            return

    def login_by_qq(self, request):
        """
        QQ第三方登录
        :param request: 请求
        :return:
        """

        # 获取参数
        token = request.POST.get('token', '')
        if token == '':
            return HttpResponse(json.dumps(self._error_msg['token_error']))

        # 验证是否已存在
        if not self.login_verify_by_token('qq', token):
            # 数据库不存在则检测token
            result = self.check_token('qq', token)
            if not result:
                return HttpResponse(json.dumps(self._error_msg['token_error']))

            else:
                # 注册新用户
                username, = result
                self.new_user_handler('qq', token, username)

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def login_by_wechat(self, request):
        """
        微信第三方登录
        :param request: 请求
        :return:
        """

        # 获取参数
        token = request.POST.get('token', '')
        if token == '':
            return HttpResponse(json.dumps(self._error_msg['token_error']))

        # 验证是否已存在
        if not self.login_verify_by_token('wechat', token):
            # 数据库不存在则检测token
            result = self.check_token('wechat', token)
            if not result:
                return HttpResponse(json.dumps(self._error_msg['token_error']))

            else:
                # 注册新用户
                username, = result
                self.new_user_handler('wechat', token, username)

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def check_token(self, source, token):
        """
        通过第三方平台检测token
        :param source: 用户来源
        :param token: 第三方token
        :return: 成功返回相关信息元组，否则None
        """

        assert source in self._source and token != ''

        if source == 'qq':
            data = {'token': token}
            result = http_fetch(THIRD_PARTY_API['QQ_LOGIN'], data)

            if not result:
                # 验证失败
                return None
            else:
                # 验证成功，获取昵称
                username = result.nickname
                return (username,)

        elif source == 'wechat':
            data = {'token': token}
            result = http_fetch(THIRD_PARTY_API['WECHAT_LOGIN'], data)

            if not result:
                # 验证失败
                return None
            else:
                # 验证成功，获取昵称
                username = result.nickname
                return (username,)

    def new_user_handler(self, source, token, username):
        """
        第三方新用户处理器
        :param source: 用户来源
        :return: token: 第三方Token
        """

        assert source in self._source and token != ''

        if source == 'qq':
            UserMongo(username=username, reg_source=source, qq_token=token).save()
        elif source == 'wechat':
            UserMongo(username=username, reg_source=source, wechat_token=token).save()


class UserCenter(views.View):
    """
     用户中心视图
    """

    # 错误消息定义
    _error_msg = {'permission_error': {'code': 6001, 'msg': '无请求权限'},
                  'source_error': {'code': 6002, 'msg': '第三方账号无法修改密码'},
                  'pass_error': {'code': 6003, 'msg': '密码格式不正确，请确保长度在8-20个字符之间'},
                  'portrait_empty_error': {'code': 6004, 'msg': '头像不能为空'},
                  'portrait_upload_error': {'code': 6005, 'msg': '头像上传失败'},
                  'general_error': {'code': 6000, 'msg': '操作失败'}
                  }

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '操作成功'}

    def get_user_data(self, request):
        """
        获取当前用户数据
        :param request: 请求
        :return: 用户数据
        """

        # 权限验证
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(self._error_msg['permission_error']))

        # 获取数据
        data = {}
        user = users[0]

        data['id'] = user.id
        data['username'] = user.username
        data['mobile'] = user.mobile
        data['topic_num'] = user.topic_num
        data['following_num'] = user.following_num
        data['follower_num'] = user.follower_num
        data['collected_market_num'] = user.collected_market_num

        result = copy.copy(self._success_msg)
        result['data'] = data

        # 返回正确响应
        return HttpResponse(json.dumps(result))

    def change_password(self, request):
        """
        修改密码
        :param request: 请求
        :return:
        """

        # 权限验证
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(self._error_msg['permission_error']))

        # 获取参数
        new_password = request.POST.get('new_password', '')
        if re.match(r'[\w\d]{8,20}', new_password) is None:
            return HttpResponse(json.dumps(self._error_msg['pass_error']))

        # 处理请求
        if not self._on_change_password(users, make_password(new_password)):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_change_password(self, users, new_password):
        """
        改变密码时的数据库相关处理程序
        :param users: 验证的用户对象
        :param new_password: 新密码
        :return:
        """

        result = False

        for u in users:
            if u.update(set__password=new_password):
                result = True

        return result

    def upload_portrait(self, request):
        """
        上传头像
        :param request: 请求
        :return:
        """

        # 权限验证
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(self._error_msg['permission_error']))

        # 获取参数
        portrait_image = request.POST.get('portrait', b'')
        if not portrait_image:
            return HttpResponse(json.dumps(self._error_msg['portrait_error']))

        # 上传到七牛云
        data = {'file': portrait_image}
        upload_result = http_fetch(THIRD_PARTY_API['QINIU'], data)

        if not upload_result:
            # 上传失败
            return HttpResponse(json.dumps(self._error_msg['portrait_upload_error']))
        else:
            # 上传成功，获取url
            portrait_url = upload_result.url

        # 更新用户数据
        if not self._on_upload(users, portrait_url):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回正确响应
        result = copy.copy(self._success_msg)
        result['data'] = portrait_url
        return HttpResponse(json.dumps(result))

    def _on_upload(self, users, portrait_url):
        """
        上传时的数据库相关处理程序
        :param users: 验证的用户列表
        :param portrait_url: 头像url
        :return: 成功为真，否则假
        """

        result = False

        for u in users:
            if u.update(set__portrait=portrait_url):
                result = True

        return result

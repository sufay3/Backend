from mongoengine.django.auth import auth as auth_mongo
from django.contrib import auth


class Auth(object):
    """
    权限包装器，用于权限验证
    """

    _no_permission_msg = {'code': -1, 'msg': '无操作权限'}

    @classmethod
    def get_authenticated_user(cls,request):
        """
        从请求中获取已验证用户
        :param request: 请求
        :return: User列表
        """

        users=[]

        user_mongo=cls.get_authenticated_user_mongo(request)
        if user_mongo:
            users.append(user_mongo)

        user_sql=cls.get_authenticated_user_sql(request)
        if user_sql:
            users.append(user_sql)

        return users

    @classmethod
    def get_authenticated_user_mongo(cls,request):
        """
        从请求中获取已验证对象，mongo后端
        :param request: 请求
        :return: User对象，或者None
        """

        user=auth_mongo.get_user(request)
        return user if user.is_authenticated() else None

    @classmethod
    def get_authenticated_user_sql(cls, request):
        """
        从请求中获取已验证用户，sql后端
        :param request: 请求
        :return: User对象，或者None
        """

        user = auth.get_user(request)
        return user if user.is_authenticated() else None

    @classmethod
    def authenticate(cls, username, password):
        """
        验证用户凭据
        :param username: 用户名
        :param password: 密码
        :return: 验证通过返回用户对象，否则None
        """

        user=cls.authenticate_mongo(username, password)
        return user if user else cls.authenticate_sql(username, password)

    @classmethod
    def authenticate_mongo(cls, username,password):
        """
        验证用户凭据，mongo后端
        :param username: 用户名
        :param password: 密码
        :return: 验证通过返回用户对象，否则None
        """
        return auth_mongo.authenticate(username,password)

    @classmethod
    def authenticate_sql(cls, username, password):
        """
        验证用户凭据，sql后端
        :param username: 用户名
        :param password: 密码
        :return: 验证通过返回用户对象，否则None
        """
        return auth.authenticate(username, password)

    @classmethod
    def get_no_permission_msg(cls):
        """
        无权限时的响应消息
        :return: no_permission_msg
        """
        return cls._no_permission_msg

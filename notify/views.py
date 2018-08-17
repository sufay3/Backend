from django.http.response import HttpResponse
from django import views
from account.auth import Auth
from account.models import User, UserMongo
from notify.models import Notify,NotifyMongo
import json
import datetime


class NotifyView(views.View):
    """
    通知视图
    """

    # 错误消息定义
    _error_msg = {'notify_id_error': {'code': 7001, 'msg': 'ID不正确'},
                  'general_error': {'code': 7000, 'msg': '操作失败'}
                  }

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '操作成功'}

    def get_notify(self, request):
        """
        获取通知
        :param request: 请求
        :return:
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))


        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_get_notify(self,users):
        """
        获取通知时的数据库处理程序
        :param users: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        assert len(users) >= 2

        return [self._on_get_notify_mongo(users[0]),
                self._on_get_notify_sql(users[1])] == [False, False]

    def _on_get_notify_mongo(self,id,num):
        """
         获取通知时的数据库处理程序，mongo后端
        :param id: 用户ID
        :param num: 数目
        :return: json格式数据 或 None
        """




    def _on_get_notify_sql(self,id,num):
        """
         获取通知时的数据库处理程序，sql后端
        :param id: 用户ID
        param num: 数目
        :return: json格式数据 或  None
        """



    def read_notify(self, request):
        """
        通知被读取时的处理程序
        :param request: 请求
        :return:
        """

        # 验证权限
        user = Auth.get_user(request)
        if not user:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_read_notify(self, uid,nid):
        """
        读取通知时的数据库处理程序
        :param uid: 用户ID
        :param nid: 通知ID
        :return: 成功返回真，失败返回假
        """

        return [self._on_read_notify_mongo(uid,nid),
                self._on_read_notify_sql(uid,nid)] != [False, False]

    def _on_read_notify_mongo(self, uid, nid):
        """
         读取通知时的数据库处理程序，mongo后端
        :param uid: 用户ID
        :param nid: 通知ID
        :return: 成功返回真，失败返回假
        """

        assert uid > 0 and nid > 0
        return NotifyMongo.objects(id=nid,to=uid).update(set__status=1) is not None

    def _on_read_notify_sql(self, uid, nid):
        """
         读取通知时的数据库处理程序，sql后端
        :param uid: 用户ID
        :param nid: 通知ID
        :return: 成功返回真，失败返回假
        """

        assert uid > 0 and nid > 0
        return Notify.objects.filter(id=nid, to=uid).update(set__status=1) is not None

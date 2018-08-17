from account.models import User, Follow, UserMongo, FollowMongo
from coin.models import Market, MarketMongo
from django.http import HttpResponse
from django import views
from account.auth import Auth
import json


class ActionView(views.View):
    """
    行为视图
    """

    # 错误消息定义
    _error_msg = {'follow_uid_error': {'code': 4001, 'msg': '目标UID错误'},
                  'follow_done_error': {'code': 4002, 'msg': '已关注过该用户'},
                  'follow_none_error': {'code': 4003, 'msg': '尚未关注过该用户'},
                  'market_id_error': {'code': 4004, 'msg': '所收藏的市场不存在'},
                  'collect_done_error': {'code': 4005, 'msg': '该市场已被收藏过'},
                  'uncollect_none_error': {'code': 4006, 'msg': '尚未收藏过该市场'},
                  'general_error': {'code': 4000, 'msg': '操作失败'}}

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '操作成功'}

    def follow_user(self, request):
        """
        关注用户
        :param request: 请求
        :return:
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        follow_id = request.POST.get('id', 0)

        if follow_id == 0:
            return HttpResponse(json.dumps(self._error_msg['follow_uid_error']))

        # 处理请求
        if not self._on_follow(users,follow_id):
            return self._follow_error_response

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_follow(self, users, follow_id):
        """
        关注时的数据库处理程序
        :param users: 已验证的用户对象
        :param follow_id: 目标用户ID
        :return: 成功返回真，失败返回假
        """
        assert len(users) >= 2 and follow_id > 0

        result_mongo = self._on_follow_mongo(users[0], follow_id)
        result_sql = self._on_follow_sql(users[1], follow_id)

        if not result_mongo and not result_sql:
            if self._follow_error_code_mongo == self._follow_error_code_sql == self._error_msg['follow_done_error']['code']:
                self._follow_error_response = HttpResponse(json.dumps(self._error_msg['follow_done_error']))
            else:
                self._follow_error_response = HttpResponse(json.dumps(self._error_msg['follow_general_error']))

            return False

        return True

    def _on_follow_mongo(self, user, follow_id):
        """
        关注时的数据库处理程序，mongo后端
        :param user: 已验证的用户对象
        :param follow_id: 目标用户ID:
        :return: 成功返回真，失败返回假
        """

        assert isinstance(user, UserMongo) and follow_id > 0

        # 重置错误对象
        self._follow_error_code_mongo = None

        # 查询是否已关注过目标用户
        if FollowMongo.objects(uid=user.id, follow_id=follow_id):
            # 已关注情形
            self._follow_error_code_mongo = self._error_msg['follow_done_error']['code']
            return False

        # 处理请求
        following = FollowMongo(uid=user.id, follow_uid=follow_id)
        following.save()

        if [user.update(push__followings=follow_id, inc__following_num=1), UserMongo.objects(id=follow_id).update(
                push__followers=user.id, inc__follower_num=1)] == [None, None]:
             # 处理失败
             self._follow_error_code_mongo = self._error_msg['follow_general_error']['code']
             return False

        return True

    def _on_follow_sql(self, user, follow_id):
        """
        关注时的数据库处理程序，sql后端
        :param user: 已验证的用户对象
        :param follow_id: 目标用户ID
        :return: 成功返回真，失败返回假
        """

        assert isinstance(user, User) and follow_id > 0

        # 重置错误对象
        self._follow_error_code_sql = None

        # 查询是否已关注过目标用户
        if Follow.objects.filter(uid=user.id, follow_id=follow_id):
            # 已关注情形
            self._follow_error_code_sql = HttpResponse(json.dumps(self._error_msg['follow_done_error']))
            return False

        # 处理请求
        following = Follow(uid=user.id, follow_uid=follow_id)
        following.save()

        if [user.update(inc__following_num=1),User.objects.filter(id=follow_id).update(inc__follower_num=1)]==[None,None]:
            # 处理失败
            self._follow_error_code_sql = HttpResponse(json.dumps(self._error_msg['follow_general_error']))
            return False

        return True

    def unfollow_user(self, request):
        """
        取消关注用户
        :param request 请求
        :return:
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        follow_id = request.POST.get('id', 0)

        if follow_id == 0:
            return HttpResponse(json.dumps(self._error_msg['follow_uid_error']))

        # 查询是否已关注过目标用户
        follow = FollowMongo.objects(uid=user.id, follow_id=follow_id).first()
        if not follow:
            return HttpResponse(json.dumps(self._error_msg['follow_none_error']))

        # 处理请求
        if not user.update(pull__followings=follow_id, dec__following_num=1) or not UserMongo.objects(
                id=follow_id).update(pull__followers=user.id, dec__follower_num=1):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        follow.delete()

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_unfollow(self, users, follow_id):
        """
        取消关注时的数据库处理程序
        :param users: 已验证的用户对象
        :param follow_id: 目标用户ID
        :return: 成功返回真，失败返回假
        """
        assert len(users) >= 2 and follow_id > 0

        result_mongo = self._on_unfollow_mongo(users[0], follow_id)
        result_sql = self._on_unfollow_sql(users[1], follow_id)

        if not result_mongo and not result_sql:
            if self._follow_error_code_mongo == self._follow_error_code_sql == self._error_msg['follow_none_error']['code']:
                self._follow_error_response = HttpResponse(json.dumps(self._error_msg['follow_none_error']))
            else:
                self._follow_error_response = HttpResponse(json.dumps(self._error_msg['follow_general_error']))

            return False

        return True

    def _on_unfollow_mongo(self, user, follow_id):
        """
        取消关注时的数据库处理程序，mongo后端
        :param user: 已验证的用户对象
        :param follow_id: 目标用户ID:
        :return: 成功返回真，失败返回假
        """

        assert isinstance(user, UserMongo) and follow_id > 0

        # 重置错误对象
        self._follow_error_code_mongo = None

        # 查询是否已关注过目标用户
        if not FollowMongo.objects(uid=user.id, follow_id=follow_id):
            # 未关注情形
            self._follow_error_code_mongo = self._error_msg['follow_none_error']['code']
            return False

        # 处理请求
        if [user.update(pull__followings=follow_id, dec__following_num=1), UserMongo.objects(id=follow_id).update(
                pull__followers=user.id, dec__follower_num=1)] == [None, None]:
            # 处理失败
            self._follow_error_code_mongo = self._error_msg['follow_general_error']['code']
            return False

        return True

    def _on_unfollow_sql(self, user, follow_id):
        """
        取消关注时的数据库处理程序，sql后端
        :param user: 已验证的用户对象
        :param follow_id: 目标用户ID
        :return: 成功返回真，失败返回假
        """

        assert isinstance(user, User) and follow_id > 0

        # 重置错误对象
        self._follow_error_code_sql = None

        # 查询是否已关注过目标用户
        if not Follow.objects.filter(uid=user.id, follow_id=follow_id):
            # 未关注情形
            self._follow_error_code_sql = HttpResponse(json.dumps(self._error_msg['follow_none_error']))
            return False

        # 处理请求
        if [user.update(dec__following_num=1), User.objects.filter(id=follow_id).update(dec__follower_num=1)] == [None,None]:
            # 处理失败
            self._follow_error_code_sql = HttpResponse(json.dumps(self._error_msg['follow_general_error']))
            return False

        return True

    def collect_market(self, request):
        """
        收藏市场
        :param request 请求
        :return:
        """

        # 验证权限
        user = Auth.get(request)
        if not user:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        market_id = request.POST.get('id', 0)
        if market_id == 0:
            return HttpResponse(json.dumps(self._error_msg['market_id_error']))

        # 查询是否已收藏过目标市场
        if market_id in user.collected_markets:
            return HttpResponse(json.dumps(self._error_msg['market_done_error']))

        # 处理请求
        if not user.update(push__collected_markets=market_id, inc__collected_market_num=1):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_collect(self, users, market_id):
        """
        收藏市场时的数据库处理程序
        :param users: 已验证的用户对象
        :param market_id: 市场ID
        :return: 成功返回真，失败返回假
        """
        assert len(users) >= 2 and market_id > 0

        result_mongo = self._on_unfollow_mongo(users[0], market_id)
        result_sql = self._on_unfollow_sql(users[1], market_id)

        if not result_mongo and not result_sql:
            if self._follow_error_code_mongo == self._follow_error_code_sql == self._error_msg['follow_none_error'][
                'code']:
                self._follow_error_response = HttpResponse(json.dumps(self._error_msg['follow_none_error']))
            else:
                self._follow_error_response = HttpResponse(json.dumps(self._error_msg['follow_general_error']))

            return False

        return True

    def _on_collect_mongo(self, user, market_id):
        """
        收藏市场时的数据库处理程序，mongo后端
        :param user: 已验证的用户对象
        :param market_id: 市场ID:
        :return: 成功返回真，失败返回假
        """

        assert isinstance(user, UserMongo) and market_id > 0

        # 重置错误对象
        self._follow_error_code_mongo = None

        # 查询是否已关注过目标用户
        if not FollowMongo.objects(uid=user.id, follow_id=market_id):
            # 未关注情形
            self._follow_error_code_mongo = self._error_msg['follow_none_error']['code']
            return False

        # 处理请求
        if [user.update(pull__followings=follow_id, dec__following_num=1), UserMongo.objects(id=follow_id).update(
                pull__followers=user.id, dec__follower_num=1)] == [None, None]:
            # 处理失败
            self._follow_error_code_mongo = self._error_msg['follow_general_error']['code']
            return False

        return True

    def _on_collect_sql(self, user, market_id):
        """
        收藏市场时的数据库处理程序，sql后端
        :param user: 已验证的用户对象
        :param market_id: 目标用户ID
        :return: 成功返回真，失败返回假
        """

        assert isinstance(user, User) and follow_id > 0

        # 重置错误对象
        self._follow_error_code_sql = None

        # 查询是否已关注过目标用户
        if not Follow.objects.filter(uid=user.id, follow_id=follow_id):
            # 未关注情形
            self._follow_error_code_sql = HttpResponse(json.dumps(self._error_msg['follow_none_error']))
            return False

        # 处理请求
        if [user.update(dec__following_num=1), User.objects.filter(id=follow_id).update(dec__follower_num=1)] == [None,
                                                                                                                  None]:
            # 处理失败
            self._follow_error_code_sql = HttpResponse(json.dumps(self._error_msg['follow_general_error']))
            return False

        return True

    def uncollect_market(self, request):
        """
        从收藏的市场中删除目标市场
        :param request 请求
        :return:
        """

        # 验证权限
        user = Auth.get_user(request)
        if not user:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        market_id = request.POST.get('id', 0)
        if market_id == 0:
            return HttpResponse(json.dumps(self._error_msg['market_id_error']))

        # 查询是否已收藏过目标市场
        if market_id not in user.collected_markets:
            return HttpResponse(json.dumps(self._error_msg['market_none_error']))

        # 处理请求
        if not user.update(pull__collected_markets=market_id, dec__collected_market_num=1):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

from django.http.response import HttpResponse
from django import views
from forum.models import Topic, Comment, TopicMongo, CommentMongo
from account.models import User, UserMongo
from account.auth import Auth
import json
import datetime


class ForumView(views.View):
    """
    论坛视图
    """

    # 错误消息定义
    _error_msg = {'title_len_error': {'code': 3001, 'msg': '标题过长'},
                  'title_words_error': {'code': 3002, 'msg': '标题含有敏感词'},
                  'content_len_error': {'code': 3003, 'msg': '内容长度超过限制'},
                  'content_words_error': {'code': 3004, 'msg': '内容含有敏感词'},
                  'post_type_error': {'code': 3005, 'msg': '贴子类型不正确'},
                  'post_id_error': {'code': 3005, 'msg': '贴子ID不正确'},
                  'general_error': {'code': 3000, 'msg': '操作失败'}
                  }

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '操作成功'}

    # 敏感词列表
    _forbidden_words = ['共产党']

    def digg_post(self, request):
        """
        赞贴子
        :param request: 请求
        :return:
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        post_type = request.POST.get('type', 0)
        post_id = request.POST.get('id', 0)

        if post_type not in [0, 1]:
            return HttpResponse(json.dumps(self._error_msg['post_type_error']))

        if post_id <= 0:
            return HttpResponse(json.dumps(self._error_msg['post_id_error']))

        # 处理请求
        if not self._on_digg(post_type, post_id):
            return HttpResponse(json.dumps(self._error_msg['post_id_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_digg(self, post_type, post_id):
        """
        点赞时的数据库处理程序
        :param post_type: 贴子类型 0为主题，1为评论
        :param post_id: 贴子ID
        :return: 失败返回假
        """

        return [self._on_digg_mongo(post_type, post_id), self._on_digg_sql(post_type, post_id)] != [None, None]

    def _on_digg_mongo(self, post_type, post_id):
        """
        点赞时的数据库处理程序,mongo后端
        :param post_type: 贴子类型 0为主题，1为评论
        :param post_id: 贴子ID
        :return: 失败返回None
        """

        assert post_type in [0, 1] and post_id > 0

        if post_type == 0:
            result = TopicMongo.objects(id=post_id).update(inc__digg_num=1)
        else:
            result = CommentMongo.objects(id=post_id).update(inc__digg_num=1)

        return result

    def _on_digg_sql(self, post_type, post_id):
        """
        点赞时的数据库处理程序,sql后端
        :param post_type: 贴子类型 0为主题，1为评论
        :param post_id: 贴子ID
        :return: 失败返回None
        """

        assert post_type in [0, 1] and post_id > 0

        if post_type == 0:
            result = Topic.objects.filter(id=post_id).update(inc__digg_num=1)
        else:
            result = Comment.objects.filter(id=post_id).update(inc__digg_num=1)

        return result

    def diss_post(self, request):
        """
        踩贴子
        :param request: 请求
        :return:
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        post_type = request.POST.get('type', 0)
        post_id = request.POST.get('id', 0)

        if post_type not in [0, 1]:
            return HttpResponse(json.dumps(self._error_msg['post_type_error']))

        if post_id <= 0:
            return HttpResponse(json.dumps(self._error_msg['post_id_error']))

        # 处理请求
        if not self._on_diss(post_type, post_id):
            return HttpResponse(json.dumps(self._error_msg['post_id_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_diss(self, post_type, post_id):
        """
        踩贴时的数据库处理程序
        :param post_type: 贴子类型 0为主题，1为评论
        :param post_id: 贴子ID
        :return: 失败返回假
        """

        return [self._on_diss_mongo(post_type, post_id), self._on_diss_sql(post_type, post_id)] != [None, None]

    def _on_diss_mongo(self, post_type, post_id):
        """
        踩贴时的数据库处理程序,mongo后端
        :param post_type: 贴子类型 0为主题，1为评论
        :param post_id: 贴子ID
        :return: 失败返回None
        """

        assert post_type in [0, 1] and post_id > 0

        if post_type == 0:
            result = TopicMongo.objects(id=post_id).update(dec__digg_num=1)
        else:
            result = CommentMongo.objects(id=post_id).update(dec__digg_num=1)

        return result

    def _on_diss_sql(self, post_type, post_id):
        """
        踩贴时的数据库处理程序,sql后端
        :param post_type: 贴子类型 0为主题，1为评论
        :param post_id: 贴子ID
        :return: 失败返回None
        """

        assert post_type in [0, 1] and post_id > 0

        if post_type == 0:
            result = Topic.objects.filter(id=post_id).update(dec__digg_num=1)
        else:
            result = Comment.objects.filter(id=post_id).update(dec__digg_num=1)

        return result

    def publish_topic(self, request):
        """
        发表主题
        :param request: 请求
        :return:
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')

        # 验证标题
        if len(title) > 50:
            return HttpResponse(json.dumps(self._error_msg['title_len_error']))

        for w in self._forbidden_words:
            if title.find(w) >= 0:
                return HttpResponse(json.dumps(self._error_msg['title_words_error']))

        # 验证内容
        if len(content) > 10000:
            return HttpResponse(json.dumps(self._error_msg['content_len_error']))

        for w in self._forbidden_words:
            if content.find(w) >= 0:
                return HttpResponse(json.dumps(self._error_msg['content_words_error']))

        # 处理请求
        if not self._on_publish_topic(title, content, users):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_publish_topic(self, title, content, users):
        """
        发表主题时的数据库处理程序
        :param title: 标题
        :param content: 内容
        :param users: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        return [self._on_publish_topic_mongo(title, content, users),
                self._on_publish_topic_sql(title, content, users)] != [False, False]

    def _on_publish_topic_mongo(self, title, content, users):
        """
        发表主题时的数据库处理程序，mongo后端
        :param title: 标题
        :param content: 内容
        :param users: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        assert title != '' and content != '' and len(users) >= 1 and isinstance(users[0], UserMongo)

        new_topic = TopicMongo(title=title, content=content, author=users[0])
        new_topic.save()

        result = UserMongo.objects(id=users[0].id).update(push__topics=new_topic,
                                                          inc__topic_num=1)
        return result is not None

    def _on_publish_topic_sql(self, title, content, users):
        """
        发表主题时的数据库处理程序，sql后端
        :param title: 标题
        :param content: 内容
        :param users: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        assert title != '' and content != '' and len(users) > 1 and isinstance(users[1], User)

        new_topic = Topic(title=title, content=content, author=users[1])
        new_topic.save()

        result = User.objects.filter(id=users[1].id).update(inc__topic_num=1)
        return result is not None

    def publish_comment(self, request):
        """
        发表评论
        :param request: 请求
        """

        # 验证权限
        users = Auth.get_authenticated_user(request)
        if not users:
            return HttpResponse(json.dumps(Auth.get_no_permission_msg()))

        # 获取参数
        content = request.POST.get('content', '')
        post_type = request.POST.get('type', 0)
        post_id = request.POST.get('id', 0)

        if post_type not in [0, 1]:
            return HttpResponse(json.dumps(self._error_msg['post_type_error']))
        if post_id == 0:
            return HttpResponse(json.dumps(self._error_msg['post_id_error']))

        # 验证内容
        if len(content) > 10000:
            return HttpResponse(json.dumps(self._error_msg['content_len_error']))

        for w in self._forbidden_words:
            if content.find(w) >= 0:
                return HttpResponse(json.dumps(self._error_msg['content_words_error']))

        # 处理请求
        if not self._on_publish_comment(post_id, post_type, content, users):
            return HttpResponse(json.dumps(self._error_msg['general_error']))

        # 返回正确响应
        return HttpResponse(json.dumps(self._success_msg))

    def _on_publish_comment(self, post_id, post_type, content, users):
        """
        发表评论时的数据库处理程序
        :param post_id: 被评论的ID
        :param post_type: 被评论的类型，0为主题，1为评论
        :param content: 内容
        :param users: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        assert len(users) >= 2

        return [self._on_publish_comment_mongo(post_id, post_type, content, users[0]),
                self._on_publish_comment_sql(post_id, post_type, content, users[1])] != [False, False]

    def _on_publish_comment_mongo(self, post_id, post_type, content, user):
        """
        发表评论时的数据库处理程序，mongo后端
         :param post_id: 被评论的贴子ID
        :param post_type: 被评论的评论类型，0为主题，1为评论
        :param content: 内容
        :param user: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        assert post_id > 0 and post_type in [0, 1] and content != '' and isinstance(user, UserMongo)

        if post_type == 0:
            # 评论对象为主题的情形
            topic = TopicMongo.objects(id=post_id).first()

            if not topic:
                return False

            new_comment = CommentMongo(content=content, user=user, topic=topic, time=datetime.datetime.now)
            new_comment.save()

            result = topic.update(push__comments=new_comment, inc__comment_num=1)
        else:
            # 评论对象为评论的情形
            comment = CommentMongo.objects(id=post_id).first()

            if not comment:
                return False

            new_comment = CommentMongo(content=content, user=user, type=1, comment=comment,
                                       time=datetime.datetime.now)
            new_comment.save()

            result = comment.update(inc__comment_num=1)

        return result is not None

    def _on_publish_comment_sql(self, post_id, post_type, content, user):
        """
        发表评论时的数据库处理程序，sql后端
         :param post_id: 被评论的贴子ID
        :param post_type: 评论类型，0为主题，1为评论
        :param content: 内容
        :param user: 已验证的用户对象
        :return: 成功返回真，失败返回假
        """

        assert post_id > 0 and post_type in [0, 1] and content != '' and isinstance(user, User)

        if post_type == 0:
            # 评论对象为主题的情形
            topic = Topic.objects.filter(id=post_id).first()

            if not topic:
                return False

            new_comment = Comment(content=content, user=user, tid=topic.id, time=datetime.datetime.now)
            new_comment.save()

            result = topic.update(inc__comment_num=1)
        else:
            # 评论对象为评论的情形
            comment = Comment.objects.filter(id=post_id).first()

            if not comment:
                return False

            new_comment = Comment(content=content, user=user, type=1, cid=comment.id,
                                  time=datetime.datetime.now)
            new_comment.save()

            result = comment.update(inc__comment_num=1)

        return result is not None

from mongoengine import *
import json
import time
import datetime
import copy
from LH.settings import DEFAULT_PORTRAIT_URL

connect('liansea')


class CommentMongo(Document):
    """
    评论MongoDB数据模型，各字段说明如下：

      id: ID，整型
      author: 作者，引用字段
      type: 类型，整型
      topic: 所评论的主题, 引用字段
      comment: 所评论的评论，引用字段
      content: 评论内容，字符串
      digg_num: 点赞数，整型
      diss_num: 踩数，整型
      comment_num: 评论数，整型
      time: 评论时间，日期型
    """

    # 字段声明

    author = ReferenceField('UserMongo', required=True)
    type = IntField(default=0)
    topic = ReferenceField('TopicMongo')
    comment = ReferenceField('CommentMongo')
    content = StringField(min_length=10, max_length=10000, required=True)
    digg_num = IntField(default=0)
    diss_num = IntField(default=0)
    comment_num = IntField(default=0)
    time = DateTimeField(required=True)

    # 元数据：指定集合和索引
    meta = {'collection': 'comment', 'indexes': []}


class TopicMongo(Document):
    """
     主题MongoDB数据模型，各字段说明如下：

      id: ID, 整型
      title: 标题，字符串
      content: 内容，字符串
      publish_time: 发布时间，日期型
      author: 作者，引用字段
      comments: 评论，引用列表
      comment_num: 评论数，整型
      digg_num: 点赞数，整型
      diss_num: 踩数，整型

    """

    # 字段声明


    title = StringField(max_length=50, required=True)
    content = StringField(max_length=10000, required=True)
    publish_time = DateTimeField(required=True)
    author = ReferenceField('UserMongo', required=True)
    oomments = ListField(ReferenceField('CommentMongo'), default=[])
    comment_num = IntField(default=0)
    digg_num = IntField(default=0)
    diss_num = IntField(default=0)

    # 元数据：指定集合和索引
    meta = {'collection': 'topic', 'indexes': []}


class FollowMongo(Document):
    """
    关注MongoDB数据模型，各字段说明如下：

      uid: 用户ID，整型
      follow_id: 关注用户ID，整型
      time: 关注时间，日期型
    """

    # 字段声明

    uid = IntField(required=True)
    follow_id = IntField(required=True)
    time = DateTimeField(default=datetime.datetime.now)


class UserMongo(Document):
    """
    用户MongoDB数据模型，各字段说明如下：

      uid: 用户ID, 整型
      username: 用户名，字符串
      reg_time: 注册时间，日期型
      reg_source: 注册来源，字符串
      mobile: 手机号，字符串
      password: 密码，字符串
      portrait: 头像url，URL
      followings: 关注列表，整型列表
      followers: 粉丝列表，整型列表
      follow_num: 关注数，整型
      follower_num: 粉丝数，整型
      collected_markets: 收藏市场，引用列表
      collectd_market_num: 收藏的市场数
      topics: 主题，引用列表
      topic_num: 主题数
      qq_token: QQ token，字符串
      wechat_token: 微信token，字符串
      login_login_time: 最后登录时间，日期型
    """

    # 字段声明


    username = StringField(min_length=4, max_length=20, unique=True, required=True)
    reg_time = DateTimeField(default=datetime.datetime.now)
    reg_source = StringField(max_length=50, default='mobile')
    mobile = StringField(regex=r'^1\d{10}', unique=True, required=True)
    password = StringField(regex=r'[0-9a-fA-F]{3}', required=True)
    portrait = URLField(default=DEFAULT_PORTRAIT_URL)
    followings = ListField(ReferenceField('FollowMongo'), default=[])
    followers = ListField(ReferenceField('FollowMongo'), default=[])
    follow_num = IntField(default=0)
    follower_num = IntField(default=0)
    collected_markets = ListField(ReferenceField('MarketMongo'), default=[])
    collected_market_num = IntField(default=0)
    topics = ListField(ReferenceField('TopicMongo'), default=[])
    topic_num = IntField(default=0)
    qq_token = StringField(max_length=256, default='')
    wechat_token = StringField(max_length=256, default='')
    last_login_time = DateTimeField(default=datetime.datetime.now)

    # 元数据：指定集合和索引
    meta = {'collection': 'user', 'indexes': ['+username', '+mobile']}


if __name__ == '__main__':
    # user = UserMongo( username='user2', mobile='15658585544', password='111')
    # user.save()
    user2 = UserMongo.objects(username='user2').first()
    print(user2)

    #
    # topic1 = Topic(title='1', content='aaa8', publish_time=datetime.datetime.now, user=user)
    # topic2 = Topic(title='2', content='aaa8', publish_time=datetime.datetime.now, user=user)
    #
    # user2.save()
    # user.save()
    # topic1.save()
    # topic2.save()

    comment = CommentMongo(author=user2, content='user2 comment 1', time=datetime.datetime.now)
    comment.save()
    topic = TopicMongo(title='title 1', content='content 1', publish_time=datetime.datetime.now, author=user2)
    topic.oomments.append(comment)
    topic.save()

    # result = Topic.objects(title='1').update(set__title='12')

    # topic = TopicMongo.objects(title='3').first()
    # user = UserMongo.objects(id=topic.user.id).first().to_json()

    result = TopicMongo.objects().first()
    result = CommentMongo.objects(result.
    if not result:
        print('no data')
    else:
        print('ok', result)

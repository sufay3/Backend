from mongoengine import *
from django.db import models
from coin.models import Market
import datetime
from LH.settings import DEFAULT_PORTRAIT_URL


class FollowMongo(Document):
    """
    关注MongoDB数据模型，各字段说明如下：

      id:  ID，整型
      uid: 用户ID，整型
      follow_id: 关注用户ID，整型
      time: 关注时间，日期型
    """

    # 字段声明

    id = IntField(unique=True, required=True)
    uid = IntField(required=True)
    follow_id=IntField(required=True)
    time = DateTimeField(default=datetime.datetime.now)

    # 元数据：指定集合和索引
    meta = {'collection': 'follow'}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<uid: %d, follow_id: %d, time: %s>' % (
        self.uid, self.follow_id,self.time)

class UserMongo(Document):
    """
    用户MongoDB数据模型，各字段说明如下：

      id: ID, 整型
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

    id = IntField(unique=True, required=True)
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
    meta = {'collection': 'user', 'indexes': ['+id', '+username', '+mobile']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<id: %s, username: %s, mobile: %s, last_login_time: %s>' % (self.id, self.username, self.mobile,self.last_login_time)

class Follow(models.Model):
    """
    关注数据模型，各字段说明如下：

      id: ID，自增字段
      uid: 用户ID，整型
      follow_id: 被关注用户ID,整型
      time: 关注时间，日期型
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    uid = models.IntegerField()
    follow_id = models.IntegerField()
    time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        verbose_name='Follow'
        verbose_name_plural=verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<uid: %d, follow_id: %d, time: %s>' % (self.uid,self.follow_id,self.time)

class User(models.Model):
    """
    用户数据模型，各字段说明如下：

      id: ID, 自增字段
      username: 用户名，字符串
      reg_time: 注册时间，日期型
      reg_source: 注册来源，字符串
      mobile: 手机号，字符串
      password: 密码，字符串
      portrait: 头像url，URL
      follow_num: 关注数，整型
      follower_num: 粉丝数，整型
      topic_num: 主题数，整型
      collectd_market_num: 收藏的市场数
      qq_token: QQ token，字符串
      wechat_token: 微信token，字符串
      last_login_time: 最后登录时间，日期型
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    reg_time = models.DateTimeField(default=datetime.datetime.now)
    reg_source = models.CharField(max_length=10, default='mobile')
    mobile = models.CharField(max_length=11)
    password = models.CharField(max_length=32)
    portrait = models.URLField(default=DEFAULT_PORTRAIT_URL)
    follow_num = models.IntegerField(default=0)
    follower_num = models.IntegerField(default=0)
    topic_num = models.IntegerField(default=0)
    collected_market_num = models.IntegerField(default=0)
    qq_token = models.CharField(max_length=256, default='')
    wechat_token = models.CharField(max_length=256, default='')
    last_login_time = models.DateTimeField(default=datetime.datetime.now)



    class Meta:
        verbose_name='User'
        verbose_name_plural=verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<id: %s, username: %s>' % (self.id,self.username)
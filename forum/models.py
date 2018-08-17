from mongoengine import *
from account.models import User, UserMongo
from django.db import models
import datetime


class CommentMongo(Document):
    """
    评论MongoDB数据模型，各字段说明如下：

      id: ID，整型
      user: 作者，引用字段
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
    id = IntField(required=True)
    user = ReferenceField('UserMongo', required=True)
    type = IntField(default=0)
    topic = ReferenceField('TopicMongo')
    comment = ReferenceField('CommentMongo')
    content = StringField(min_length=10, max_length=10000, required=True)
    digg_num = IntField(default=0)
    diss_num = IntField(default=0)
    comment_num = IntField(default=0)
    time = DateTimeField(required=True)

    # 元数据：指定集合和索引
    meta = {'collection': 'comment', 'indexes': ['+id']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<user: %s, content: %s>' % (self.user.username, self.content)


class TopicMongo(Document):
    """
     主题MongoDB数据模型，各字段说明如下：

      id: ID, 整型
      title: 标题，字符串
      content: 内容，字符串
      publish_time: 发布时间，日期型
      user: 作者，引用字段
      comments: 评论，引用列表
      comment_num: 评论数，整型
      digg_num: 点赞数，整型
      diss_num: 踩数，整型

    """

    # 字段声明

    id = IntField(required=True)
    title = StringField(max_length=50, required=True)
    content = StringField(max_length=10000, required=True)
    publish_time = DateTimeField(required=True)
    user = ReferenceField('UserMongo', required=True)
    oomments = ListField(ReferenceField('CommentMongo'), default=[])
    comment_num = IntField(default=0)
    digg_num = IntField(default=0)
    diss_num = IntField(default=0)

    # 元数据：指定集合和索引
    meta = {'collection': 'topic', 'indexes': ['+id']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<user: %s, title: %s, content: %s>' % (self.user.username, self.title, self.content)


class Comment(models.Model):
    """
    Comment 评论数据模型，各字段说明如下：

      id: ID，自增字段
      user: 作者，外键
      type: 评论类型，整型
      tid: 所评论的主题ID，整型
      cid: 所评论的评论ID，整型
      content: 内容，字符串
      digg_num: 点赞数，整型
      diss_num: 踩数，整型
      time: 评论时间，日期型

    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User')
    type = models.IntegerField(default=0)
    tid = models.IntegerField(null=True)
    cid = models.IntegerField(null=True)
    content = models.TextField(max_length=10000)
    digg_num = models.IntegerField(default=0)
    diss_num = models.IntegerField(default=0)
    time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<user: %s, content: %s>' % (self.user.username, self.content)


class Topic(models.Model):
    """
    Topic 主题数据模型，各字段说明如下：

      id: ID，自增字段
      uid: 作者ID，外键
      title: 标题，字符串
      content: 内容，字符串
      publish_time: 发布时间，日期型
      comment_num: 评论数，整型
      digg_num: 点赞数，整型
      diss_num: 踩数，整型
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User')
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=10000)
    publish_time = models.DateTimeField(default=datetime.datetime.now)
    comment_num = models.IntegerField(default=0)
    digg_num = models.IntegerField(default=0)
    diss_num = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<user: %s, title: %s, content: %s>' % (self.user.username, self.title, self.content)


class Forum(models.Model):
    """
    Forum 论坛数据模型，各字段说明如下：

      id: ID，自增字段
      name: 名字，字符串
      coin: 币种，外键
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    coin = models.ForeignKey('Coin')

    class Meta:
        verbose_name = 'Forum'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return self.name

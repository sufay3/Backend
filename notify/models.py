from mongoengine import *
from account.models import User, UserMongo
from django.db import models
import datetime


class NotifyMongo(EmbeddedDocument):
    """
    通知MongoDB数据模型，各字段说明如下：

      id: ID，整型
      event: 事件，字符串
      to: 被通知用户ID，整型
      title: 标题，字符串
      content: 内容，字符串
      path: 路径，字符串
      status: 状态，整数型
      time: 时间，日期型
    """

    # 字段声明

    id = IntField(required=True)
    event = StringField(max_length=20, required=True)
    to = IntField(required=True)
    title = StringField(max_length=50, required=True)
    content = StringField(max_length=100, required=True)
    path = StringField(max_length=100, default='')
    status = IntField(default=0)
    time = DateTimeField(required=True)

    # 元数据：指定集合和索引
    meta = {'collection': 'notify', 'indexes': ['-time']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<event: %s, title: %s, content: %s, to: %d, status: %d>' % (
            self.event, self.title, self.content, self.to, self.status)

class NotifyStatus(EmbeddedDocument):
    """
    通知MongoDB数据模型，各字段说明如下：

      id: ID，整型
      event: 事件，字符串
      to: 被通知用户ID，整型
      title: 标题，字符串
      content: 内容，字符串
      path: 路径，字符串
      status: 状态，整数型
      time: 时间，日期型
    """

    # 字段声明

    id = IntField(required=True)
    event = StringField(max_length=20, required=True)
    to = IntField(required=True)
    title = StringField(max_length=50, required=True)
    content = StringField(max_length=100, required=True)
    path = StringField(max_length=100, default='')
    status = IntField(default=0)
    time = DateTimeField(required=True)

    # 元数据：指定集合和索引
    meta = {'collection': 'notify', 'indexes': ['-time']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<event: %s, title: %s, content: %s, to: %d, status: %d>' % (
            self.event, self.title, self.content, self.to, self.status)


class Notify(models.Model):
    """
    通知数据模型，各字段说明如下：

      id: ID，自增字段
      event: 事件，字符串
      to: 被通知用户ID，整型
      title: 标题，字符串
      content: 内容，字符串
      path: 路径，字符串
      status: 状态，整数型
      time: 时间，日期型
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    event = models.CharField(max_length=20)
    to = models.IntegerField()
    title = models.TextField(max_length=50)
    content = models.TextField(max_length=100)
    path = models.CharField(max_length=100, default='')
    status = models.IntegerField(default=0)
    time = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<event: %s, title: %s, content: %s, to: %d, status: %d>' % (
            self.event, self.title, self.content, self.to, self.status)

    class Meta:
        verbose_name = 'Notify'
        verbose_name_plural = verbose_name
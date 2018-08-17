from mongoengine import *
from django.db import models


class CoinMongo(Document):
    """
    币种MongoDB数据模型，各字段说明如下：

      id: ID，整型
      name: 币种名字，字符串
      symbol: 符号，字符串
      chinese_name: 中文名，字符串
      desc: 描述，字符串
      ico_price: ico价格，字符串
      ico_time: ico启动时间，字符串
    """

    # 字段声明

    id = IntField(required=True)
    name = StringField(max_length=20, unique=True, required=True)
    symbol = StringField(max_length=20, unique=True, required=True)
    chinese_name = StringField(max_length=20, required=True)
    desc = StringField(max_length=10000, default='')
    ico_price = StringField(max_length=20, default='')
    ico_time = StringField(max_length=20, default='')

    # 元数据：指定集合和索引
    meta = {'collection': 'coin', 'indexes': ['+id', '+name']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<%s, %s, %s>' % (self.name, self.symbol, self.chinese_name)


class MarketMongo(Document):
    """
     市场MongoDB数据模型，各字段说明如下：

        id: ID，整型
        name: 市场名，字符串
        base_coin: 基本币种，引用字段
        quot_coin: 行情币种，引用字段
        exchange: 交易所，引用字段
    """

    # 字段声明

    id = IntField(required=True)
    name = StringField(max_length=50, required=True)
    base_coin = ReferenceField('CoinMongo', required=True)
    quot_coin = ReferenceField('CoinMongo', required=True)
    exchange = ReferenceField('ExchangeMongo', required=True)

    # 元数据：指定集合和索引
    meta = {'collection': 'market', 'indexes': ['+id', '+name']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<name: %s, coin: %s, quot_coin: %s, exchange: %s>' % (
            self.name, self.base_coin.name, self.quot_coin.name, self.exchange.name)


class ExchangeMongo(Document):
    """
    交易所MongoDB数据模型，各字段说明如下：

      id: ID，整型
      name: 交易所名字，字符串
      abbr: 名字缩写，字符串
      chinese_name: 中文名字，字符串
      markets: 市场，引用列表
      url: 交易所网址，URL
      desc: 描述，字符串
      start_time: 创建时间，字符串
    """

    # 字段声明

    id = IntField(required=True)
    name = StringField(max_length=20, unique=True, required=True)
    abbr = StringField(max_length=20, required=True)
    chinese_name = StringField(max_length=20, required=True)
    markets = ListField(ReferenceField('MarketMongo'), default=[])
    url = URLField(required=True)
    desc = StringField(max_length=10000, default='')
    start_time = StringField(max_length=20, default='')

    # 元数据：指定集合和索引
    meta = {'collection': 'exchange', 'indexes': ['+id', '+name']}

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<%s, %s, %s>' % (self.name, self.abbr, self.chinese_name)


class Coin(models.Model):
    """
    币种数据模型，各字段说明如下：

      id: ID，自增字段
      name: 币种名字，字符串
      symbol: 符号，字符串
      chinese_name: 中文名，字符串
      desc: 描述，字符串
      ico_price: ico价格，字符串
      ico_time: ico启动时间，字符串
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    chinese_name = models.CharField(max_length=20)
    desc = models.TextField(max_length=10000, default='')
    ico_price = models.CharField(max_length=20, default='')
    ico_time = models.CharField(max_length=20, default='')

    class Meta:
        verbose_name = 'Coin'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<%s, %s, %s>' % (self.name, self.symbol, self.chinese_name)


class Market(models.Model):
    """
     市场数据模型，各字段说明如下：

        id: ID，自增ID
        name: 市场名，字符串
        cid: 基本币种ID，外键
        qcid: 行情币种ID，外键
        eid: 交易所ID，多对多字段
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    base_coin = models.ForeignKey('Coin')
    quot_coin = models.ForeignKey('Coin')
    exchange = models.ForeignKey('Exchange')

    class Meta:
        verbose_name = 'Market'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<name: %s, coin: %s, quot_coin: %s, exchange: %s>' % (
            self.name, self.base_coin.name, self.quot_coin.name, self.exchange.name)


class Exchange(models.Model):
    """
    交易所数据模型，各字段说明如下：

      id: ID，自增字段
      name: 交易所名字，字符串
      abbr: 名字缩写，字符串
      chinese_name: 中文名字，字符串
      url: 交易所网址，URL
      desc: 描述，字符串
      start_time: 创建时间，字符串
    """

    # 字段声明

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    abbr = models.CharField(max_length=20)
    chinese_name = models.CharField(max_length=20)
    url = models.URLField()
    desc = models.TextField(max_length=10000, default='')
    start_time = models.CharField(max_length=20, default='')

    class Meta:
        verbose_name = 'Exchange'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        string representation
        :return:
        """
        return '<%s, %s, %s>' % (self.name, self.abbr, self.chinese_name)

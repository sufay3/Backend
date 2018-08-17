from django.http import HttpResponse
from django.views import View
from coin.models import Coin, Market, Exchange, CoinMongo, MarketMongo, ExchangeMongo
import json
import copy


class CoinView(View):
    """
    币种视图
    """

    # 错误消息定义
    _error_msg = {'coin_error': {'code': 5001, 'msg': '币种名字不能为空'},
                  'exchange_error': {'code': 5002, 'msg': '交易所名字不能为空'},
                  'market_error': {'code': 5003, 'msg': '市场名字不能为空'},
                  'general_error': {'code': 5000, 'msg': '请求失败'}
                  }

    # 成功消息定义
    _success_msg = {'code': 0, 'msg': '操作成功'}

    def get_coins(self, request):
        """
        获取币种
        :param request: 请求
        :return: json格式数据
        """

        # 获取参数
        num = request.POST.get('num', 20)

        # 处理请求
        coins = self._on_coin(num)
        if not coins:
            return HttpResponse(json.dumps((self._error_msg['general_error'])))

        # 将数据加入响应结果
        result = copy.copy(self._success_msg)
        result['data'] = coins

        # 返回正确响应
        return HttpResponse(json.dumps(result))

    def get_coin_by_name(self, request):
        """
        获取给定名字的币种数据
        :param request: 请求
        :return: json格式数据
        """

        # 获取参数
        name = request.POST.get('name', '')

        # 处理请求
        coin = self._on_coin_by_name(name)
        if not coin:
            return HttpResponse(json.dumps((self._error_msg['coin_error'])))

        # 将数据加入响应结果
        result = copy.copy(self._success_msg)
        result['data'] = coin

        # 返回正确响应
        return HttpResponse(json.dumps(result))

    def get_exchanges(self, request):
        """
        获取交易所
        :param request: 请求
        :return: json格式数据
        """

        # 获取参数
        num = request.POST.get('num', 20)

        #处理请求
        exchanges = self._on_exchange(num)
        if not exchanges:
            return HttpResponse(json.dumps((self._error_msg['general_error'])))

        # 将数据加入响应结果
        result = copy.copy(self._success_msg)
        result['data'] = exchanges

        # 返回正确响应
        return HttpResponse(json.dumps(result))

    def get_exchange_by_name(self, request):
        """
        获取给定名字的交易所数据
        :param request: 请求
        :return: json格式数据
        """

        # 获取参数
        name = request.POST.get('name', '')

        # 处理请求
        exchange = self._on_exchange_by_name(name)
        if not exchange:
            return HttpResponse(json.dumps((self._error_msg['exchange_error'])))

        # 将数据加入响应结果
        result = copy.copy(self._success_msg)
        result['data'] = exchange

        # 返回正确响应
        return HttpResponse(json.dumps(result))

    def get_markets(self, request):
        """
        获取交易所的市场数据
        :param request: 请求
        :return: json格式数据
        """

        # 获取参数
        exchange = request.POST.get('exchange', '')
        num = request.POST.get('num', 20)

        if exchange == '':
            return HttpResponse(json.dumps((self._error_msg['exchange_error'])))

        # 处理请求
        markets = self._on_market(exchange, num)
        if not markets:
            return HttpResponse(json.dumps((self._error_msg['exchange_error'])))

        # 将数据加入响应结果
        result = copy.copy(self._success_msg)
        result['data'] = markets

        # 返回正确响应
        return HttpResponse(json.dumps(result))

    def _on_coin(self, num):
        """
        从数据库中获取币种数据
        :param num: 数目
        :return: 列表 或 None
        """
        coins = self._on_coin_mongo(num)
        return coins if coins else self._on_coin_sql(num)

    def _on_coin_mongo(self, num):
        """
        从数据库中获取币种数据，mongo后端
        :param num: 数目
        :return: 列表 或 None
        """
        assert  num > 0

        coins = CoinMongo.objects.only('name').limit(num)
        if not coins:
            return None

        result = []
        for c in coins:
            result.append(c.name)

        return result

    def _on_coin_sql(self, num):
        """
        从数据库中获取币种数据，sql后端
        :param num: 数目
        :return: 列表 或 None
        """
        assert num > 0

        coins = Coin.objects.only('name').limit(num)
        if not coins:
            return None

        result = []
        for c in coins:
            result.append(c.name)

        return result

    def _on_coin_by_name(self, name):
        """
        从数据库中获取指定币种的数据
        :param name: 名字
        :return: json数据 或 None
        """
        coin = self._on_coin_by_name_mongo(name)
        return coin if coin else self._on_coin_by_name_sql(name)

    def _on_coin_by_name_mongo(self, name):

        """
        从数据库中获取指定币种的数据，mongo后端
        :param name: 名字
        :return: json数据 或 None
        """
        assert name != ''

        coin = CoinMongo.objects(name=name).exclude('id').first()
        if not coin:
            return None

        return coin.to_json()

    def _on_coin_by_name_sql(self, name):
        """
        从数据库中获取指定币种的数据，sql后端
        :param name: 名字
        :return: json数据 或 None
        """
        assert name != ''

        coin = Coin.objects.filter(name=name).first()
        if not coin:
            return None

        return coin.to_json()

    def _on_exchange(self, num):
        """
        从数据库中获取交易所
        :param num: 数目
        :return: 列表 或 None
        """
        exchanges = self._on_exchange_mongo(num)
        return exchanges if exchanges else self._on_exchange_sql(num)

    def _on_exchange_mongo(self, num):
        """
        从数据库中获取交易所，mongo后端
        :param num: 数目
        :return: 列表 或 None
        """
        assert  num > 0

        exchanges = ExchangeMongo.objects.only('name').limit(num)
        if not exchanges:
            return None

        result = []
        for e in exchanges:
            result.append(e.name)

        return result

    def _on_exchange_sql(self, num):
        """
        从数据库中获取交易所，sql后端
        :param num: 数目
        :return: 列表 或 None
        """
        assert num > 0

        exchanges = Exchange.objects.only('name').limit(num)
        if not exchanges:
            return None

        result = []
        for e in exchanges:
            result.append(e.name)

        return result

    def _on_exchange_by_name(self, name):
        """
        从数据库中获取指定交易所的数据
        :param name: 名字
        :return: json数据 或 None
        """
        exchange = self._on_exchange_by_name_mongo(name)
        return exchange if exchange else self._on_exchange_by_name_sql(name)

    def _on_exchange_by_name_mongo(self, name):

        """
        从数据库中获取指定交易所的数据，mongo后端
        :param name: 名字
        :return: json数据 或 None
        """
        assert name != ''

        exchange = ExchangeMongo.objects(name=name).exclude('id').first()
        if not exchange:
            return None

        return exchange.to_json()

    def _on_exchange_by_name_sql(self, name):
        """
        从数据库中获取指定交易所的数据，sql后端
        :param name: 名字
        :return: json数据 或 None
        """
        assert name != ''

        exchange = Exchange.objects.filter(name=name).first()
        if not exchange:
            return None

        return exchange.to_json()

    def _on_market(self, exchange, num):
        """
        从数据库中获取市场数据
        :param exchange: 交易所
        :param num: 数目
        :return: 市场列表 或 None
        """
        markets = self._on_market_mongo(exchange, num)
        return markets if markets else self._on_market_sql(exchange, num)

    def _on_market_mongo(self, exchange, num):
        """
        从数据库中获取市场数据，mongo后端
        :param exchange: 交易所
        :param num: 数目
        :return: 市场列表 或 None
        """
        assert exchange != '' and num > 0

        exchange = ExchangeMongo.objects(name=exchange).only('markets').first()
        if not exchange:
            return None

        markets = MarketMongo.objects(id__in=exchange.markets).only('name').limit(num)
        if not markets:
            return None

        result = []
        for m in markets:
            result.append(m.name)

        return result

    def _on_market_sql(self, exchange, num):
        """
        从数据库中获取市场数据，sql后端
        :param exchange: 交易所
        :param num: 数目
        :return: 市场列表 或 None
        """
        assert exchange != '' and num > 0

        exchange = Exchange.objects.filter(name=exchange).first()
        if not exchange:
            return None

        markets = exchange.market_set.all().limit(num)
        if not markets:
            return None

        result = []
        for m in markets:
            result.append(m.name)

        return result

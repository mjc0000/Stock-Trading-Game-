from datetime import datetime, timedelta
import random
import math

class Currency:
    def __init__(self, code, name, rate_to_usd, volatility=0.001):
        self.code = code
        self.name = name
        self.rate_to_usd = float(rate_to_usd)  # 对美元汇率
        self.initial_rate = float(rate_to_usd)
        self.volatility = volatility
        self.rate_history = [(datetime.now(), rate_to_usd)]
        
        # 趋势参数
        self.trend = random.uniform(-0.0001, 0.0001)
        self.momentum = 0

class ForexMarket:
    def __init__(self):
        # 初始化汇率
        self.rates = {
            'USD': 1.0,      # 基准货币
            'EUR': 0.85,     # 欧元
            'GBP': 0.73,     # 英镑
            'JPY': 110.0,    # 日元
            'CNY': 6.45,     # 人民币
            'AUD': 1.35,     # 澳元
            'CAD': 1.25,     # 加元
            'CHF': 0.92,     # 瑞士法郎
            'HKD': 7.78,     # 港币
            'SGD': 1.35      # 新加坡元
        }
        
        # 保存初始汇率
        self.initial_rates = self.rates.copy()
        
        # 市场情绪
        self.market_sentiment = 0
        
        # 波动率设置
        self.volatilities = {
            'EUR': 0.002,
            'GBP': 0.003,
            'JPY': 0.002,
            'CNY': 0.001,
            'AUD': 0.003,
            'CAD': 0.002,
            'CHF': 0.002,
            'HKD': 0.001,
            'SGD': 0.002
        }
    
    def update_market(self):
        """更新外汇市场"""
        # 更新市场情绪
        self.market_sentiment = self.market_sentiment * 0.95 + random.normalvariate(0, 0.01)
        
        # 更新每个货币对的汇率
        for currency in self.rates:
            if currency != 'USD':  # 跳过基准货币
                volatility = self.volatilities.get(currency, 0.002)
                change = random.normalvariate(0, volatility) + self.market_sentiment * 0.1
                self.rates[currency] *= (1 + change)
    
    def get_rate(self, from_currency, to_currency):
        """获取货币对的汇率"""
        if from_currency == to_currency:
            return 1.0
        
        # 通过美元计算交叉汇率
        usd_to_from = self.rates.get(from_currency, 1.0)
        usd_to_to = self.rates.get(to_currency, 1.0)
        
        return usd_to_to / usd_to_from

class ForexWallet:
    def __init__(self):
        self.balances = {
            'USD': 0.0,
            'EUR': 0.0,
            'GBP': 0.0,
            'JPY': 0.0,
            'CNY': 0.0,
            'AUD': 0.0,
            'CAD': 0.0,
            'CHF': 0.0,
            'HKD': 0.0,
            'SGD': 0.0
        }
        self.transaction_history = []
    
    def buy(self, from_currency, to_currency, amount, rate, date):
        """买入货币"""
        if from_currency not in self.balances or to_currency not in self.balances:
            return False, "不支持的货币对"
        
        cost = amount * rate
        if self.balances[from_currency] < cost:
            return False, "余额不足"
        
        self.balances[from_currency] -= cost
        self.balances[to_currency] += amount
        
        self.transaction_history.append({
            'type': 'buy',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'rate': rate,
            'date': date
        })
        
        return True, "交易成功"
    
    def sell(self, from_currency, to_currency, amount, rate, date):
        """卖出货币"""
        if from_currency not in self.balances or to_currency not in self.balances:
            return False, "不支持的货币对"
        
        if self.balances[from_currency] < amount:
            return False, "余额不足"
        
        self.balances[from_currency] -= amount
        self.balances[to_currency] += amount * rate
        
        self.transaction_history.append({
            'type': 'sell',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'rate': rate,
            'date': date
        })
        
        return True, "交易成功"

    def get_total_value_usd(self, forex_market):
        """计算总资产（美元）"""
        total = 0
        for currency, amount in self.balances.items():
            if currency == "USD":
                total += amount
            else:
                rate = forex_market.rates[currency]
                total += amount * rate
        return total 
import random
from datetime import datetime, timedelta
import math

class Cryptocurrency:
    def __init__(self, symbol, name, initial_price, volatility=0.02):
        self.symbol = symbol
        self.name = name
        self.price = float(initial_price)
        self.initial_price = float(initial_price)
        self.volatility = volatility
        self.volume_24h = 0
        self.price_history = [(datetime.now(), self.price)]
        
        # 趋势参数
        self.trend = random.uniform(-0.0002, 0.0002)
        self.momentum = 0
        
    def update_price(self, market_sentiment=0):
        """更新价格"""
        # 基础波动
        change = random.normalvariate(self.trend, self.volatility)
        
        # 市场情绪影响
        change += market_sentiment * random.uniform(1.5, 2.5)
        
        # 动量影响
        self.momentum = self.momentum * 0.95 + change * 0.05
        change += self.momentum
        
        # 更新价格
        self.price *= (1 + change)
        
        # 确保价格不会太低
        self.price = max(self.price, self.initial_price * 0.01)
        
        # 更新24小时交易量
        self.volume_24h = self.price * random.uniform(1000, 10000)
        
        # 记录历史
        self.price_history.append((datetime.now(), self.price))
        if len(self.price_history) > 1440:  # 保留24小时的分钟数据
            self.price_history.pop(0)

class CryptoMarket:
    def __init__(self):
        self.cryptos = {
            'BTC': Cryptocurrency("BTC", "BitCoinage", 45000, 0.02),
            'ETH': Cryptocurrency("ETH", "Etherium", 3000, 0.025),
            'DOGE': Cryptocurrency("DOGE", "DogeCoinage", 0.2, 0.05),
            'XRP': Cryptocurrency("XRP", "RippCoin", 0.5, 0.03),
            'LTC': Cryptocurrency("LTC", "LiteCoinage", 100, 0.035)
        }
        self.market_sentiment = 0
    
    def update_market(self):
        """更新市场"""
        # 更新市场情绪
        self.market_sentiment = self.market_sentiment * 0.95 + random.normalvariate(0, 0.01)
        
        # 随机事件
        if random.random() < 0.01:  # 1%概率发生重大事件
            self.market_sentiment += random.uniform(-0.1, 0.1)
        
        # 更新所有加密货币价格
        for crypto in self.cryptos.values():
            crypto.update_price(self.market_sentiment)

class CryptoWallet:
    def __init__(self):
        self.holdings = {}          # 持仓量
        self.staking = {}           # 质押量
        self.transaction_history = []  # 交易历史
    
    def buy(self, symbol, amount, price, current_date):
        """买入加密货币"""
        if symbol not in self.holdings:
            self.holdings[symbol] = 0
        
        self.holdings[symbol] += amount
        
        # 记录交易
        self.transaction_history.append({
            'date': current_date,
            'type': 'buy',
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'total': amount * price
        })
        
        return True
    
    def sell(self, symbol, amount, price, current_date):
        """卖出加密货币"""
        if symbol not in self.holdings or self.holdings[symbol] < amount:
            return False
        
        self.holdings[symbol] -= amount
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # 记录交易
        self.transaction_history.append({
            'date': current_date,
            'type': 'sell',
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'total': amount * price
        })
        
        return True
    
    def stake(self, symbol, amount):
        """质押加密货币"""
        if symbol not in self.holdings or self.holdings[symbol] < amount:
            return False
        
        self.holdings[symbol] -= amount
        if symbol not in self.staking:
            self.staking[symbol] = 0
        self.staking[symbol] += amount
        
        return True
    
    def unstake(self, symbol, amount):
        """解除质押"""
        if symbol not in self.staking or self.staking[symbol] < amount:
            return False
        
        self.staking[symbol] -= amount
        if self.staking[symbol] == 0:
            del self.staking[symbol]
        
        if symbol not in self.holdings:
            self.holdings[symbol] = 0
        self.holdings[symbol] += amount
        
        return True
    
    def get_staking_rewards(self, current_date):
        """获取质押奖励"""
        rewards = []
        for symbol, amount in self.staking.items():
            # 基础年化收益率5-15%
            apy = random.uniform(0.05, 0.15)
            daily_rate = apy / 365
            reward = amount * daily_rate
            
            if symbol not in self.holdings:
                self.holdings[symbol] = 0
            self.holdings[symbol] += reward
            
            rewards.append({
                'date': current_date,
                'symbol': symbol,
                'amount': reward,
                'apy': apy
            })
        
        return rewards

    def check_airdrops(self, current_date):
        """检查空投资格"""
        # 根据持仓量和质押量计算空投资格
        eligible_airdrops = []
        for symbol, amount in self.holdings.items():
            # 检查持仓量是否满足空投条件
            if amount >= 100:  # 示例：持有100个以上代币才有资格
                airdrop_amount = amount * 0.01  # 示例：1%的空投比例
                eligible_airdrops.append({
                    'symbol': symbol,
                    'amount': airdrop_amount,
                    'reason': '持仓奖励'
                })
        
        # 检查质押奖励
        for symbol, stakes in self.staking.items():
            total_staked = sum(stake['amount'] for stake in stakes if not stake['claimed'])
            if total_staked >= 1000:  # 示例：质押1000个以上有额外空投
                airdrop_amount = total_staked * 0.02  # 示例：2%的空投比例
                eligible_airdrops.append({
                    'symbol': symbol,
                    'amount': airdrop_amount,
                    'reason': '质押奖励'
                })
        
        return eligible_airdrops
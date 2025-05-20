import random
from datetime import datetime

class Stock:
    def __init__(self, code, name, industry, initial_price, params):
        self.code = code
        self.name = name
        self.industry = industry
        self.price = float(initial_price)
        self.initial_price = float(initial_price)
        self.price_history = [(datetime.now(), self.price)]
        
        # 从参数字典中获取基础波动参数
        self.volatility = params['volatility']  # 波动率
        self.trend = params['trend']            # 基础趋势
        self.beta = params['beta']              # 市场敏感度
        self.resistance = params['resistance']   # 抗跌性
        
        # 新增市场因子
        self.pe_ratio = params.get('pe_ratio', random.uniform(10, 50))  # 市盈率
        self.pb_ratio = params.get('pb_ratio', random.uniform(1, 5))    # 市净率
        self.market_cap = params.get('market_cap', initial_price * random.uniform(1e8, 1e10))  # 市值
        self.float_shares = params.get('float_shares', self.market_cap / initial_price)  # 流通股本
        self.dividend_yield = params.get('dividend_yield', random.uniform(0, 0.05))  # 股息率
        self.turnover_rate = params.get('turnover_rate', random.uniform(0.5, 5))    # 换手率
        
        # 财务指标
        self.revenue_growth = params.get('revenue_growth', random.uniform(-0.1, 0.3))  # 营收增长率
        self.profit_margin = params.get('profit_margin', random.uniform(0.05, 0.3))    # 利润率
        self.debt_ratio = params.get('debt_ratio', random.uniform(0.3, 0.7))          # 资产负债率
        self.roe = params.get('roe', random.uniform(0.05, 0.25))                      # 净资产收益率
        
    def update_price(self, market_sentiment=0):
        """更新股票价格"""
        # 基础波动
        change = random.normalvariate(self.trend, self.volatility)
        
        # 市场情绪影响
        market_impact = market_sentiment * self.beta
        if market_sentiment < 0:
            market_impact *= (2 - self.resistance)  # 下跌时考虑抗跌性
        
        # 考虑估值影响
        if self.pe_ratio > 30:  # 高估值股票更容易下跌
            change -= random.uniform(0, 0.001)  # 减小影响幅度
        elif self.pe_ratio < 15:  # 低估值股票有上涨动力
            change += random.uniform(0, 0.0005)  # 减小影响幅度
            
        # 考虑市值影响
        if self.market_cap > 1e10:  # 大市值股票波动较小
            change *= 0.9
        elif self.market_cap < 1e9:  # 小市值股票波动较大
            change *= 1.1
            
        # 考虑换手率影响
        if self.turnover_rate > 3:  # 高换手率增加波动性
            change *= 1.1
            
        # 考虑财务指标影响
        if self.revenue_growth > 0.2 and self.profit_margin > 0.15:  # 业绩优秀
            change += random.uniform(0, 0.0005)  # 减小影响幅度
        elif self.revenue_growth < 0 or self.profit_margin < 0.05:   # 业绩不佳
            change -= random.uniform(0, 0.0005)  # 减小影响幅度
            
        # 价格回归机制
        price_diff_ratio = (self.price - self.initial_price) / self.initial_price
        if abs(price_diff_ratio) > 0.5:  # 如果价格偏离初始价格超过50%
            regression = -price_diff_ratio * 0.001  # 添加小幅回归力
            change += regression
        
        # 更新价格
        self.price *= (1 + change + market_impact)
        
        # 限制单日波动幅度（±10%）
        if self.price_history:
            last_price = self.price_history[-1][1]
            max_change = last_price * 0.1
            self.price = max(min(self.price, last_price + max_change), 
                            last_price - max_change)
        
        # 确保价格不会太低
        min_price = self.initial_price * 0.2  # 最低不低于初始价格的20%
        self.price = max(self.price, min_price)
        
        # 更新相关指标
        self.market_cap = self.price * self.float_shares
        self.turnover_rate = random.uniform(0.5, 5)  # 随机更新换手率
        
        # 记录历史
        self.price_history.append((datetime.now(), self.price))
        if len(self.price_history) > 100:  # 保留最近100个价格点
            self.price_history.pop(0)

class StockMarket:
    def __init__(self):
        """初始化股票市场"""
        self.stocks = {}  # 存储所有股票
        self.market_sentiment = 0  # 市场情绪
        self._initialize_stocks()  # 注意是下划线开头
    
    def _initialize_stocks(self):  # 改为私有方法
        """初始化股票列表"""
        self.stocks = {
            "000858": ("鑫穗酒业", "白酒", 180, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1,
                'pe_ratio': 38,           # 高市盈率
                'pb_ratio': 8,            # 高市净率
                'market_cap': 7.2e11,     # 7200亿市值
                'float_shares': 3.88e9,   # 38.8亿流通股
                'dividend_yield': 0.015,  # 1.5%股息率
                'turnover_rate': 0.9,     # 较低换手率
                'revenue_growth': 0.12,   # 12%收入增长
                'profit_margin': 0.40,    # 40%利润率
                'debt_ratio': 0.15,       # 低负债率
                'roe': 0.30              # 30%净资产收益率
            }),
            "600036": ("华岳银行", "银行", 45, {
                'volatility': 0.012,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            "601318": ("安平保险", "保险", 80, {
                'volatility': 0.016,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "000333": ("格瑞电器", "家电", 90, {
                'volatility': 0.014,
                'trend': 0.0002,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "600276": ("康恒医药", "医药", 60, {
                'volatility': 0.020,
                'trend': 0.0003,
                'beta': 0.7,
                'resistance': 1.3
            }),
            "601888": ("环游免税", "免税", 280, {
                'volatility': 0.025,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "002594": ("比迪汽车", "新能源车", 280, {
                'volatility': 0.028,
                'trend': 0.0004,
                'beta': 1.4,
                'resistance': 0.6
            }),
            "600887": ("伊品乳业", "食品饮料", 35, {
                'volatility': 0.012,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "601899": ("紫晶矿业", "有色金属", 12, {
                'volatility': 0.022,
                'trend': 0.0001,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "600030": ("中诚证券", "证券", 30, {
                'volatility': 0.020,
                'trend': 0.0002,
                'beta': 1.4,
                'resistance': 0.6
            }),
            "601012": ("龙晶能源", "光伏", 60, {
                'volatility': 0.025,
                'trend': 0.0003,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "600031": ("华工科技", "机械", 25, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            "601668": ("中坚建设", "建筑", 6, {
                'volatility': 0.015,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "600585": ("东虹建材", "建材", 45, {
                'volatility': 0.016,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            "601857": ("中石能源", "石油", 8, {
                'volatility': 0.014,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "600028": ("国能化功", "石油", 5, {
                'volatility': 0.013,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "601398": ("华尚银行", "银行", 5.5, {
                'volatility': 0.011,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0,
                'pe_ratio': 5.5,          # 低市盈率
                'pb_ratio': 0.8,          # 低市净率
                'market_cap': 2.1e12,     # 2.1万亿市值
                'float_shares': 3.45e11,  # 3450亿流通股
                'dividend_yield': 0.055,  # 5.5%高股息率
                'turnover_rate': 0.5,     # 低换手率
                'revenue_growth': 0.05,   # 5%稳定增长
                'profit_margin': 0.35,    # 35%利润率
                'debt_ratio': 0.85,       # 高负债率(银行特点)
                'roe': 0.12              # 12%净资产收益率
            }),
            "600104": ("东坊汽车", "汽车", 20, {
                'volatility': 0.016,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            "601288": ("农尚银行", "银行", 4, {
                'volatility': 0.010,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "600809": ("金岁酒厂", "白酒", 380, {
                'volatility': 0.020,
                'trend': 0.0002,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "000568": ("金全酒业", "白酒", 220, {
                'volatility': 0.019,
                'trend': 0.0002,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "600436": ("仁禾药业", "中药", 420, {
                'volatility': 0.018,
                'trend': 0.0002,
                'beta': 0.7,
                'resistance': 1.3,
                'pe_ratio': 55,           # 高市盈率
                'pb_ratio': 18,           # 高市净率
                'market_cap': 2.5e11,     # 2500亿市值
                'float_shares': 6.03e8,   # 6.03亿流通股
                'dividend_yield': 0.008,  # 0.8%低股息率
                'turnover_rate': 1.8,     # 中等换手率
                'revenue_growth': 0.25,   # 25%高增长
                'profit_margin': 0.35,    # 35%高利润率
                'debt_ratio': 0.25,       # 低负债率
                'roe': 0.28              # 28%高净资产收益率
            }),
            "000661": ("北芳医药", "医药", 380, {
                'volatility': 0.022,
                'trend': 0.0003,
                'beta': 0.8,
                'resistance': 1.2
            }),
            "600763": ("康态医疗", "医疗服务", 220, {
                'volatility': 0.021,
                'trend': 0.0002,
                'beta': 0.8,
                'resistance': 1.2,
                'pe_ratio': 60,           # 高市盈率
                'pb_ratio': 12,           # 高市净率
                'market_cap': 7.5e10,     # 750亿市值
                'float_shares': 3.2e8,    # 3.2亿流通股
                'dividend_yield': 0.003,  # 低股息率
                'turnover_rate': 2.5,     # 较高换手率
                'revenue_growth': 0.30,   # 高增长
                'profit_margin': 0.25,    # 25%利润率
                'debt_ratio': 0.30,       # 低负债率
                'roe': 0.22              # 22%净资产收益率
            }),
            "603259": ("明得生物", "医药", 120, {
                'volatility': 0.025,
                'trend': 0.0003,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "002460": ("华里科技", "新能源材料", 180, {
                'volatility': 0.028,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.7,
                'pe_ratio': 42,           # 高市盈率
                'pb_ratio': 6.5,          # 高市净率
                'market_cap': 2.8e11,     # 2800亿市值
                'float_shares': 1.56e9,   # 15.6亿流通股
                'dividend_yield': 0.005,  # 0.5%低股息率
                'turnover_rate': 4.2,     # 高换手率
                'revenue_growth': 0.55,   # 55%高增长
                'profit_margin': 0.25,    # 25%利润率
                'debt_ratio': 0.45,       # 中等负债率
                'roe': 0.22              # 22%净资产收益率
            }),
            "002466": ("东坊锂业", "新能源材料", 160, {
                'volatility': 0.028,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.7
            }),
            "601633": ("华星汽车", "汽车", 35, {
                'volatility': 0.020,
                'trend': 0.0002,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "600660": ("华兴玻璃", "汽车零部件", 45, {
                'volatility': 0.015,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1,
                'pe_ratio': 22,           # 中等市盈率
                'pb_ratio': 3.2,          # 中等市净率
                'market_cap': 1.1e11,     # 1100亿市值
                'float_shares': 2.5e9,    # 25亿流通股
                'dividend_yield': 0.035,  # 3.5%股息率
                'turnover_rate': 1.5,     # 中等换手率
                'revenue_growth': 0.12,   # 稳定增长
                'profit_margin': 0.20,    # 20%利润率
                'debt_ratio': 0.40,       # 中等负债率
                'roe': 0.15              # 15%净资产收益率
            }),
            "002475": ("华迅科技", "电子", 35, {
                'volatility': 0.025,
                'trend': 0.0003,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "002241": ("东坊电子", "电子", 30, {
                'volatility': 0.024,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "002415": ("华按科技", "电子", 40, {
                'volatility': 0.020,
                'trend': 0.0002,
                'beta': 1.1,
                'resistance': 0.9,
                'pe_ratio': 28,           # 中等市盈率
                'pb_ratio': 5.8,          # 中等市净率
                'market_cap': 3.8e11,     # 3800亿市值
                'float_shares': 9.5e9,    # 95亿流通股
                'dividend_yield': 0.02,   # 2%股息率
                'turnover_rate': 2.2,     # 中等换手率
                'revenue_growth': 0.18,   # 18%增长
                'profit_margin': 0.28,    # 28%利润率
                'debt_ratio': 0.35,       # 低负债率
                'roe': 0.25              # 25%净资产收益率
            }),
            "600745": ("华新科技", "电子", 80, {
                'volatility': 0.026,
                'trend': 0.0003,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "601166": ("华星银行", "银行", 18, {
                'volatility': 0.012,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0,
                'pe_ratio': 5.8,          # 低市盈率
                'pb_ratio': 0.75,         # 低市净率
                'market_cap': 4.2e11,     # 4200亿市值
                'float_shares': 2.1e10,   # 210亿流通股
                'dividend_yield': 0.05,   # 5%高股息率
                'turnover_rate': 0.8,     # 低换手率
                'revenue_growth': 0.06,   # 6%增长
                'profit_margin': 0.35,    # 35%利润率
                'debt_ratio': 0.88,       # 高负债率
                'roe': 0.13              # 13%净资产收益率
            }),
            "600016": ("华敏银行", "银行", 4.5, {
                'volatility': 0.011,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "601688": ("华态证券", "证券", 20, {
                'volatility': 0.022,
                'trend': 0.0002,
                'beta': 1.4,
                'resistance': 0.6,
                'pe_ratio': 15,           # 中等市盈率
                'pb_ratio': 1.8,          # 较低市净率
                'market_cap': 1.8e11,     # 1800亿市值
                'float_shares': 9.1e9,    # 91亿流通股
                'dividend_yield': 0.025,  # 2.5%股息率
                'turnover_rate': 2.8,     # 较高换手率
                'revenue_growth': 0.15,   # 15%收入增长
                'profit_margin': 0.32,    # 32%利润率
                'debt_ratio': 0.65,       # 较高负债率
                'roe': 0.18              # 18%净资产收益率
            }),
            "600837": ("海同证券", "证券", 15, {
                'volatility': 0.022,
                'trend': 0.0002,
                'beta': 1.4,
                'resistance': 0.6
            }),
            "601628": ("中囯人寿", "保险", 35, {
                'volatility': 0.015,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            "600048": ("保力发展", "房地产", 15, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8,
                'pe_ratio': 6.5,          # 低市盈率
                'pb_ratio': 1.0,          # 低市净率
                'market_cap': 1.8e11,     # 1800亿市值
                'float_shares': 1.2e10,   # 120亿流通股
                'dividend_yield': 0.06,   # 6%高股息率
                'turnover_rate': 1.8,     # 中等换手率
                'revenue_growth': -0.05,  # 收入下滑
                'profit_margin': 0.15,    # 15%利润率
                'debt_ratio': 0.75,       # 高负债率
                'roe': 0.10              # 10%净资产收益率
            }),
            "001979": ("招尚蛇口", "房地产", 18, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "600009": ("上海机常", "机场", 80, {
                'volatility': 0.020,
                'trend': 0.0002,
                'beta': 1.0,
                'resistance': 1.0,
                'pe_ratio': 35,           # 较高市盈率
                'pb_ratio': 3.2,          # 中等市净率
                'market_cap': 1.6e11,     # 1600亿市值
                'float_shares': 1.93e9,   # 19.3亿流通股
                'dividend_yield': 0.015,  # 1.5%股息率
                'turnover_rate': 1.5,     # 中等换手率
                'revenue_growth': 0.25,   # 疫情后复苏
                'profit_margin': 0.30,    # 30%利润率
                'debt_ratio': 0.35,       # 较低负债率
                'roe': 0.12              # 12%净资产收益率
            }),
            "601021": ("春丘航空", "航空", 45, {
                'volatility': 0.025,
                'trend': 0.0001,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "600795": ("国点电力", "电力", 3.5, {
                'volatility': 0.012,
                'trend': 0.0001,
                'beta': 0.7,
                'resistance': 1.3
            }),
            "600900": ("长讲电力", "电力", 22, {
                'volatility': 0.010,
                'trend': 0.0001,
                'beta': 0.6,
                'resistance': 1.4,
                'pe_ratio': 18,           # 中等偏低市盈率
                'pb_ratio': 2.5,          # 中等市净率
                'market_cap': 5.2e11,     # 5200亿市值
                'float_shares': 2.2e10,   # 220亿流通股
                'dividend_yield': 0.045,  # 4.5%高股息率
                'turnover_rate': 0.8,     # 低换手率
                'revenue_growth': 0.08,   # 稳定增长
                'profit_margin': 0.45,    # 高利润率
                'debt_ratio': 0.55,       # 中等负债率
                'roe': 0.15              # 15%净资产收益率
            }),
            "600025": ("华能水点", "电力", 8, {
                'volatility': 0.011,
                'trend': 0.0001,
                'beta': 0.7,
                'resistance': 1.3
            }),
            "600050": ("中囯联通", "通信", 5, {
                'volatility': 0.015,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "600941": ("中囯移动", "通信", 80, {
                'volatility': 0.012,
                'trend': 0.0001,
                'beta': 0.8,
                'resistance': 1.2,
                'pe_ratio': 12,           # 低市盈率
                'pb_ratio': 1.2,          # 低市净率
                'market_cap': 1.6e12,     # 1.6万亿市值
                'float_shares': 2.1e10,   # 210亿流通股
                'dividend_yield': 0.05,   # 5%高股息率
                'turnover_rate': 0.8,     # 低换手率
                'revenue_growth': 0.06,   # 稳定增长
                'profit_margin': 0.15,    # 15%利润率
                'debt_ratio': 0.25,       # 低负债率
                'roe': 0.12              # 12%净资产收益率
            }),
            "601360": ("三溜零", "互联网", 15, {
                'volatility': 0.025,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7,
                'pe_ratio': 25,           # 中等市盈率
                'pb_ratio': 3.5,          # 中等市净率
                'market_cap': 1.2e11,     # 1200亿市值
                'float_shares': 7.8e9,    # 78亿流通股
                'dividend_yield': 0.008,  # 0.8%低股息率
                'turnover_rate': 2.8,     # 较高换手率
                'revenue_growth': 0.25,   # 25%高增长
                'profit_margin': 0.20,    # 20%利润率
                'debt_ratio': 0.30,       # 较低负债率
                'roe': 0.18              # 18%净资产收益率
            }),
            "600132": ("重庆啤玖", "啤酒", 120, {
                'volatility': 0.016,
                'trend': 0.0001,
                'beta': 0.8,
                'resistance': 1.2,
                'pe_ratio': 32,           # 较高市盈率
                'pb_ratio': 8.5,          # 较高市净率
                'market_cap': 5.8e10,     # 580亿市值
                'float_shares': 4.8e8,    # 4.8亿流通股
                'dividend_yield': 0.02,   # 2%股息率
                'turnover_rate': 1.5,     # 中等换手率
                'revenue_growth': 0.15,   # 15%增长
                'profit_margin': 0.18,    # 18%利润率
                'debt_ratio': 0.35,       # 较低负债率
                'roe': 0.20              # 20%净资产收益率
            }),
            "600600": ("青岛啤玖", "啤酒", 110, {
                'volatility': 0.015,
                'trend': 0.0001,
                'beta': 0.8,
                'resistance': 1.2
            }),
            "000729": ("燕晶啤酒", "啤酒", 15, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "603288": ("海添味业", "食品", 120, {
                'volatility': 0.014,
                'trend': 0.0002,
                'beta': 0.7,
                'resistance': 1.3,
                'pe_ratio': 45,           # 高市盈率
                'pb_ratio': 12,           # 高市净率
                'market_cap': 3.8e11,     # 380亿市值
                'float_shares': 3.2e9,    # 32亿流通股
                'dividend_yield': 0.015,  # 1.5%股息率
                'turnover_rate': 1.2,     # 中等换手率
                'revenue_growth': 0.18,   # 18%增长
                'profit_margin': 0.30,    # 30%高利润率
                'debt_ratio': 0.20,       # 低负债率
                'roe': 0.28              # 28%高净资产收益率
            }),
            "603899": ("晨广文具", "文具", 90, {
                'volatility': 0.016,
                'trend': 0.0002,
                'beta': 0.8,
                'resistance': 1.2,
                'pe_ratio': 35,           # 较高市盈率
                'pb_ratio': 7.5,          # 较高市净率
                'market_cap': 8.5e10,     # 850亿市值
                'float_shares': 9.2e8,    # 9.2亿流通股
                'dividend_yield': 0.012,  # 1.2%股息率
                'turnover_rate': 1.8,     # 中等换手率
                'revenue_growth': 0.20,   # 20%增长
                'profit_margin': 0.22,    # 22%利润率
                'debt_ratio': 0.25,       # 低负债率
                'roe': 0.25              # 25%净资产收益率
            }),
            "600690": ("海儿智家", "家电", 35, {
                'volatility': 0.016,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9,
                'pe_ratio': 18,           # 中等市盈率
                'pb_ratio': 2.8,          # 中等市净率
                'market_cap': 3.2e11,     # 3200亿市值
                'float_shares': 9.1e9,    # 91亿流通股
                'dividend_yield': 0.03,   # 3%股息率
                'turnover_rate': 1.6,     # 中等换手率
                'revenue_growth': 0.12,   # 12%增长
                'profit_margin': 0.08,    # 8%利润率
                'debt_ratio': 0.45,       # 中等负债率
                'roe': 0.15              # 15%净资产收益率
            }),
            "000651": ("格利电器", "家电", 55, {
                'volatility': 0.015,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0,
                'pe_ratio': 12,           # 低市盈率
                'pb_ratio': 2.5,          # 中等市净率
                'market_cap': 3.8e11,     # 3800亿市值
                'float_shares': 5.8e9,    # 58亿流通股
                'dividend_yield': 0.045,  # 4.5%高股息率
                'turnover_rate': 1.2,     # 中等换手率
                'revenue_growth': 0.08,   # 8%增长
                'profit_margin': 0.12,    # 12%利润率
                'debt_ratio': 0.40,       # 中等负债率
                'roe': 0.18              # 18%净资产收益率
            }),
            "002508": ("老斑电器", "家电", 40, {
                'volatility': 0.017,
                'trend': 0.0001,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "600741": ("华宇汽车", "汽车零部件", 28, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8,
                'pe_ratio': 15,           # 中等市盈率
                'pb_ratio': 1.8,          # 较低市净率
                'market_cap': 8.8e10,     # 880亿市值
                'float_shares': 3.1e9,    # 31亿流通股
                'dividend_yield': 0.035,  # 3.5%股息率
                'turnover_rate': 1.6,     # 中等换手率
                'revenue_growth': 0.10,   # 10%增长
                'profit_margin': 0.08,    # 8%利润率
                'debt_ratio': 0.45,       # 中等负债率
                'roe': 0.12              # 12%净资产收益率
            }),
            "603799": ("华有钴业", "新能源材料", 120, {
                'volatility': 0.028,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.6,
                'pe_ratio': 38,           # 高市盈率
                'pb_ratio': 4.8,          # 较高市净率
                'market_cap': 1.5e11,     # 1500亿市值
                'float_shares': 1.2e9,    # 12亿流通股
                'dividend_yield': 0.006,  # 0.6%低股息率
                'turnover_rate': 3.8,     # 高换手率
                'revenue_growth': 0.45,   # 45%高增长
                'profit_margin': 0.15,    # 15%利润率
                'debt_ratio': 0.50,       # 较高负债率
                'roe': 0.20              # 20%净资产收益率
            }),
            "603993": ("洛阳牧业", "有色金属", 8, {
                'volatility': 0.022,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "601225": ("陕西美业", "煤炭", 15, {
                'volatility': 0.020,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8,
                'pe_ratio': 8,            # 低市盈率
                'pb_ratio': 1.5,          # 低市净率
                'market_cap': 1.5e11,     # 1500亿市值
                'float_shares': 1.0e10,   # 100亿流通股
                'dividend_yield': 0.07,   # 7%高股息率
                'turnover_rate': 1.2,     # 中等换手率
                'revenue_growth': 0.15,   # 15%增长
                'profit_margin': 0.25,    # 25%利润率
                'debt_ratio': 0.45,       # 中等负债率
                'roe': 0.18              # 18%净资产收益率
            }),
            "601088": ("中囯神华", "煤炭", 30, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9,
                'pe_ratio': 9,            # 低市盈率
                'pb_ratio': 1.3,          # 低市净率
                'market_cap': 5.8e11,     # 5800亿市值
                'float_shares': 1.95e10,  # 195亿流通股
                'dividend_yield': 0.08,   # 8%高股息率
                'turnover_rate': 1.0,     # 低换手率
                'revenue_growth': 0.12,   # 12%增长
                'profit_margin': 0.28,    # 28%利润率
                'debt_ratio': 0.40,       # 中等负债率
                'roe': 0.20              # 20%净资产收益率
            }),
            "600188": ("兖框能源", "煤炭", 25, {
                'volatility': 0.019,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "600309": ("万花化学", "化工", 150, {
                'volatility': 0.022,
                'trend': 0.0002,
                'beta': 1.2,
                'resistance': 0.8,
                'pe_ratio': 15,           # 中等市盈率
                'pb_ratio': 3.2,          # 中等市净率
                'market_cap': 4.2e11,     # 4200亿市值
                'float_shares': 2.8e9,    # 28亿流通股
                'dividend_yield': 0.025,  # 2.5%股息率
                'turnover_rate': 2.0,     # 中等换手率
                'revenue_growth': 0.20,   # 20%增长
                'profit_margin': 0.22,    # 22%利润率
                'debt_ratio': 0.48,       # 中等负债率
                'roe': 0.22              # 22%净资产收益率
            }),
            "600346": ("恒丽石化", "化工", 25, {
                'volatility': 0.024,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7,
                'pe_ratio': 12,           # 中等偏低市盈率
                'pb_ratio': 2.2,          # 中等市净率
                'market_cap': 1.8e11,     # 1800亿市值
                'float_shares': 7.0e9,    # 70亿流通股
                'dividend_yield': 0.035,  # 3.5%股息率
                'turnover_rate': 2.2,     # 中等换手率
                'revenue_growth': 0.18,   # 18%增长
                'profit_margin': 0.15,    # 15%利润率
                'debt_ratio': 0.55,       # 较高负债率
                'roe': 0.16              # 16%净资产收益率
            }),
            "002601": ("龙百集团", "化工", 35, {
                'volatility': 0.023,
                'trend': 0.0002,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "600487": ("亨同光电", "通信设备", 20, {
                'volatility': 0.024,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "002230": ("科大迅飞", "人工智能", 45, {
                'volatility': 0.028,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.6,
                'pe_ratio': 68,           # 高市盈率
                'pb_ratio': 8.5,          # 高市净率
                'market_cap': 1.1e11,     # 1100亿市值
                'float_shares': 2.2e9,    # 22亿流通股
                'dividend_yield': 0.002,  # 0.2%低股息率
                'turnover_rate': 3.5,     # 高换手率
                'revenue_growth': 0.35,   # 35%高增长
                'profit_margin': 0.12,    # 12%利润率
                'debt_ratio': 0.30,       # 低负债率
                'roe': 0.15              # 15%净资产收益率
            }),
            "002410": ("广联大", "软件", 85, {
                'volatility': 0.025,
                'trend': 0.0003,
                'beta': 1.3,
                'resistance': 0.7,
                'pe_ratio': 72,           # 高市盈率
                'pb_ratio': 12,           # 高市净率
                'market_cap': 9.8e10,     # 980亿市值
                'float_shares': 1.15e9,   # 11.5亿流通股
                'dividend_yield': 0.001,  # 0.1%低股息率
                'turnover_rate': 3.2,     # 高换手率
                'revenue_growth': 0.30,   # 30%高增长
                'profit_margin': 0.25,    # 25%利润率
                'debt_ratio': 0.25,       # 低负债率
                'roe': 0.20              # 20%净资产收益率
            }),
            "600588": ("用有网络", "软件", 35, {
                'volatility': 0.026,
                'trend': 0.0003,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "300059": ("东坊财富", "金融科技", 25, {
                'volatility': 0.028,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.6
            }),
            "300760": ("迈睿医疗", "医疗器械", 380, {
                'volatility': 0.022,
                'trend': 0.0003,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "300015": ("爱儿眼科", "医疗服务", 45, {
                'volatility': 0.024,
                'trend': 0.0002,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "300347": ("泰哥医药", "医药", 90, {
                'volatility': 0.024,
                'trend': 0.0003,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "603882": ("金玉医学", "医疗服务", 65, {
                'volatility': 0.023,
                'trend': 0.0002,
                'beta': 0.9,
                'resistance': 1.1
            }),
            # 军工板块
            "600760": ("国防科技", "军工", 65, {
                'volatility': 0.025,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "000768": ("航空科技", "军工", 45, {
                'volatility': 0.024,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "002013": ("航天动力", "军工", 25, {
                'volatility': 0.023,
                'trend': 0.0002,
                'beta': 1.2,
                'resistance': 0.8
            }),
            # 半导体板块
            "688981": ("华芯半导体", "半导体", 55, {
                'volatility': 0.030,
                'trend': 0.0003,
                'beta': 1.5,
                'resistance': 0.5
            }),
            "002049": ("华光芯片", "半导体", 120, {
                'volatility': 0.028,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.6
            }),
            "002371": ("华创科技", "半导体设备", 180, {
                'volatility': 0.029,
                'trend': 0.0003,
                'beta': 1.4,
                'resistance': 0.6
            }),
            # 农业板块
            "000998": ("金禾农业", "农业", 25, {
                'volatility': 0.018,
                'trend': 0.0001,
                'beta': 0.8,
                'resistance': 1.2
            }),
            "002714": ("华牧农业", "养殖", 65, {
                'volatility': 0.022,
                'trend': 0.0002,
                'beta': 0.9,
                'resistance': 1.1
            }),
            "002311": ("东方饲料", "饲料", 45, {
                'volatility': 0.020,
                'trend': 0.0002,
                'beta': 0.9,
                'resistance': 1.1
            }),
            # 物流板块
            "600233": ("华通快递", "物流", 18, {
                'volatility': 0.020,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            "002352": ("华丰物流", "物流", 55, {
                'volatility': 0.018,
                'trend': 0.0002,
                'beta': 1.0,
                'resistance': 1.0
            }),
            "603056": ("华通物流", "物流", 15, {
                'volatility': 0.022,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            # 旅游板块
            "600054": ("东方旅游", "旅游", 12, {
                'volatility': 0.020,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "603136": ("青山湖", "旅游", 25, {
                'volatility': 0.021,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "000069": ("华旅地产", "旅游地产", 8, {
                'volatility': 0.019,
                'trend': 0.0001,
                'beta': 1.1,
                'resistance': 0.9
            }),
            # 教育板块
            "003032": ("华育教育", "教育", 15, {
                'volatility': 0.024,
                'trend': 0.0002,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "003989": ("国科航天", "航天", 85, {
                'volatility': 0.026,
                'trend': 0.0002,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "002841": ("华科教育", "教育设备", 75, {
                'volatility': 0.023,
                'trend': 0.0002,
                'beta': 1.2,
                'resistance': 0.8
            }),
            # 体育板块
            "600136": ("华体文化", "体育", 8, {
                'volatility': 0.025,
                'trend': 0.0001,
                'beta': 1.3,
                'resistance': 0.7
            }),
            "300651": ("华兴体育", "体育器材", 25, {
                'volatility': 0.024,
                'trend': 0.0001,
                'beta': 1.2,
                'resistance': 0.8
            }),
            "002780": ("远征户外", "体育用品", 15, {
                'volatility': 0.026,
                'trend': 0.0001,
                'beta': 1.3,
                'resistance': 0.7
            })
        }
        
        # 初始化时统一处理股票代码格式
        for code, (name, industry, price, params) in self.stocks.items():
            # 确保code是6位字符串
            formatted_code = str(code).zfill(6)
            self.stocks[formatted_code] = Stock(formatted_code, name, industry, price, params)
    
    def get_stock(self, code):
        """获取指定股票"""
        if isinstance(code, str):
            # 如果是纯数字的字符串，补齐6位
            if code.isdigit():
                code = code.zfill(6)
            return self.stocks.get(code)
        elif isinstance(code, int):
            # 如果是数字，转换为6位字符串
            return self.stocks.get(str(code).zfill(6))
        return None
    
    def get_all_stocks(self):
        """获取所有股票"""
        return list(self.stocks.values())  # 返回列表而不是视图
    
    def update_prices(self):
        """更新所有股票价格"""
        self.update_market_sentiment()
        for stock in self.stocks.values():
            stock.update_price(self.market_sentiment)
    
    def update_market_sentiment(self):
        """更新市场情绪"""
        # 市场情绪具有延续性，但会逐渐回归
        self.market_sentiment = self.market_sentiment * 0.95 + random.normalvariate(0, 0.01)
        
        # 随机重大事件
        if random.random() < 0.01:  # 1%概率发生重大事件
            self.market_sentiment += random.uniform(-0.05, 0.05) 
    
    def apply_global_change(self, change_percent):
        """应用全局价格变化"""
        for stock in self.stocks.values():
            stock.price *= (1 + change_percent)
            stock.price_history.append((datetime.now(), stock.price))
            if len(stock.price_history) > 100:
                stock.price_history.pop(0)
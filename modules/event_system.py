import random
from datetime import datetime, timedelta

class Event:
    def __init__(self, name, description, effect_description, effect_func, 
                 probability=1.0, cooldown_days=7, tags=None):
        self.name = name
        self.description = description
        self.effect_description = effect_description
        self.effect = effect_func
        self.probability = probability  # 基础触发概率
        self.cooldown_days = cooldown_days  # 冷却时间
        self.tags = tags or []  # 事件标签
        self.last_trigger_date = None  # 上次触发时间

class EventSystem:
    def __init__(self):
        self.events = []  # 所有可能的事件
        self.event_history = []  # 已发生的事件记录
        self.market_events = []  # 市场相关事件
        self.industry_events = []  # 行业相关事件
        self.personal_events = []  # 个人事件
        self.initialize_events()
    
    def initialize_events(self):
        """初始化所有事件"""
        # 宏观经济事件
        self.market_events.extend([
            Event("央行降息", 
                  "中央银行宣布降低基准利率0.25个百分点",
                  "市场大幅上涨，金融股领涨", 
                  lambda p, m: self._handle_rate_cut(m),
                  probability=0.05,
                  tags=["政策", "利率"]),
                  
            Event("央行降准", 
                  "中央银行宣布下调存款准备金率0.5个百分点",
                  "市场流动性改善，银行股上涨", 
                  lambda p, m: self._handle_reserve_cut(m),
                  probability=0.05,
                  tags=["政策", "银行"]),
                  
            Event("外资流入", 
                  "北向资金大幅净流入",
                  "市场情绪高涨，蓝筹股表现强势", 
                  lambda p, m: self._handle_foreign_capital(m),
                  probability=0.1,
                  tags=["资金", "外资"]),
                  
            Event("外资流出", 
                  "北向资金大幅净流出",
                  "市场承压，外资持股较多的股票调整", 
                  lambda p, m: self._handle_foreign_outflow(m),
                  probability=0.1,
                  tags=["资金", "外资"]),
                  
            Event("经济数据向好", 
                  "GDP、PMI等经济数据超预期",
                  "周期股集体上涨", 
                  lambda p, m: self._handle_good_economy(m),
                  probability=0.08,
                  tags=["经济", "数据"]),
                  
            Event("通胀超预期", 
                  "CPI同比增速创新高",
                  "市场避险情绪升温", 
                  lambda p, m: self._handle_high_inflation(m),
                  probability=0.06,
                  tags=["经济", "通胀"]),
                  
            Event("美联储加息",
                  "美联储宣布加息25个基点",
                  "外资流出，市场承压",
                  lambda p, m: self._handle_fed_rate_hike(m),
                  probability=0.04,
                  tags=["国际", "利率"]),
                  
            Event("国际贸易摩擦",
                  "主要经济体之间贸易关系紧张",
                  "出口相关行业承压",
                  lambda p, m: self._handle_trade_friction(m),
                  probability=0.05,
                  tags=["国际", "贸易"]),
                  
            Event("全球供应链中断",
                  "全球供应链出现严重中断",
                  "制造业、物流行业受影响",
                  lambda p, m: self._handle_supply_chain_disruption(m),
                  probability=0.03,
                  tags=["国际", "供应链"]),
                  
            Event("节日消费",
                  "重要节日带动消费增长",
                  "消费股、免税概念走强",
                  lambda p, m: self._handle_holiday_consumption(m),
                  probability=0.08,
                  tags=["消费", "节日"]),
                  
            Event("极端天气",
                  "极端天气影响生产生活",
                  "保险、农业股波动",
                  lambda p, m: self._handle_extreme_weather(m),
                  probability=0.05,
                  tags=["天气", "农业"]),
                  
            Event("季节性疫情",
                  "季节性疫情发生",
                  "医药股、在线经济受关注",
                  lambda p, m: self._handle_seasonal_epidemic(m),
                  probability=0.06,
                  tags=["疫情", "医药"])
        ])
        
        # 产业政策事件
        self.industry_events.extend([
            Event("新能源补贴", 
                  "新能源汽车补贴政策延续",
                  "新能源车产业链集体上涨", 
                  lambda p, m: self._handle_industry_policy(m, "新能源车", 0.06),
                  probability=0.1,
                  tags=["政策", "新能源"]),
                  
            Event("医保谈判", 
                  "医保药品谈判结果公布",
                  "医药股分化", 
                  lambda p, m: self._handle_medical_insurance(m),
                  probability=0.08,
                  tags=["医药", "政策"]),
                  
            Event("芯片突破", 
                  "国产芯片取得重大技术突破",
                  "半导体板块集体大涨", 
                  lambda p, m: self._handle_tech_breakthrough(m, "半导体", 0.08),
                  probability=0.05,
                  tags=["科技", "半导体"]),
                  
            Event("房地产调控", 
                  "多地出台房地产调控政策",
                  "地产股和建材股承压", 
                  lambda p, m: self._handle_real_estate_policy(m),
                  probability=0.1,
                  tags=["房地产", "政策"]),
                  
            Event("AI突破",
                  "人工智能领域取得重大突破",
                  "科技股集体走强",
                  lambda p, m: self._handle_ai_breakthrough(m),
                  probability=0.06,
                  tags=["科技", "AI"]),
                  
            Event("新能源技术革新",
                  "新型电池技术取得突破",
                  "新能源产业链上涨",
                  lambda p, m: self._handle_energy_innovation(m),
                  probability=0.05,
                  tags=["科技", "新能源"]),
                  
            Event("生物医药突破",
                  "新药研发取得重大进展",
                  "医药股表现活跃",
                  lambda p, m: self._handle_biotech_breakthrough(m),
                  probability=0.04,
                  tags=["科技", "医药"]),
                  
            Event("产业升级",
                  "传统产业加速数字化转型",
                  "科技服务股走强",
                  lambda p, m: self._handle_industry_upgrade(m),
                  probability=0.07,
                  tags=["产业", "科技"]),
                  
            Event("环保督查",
                  "环保督查行动开展",
                  "高污染行业承压，环保股上涨",
                  lambda p, m: self._handle_environmental_inspection(m),
                  probability=0.06,
                  tags=["环保", "政策"]),
                  
            Event("产能过剩",
                  "部分行业产能过剩问题突出",
                  "相关行业股票调整",
                  lambda p, m: self._handle_overcapacity(m),
                  probability=0.05,
                  tags=["产业", "产能"])
        ])
        
        # 突发事件
        self.market_events.extend([
            Event("地缘冲突",
                  "全球重要地区发生地缘政治冲突",
                  "避险情绪升温，国防军工股上涨",
                  lambda p, m: self._handle_geopolitical_event(m),
                  probability=0.03,
                  tags=["国际", "冲突"]),
                  
            Event("自然灾害",
                  "某地区发生重大自然灾害",
                  "保险股和基建股表现活跃",
                  lambda p, m: self._handle_natural_disaster(m),
                  probability=0.02,
                  tags=["灾害", "保险"]),
                  
            Event("重大事故",
                  "某行业发生重大安全事故",
                  "相关行业股票调整",
                  lambda p, m: self._handle_major_accident(m),
                  probability=0.02,
                  tags=["事故", "安全"])
        ])
        
        # 公司事件
        self.market_events.extend([
            Event("重大收购",
                  "大型公司宣布重要收购计划",
                  "并购重组概念股活跃",
                  lambda p, m: self._handle_major_acquisition(m),
                  probability=0.05,
                  tags=["公司", "并购"]),
                  
            Event("业绩预警",
                  "多家公司发布业绩预警",
                  "相关个股承压",
                  lambda p, m: self._handle_profit_warning(m),
                  probability=0.08,
                  tags=["公司", "业绩"]),
                  
            Event("研发突破",
                  "龙头公司取得重要研发突破",
                  "相关概念股走强",
                  lambda p, m: self._handle_research_breakthrough(m),
                  probability=0.06,
                  tags=["公司", "研发"])
        ])
        
        # 个人事件
        self.personal_events.extend([
            Event("意外收入", 
                  "收到一笔意外理财收益",
                  "获得5000元现金", 
                  lambda p, m: self._handle_cash_bonus(p, 5000),
                  probability=0.05,
                  tags=["收入", "理财"]),
                  
            Event("投资课程", 
                  "参加高级投资培训",
                  "获得一条有价值的投资建议", 
                  lambda p, m: self._handle_investment_tip(p),
                  probability=0.1,
                  tags=["学习", "技能"]),
                  
            Event("市场内幕",
                  "获得一条市场内幕消息",
                  "对某个行业有了新的认识",
                  lambda p, m: self._handle_market_insight(p),
                  probability=0.08,
                  tags=["信息", "内幕"]),
                  
            Event("操作失误",
                  "交易操作出现失误",
                  "损失一部分资金",
                  lambda p, m: self._handle_operation_mistake(p),
                  probability=0.05,
                  tags=["风险", "操作"])
        ])
        
        # 合并所有事件
        self.events = self.market_events + self.industry_events + self.personal_events
    
    def check_events(self, player, market, current_date):
        """检查并触发事件"""
        triggered_events = []
        
        # 限制每天最多触发的事件数量
        max_events_per_day = 2  # 每天最多发生2个事件
        triggered_count = 0
        
        # 随机打乱事件列表,使得触发更随机
        potential_events = self.events.copy()
        random.shuffle(potential_events)
        
        for event in potential_events:
            # 如果已经触发足够多的事件,就停止检查
            if triggered_count >= max_events_per_day:
                break
            
            # 检查冷却时间
            if (event.last_trigger_date and 
                (current_date - event.last_trigger_date).days < event.cooldown_days):
                continue
            
            # 根据概率触发事件
            if random.random() < event.probability:
                # 执行事件效果
                event.effect(player, market)
                event.last_trigger_date = current_date
                
                # 记录事件
                event_record = {
                    'date': current_date,
                    'name': event.name,
                    'description': event.description,
                    'effect': event.effect_description
                }
                self.event_history.append(event_record)
                triggered_events.append(event_record)
                
                # 增加已触发事件计数
                triggered_count += 1
        
        return triggered_events
    
    # 事件处理方法
    def _handle_rate_cut(self, market):
        """处理降息事件"""
        market.apply_global_change(0.03)  # 整体上涨3%
        self._boost_industry(market, "银行", 0.05)  # 银行股额外上涨5%
        self._boost_industry(market, "券商", 0.04)  # 券商股额外上涨4%
    
    def _handle_reserve_cut(self, market):
        """处理降准事件"""
        market.apply_global_change(0.02)  # 整体上涨2%
        self._boost_industry(market, "银行", 0.04)  # 银行股额外上涨4%
    
    def _handle_foreign_capital(self, market):
        """处理外资流入事件"""
        market.apply_global_change(0.02)  # 整体上涨2%
        self._boost_industry(market, "消费", 0.03)  # 消费股额外上涨3%
    
    def _handle_foreign_outflow(self, market):
        """处理外资流出事件"""
        market.apply_global_change(-0.02)  # 整体下跌2%
        self._boost_industry(market, "消费", -0.03)  # 消费股额外下跌3%
    
    def _handle_good_economy(self, market):
        """处理经济向好事件"""
        market.apply_global_change(0.02)
        industries = ["周期", "基建", "消费"]
        for industry in industries:
            self._boost_industry(market, industry, random.uniform(0.02, 0.04))
    
    def _handle_high_inflation(self, market):
        """处理通胀事件"""
        market.apply_global_change(-0.01)
        self._boost_industry(market, "黄金", 0.03)
        self._boost_industry(market, "消费", -0.02)
    
    def _handle_tech_breakthrough(self, market, industry, change):
        """处理技术突破事件"""
        self._boost_industry(market, industry, change)
    
    def _handle_industry_policy(self, market, industry, change):
        """处理行业政策事件"""
        self._boost_industry(market, industry, change)
    
    def _handle_cash_bonus(self, player, amount):
        """处理现金奖励事件"""
        player.cash += amount
    
    def _handle_investment_tip(self, player):
        """处理投资建议事件"""
        # TODO: 实现具体的投资建议逻辑
        pass
    
    def _handle_medical_insurance(self, market):
        """处理医保谈判事件"""
        stocks = [s for s in market.stocks.values() if s.industry in ["医药", "医疗器械"]]
        for stock in stocks:
            change = random.uniform(-0.05, 0.05)  # 医药股分化
            stock.price *= (1 + change)
            stock.price_history.append((datetime.now(), stock.price))
    
    def _handle_real_estate_policy(self, market):
        """处理房地产调控事件"""
        self._boost_industry(market, "房地产", -0.03)
        self._boost_industry(market, "建材", -0.02)
        self._boost_industry(market, "银行", -0.01)
    
    def _handle_geopolitical_event(self, market):
        """处理地缘冲突事件"""
        market.apply_global_change(-0.01)
        self._boost_industry(market, "军工", 0.05)
        self._boost_industry(market, "石油", 0.03)
    
    def _handle_natural_disaster(self, market):
        """处理自然灾害事件"""
        market.apply_global_change(-0.01)  # 整体下跌1%
        self._boost_industry(market, "保险", 0.02)  # 保险股额外上涨2%
        self._boost_industry(market, "基建", 0.01)  # 基建股额外上涨1%
    
    def _handle_major_accident(self, market):
        """处理重大事故事件"""
        market.apply_global_change(-0.01)  # 整体下跌1%
        self._boost_industry(market, "安全", -0.02)  # 安全股额外下跌2%
    
    def _handle_major_acquisition(self, market):
        """处理重大收购事件"""
        market.apply_global_change(0.02)  # 整体上涨2%
        self._boost_industry(market, "并购重组概念股", 0.05)  # 并购重组概念股额外上涨5%
    
    def _handle_profit_warning(self, market):
        """处理业绩预警事件"""
        market.apply_global_change(-0.01)  # 整体下跌1%
        self._boost_industry(market, "业绩预警股", -0.02)  # 业绩预警股额外下跌2%
    
    def _handle_research_breakthrough(self, market):
        """处理研发突破事件"""
        market.apply_global_change(0.01)  # 整体上涨1%
        self._boost_industry(market, "研发突破股", 0.02)  # 研发突破股额外上涨2%
    
    def _handle_market_insight(self, player):
        """处理市场内幕事件"""
        # TODO: 实现具体的市场内幕逻辑
        pass
    
    def _handle_operation_mistake(self, player):
        """处理操作失误事件"""
        loss = player.cash * random.uniform(0.01, 0.05)  # 损失1-5%的现金
        player.cash -= loss
    
    def _handle_fed_rate_hike(self, market):
        """处理美联储加息事件"""
        market.apply_global_change(-0.02)
        self._boost_industry(market, "银行", 0.02)
        self._boost_industry(market, "出口", -0.03)
    
    def _handle_trade_friction(self, market):
        """处理贸易摩擦事件"""
        market.apply_global_change(-0.02)
        self._boost_industry(market, "出口", -0.04)
        self._boost_industry(market, "内需", 0.02)
    
    def _handle_supply_chain_disruption(self, market):
        """处理供应链中断事件"""
        self._boost_industry(market, "制造业", -0.03)
        self._boost_industry(market, "物流", -0.02)
        self._boost_industry(market, "本土供应链", 0.03)
    
    def _handle_holiday_consumption(self, market):
        """处理节日消费事件"""
        self._boost_industry(market, "消费", 0.03)
        self._boost_industry(market, "免税", 0.04)
        self._boost_industry(market, "旅游", 0.03)
    
    def _handle_extreme_weather(self, market):
        """处理极端天气事件"""
        self._boost_industry(market, "农业", random.uniform(-0.05, 0.05))
        self._boost_industry(market, "保险", 0.02)
    
    def _handle_seasonal_epidemic(self, market):
        """处理季节性疫情事件"""
        market.apply_global_change(-0.01)  # 整体下跌1%
        self._boost_industry(market, "医药股", -0.02)  # 医药股额外下跌2%
        self._boost_industry(market, "在线经济", 0.01)  # 在线经济股额外上涨1%
    
    def _handle_ai_breakthrough(self, market):
        """处理AI突破事件"""
        self._boost_industry(market, "人工智能", 0.05)
        self._boost_industry(market, "芯片", 0.03)
        self._boost_industry(market, "软件", 0.02)
    
    def _handle_energy_innovation(self, market):
        """处理新能源技术革新事件"""
        self._boost_industry(market, "新能源", 0.04)
        self._boost_industry(market, "电池", 0.05)
        self._boost_industry(market, "新材料", 0.03)
    
    def _handle_biotech_breakthrough(self, market):
        """处理生物医药突破事件"""
        self._boost_industry(market, "医药股", 0.01)  # 医药股额外上涨1%
    
    def _handle_industry_upgrade(self, market):
        """处理产业升级事件"""
        self._boost_industry(market, "科技服务", 0.04)
        self._boost_industry(market, "自动化", 0.03)
        self._boost_industry(market, "传统制造", -0.02)
    
    def _handle_environmental_inspection(self, market):
        """处理环保督查事件"""
        self._boost_industry(market, "高污染", -0.03)
        self._boost_industry(market, "环保", 0.04)
        self._boost_industry(market, "新能源", 0.02)
    
    def _handle_overcapacity(self, market):
        """处理产能过剩事件"""
        self._boost_industry(market, "产能过剩股", -0.01)  # 产能过剩股额外下跌1%
    
    def _boost_industry(self, market, industry, change):
        """提升特定行业股票"""
        for stock in market.stocks.values():
            if stock.industry == industry:
                stock.price *= (1 + change)
                stock.price_history.append((datetime.now(), stock.price)) 
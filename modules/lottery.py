import random
from datetime import datetime, timedelta
from collections import defaultdict

class Lottery:
    def __init__(self):
        self.tickets = defaultdict(list)  # {date: [(red_numbers, blue_number)]}
        self.prize_pool = 1000000  # 初始奖池100万
        self.last_draw_date = None
        self.unclaimed_prizes = []  # 未领取的奖金
        self.claimed_prizes = []    # 已领取的奖金
        
        # 奖金设置
        self.prize_settings = {
            1: {"match": (6, True),  "base": 5000000, "desc": "一等奖"},  # 6红+1蓝
            2: {"match": (6, False), "base": 200000,  "desc": "二等奖"},  # 6红
            3: {"match": (5, True),  "base": 3000,    "desc": "三等奖"},  # 5红+1蓝
            4: {"match": (5, False), "base": 200,     "desc": "四等奖"},  # 5红或4红+1蓝
            5: {"match": (4, False), "base": 10,      "desc": "五等奖"},  # 4红或3红+1蓝
            6: {"match": (0, True),  "base": 5,       "desc": "六等奖"}   # 只中蓝球
        }
    
    def add_tickets(self, date, tickets):
        """添加彩票"""
        # 验证号码格式
        for red_numbers, blue_number in tickets:
            if not self._validate_numbers(red_numbers, blue_number):
                continue
            self.tickets[date].append((sorted(red_numbers), blue_number))
        
        # 增加奖池
        self.prize_pool += len(tickets) * 2  # 每注2元
    
    def draw_lottery(self, current_date):
        """开奖"""
        # 检查是否是开奖日（每周二、四、日）
        if current_date.weekday() not in [1, 3, 6]:
            return None
        
        # 避免重复开奖
        if self.last_draw_date == current_date:
            return None
        
        self.last_draw_date = current_date
        
        # 生成开奖号码
        winning_red = sorted(random.sample(range(1, 34), 6))
        winning_blue = random.randint(1, 16)
        
        # 检查中奖
        winners = defaultdict(int)  # {prize_level: count}
        total_prize = 0
        
        # 检查60天内的票
        check_date = current_date - timedelta(days=60)
        for date, date_tickets in list(self.tickets.items()):
            if date < check_date:
                del self.tickets[date]  # 清理过期票
                continue
            
            if date >= current_date:
                continue  # 跳过未来的票
            
            for red_numbers, blue_number in date_tickets:
                prize_level = self._check_prize(
                    red_numbers, blue_number, 
                    winning_red, winning_blue
                )
                if prize_level:
                    winners[prize_level] += 1
                    
                    # 记录未领取奖项
                    self.unclaimed_prizes.append({
                        "date": current_date,
                        "level": prize_level,
                        "amount": self._calculate_prize_amount(prize_level, winners[prize_level]),
                        "numbers": (red_numbers, blue_number),
                        "winning_numbers": (winning_red, winning_blue)
                    })
        
        return winning_red, winning_blue, winners
    
    def claim_prizes(self, current_date):
        """领取奖金"""
        total_claimed = 0
        expired_prizes = []
        remaining_prizes = []
        
        for prize in self.unclaimed_prizes:
            days_passed = (current_date - prize["date"]).days
            if days_passed <= 60:  # 60天内可以领奖
                total_claimed += prize["amount"]
                self.claimed_prizes.append(prize)
            else:
                expired_prizes.append(prize)
                # 过期奖金返回奖池
                self.prize_pool += prize["amount"]
        
        # 更新未领取奖金列表
        self.unclaimed_prizes = [p for p in self.unclaimed_prizes 
                               if (current_date - p["date"]).days <= 60]
        
        return total_claimed, expired_prizes
    
    def _validate_numbers(self, red_numbers, blue_number):
        """验证号码是否合法"""
        # 检查红球
        if len(red_numbers) != 6:
            return False
        if not all(1 <= n <= 33 for n in red_numbers):
            return False
        if len(set(red_numbers)) != 6:
            return False
            
        # 检查蓝球
        if not 1 <= blue_number <= 16:
            return False
            
        return True
    
    def _check_prize(self, red_numbers, blue_number, winning_red, winning_blue):
        """检查中奖等级"""
        red_matches = len(set(red_numbers) & set(winning_red))
        blue_match = blue_number == winning_blue
        
        for level, settings in self.prize_settings.items():
            required_red, required_blue = settings["match"]
            if required_red == 0:  # 六等奖特殊处理
                if blue_match:
                    return level
            elif red_matches == required_red and blue_match == required_blue:
                return level
        
        return None
    
    def _calculate_prize_amount(self, level, winner_count):
        """计算奖金金额"""
        base_amount = self.prize_settings[level]["base"]
        
        if level <= 2:  # 一、二等奖特殊处理
            if self.prize_pool >= 100000000:  # 奖池过亿
                pool_share = self.prize_pool * (0.55 if level == 1 else 0.25)
            else:
                pool_share = self.prize_pool * (0.75 if level == 1 else 0.25)
            
            amount = min(5000000, pool_share / winner_count)
        else:
            amount = base_amount
        
        return amount 
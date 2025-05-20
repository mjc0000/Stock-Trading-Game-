from datetime import datetime, timedelta
import math

class Player:
    def __init__(self, initial_money=10000):
        self.cash = float(initial_money)  # 现金
        self.stocks = {}                  # 持仓股票 {code: quantity}
        self.stock_holdings = {}          # 与 stocks 相同，为了兼容性
        self.stock_costs = {}             # 股票成本 {code: total_cost}
        self.loans = []                   # 贷款列表
        self.deposits = []                # 存款列表
        self.transaction_history = []      # 交易历史
        self.has_loan_default = False
        
    @property
    def total_assets(self):
        """计算总资产"""
        total = self.cash
        
        # 股票市值
        from modules.stock_market import StockMarket
        stock_market = StockMarket()
        for code, quantity in self.stocks.items():
            if code in stock_market.stocks:
                stock = stock_market.stocks[code]
                total += stock.price * quantity
        
        # 存款及利息
        for deposit in self.deposits:
            total += deposit['amount'] + deposit['interest']
        
        # 扣除贷款
        for loan in self.loans:
            if not loan['is_repaid']:
                total -= loan['remaining_amount']
        
        return total

    def buy_stock(self, code, quantity, price):
        """买入股票"""
        total_cost = quantity * price
        
        # 检查现金是否足够
        if total_cost > self.cash:
            return False, f"现金不足！需要 ¥{total_cost:,.2f}，当前现金 ¥{self.cash:,.2f}"
        
        # 执行交易
        self.cash -= total_cost
        if code not in self.stocks:
            self.stocks[code] = 0
            self.stock_costs[code] = 0
        
        self.stocks[code] += quantity
        self.stock_costs[code] += total_cost
        
        # 记录交易
        self.transaction_history.append({
            'type': 'buy',
            'code': code,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'date': datetime.now()
        })
        
        return True, f"成功买入 {quantity} 股 {code}"

    def sell_stock(self, code, quantity, price):
        """卖出股票"""
        if code not in self.stocks or self.stocks[code] < quantity:
            return False, "持仓不足"
        
        # 计算收益
        total_revenue = quantity * price
        avg_cost = self.stock_costs[code] / self.stocks[code]
        profit = total_revenue - (avg_cost * quantity)
        
        # 执行交易
        self.cash += total_revenue
        self.stocks[code] -= quantity
        
        # 更新成本基础
        if self.stocks[code] == 0:
            del self.stocks[code]
            del self.stock_costs[code]
        else:
            self.stock_costs[code] *= (self.stocks[code] / (self.stocks[code] + quantity))
        
        # 记录交易
        self.transaction_history.append({
            'type': 'sell',
            'code': code,
            'quantity': quantity,
            'price': price,
            'total': total_revenue,
            'profit': profit,
            'date': datetime.now()
        })
        
        return True, f"成功卖出 {quantity} 股 {code}，盈亏: ¥{profit:,.2f}"

    def take_loan(self, amount, rate, months=12):
        """申请贷款"""
        # 计算每月还款
        monthly_payment = amount * (1 + rate) / months
        
        self.loans.append({
            'amount': amount,
            'rate': rate,
            'start_date': datetime.now(),
            'monthly_payment': monthly_payment,
            'remaining_months': months,
            'remaining_amount': amount * (1 + rate),
            'is_repaid': False
        })
        
        self.cash += amount
        return True, f"成功贷款 ¥{amount:,.2f}"

    def make_deposit(self, amount, rate):
        """存款"""
        if amount > self.cash:
            return False, "现金不足"
        
        self.cash -= amount
        self.deposits.append({
            'amount': amount,
            'rate': rate,
            'start_date': datetime.now(),
            'interest': 0
        })
        
        return True, f"成功存入 ¥{amount:,.2f}"

    def update_loans_and_deposits(self, current_date):
        """更新贷款和存款状态"""
        # 处理贷款还款
        for loan in self.loans:
            if not loan['is_repaid'] and loan['remaining_months'] > 0:
                if self.cash >= loan['monthly_payment']:
                    self.cash -= loan['monthly_payment']
                    loan['remaining_months'] -= 1
                    loan['remaining_amount'] -= loan['monthly_payment']
                    
                    if loan['remaining_months'] == 0:
                        loan['is_repaid'] = True
                else:
                    # 尝试通过卖出股票还款
                    self._try_sell_stocks_for_payment(loan['monthly_payment'])

        # 计算存款利息
        for deposit in self.deposits:
            days = (current_date - deposit['start_date']).days
            if days > 0:
                daily_rate = deposit['rate'] / 365
                deposit['interest'] = deposit['amount'] * daily_rate * days

    def _try_sell_stocks_for_payment(self, needed_amount):
        """尝试卖出股票还款"""
        if self.cash >= needed_amount:
            return True
            
        # 按市值从大到小排序持仓
        from modules.stock_market import StockMarket
        stock_market = StockMarket()
        holdings = []
        for code, quantity in self.stocks.items():
            if code in stock_market.stocks:
                stock = stock_market.stocks[code]
                holdings.append((code, quantity, stock.price))
        
        holdings.sort(key=lambda x: x[1] * x[2], reverse=True)
        
        # 尝试卖出
        for code, quantity, price in holdings:
            if self.cash >= needed_amount:
                break
                
            sell_quantity = min(quantity, 
                              int((needed_amount - self.cash) / price) + 1)
            self.sell_stock(code, sell_quantity, price)
        
        return self.cash >= needed_amount

    def get_stock_cost_basis(self, stock_code):
        """获取股票的成本基础"""
        return self.stock_costs.get(stock_code, 0)

    def try_sell_stocks_for_cash(self, needed_cash):
        """尝试卖出股票来获取现金"""
        from modules.stock_market import StockMarket
        stock_market = StockMarket()
        
        # 计算所有持仓的市值
        holdings_value = []
        for code, quantity in self.stocks.items():
            if code in stock_market.stocks:
                stock = stock_market.stocks[code]
                value = stock.price * quantity
                holdings_value.append((code, quantity, value))
        
        # 按市值从大到小排序
        holdings_value.sort(key=lambda x: x[2], reverse=True)
        
        # 尝试卖出股票直到获得足够的现金
        cash_raised = 0
        for code, quantity, value in holdings_value:
            if cash_raised >= needed_cash:
                break
            
            stock = stock_market.stocks[code]
            # 计算需要卖出的数量
            shares_to_sell = min(quantity, 
                               math.ceil((needed_cash - cash_raised) / stock.price))
            
            if self.sell_stock(code, shares_to_sell, stock.price):
                cash_raised += shares_to_sell * stock.price
        
        return cash_raised >= needed_cash

    def calculate_total_assets(self, stock_market):
        """计算总资产"""
        total = self.cash
        
        # 计算股票资产
        for code, quantity in self.stocks.items():
            stock = stock_market.get_stock(code)
            if stock:
                total += stock.price * quantity
        
        # 计算存款及利息
        for deposit in self.deposits:
            total += deposit['amount'] + deposit['interest']
        
        # 扣除贷款
        for loan in self.loans:
            if not loan['is_repaid']:
                total -= loan['remaining_amount']
        
        return total 
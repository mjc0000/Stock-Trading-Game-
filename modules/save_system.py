import json
import os
from datetime import datetime

class SaveSystem:
    def __init__(self):
        self.save_dir = "saves"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def save_game(self, game, save_name):
        """保存游戏状态"""
        try:
            save_data = {
                'date': game.game_date.strftime('%Y-%m-%d %H:%M:%S'),
                'player': {
                    'cash': game.player.cash,
                    'stocks': game.player.stocks,
                    'stock_costs': game.player.stock_costs,
                    'loans': game.player.loans,
                    'deposits': game.player.deposits,
                    'transaction_history': game.player.transaction_history
                },
                'stock_market': {
                    code: {
                        'price': stock.price,
                        'initial_price': stock.initial_price,
                        'price_history': [(t.strftime('%Y-%m-%d %H:%M:%S'), p) 
                                        for t, p in stock.price_history]
                    } for code, stock in game.stock_market.stocks.items()
                },
                'crypto_market': {
                    symbol: {
                        'price': crypto.price,
                        'initial_price': crypto.initial_price,
                        'price_history': [(t.strftime('%Y-%m-%d %H:%M:%S'), p) 
                                        for t, p in crypto.price_history]
                    } for symbol, crypto in game.crypto_market.cryptos.items()
                },
                'crypto_wallet': {
                    'holdings': game.crypto_wallet.holdings,
                    'transaction_history': game.crypto_wallet.transaction_history
                },
                'forex_market': {
                    'rates': game.forex_market.rates,
                    'initial_rates': game.forex_market.initial_rates
                },
                'forex_wallet': {
                    'balances': game.forex_wallet.balances,
                    'transaction_history': game.forex_wallet.transaction_history
                },
                'game_speed': game.game_speed,
                'is_paused': game.is_paused
            }
            
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True, "游戏已保存"
            
        except Exception as e:
            return False, f"保存失败: {str(e)}"
    
    def load_game(self, game, save_name):
        """加载游戏存档"""
        try:
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 恢复游戏日期
            game.game_date = datetime.strptime(save_data['date'], '%Y-%m-%d %H:%M:%S')
            
            # 恢复玩家状态
            player_data = save_data['player']
            game.player.cash = player_data['cash']
            game.player.stocks = player_data['stocks']
            game.player.stock_costs = player_data['stock_costs']
            game.player.loans = player_data['loans']
            game.player.deposits = player_data['deposits']
            game.player.transaction_history = player_data['transaction_history']
            
            # 恢复股票市场
            for code, stock_data in save_data['stock_market'].items():
                stock = game.stock_market.stocks[code]
                stock.price = stock_data['price']
                stock.initial_price = stock_data['initial_price']
                stock.price_history = [
                    (datetime.strptime(t, '%Y-%m-%d %H:%M:%S'), p)
                    for t, p in stock_data['price_history']
                ]
            
            # 恢复加密货币市场
            for symbol, crypto_data in save_data['crypto_market'].items():
                crypto = game.crypto_market.cryptos[symbol]
                crypto.price = crypto_data['price']
                crypto.initial_price = crypto_data['initial_price']
                crypto.price_history = [
                    (datetime.strptime(t, '%Y-%m-%d %H:%M:%S'), p)
                    for t, p in crypto_data['price_history']
                ]
            
            # 恢复加密货币钱包
            crypto_wallet_data = save_data['crypto_wallet']
            game.crypto_wallet.holdings = crypto_wallet_data['holdings']
            game.crypto_wallet.transaction_history = crypto_wallet_data['transaction_history']
            
            # 恢复外汇市场
            forex_data = save_data['forex_market']
            game.forex_market.rates = forex_data['rates']
            game.forex_market.initial_rates = forex_data['initial_rates']
            
            # 恢复外汇钱包
            forex_wallet_data = save_data['forex_wallet']
            game.forex_wallet.balances = forex_wallet_data['balances']
            game.forex_wallet.transaction_history = forex_wallet_data['transaction_history']
            
            # 恢复游戏速度和暂停状态
            game.game_speed = save_data['game_speed']
            game.is_paused = save_data['is_paused']
            game.update_interval = game.base_update_interval / game.game_speed
            
            return True, "游戏已加载"
            
        except Exception as e:
            return False, f"加载失败: {str(e)}"
    
    def list_saves(self):
        """列出所有存档"""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json"):
                save_path = os.path.join(self.save_dir, filename)
                try:
                    with open(save_path, "r", encoding="utf-8") as f:
                        save_data = json.load(f)
                    saves.append({
                        "name": filename[:-5],
                        "date": save_data["date"],
                        "game_date": save_data["date"],
                        "cash": save_data["player"]["cash"]
                    })
                except:
                    continue
        return saves 
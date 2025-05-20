import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import json
import random
import time
import os
import shutil
from modules.stock_market import StockMarket
from modules.player import Player
from modules.game_ui import GameUI
from modules.event_system import EventSystem
from modules.save_system import SaveSystem
from modules.lottery import Lottery
from modules.crypto import CryptoMarket, CryptoWallet
from modules.forex import ForexMarket, ForexWallet

class StockGame:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("股票交易游戏")
        self.root.geometry("1200x800")
        
        # 初始化样式
        self.style = ttk.Style()
        self.theme_colors = {
            'light': {
                'bg': '#ffffff',          # 白色背景
                'fg': '#000000',          # 黑色文字
                'frame_bg': '#f0f0f0',    # 浅灰色框架背景
                'accent': '#4a90e2',      # 蓝色强调色
                'chart_bg': '#ffffff',    # 图表背景色
                'grid': '#cccccc'         # 网格线颜色
            },
            'dark': {
                'bg': '#2d2d2d',          # 深灰色背景
                'fg': '#ffffff',          # 白色文字
                'frame_bg': '#363636',    # 稍浅的灰色框架背景
                'accent': '#61afef',      # 亮蓝色强调色
                'chart_bg': '#2d2d2d',    # 图表背景色
                'grid': '#404040'         # 深色网格线
            }
        }
        self.current_theme = 'light'  # 默认使用浅色主题
        
        # 初始化游戏系统
        self.game_date = datetime(2023, 1, 1)  # 游戏起始日期
        self.tick_count = 0  # 用于计数刷新次数
        self.is_paused = False  # 游戏暂停状态
        
        # 初始化各个子系统
        self.stock_market = StockMarket()
        self.player = Player(initial_money=100000)  # 初始资金10万
        self.event_system = EventSystem()
        self.save_system = SaveSystem()
        self.lottery = Lottery()
        self.crypto_market = CryptoMarket()
        self.crypto_wallet = CryptoWallet()
        self.forex_market = ForexMarket()
        self.forex_wallet = ForexWallet()
        
        # 初始化UI
        self.game_ui = GameUI(self.root, self)
        
        # 应用主题
        self.apply_theme()
        
        # 游戏速度控制
        self.base_update_interval = 1000  # 基础更新间隔（毫秒）
        self.game_speed = 1.0  # 游戏速度倍率
        self.update_interval = self.base_update_interval / self.game_speed
        
        # 启动游戏循环
        self.update_game()
    
    def apply_theme(self):
        """应用当前主题"""
        colors = self.theme_colors[self.current_theme]
        
        # 设置主窗口样式
        self.style.configure('TFrame', background=colors['frame_bg'])
        self.style.configure('TLabel', background=colors['frame_bg'], foreground=colors['fg'])
        self.style.configure('TButton', background=colors['accent'])
        self.style.configure('Treeview', background=colors['bg'], foreground=colors['fg'], fieldbackground=colors['bg'])
        self.style.configure('TLabelframe', background=colors['frame_bg'])
        self.style.configure('TLabelframe.Label', background=colors['frame_bg'], foreground=colors['fg'])
        
        # 更新图表样式
        self.game_ui.update_chart_theme(colors)
    
    def toggle_theme(self):
        """切换主题"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
    
    def bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<Control-s>', lambda e: self.save_game())
        self.root.bind('<Control-l>', lambda e: self.load_game())
        self.root.bind('<space>', lambda e: self.toggle_pause())
        self.root.bind('<Control-q>', lambda e: self.quit_game())
    
    def update_game(self):
        """游戏主循环"""
        if not self.is_paused:
            self.tick_count += 1
            
            # 每60个tick更新一次日期（相当于1分钟=1天）
            if self.tick_count >= 60:
                self.game_date += timedelta(days=1)
                self.tick_count = 0
                
                # 检查事件
                self.event_system.check_events(self.player, self.stock_market, self.game_date)
                
                # 更新彩票
                self.lottery.draw_lottery(self.game_date)
                self.lottery.claim_prizes(self.game_date)
            
            # 更新市场
            self.stock_market.update_prices()
            
            # 直接更新加密货币和外汇市场，它们的波动频率会随游戏速度变化
            self.crypto_market.update_market()
            self.forex_market.update_market()
            
            # 更新玩家状态
            self.player.update_loans_and_deposits(self.game_date)
            
            # 更新UI显示
            self.game_ui.update_display()
        
        # 继续游戏循环，更新间隔随游戏速度变化
        self.root.after(int(self.update_interval), self.update_game)
    
    def save_game(self):
        """保存游戏"""
        save_name = f"autosave_{self.game_date.strftime('%Y%m%d_%H%M%S')}"
        success, message = self.save_system.save_game(self, save_name)
        if success:
            messagebox.showinfo("保存成功", message)
        else:
            messagebox.showerror("保存失败", message)
    
    def load_game(self):
        """加载游戏"""
        saves = self.save_system.list_saves()
        if not saves:
            messagebox.showinfo("提示", "没有找到存档")
            return
            
        # TODO: 显示存档列表供选择
        save_name = saves[-1]["name"]  # 暂时加载最新存档
        success, message = self.save_system.load_game(self, save_name)
        if success:
            messagebox.showinfo("加载成功", message)
            self.game_ui.update_display()
        else:
            messagebox.showerror("加载失败", message)
    
    def toggle_pause(self):
        """切换游戏暂停状态"""
        self.is_paused = not self.is_paused
        self.game_ui.update_pause_button()
    
    def quit_game(self):
        """退出游戏"""
        if messagebox.askyesno("确认退出", "是否要保存并退出游戏？"):
            self.save_game()
            self.root.quit()
    
    def start(self):
        """启动游戏"""
        self.root.mainloop()

    def export_save(self):
        """导出存档"""
        save_name = f"game_save_{self.game_date.strftime('%Y%m%d_%H%M%S')}"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sav",
            filetypes=[("Save files", "*.sav")],
            initialfile=save_name
        )
        if file_path:
            try:
                self.save_system.export_save(self, file_path)
                messagebox.showinfo("成功", "存档已导出")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def import_save(self):
        """导入存档"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Save files", "*.sav")]
        )
        if file_path:
            try:
                self.save_system.import_save(self, file_path)
                messagebox.showinfo("成功", "存档已导入")
                self.game_ui.update_display()
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")

    def reset_game(self):
        """重置游戏"""
        if messagebox.askyesno("警告", "重置游戏将删除所有存档数据，确定要继续吗？", icon='warning'):
            try:
                # 删除所有存档
                self.save_system.delete_all_saves()
                
                # 重置游戏状态
                self.game_date = datetime(2023, 1, 1)
                self.tick_count = 0
                self.is_paused = False
                self.game_speed = 1.0
                self.update_interval = self.base_update_interval / self.game_speed
                
                # 重新初始化所有系统
                self.stock_market = StockMarket()
                self.player = Player(initial_money=100000)
                self.event_system = EventSystem()
                self.lottery = Lottery()
                self.crypto_market = CryptoMarket()
                self.crypto_wallet = CryptoWallet()
                self.forex_market = ForexMarket()
                self.forex_wallet = ForexWallet()
                
                # 更新显示
                self.game_ui.update_display()
                messagebox.showinfo("成功", "游戏已重置")
            except Exception as e:
                messagebox.showerror("错误", f"重置失败: {str(e)}")

    def show_menu(self, event):
        """显示右键菜单"""
        self.main_menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    game = StockGame()
    game.start() 
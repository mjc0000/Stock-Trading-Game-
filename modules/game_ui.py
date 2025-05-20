import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter  # 修正 DateFormatter 导入
import tkinter.messagebox as messagebox
import random
from pygame import mixer  # 在文件开头添加
import os
import requests
import json
from streamlink import Streamlink

class GameUI:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.selected_stock = None
        self.last_total_assets = self.game.player.total_assets
        
        # 添加键盘事件绑定
        self.root.bind('<space>', self.toggle_pause)  # 添加空格键绑定
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧股票列表
        self.create_stock_list()
        
        # 创建中间功能区
        self.create_function_panel()
        
        # 创建右侧股票详情
        self.create_stock_detail()
        
        # 创建底部信息栏
        self.create_status_bar()
        
        # 初始更新股票列表
        self.update_stock_list()
        
        # 创建全局右键菜单
        self.main_menu = tk.Menu(self.root, tearoff=0)
        
        # 游戏菜单
        game_menu = tk.Menu(self.main_menu, tearoff=0)
        game_menu.add_command(label="保存存档", command=self.game.save_game)
        game_menu.add_command(label="加载存档", command=self.game.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="导出存档", command=self.game.export_save)
        game_menu.add_command(label="导入存档", command=self.game.import_save)
        game_menu.add_separator()
        game_menu.add_command(label="重置游戏", command=self.game.reset_game)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self.game.quit_game)
        self.main_menu.add_cascade(label="游戏", menu=game_menu)
        
        # 添加暂停/继续选项
        self.main_menu.add_command(label="暂停", command=self.toggle_pause)
        
        # 速度菜单
        self.main_menu.add_command(label="修改游戏速度", command=self.show_speed_settings)
        
        # 设置菜单
        settings_menu = tk.Menu(self.main_menu, tearoff=0)
        settings_menu.add_command(label="切换主题", command=self.game.toggle_theme)
        settings_menu.add_command(label="音效设置", command=self.show_sound_settings)
        settings_menu.add_command(label="收听广播", command=self.show_radio)
        self.main_menu.add_cascade(label="设置", menu=settings_menu)
        
        # 绑定右键事件到主窗口
        self.root.bind("<Button-3>", self.show_menu)
        
        # 初始化音乐系统
        mixer.init()
        self.bgm_playing = False
        self.current_bgm = None
        self.bgm_volume = 0.5
        
        # 创建音乐文件夹
        self.music_dir = "assets/music"
        os.makedirs(self.music_dir, exist_ok=True)
        
        # 默认音乐列表
        self.music_list = self._get_music_list()
        
        # 初始化收音机
        self.radio_player = None
        self.current_station = None
        self.radio_volume = 0.5
        self.session = Streamlink()
        
        # 预设电台列表（真实广播流）
        self.radio_stations = {
            "Classic FM XR": "https://stream.wqxr.org/wqxr-web",
            "Business News Radio": "https://www.bloomberg.com/radio/player",
            "World News Service": "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
            "Public News Radio": "https://www.npr.org/streams/",
            "Jazz FM 24": "https://live.wostreaming.net/direct/ppm-jazz24aac-ibc1",
            "City Radio NYC": "https://stream.wnyc.org/wnyc-fm939",
            "Classic Public Radio": "https://cms.stream.publicradio.org/cms.mp3",
            "Venice Classical Hits": "https://uk2.streamingpulse.com/ssl/vcr1",
            "First FM Classical": "https://strm112.1.fm/classical_mobile_mp3"
        }
        
        # 创建电台音乐文件夹
        self.radio_dir = "assets/radio"
        os.makedirs(self.radio_dir, exist_ok=True)

    def _get_music_list(self):
        """获取音乐列表"""
        if not os.path.exists(self.music_dir):
            return []
        return [f for f in os.listdir(self.music_dir) 
                if f.endswith(('.mp3', '.wav', '.ogg'))]

    def play_bgm(self, music_file):
        """播放背景音乐"""
        try:
            if self.bgm_playing:
                mixer.music.stop()
            
            full_path = os.path.join(self.music_dir, music_file)
            mixer.music.load(full_path)
            mixer.music.set_volume(self.bgm_volume)
            mixer.music.play(-1)  # -1表示循环播放
            self.bgm_playing = True
            self.current_bgm = music_file
        except Exception as e:
            print(f"播放音乐出错: {str(e)}")

    def stop_bgm(self):
        """停止背景音乐"""
        if self.bgm_playing:
            mixer.music.stop()
            self.bgm_playing = False

    def set_bgm_volume(self, volume):
        """设置音乐音量"""
        self.bgm_volume = volume
        mixer.music.set_volume(volume)

    def create_stock_list(self):
        """创建左侧股票列表"""
        frame = ttk.LabelFrame(self.main_frame, text="股票列表")
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 搜索框
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_stocks)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X)
        
        # 股票列表
        columns = ("代码", "名称", "行业", "现价")
        self.stock_tree = ttk.Treeview(frame, columns=columns, show="headings", height=30)
        
        # 设置列宽和对齐方式
        self.stock_tree.column("代码", width=80, anchor="center")
        self.stock_tree.column("名称", width=100, anchor="w")
        self.stock_tree.column("行业", width=80, anchor="center")
        self.stock_tree.column("现价", width=80, anchor="e")
        
        # 设置列标题
        for col in columns:
            self.stock_tree.heading(col, text=col)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.stock_tree.bind("<<TreeviewSelect>>", self.on_stock_select)
        
        # 添加右键菜单
        self.stock_menu = tk.Menu(self.root, tearoff=0)
        self.stock_menu.add_command(label="买入", command=self.buy_stock)
        self.stock_menu.add_command(label="卖出", command=self.sell_stock)
        self.stock_menu.add_separator()
        self.stock_menu.add_command(label="查看K线", command=self.show_kline)
        self.stock_menu.add_command(label="查看公司信息", command=self.show_company_info)
        
        # 绑定右键事件
        self.stock_tree.bind("<Button-3>", self.show_stock_menu)
        
    def create_function_panel(self):
        """创建中间功能区"""
        frame = ttk.LabelFrame(self.main_frame, text="功能区")
        frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 添加功能按钮
        ttk.Button(frame, text="银行", command=self.show_bank).pack(pady=5)
        ttk.Button(frame, text="双色球", command=self.show_lottery).pack(pady=5)
        ttk.Button(frame, text="加密货币", command=self.show_crypto).pack(pady=5)
        ttk.Button(frame, text="外汇交易", command=self.show_forex).pack(pady=5)
        ttk.Button(frame, text="事件记录", command=self.show_events).pack(pady=5)
        
    def create_stock_detail(self):
        """创建右侧股票详情"""
        frame = ttk.LabelFrame(self.main_frame, text="股票详情")
        frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 股票信息
        info_frame = ttk.LabelFrame(frame, text="基本信息")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=4, width=50)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 持仓信息
        holdings_frame = ttk.LabelFrame(frame, text="持仓信息")
        holdings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.holdings_text = tk.Text(holdings_frame, height=4, width=50)
        self.holdings_text.pack(fill=tk.X, padx=5, pady=5)
        
        # K线图
        chart_frame = ttk.LabelFrame(frame, text="价格走势")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.fig = Figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 交易控制
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="数量:").pack(side=tk.LEFT)
        self.quantity_var = tk.StringVar(value="100")
        ttk.Entry(control_frame, textvariable=self.quantity_var, width=10).pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="买入", command=self.buy_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="卖出", command=self.sell_stock).pack(side=tk.LEFT)
        
    def create_status_bar(self):
        """创建底部状态栏"""
        frame = ttk.Frame(self.root)
        frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 日期显示
        self.date_label = ttk.Label(frame, text="2023-01-01")
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        # 资金显示
        self.cash_label = ttk.Label(frame, text="现金: ¥10000")
        self.cash_label.pack(side=tk.LEFT, padx=10)
        
        # 总资产显示
        self.assets_label = ttk.Label(frame, text="总资产: ¥10000")
        self.assets_label.pack(side=tk.LEFT, padx=10)
        
        # 心情指示器
        self.mood_label = ttk.Label(frame, text="😊", font=('TkDefaultFont', 20))
        self.mood_label.pack(side=tk.RIGHT, padx=10)
        
    def update_stock_list(self):
        """更新股票列表显示"""
        # 清空现有列表
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # 获取搜索文本
        search_text = self.search_var.get().lower()
        
        # 添加所有股票
        for stock in self.game.stock_market.get_all_stocks():  # 使用get_all_stocks()
            # 如果有搜索文本，进行过滤
            if (search_text in stock.code.lower() or 
                search_text in stock.name.lower() or 
                search_text in stock.industry.lower()):
                self.stock_tree.insert("", tk.END, values=(
                    stock.code,
                    stock.name,
                    stock.industry,
                    f"¥{stock.price:.2f}"
                ))
        
    def filter_stocks(self, *args):
        """过滤股票列表"""
        # 清空现有列表
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # 获取搜索文本
        search_text = self.search_var.get().lower()
        
        # 添加符合搜索条件的股票
        for stock in self.game.stock_market.get_all_stocks():
            if (search_text in stock.code.lower() or 
                search_text in stock.name.lower() or 
                search_text in stock.industry.lower()):
                self.stock_tree.insert("", tk.END, values=(
                    stock.code,
                    stock.name,
                    stock.industry,
                    f"¥{stock.price:.2f}"
                ))
        
    def on_stock_select(self, event):
        """处理股票选择事件"""
        selected_items = self.stock_tree.selection()
        if selected_items:
            # 获取选中项的值
            item_values = self.stock_tree.item(selected_items[0])['values']
            if item_values:
                self.selected_stock = item_values[0]  # 获取股票代码
                self.update_display()
            
    def buy_stock(self):
        """买入股票"""
        if not self.selected_stock:
            messagebox.showinfo("提示", "请先选择要购买的股票！")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showinfo("提示", "请输入正确的购买数量！")
                return
            
            stock = self.game.stock_market.get_stock(self.selected_stock)
            success, message = self.game.player.buy_stock(self.selected_stock, quantity, stock.price)
            
            if success:
                messagebox.showinfo("成功", message)
                self.update_display()
            else:
                messagebox.showwarning("失败", message)
        except ValueError:
            messagebox.showwarning("错误", "请输入正确的数量！")
        except Exception as e:
            messagebox.showerror("错误", f"购买失败: {str(e)}")
            
    def sell_stock(self):
        """卖出股票"""
        if not self.selected_stock:
            return
            
        try:
            quantity = int(self.quantity_var.get())
            stock = self.game.stock_market.get_stock(self.selected_stock)
            
            if self.game.player.sell_stock(self.selected_stock, quantity, stock.price):
                self.update_display()
        except (ValueError, KeyError):
            print("卖出操作失败")
            
    def update_display(self):
        """更新所有显示"""
        try:
            # 更新股票列表
            self.update_stock_list()
            
            # 更新图表
            if self.selected_stock:
                self.update_chart(self.game.stock_market.get_stock(self.selected_stock))
            
            # 更新加密货币显示（如果加密货币窗口存在）
            if hasattr(self, 'crypto_window') and self.crypto_window.winfo_exists():
                self.update_crypto_display()
            
            # 更新状态栏
            self.update_status_bar()
            
            # 更新持仓信息
            self.update_holdings_info()
            
        except Exception as e:
            print(f"更新显示时出错: {str(e)}")

    def update_status_bar(self):
        """更新状态栏信息"""
        # 更新日期显示
        self.date_label.config(text=self.game.game_date.strftime('%Y-%m-%d'))
        
        # 更新现金显示
        self.cash_label.config(text=f"现金: ¥{self.game.player.cash:,.2f}")
        
        # 更新总资产显示
        total_assets = self.game.player.calculate_total_assets(self.game.stock_market)
        self.assets_label.config(text=f"总资产: ¥{total_assets:,.2f}")
        
        # 更新心情指示器（根据资产变化）
        if total_assets > self.last_total_assets:
            self.mood_label.config(text="😊")
        elif total_assets < self.last_total_assets:
            self.mood_label.config(text="😢")
        else:
            self.mood_label.config(text="😐")
        
        self.last_total_assets = total_assets

    def update_holdings_info(self):
        """更新持仓信息"""
        if not self.selected_stock:
            return
        
        stock = self.game.stock_market.get_stock(self.selected_stock)
        if not stock:
            return
        
        # 获取持仓信息
        holdings = self.game.player.stock_holdings.get(self.selected_stock, 0)
        cost = self.game.player.stock_costs.get(self.selected_stock, 0)
        
        if holdings > 0:
            avg_cost = cost / holdings
            profit = (stock.price - avg_cost) * holdings
            profit_percent = (stock.price / avg_cost - 1) * 100
            
            holdings_text = (
                f"持仓数量: {holdings:,} 股\n"
                f"平均成本: ¥{avg_cost:.2f}\n"
                f"当前盈亏: ¥{profit:,.2f} ({profit_percent:+.2f}%)"
            )
        else:
            holdings_text = "当前未持仓"
        
        # 更新持仓信息显示
        self.holdings_text.config(state='normal')
        self.holdings_text.delete(1.0, tk.END)
        self.holdings_text.insert(tk.END, holdings_text)
        self.holdings_text.config(state='disabled')

    def update_realtime_info(self):
        """更新实时行情信息"""
        info_text = "实时行情:\n\n"
        
        # 添加股票市场信息
        info_text += "股票市场:\n"
        for stock in self.game.stock_market.get_all_stocks()[:5]:  # 显示前5支股票
            info_text += f"{stock.name}: ¥{stock.price:.2f}\n"
        
        # 添加加密货币信息
        info_text += "\n加密货币市场:\n"
        for crypto in self.game.crypto_market.cryptos.values():
            info_text += f"{crypto.name}: ${crypto.price:.2f}\n"
        
        # 更新信息文本
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state='disabled')

    def show_crypto(self):
        """显示加密货币交易界面"""
        crypto_window = tk.Toplevel(self.root)
        crypto_window.title("加密货币交易")
        crypto_window.geometry("1000x600")
        
        # 创建左侧加密货币列表
        list_frame = ttk.LabelFrame(crypto_window, text="加密货币列表")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        columns = ("名称", "代码")  # 简化列表显示
        self.crypto_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.crypto_tree.heading(col, text=col)
            self.crypto_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.crypto_tree.yview)
        self.crypto_tree.configure(yscrollcommand=scrollbar.set)
        
        self.crypto_tree.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建右侧详情面板
        detail_frame = ttk.LabelFrame(crypto_window, text="币种详情")
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 实时价格信息
        price_frame = ttk.LabelFrame(detail_frame, text="实时行情")
        price_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.crypto_price_label = ttk.Label(price_frame, text="当前价格: --")
        self.crypto_price_label.pack(pady=2)
        
        self.crypto_change_label = ttk.Label(price_frame, text="24h涨跌幅: --")
        self.crypto_change_label.pack(pady=2)
        
        # 持仓信息
        holdings_frame = ttk.LabelFrame(detail_frame, text="持仓信息")
        holdings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.crypto_holdings_text = tk.Text(holdings_frame, height=4, width=50)
        self.crypto_holdings_text.pack(fill=tk.X, padx=5, pady=5)
        
        # K线图
        chart_frame = ttk.LabelFrame(detail_frame, text="价格走势")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.crypto_fig = Figure(figsize=(6, 4))
        self.crypto_ax = self.crypto_fig.add_subplot(111)
        self.crypto_canvas = FigureCanvasTkAgg(self.crypto_fig, master=chart_frame)
        self.crypto_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 交易控制
        control_frame = ttk.Frame(detail_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="数量:").pack(side=tk.LEFT)
        self.crypto_amount = tk.StringVar(value="1")
        ttk.Entry(control_frame, textvariable=self.crypto_amount, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="买入", command=self.buy_crypto).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="卖出", command=self.sell_crypto).pack(side=tk.LEFT, padx=5)
        
        # 绑定选择事件
        self.crypto_tree.bind("<<TreeviewSelect>>", self.on_crypto_select)
        
        # 保存窗口引用以便更新
        self.crypto_window = crypto_window
        self.selected_crypto = None
        
        # 更新显示
        self.update_crypto_display()

    def on_crypto_select(self, event):
        """处理加密货币选择事件"""
        selection = self.crypto_tree.selection()
        if selection:
            values = self.crypto_tree.item(selection[0])['values']
            if values:
                self.selected_crypto = values[1]  # 获取币种代码
                self.update_crypto_details()

    def update_crypto_details(self):
        """更新加密货币详情"""
        if not self.selected_crypto:
            return
        
        crypto = self.game.crypto_market.cryptos.get(self.selected_crypto)
        if not crypto:
            return
        
        # 更新价格信息
        change = ((crypto.price/crypto.initial_price - 1) * 100)
        self.crypto_price_label.config(text=f"当前价格: ${crypto.price:.2f}")
        self.crypto_change_label.config(text=f"24h涨跌幅: {change:+.2f}%")
        
        # 更新持仓信息
        holdings = self.game.crypto_wallet.holdings.get(crypto.symbol, 0)
        if holdings > 0:
            holdings_value = holdings * crypto.price
            holdings_text = (
                f"持仓数量: {holdings:.8f}\n"
                f"持仓价值: ${holdings_value:.2f}"
            )
        else:
            holdings_text = "当前未持仓"
        
        self.crypto_holdings_text.config(state='normal')
        self.crypto_holdings_text.delete(1.0, tk.END)
        self.crypto_holdings_text.insert(tk.END, holdings_text)
        self.crypto_holdings_text.config(state='disabled')
        
        # 更新价格走势图
        self.update_crypto_chart(crypto)

    def update_crypto_chart(self, crypto):
        """更新加密货币价格走势图"""
        self.crypto_ax.clear()
        if crypto.price_history:
            times, prices = zip(*crypto.price_history)
            self.crypto_ax.plot(times, prices, 'b-', linewidth=1)
            
            self.crypto_ax.set_title(f"{crypto.name} ({crypto.symbol})")
            self.crypto_ax.set_ylabel("Price (USD)")
            self.crypto_ax.grid(True)
            
            # 设置y轴范围
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price
            self.crypto_ax.set_ylim(min_price - price_range*0.1, max_price + price_range*0.1)
            
            # 设置x轴为时间格式
            self.crypto_ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            self.crypto_ax.set_xlabel("Time")
            
            # 添加最新价格标注
            self.crypto_ax.annotate(f'${prices[-1]:.2f}', 
                                   xy=(times[-1], prices[-1]),
                                   xytext=(10, 10), textcoords='offset points',
                                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                                   arrowprops=dict(arrowstyle='->'))
            
            self.crypto_canvas.draw()

    def buy_crypto(self):
        """买入加密货币"""
        selection = self.crypto_tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要购买的加密货币！")
            return
        
        try:
            amount = float(self.crypto_amount.get())
            if amount <= 0:
                messagebox.showinfo("提示", "请输入正确的购买数量！")
                return
            
            values = self.crypto_tree.item(selection[0])['values']
            symbol = values[1]  # 获取币种代码
            crypto = self.game.crypto_market.cryptos[symbol]
            
            total_cost = amount * crypto.price
            if total_cost > self.game.player.cash:
                messagebox.showwarning("失败", f"现金不足！需要 ${total_cost:.2f}")
                return
            
            # 执行购买
            self.game.player.cash -= total_cost
            self.game.crypto_wallet.buy(symbol, amount, crypto.price, self.game.game_date)
            messagebox.showinfo("成功", f"成功购买 {amount} {symbol}")
            
            # 更新显示
            self.update_display()
            
        except ValueError:
            messagebox.showwarning("错误", "请输入正确的数量！")

    def sell_crypto(self):
        """卖出加密货币"""
        selection = self.crypto_tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要卖出的加密货币！")
            return
        
        try:
            amount = float(self.crypto_amount.get())
            if amount <= 0:
                messagebox.showinfo("提示", "请输入正确的卖出数量！")
                return
            
            values = self.crypto_tree.item(selection[0])['values']
            symbol = values[1]  # 获取币种代码
            crypto = self.game.crypto_market.cryptos[symbol]
            
            if self.game.crypto_wallet.sell(symbol, amount, crypto.price, self.game.game_date):
                self.game.player.cash += amount * crypto.price
                messagebox.showinfo("成功", f"成功卖出 {amount} {symbol}")
                self.update_display()
            else:
                messagebox.showwarning("失败", "持仓不足！")
            
        except ValueError:
            messagebox.showwarning("错误", "请输入正确的数量！")

    def update_crypto_display(self):
        """更新加密货币显示"""
        if not hasattr(self, 'crypto_tree') or not self.crypto_window.winfo_exists():
            return
        
        # 清空现有列表
        for item in self.crypto_tree.get_children():
            self.crypto_tree.delete(item)
        
        # 添加所有加密货币
        for crypto in self.game.crypto_market.cryptos.values():
            self.crypto_tree.insert("", tk.END, values=(
                crypto.name,
                crypto.symbol
            ))
        
        # 如果有选中的币种，更新其详细信息
        if self.selected_crypto:
            self.update_crypto_details()

    def show_bank(self):
        """显示银行界面"""
        bank_window = tk.Toplevel(self.root)
        bank_window.title("银行")
        bank_window.geometry("400x500")
        bank_window.transient(self.root)
        
        # 获取当前利率
        current_date = self.game.game_date
        deposit_rate = self.get_deposit_rate(current_date)
        loan_rate = self.get_loan_rate(current_date)
        
        # 显示当前利率信息
        info_frame = ttk.LabelFrame(bank_window, text="利率信息")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(info_frame, text=f"存款年利率: {deposit_rate*100:.2f}%").pack(pady=2)
        ttk.Label(info_frame, text=f"贷款年利率: {loan_rate*100:.2f}%").pack(pady=2)
        
        # 存款功能
        deposit_frame = ttk.LabelFrame(bank_window, text="存款")
        deposit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(deposit_frame, text="存款金额:").pack(side=tk.LEFT, padx=5)
        deposit_amount = tk.StringVar()
        ttk.Entry(deposit_frame, textvariable=deposit_amount, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(deposit_frame, text="存入", 
                   command=lambda: self.make_deposit(float(deposit_amount.get() or 0))).pack(side=tk.LEFT, padx=5)
        
        # 贷款功能
        loan_frame = ttk.LabelFrame(bank_window, text="贷款")
        loan_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 计算最大贷款额度
        max_loan = max(1000000, self.game.player.total_assets * 2)  # 最低100万，或总资产2倍
        ttk.Label(loan_frame, text=f"最大可贷: ¥{max_loan:,.2f}").pack(pady=2)
        
        ttk.Label(loan_frame, text="贷款金额:").pack(side=tk.LEFT, padx=5)
        loan_amount = tk.StringVar()
        ttk.Entry(loan_frame, textvariable=loan_amount, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(loan_frame, text="贷款", 
                   command=lambda: self.take_loan(float(loan_amount.get() or 0))).pack(side=tk.LEFT, padx=5)
        
        # 显示当前贷款信息
        loan_info_frame = ttk.LabelFrame(bank_window, text="当前贷款")
        loan_info_frame.pack(fill=tk.X, padx=5, pady=5)
        self.update_loan_info(loan_info_frame)

    def get_deposit_rate(self, date):
        """获取存款利率"""
        if date.year >= 2015 and date.month >= 10:
            return 0.015  # 1.50%
        return 0.015  # 默认值

    def get_loan_rate(self, date):
        """获取贷款利率"""
        if date.year >= 2023 and date.month >= 6:
            return 0.0355  # 3.55%
        elif date.year >= 2022 and date.month >= 8:
            return 0.0365
        elif date.year >= 2022 and date.month >= 5:
            return 0.0370
        elif date.year >= 2022 and date.month >= 1:
            return 0.0370
        elif date.year >= 2020 and date.month >= 4:
            return 0.0385
        elif date.year >= 2020 and date.month >= 2:
            return 0.0405
        elif date.year >= 2019 and date.month >= 8:
            return 0.0425
        return 0.0435  # 2015-2019默认值

    def make_deposit(self, amount):
        """存款"""
        if amount <= 0:
            messagebox.showwarning("错误", "请输入正确的存款金额！")
            return
        if amount > self.game.player.cash:
            messagebox.showwarning("错误", "现金不足！")
            return
        
        self.game.player.cash -= amount
        # 添加到存款列表
        deposit_rate = self.get_deposit_rate(self.game.game_date)
        self.game.player.deposits.append({
            'amount': amount,
            'rate': deposit_rate,
            'start_date': self.game.game_date,
            'interest': 0
        })
        messagebox.showinfo("成功", f"成功存入 ¥{amount:,.2f}")
        self.update_display()

    def take_loan(self, amount):
        """贷款"""
        if amount <= 0:
            messagebox.showwarning("错误", "请输入正确的贷款金额！")
            return
        
        # 计算当前未还贷款总额
        current_loans = sum(loan['amount'] for loan in self.game.player.loans 
                           if not loan['is_repaid'])
        
        # 计算最大可贷额度
        max_loan = max(1000000, self.game.player.total_assets * 2) - current_loans
        
        if amount > max_loan:
            messagebox.showwarning("错误", 
                                 f"超出最大贷款额度！\n"
                                 f"当前已贷: ¥{current_loans:,.2f}\n"
                                 f"还可贷: ¥{max_loan:,.2f}")
            return
        
        # 计算每月还款金额
        loan_rate = self.get_loan_rate(self.game.game_date)
        monthly_payment = amount * (1 + loan_rate) / 12
        
        # 检查每月还款是否超过当前现金
        if monthly_payment > self.game.player.cash:
            messagebox.showwarning("警告", 
                                 f"每月还款金额 ¥{monthly_payment:,.2f} 超过当前现金！\n"
                                 "请谨慎考虑是否贷款。")
        
        self.game.player.loans.append({
            'amount': amount,
            'rate': loan_rate,
            'start_date': self.game.game_date,
            'monthly_payment': monthly_payment,
            'remaining_months': 12,
            'is_repaid': False
        })
        self.game.player.cash += amount
        messagebox.showinfo("成功", 
                           f"成功贷款 ¥{amount:,.2f}\n"
                           f"每月还款: ¥{monthly_payment:.2f}")
        self.update_display()

    def update_loan_info(self, frame):
        """更新贷款信息显示"""
        for widget in frame.winfo_children():
            widget.destroy()
        
        if not self.game.player.loans:
            ttk.Label(frame, text="暂无贷款").pack(pady=5)
            return
        
        for i, loan in enumerate(self.game.player.loans):
            if not loan['is_repaid']:
                loan_frame = ttk.Frame(frame)
                loan_frame.pack(fill=tk.X, pady=2)
                ttk.Label(loan_frame, 
                         text=f"贷款{i+1}: ¥{loan['amount']:,.2f}, "
                              f"剩余{loan['remaining_months']}个月, "
                              f"月供: ¥{loan['monthly_payment']:,.2f}").pack(side=tk.LEFT)
                ttk.Button(loan_frame, text="提前还款", 
                          command=lambda l=loan: self.repay_loan(l)).pack(side=tk.RIGHT)

    def repay_loan(self, loan):
        """提前还款"""
        remaining_amount = loan['monthly_payment'] * loan['remaining_months']
        if remaining_amount > self.game.player.cash:
            messagebox.showwarning("错误", "现金不足以还清贷款！")
            return
        
        self.game.player.cash -= remaining_amount
        loan['is_repaid'] = True
        loan['remaining_months'] = 0
        messagebox.showinfo("成功", f"成功还清贷款！")
        self.update_display()

    def show_lottery(self):
        """显示双色球界面"""
        lottery_window = tk.Toplevel(self.root)
        lottery_window.title("双色球")
        lottery_window.geometry("800x600")
        lottery_window.transient(self.root)
        
        # 创建选号区域
        select_frame = ttk.LabelFrame(lottery_window, text="选号区")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 红球选择区
        red_frame = ttk.LabelFrame(select_frame, text="红球")
        red_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.red_vars = []
        for i in range(33):
            var = tk.BooleanVar()
            self.red_vars.append(var)
            num = i + 1
            cb = ttk.Checkbutton(red_frame, text=f"{num:02d}", variable=var)
            cb.grid(row=i//10, column=i%10, padx=2, pady=2)
        
        # 蓝球选择区
        blue_frame = ttk.LabelFrame(select_frame, text="蓝球")
        blue_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.blue_vars = []
        for i in range(16):
            var = tk.BooleanVar()
            self.blue_vars.append(var)
            num = i + 1
            cb = ttk.Checkbutton(blue_frame, text=f"{num:02d}", variable=var)
            cb.grid(row=i//8, column=i%8, padx=2, pady=2)
        
        # 控制按钮区
        control_frame = ttk.Frame(lottery_window)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="机选一注", 
                   command=self.random_select).pack(side=tk.LEFT, padx=5)
        
        # 批量投注区域
        batch_frame = ttk.LabelFrame(control_frame, text="批量投注")
        batch_frame.pack(side=tk.LEFT, padx=5)
        
        self.batch_amount = tk.StringVar(value="1")
        ttk.Entry(batch_frame, textvariable=self.batch_amount, 
                 width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(batch_frame, text="批量机选", 
                   command=self.batch_buy).pack(side=tk.LEFT, padx=5)
        
        # 确认投注按钮
        ttk.Button(control_frame, text="确认投注", 
                   command=lambda: self.confirm_lottery(lottery_window)).pack(side=tk.RIGHT, padx=5)

    def random_select(self):
        """机选一注"""
        # 清除之前的选择
        for var in self.red_vars:
            var.set(False)
        for var in self.blue_vars:
            var.set(False)
        
        # 随机选择6个红球
        red_numbers = random.sample(range(33), 6)
        for num in red_numbers:
            self.red_vars[num].set(True)
        
        # 随机选择1个蓝球
        blue_number = random.randint(0, 15)
        self.blue_vars[blue_number].set(True)

    def batch_buy(self):
        """批量机选投注"""
        try:
            amount = int(self.batch_amount.get())
            if amount <= 0 or amount > 10000:
                messagebox.showwarning("错误", "批量投注数量必须在1-10000之间！")
                return
            
            total_cost = amount * 2  # 每注2元
            if total_cost > self.game.player.cash:
                messagebox.showwarning("错误", f"现金不足！需要 ¥{total_cost:,.2f}")
                return
            
            # 添加确认对话框
            if not messagebox.askyesno("确认投注", 
                                     f"您确定要购买 {amount} 注双色球吗？\n"
                                     f"总金额: ¥{total_cost:,.2f}\n"
                                     f"每注金额: ¥2.00"):
                return
            
            # 生成投注号码
            tickets = []
            for _ in range(amount):
                red_numbers = sorted(random.sample(range(1, 34), 6))
                blue_number = random.randint(1, 16)
                tickets.append((red_numbers, blue_number))
            
            # 添加到彩票系统
            self.game.lottery.add_tickets(self.game.game_date, tickets)
            
            # 扣除费用
            self.game.player.cash -= total_cost
            
            # 更新显示
            self.lottery_info.delete(1.0, tk.END)
            self.lottery_info.insert(tk.END, 
                f"成功购买 {amount} 注双色球\n"
                f"总金额: ¥{total_cost:,.2f}\n"
                f"请等待开奖！")
            
            self.update_display()
            
        except ValueError:
            messagebox.showwarning("错误", "请输入正确的数量！")

    def confirm_lottery(self, window):
        """确认投注"""
        # 获取选择的号码
        red_numbers = []
        for i, var in enumerate(self.red_vars):
            if var.get():
                red_numbers.append(i + 1)
        
        blue_numbers = []
        for i, var in enumerate(self.blue_vars):
            if var.get():
                blue_numbers.append(i + 1)
        
        # 检查选择是否有效
        if len(red_numbers) < 6:
            messagebox.showwarning("错误", "请至少选择6个红球！")
            return
        if len(blue_numbers) < 1:
            messagebox.showwarning("错误", "请至少选择1个蓝球！")
            return
        
        # 计算注数和金额
        tickets = []
        if len(red_numbers) == 6 and len(blue_numbers) == 1:
            # 单式投注
            tickets.append((sorted(red_numbers), blue_numbers[0]))
        else:
            # 复式投注
            from itertools import combinations
            red_combinations = list(combinations(red_numbers, 6))
            for red_combo in red_combinations:
                for blue_number in blue_numbers:
                    tickets.append((sorted(red_combo), blue_number))
            amount = len(tickets)
        
        total_cost = amount * 2  # 每注2元
        
        # 确认投注
        if messagebox.askyesno("确认投注", 
                              f"共 {amount} 注，总金额 ¥{total_cost:,.2f}\n"
                              "确认投注吗？"):
            if total_cost > self.game.player.cash:
                messagebox.showwarning("错误", f"现金不足！需要 ¥{total_cost:,.2f}")
                return
            
            # 添加到彩票系统
            self.game.lottery.add_tickets(self.game.game_date, tickets)
            
            # 扣除费用
            self.game.player.cash -= total_cost
            
            # 更新显示
            self.update_display()
            window.destroy() 

    def claim_lottery_prizes(self):
        """领取彩票奖金"""
        claimed_amount, expired = self.game.lottery.claim_prizes(self.game.game_date)
        if claimed_amount > 0:
            self.game.player.cash += claimed_amount
            # 处理个人所得税（超过1万元的部分）
            if claimed_amount > 10000:
                tax = (claimed_amount - 10000) * 0.2
                self.game.player.cash -= tax
                messagebox.showinfo("恭喜", 
                    f"成功领取奖金 ¥{claimed_amount:,.2f}\n"
                    f"缴纳个人所得税 ¥{tax:,.2f}\n"
                    f"实际到账 ¥{claimed_amount-tax:,.2f}")
            else:
                messagebox.showinfo("恭喜", f"成功领取奖金 ¥{claimed_amount:,.2f}")
            self.update_display()
        else:
            messagebox.showinfo("提示", "暂无可领取的奖金")
        
        if expired:
            messagebox.showwarning("提示", f"有 {len(expired)} 个奖项已过期！")

    def show_lottery_history(self):
        """显示中奖历史"""
        history_window = tk.Toplevel(self.root)
        history_window.title("双色球中奖记录")
        history_window.geometry("400x300")
        history_window.transient(self.root)
        
        # 创建文本显示区域
        text = tk.Text(history_window, wrap=tk.WORD, width=50, height=15)
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示已领取的奖金记录
        total_claimed = 0
        text.insert(tk.END, "== 历史中奖记录 ==\n\n")
        for prize in self.game.lottery.claimed_prizes:
            text.insert(tk.END, 
                f"开奖日期: {prize['date'].strftime('%Y-%m-%d')}\n"
                f"中奖等级: {prize['level']}等奖\n"
                f"中奖金额: ¥{prize['amount']:,.2f}\n"
                f"中奖号码: 红球 {prize['numbers'][0]}, 蓝球 {prize['numbers'][1]}\n"
                f"{'-'*40}\n")
            total_claimed += prize['amount']
        
        text.insert(tk.END, f"\n累计中奖金额: ¥{total_claimed:,.2f}")
        text.config(state='disabled')

    def show_forex(self):
        """显示货币兑换界面"""
        forex_window = tk.Toplevel(self.root)
        forex_window.title("货币兑换")
        forex_window.geometry("1000x600")
        forex_window.transient(self.root)
        
        # 创建汇率显示面板
        rate_frame = ttk.LabelFrame(forex_window, text="实时汇率")
        rate_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建汇率表格
        columns = ("货币对", "汇率", "24h变化")
        self.forex_tree = ttk.Treeview(rate_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.forex_tree.heading(col, text=col)
            self.forex_tree.column(col, width=150)
        
        self.forex_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建兑换操作面板
        exchange_frame = ttk.LabelFrame(forex_window, text="货币兑换")
        exchange_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 选择货币对
        pair_frame = ttk.Frame(exchange_frame)
        pair_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 使用 rates 而不是 currencies
        currencies = list(self.game.forex_market.rates.keys())
        
        ttk.Label(pair_frame, text="从:").pack(side=tk.LEFT)
        self.from_currency = tk.StringVar(value="CNY")
        from_menu = ttk.OptionMenu(pair_frame, self.from_currency, *currencies)
        from_menu.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(pair_frame, text="到:").pack(side=tk.LEFT)
        self.to_currency = tk.StringVar(value="USD")
        to_menu = ttk.OptionMenu(pair_frame, self.to_currency, *currencies)
        to_menu.pack(side=tk.LEFT, padx=5)
        
        # 输入金额
        amount_frame = ttk.Frame(exchange_frame)
        amount_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(amount_frame, text="金额:").pack(side=tk.LEFT)
        self.exchange_amount = tk.StringVar(value="100")
        ttk.Entry(amount_frame, textvariable=self.exchange_amount).pack(side=tk.LEFT, padx=5)
        
        # 显示兑换结果
        self.exchange_result = ttk.Label(exchange_frame, text="")
        self.exchange_result.pack(pady=5)
        
        # 兑换按钮
        ttk.Button(exchange_frame, text="兑换", 
                   command=self.execute_exchange).pack(pady=5)
        
        # 显示钱包余额
        balance_frame = ttk.LabelFrame(forex_window, text="货币余额")
        balance_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.balance_text = tk.Text(balance_frame, height=5)
        self.balance_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 更新显示
        self.update_forex_display(forex_window)

    def update_forex_display(self, window):
        """更新外汇显示"""
        # 更新汇率表格
        for item in self.forex_tree.get_children():
            self.forex_tree.delete(item)
        
        base_currency = "USD"  # 使用美元作为基准货币
        for code, rate in self.game.forex_market.rates.items():
            if code != base_currency:
                # 计算24小时变化
                initial_rate = self.game.forex_market.initial_rates.get(code, rate)
                change = (rate - initial_rate) / initial_rate * 100
                change_text = f"{change:+.2f}%"
                
                self.forex_tree.insert("", tk.END, values=(
                    f"{base_currency}/{code}",
                    f"{rate:.4f}",
                    change_text
                ))
        
        # 更新余额显示
        self.balance_text.delete(1.0, tk.END)
        for currency, amount in self.game.forex_wallet.balances.items():
            self.balance_text.insert(tk.END, f"{currency}: {amount:.2f}\n")
        
        # 设置定时更新
        window.after(1000, lambda: self.update_forex_display(window))

    def execute_exchange(self):
        """执行货币兑换"""
        try:
            amount = float(self.exchange_amount.get())
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()
            
            if amount <= 0:
                messagebox.showwarning("错误", "请输入正确的金额！")
                return
            
            rate = self.game.forex_market.get_exchange_rate(from_curr, to_curr)
            if not rate:
                messagebox.showwarning("错误", "无法获取汇率！")
                return
            
            success, message = self.game.forex_wallet.exchange(
                from_curr, to_curr, amount, rate, self.game.game_date
            )
            
            if success:
                messagebox.showinfo("成功", message)
                self.exchange_result.config(
                    text=f"兑换率: 1 {from_curr} = {rate:.4f} {to_curr}"
                )
            else:
                messagebox.showwarning("错误", message)
            
        except ValueError:
            messagebox.showwarning("错误", "请输入正确的金额！") 

    def show_events(self):
        """显示事件窗口"""
        events_window = tk.Toplevel(self.root)
        events_window.title("事件记录")
        events_window.geometry("600x400")
        events_window.transient(self.root)
        
        # 创建事件列表
        columns = ("日期", "事件", "影响")
        self.events_tree = ttk.Treeview(events_window, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.events_tree.heading(col, text=col)
        
        self.events_tree.column("日期", width=100)
        self.events_tree.column("事件", width=200)
        self.events_tree.column("影响", width=250)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(events_window, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示历史事件
        for event in reversed(self.game.event_system.event_history):
            self.events_tree.insert("", 0, values=(
                event['date'].strftime('%Y-%m-%d'),
                event['name'],
                event['effect']
            )) 

    def show_stock_menu(self, event):
        """显示股票右键菜单"""
        # 获取点击位置对应的item
        item = self.stock_tree.identify_row(event.y)
        if item:
            # 选中该项
            self.stock_tree.selection_set(item)
            # 获取股票代码
            values = self.stock_tree.item(item)['values']
            if values:
                self.selected_stock = values[0]
                # 在点击位置显示菜单
                self.stock_menu.post(event.x_root, event.y_root)

    def show_kline(self):
        """显示K线图窗口"""
        if not self.selected_stock:
            return
        
        stock = self.game.stock_market.get_stock(self.selected_stock)
        if not stock:
            return
        
        kline_window = tk.Toplevel(self.root)
        kline_window.title(f"{stock.name} - K线图")
        kline_window.geometry("800x600")
        
        # 创建K线图
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        
        # 绘制K线
        times, prices = zip(*stock.price_history)
        ax.plot(times, prices, 'b-', linewidth=1)
        ax.set_title(f"{stock.name} ({stock.code})")
        ax.set_ylabel("价格 (CNY)")
        ax.grid(True)
        
        canvas = FigureCanvasTkAgg(fig, master=kline_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_company_info(self):
        """显示公司信息窗口"""
        if not self.selected_stock:
            return
        
        stock = self.game.stock_market.get_stock(self.selected_stock)
        if not stock:
            return
        
        info_window = tk.Toplevel(self.root)
        info_window.title(f"{stock.name} - 公司信息")
        info_window.geometry("400x300")
        
        # 创建信息显示
        info_frame = ttk.LabelFrame(info_window, text="基本信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_text = (
            f"股票代码：{stock.code}\n"
            f"公司名称：{stock.name}\n"
            f"所属行业：{stock.industry}\n"
            f"当前价格：¥{stock.price:.2f}\n"
            f"波动率：{stock.volatility*100:.1f}%\n"
            f"市场敏感度：{stock.beta:.2f}\n"
            f"抗跌能力：{stock.resistance:.2f}\n"
        )
        
        text = tk.Text(info_frame, height=15, width=40)
        text.insert(tk.END, info_text)
        text.config(state='disabled')
        text.pack(padx=5, pady=5)

    def update_chart_theme(self, colors):
        """更新图表主题"""
        # 更新主图表
        self.fig.set_facecolor(colors['chart_bg'])
        self.ax.set_facecolor(colors['chart_bg'])
        self.ax.tick_params(colors=colors['fg'])
        self.ax.spines['bottom'].set_color(colors['fg'])
        self.ax.spines['top'].set_color(colors['fg'])
        self.ax.spines['left'].set_color(colors['fg'])
        self.ax.spines['right'].set_color(colors['fg'])
        self.ax.title.set_color(colors['fg'])
        self.ax.xaxis.label.set_color(colors['fg'])
        self.ax.yaxis.label.set_color(colors['fg'])
        for text in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            text.set_color(colors['fg'])
        
        # 更新其他文本组件
        self.info_text.configure(bg=colors['bg'], fg=colors['fg'])
        self.holdings_text.configure(bg=colors['bg'], fg=colors['fg'])
        
        # 重绘图表
        if self.selected_stock:
            self.update_chart(self.game.stock_market.get_stock(self.selected_stock))

    def show_speed_settings(self):
        """显示速度设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("游戏速度设置")
        settings_window.geometry("300x200")
        settings_window.transient(self.root)
        
        # 创建速度滑块
        slider_frame = ttk.LabelFrame(settings_window, text="速度滑块")
        slider_frame.pack(fill=tk.X, padx=10, pady=5)
        
        speed_var = tk.DoubleVar(value=min(self.game.game_speed, 100))
        speed_label = ttk.Label(slider_frame, text=f"当前速度: {self.game.game_speed:.1f}x")
        speed_label.pack(pady=2)
        
        def update_speed(value):
            """实时更新速度"""
            try:
                speed = float(value)
                self.game.game_speed = speed
                # 限制最小更新间隔为1毫秒
                self.game.update_interval = max(0.001, self.game.base_update_interval / speed)
                speed_label.config(text=f"当前速度: {speed:.1f}x")
            except Exception as e:
                print(f"更新速度时出错: {str(e)}")
        
        speed_scale = ttk.Scale(
            slider_frame, 
            from_=0.5, 
            to=100,  # 滑块最大值为100
            variable=speed_var,
            orient=tk.HORIZONTAL,
            command=update_speed
        )
        speed_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # 快速选择按钮
        buttons_frame = ttk.LabelFrame(settings_window, text="快速选择")
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def set_speed(s):
            """设置指定速度"""
            try:
                speed_var.set(min(s, 100))  # 滑块最大显示100
                self.game.game_speed = s    # 实际速度可以更高
                # 限制最小更新间隔为1毫秒
                self.game.update_interval = max(0.001, self.game.base_update_interval / s)
                speed_label.config(text=f"当前速度: {s:.1f}x")
            except Exception as e:
                print(f"设置速度时出错: {str(e)}")
        
        # 恢复原有的速度选项，包括10000x
        speeds = [0.5, 1, 2, 5, 10, 20, 50, 100, 1000, 10000]
        for i, speed in enumerate(speeds):
            ttk.Button(
                buttons_frame, 
                text=f"{speed}x",
                command=lambda s=speed: set_speed(s)
            ).grid(row=i//3, column=i%3, padx=5, pady=2, sticky="ew")

    def show_sound_settings(self):
        """显示音效设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("音效设置")
        settings_window.geometry("400x500")
        settings_window.transient(self.root)
        
        # 音效开关
        sound_frame = ttk.LabelFrame(settings_window, text="音效设置")
        sound_frame.pack(fill=tk.X, padx=20, pady=10)
        
        sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sound_frame, text="启用音效", 
                        variable=sound_var).pack(padx=20, pady=10)
        
        # 音量控制
        volume_frame = ttk.LabelFrame(settings_window, text="音量控制")
        volume_frame.pack(fill=tk.X, padx=20, pady=10)
        
        volume_var = tk.DoubleVar(value=self.bgm_volume)
        volume_scale = ttk.Scale(volume_frame, from_=0, to=1, 
                               variable=volume_var, orient=tk.HORIZONTAL,
                               command=lambda v: self.set_bgm_volume(float(v)))
        volume_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # 音乐选择
        music_frame = ttk.LabelFrame(settings_window, text="背景音乐")
        music_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建音乐列表
        self.music_list = self._get_music_list()
        music_listbox = tk.Listbox(music_frame)
        for music in self.music_list:
            music_listbox.insert(tk.END, music)
        
        # 如果有当前播放的音乐，选中它
        if self.current_bgm in self.music_list:
            current_index = self.music_list.index(self.current_bgm)
            music_listbox.selection_set(current_index)
        
        music_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 控制按钮
        button_frame = ttk.Frame(music_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="播放", 
                  command=lambda: self.play_bgm(music_listbox.get(music_listbox.curselection()[0]) 
                  if music_listbox.curselection() else None)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="停止", 
                  command=self.stop_bgm).pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        ttk.Button(button_frame, text="刷新列表", 
                  command=lambda: self._refresh_music_list(music_listbox)).pack(side=tk.RIGHT, padx=5)

    def _refresh_music_list(self, listbox):
        """刷新音乐列表"""
        listbox.delete(0, tk.END)
        self.music_list = self._get_music_list()
        for music in self.music_list:
            listbox.insert(tk.END, music)

    def update_chart(self, stock):
        """更新股票图表"""
        self.ax.clear()
        if stock.price_history:
            times, prices = zip(*stock.price_history)
            self.ax.plot(times, prices, 'b-', linewidth=1)
            
            # 使用支持中文的字体
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            
            self.ax.set_title(f"{stock.name} ({stock.code})")
            self.ax.set_ylabel("价格 (CNY)")
            self.ax.grid(True, color=self.game.theme_colors[self.game.current_theme]["fg"], alpha=0.2)
            
            # 设置y轴范围
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price
            self.ax.set_ylim(min_price - price_range*0.1, max_price + price_range*0.1)
            
            # 设置x轴为时间格式
            self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            self.ax.set_xlabel("时间")
            
            # 添加最新价格标注
            self.ax.annotate(f'¥{prices[-1]:.2f}', 
                            xy=(times[-1], prices[-1]),
                            xytext=(10, 10), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                            arrowprops=dict(arrowstyle='->'))
            
            self.canvas.draw() 

    def toggle_pause(self, event=None):  # 添加event参数以支持事件绑定
        """切换暂停状态"""
        self.game.is_paused = not self.game.is_paused
        # 更新菜单项文本（暂停选项在第2个位置，索引为1）
        self.main_menu.entryconfig(
            1,  # 暂停菜单项的索引
            label="继续" if self.game.is_paused else "暂停"
        )
        
        # 可选：显示暂停/继续状态提示
        status = "暂停" if self.game.is_paused else "继续"
        self.root.title(f"股票交易游戏 - {status}")

    def show_menu(self, event):
        """显示右键菜单"""
        self.main_menu.post(event.x_root, event.y_root)

    def show_radio(self):
        """显示收音机界面"""
        radio_window = tk.Toplevel(self.root)
        radio_window.title("收音机")
        radio_window.geometry("400x600")
        radio_window.transient(self.root)
        
        # 创建复古收音机外观
        radio_frame = ttk.LabelFrame(radio_window, text="📻 复古收音机")
        radio_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 显示屏
        display_frame = ttk.Frame(radio_frame)
        display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.station_label = ttk.Label(display_frame, text="当前电台: 未播放", 
                                     font=('Courier', 12))
        self.station_label.pack(pady=10)
        
        # 电台列表
        station_frame = ttk.LabelFrame(radio_frame, text="电台列表")
        station_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.station_listbox = tk.Listbox(station_frame, font=('Courier', 10))
        for station in self.radio_stations.keys():
            self.station_listbox.insert(tk.END, station)
        self.station_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 控制面板
        control_frame = ttk.Frame(radio_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 音量控制
        volume_frame = ttk.LabelFrame(control_frame, text="音量")
        volume_frame.pack(fill=tk.X, pady=5)
        
        self.radio_volume_var = tk.DoubleVar(value=self.radio_volume)
        volume_scale = ttk.Scale(volume_frame, from_=0, to=1,
                               variable=self.radio_volume_var,
                               orient=tk.HORIZONTAL,
                               command=self.set_radio_volume)
        volume_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # 播放控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="播放",
                  command=self.play_radio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止",
                  command=self.stop_radio).pack(side=tk.LEFT, padx=5)
        
        # 信号强度显示（模拟）
        signal_frame = ttk.LabelFrame(control_frame, text="信号强度")
        signal_frame.pack(fill=tk.X, pady=5)
        
        self.signal_canvas = tk.Canvas(signal_frame, height=20)
        self.signal_canvas.pack(fill=tk.X, padx=10, pady=5)
        self.update_signal_strength(radio_window)
        
        # 状态栏
        self.status_label = ttk.Label(radio_frame, text="准备就绪")
        self.status_label.pack(pady=5)
        
        # 关闭窗口时停止播放
        radio_window.protocol("WM_DELETE_WINDOW", 
                            lambda: self.on_radio_window_close(radio_window))

    def play_radio(self):
        """播放选中的电台"""
        try:
            selection = self.station_listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请先选择一个电台")
                return
            
            station_name = self.station_listbox.get(selection[0])
            station_url = self.radio_stations[station_name]
            
            # 停止当前播放
            if mixer.music.get_busy():
                mixer.music.stop()
            
            try:
                # 获取流媒体URL
                streams = self.session.streams(station_url)
                if not streams:
                    raise Exception("无法获取电台流")
                
                # 获取最佳质量的流
                stream_url = streams['best'].url
                
                # 使用临时文件保存流数据
                response = requests.get(stream_url, stream=True)
                if response.status_code == 200:
                    temp_file = "temp_stream.mp3"
                    with open(temp_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # 播放音频流
                    mixer.music.load(temp_file)
                    mixer.music.set_volume(self.radio_volume)
                    mixer.music.play()
                    
                    # 更新显示
                    self.current_station = station_name
                    self.station_label.config(text=f"当前电台: {station_name}")
                    self.status_label.config(text="正在播放...")
                else:
                    raise Exception("无法连接到电台")
                    
            except Exception as e:
                raise Exception(f"播放错误: {str(e)}")
            
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("播放错误", 
                f"播放出错: {error_msg}\n"
                "可能的原因：\n"
                "1. 网络连接问题\n"
                "2. 电台暂时不可用\n"
                "3. 流媒体格式不支持")
            self.status_label.config(text=f"播放出错: {error_msg}")

    def stop_radio(self):
        """停止播放"""
        if mixer.music.get_busy():
            mixer.music.stop()
            self.current_station = None
            self.station_label.config(text="当前电台: 未播放")
            self.status_label.config(text="已停止")

    def set_radio_volume(self, value):
        """设置收音机音量"""
        self.radio_volume = float(value)
        mixer.music.set_volume(self.radio_volume)

    def update_signal_strength(self, window):
        """更新信号强度显示（模拟效果）"""
        self.signal_canvas.delete("all")
        
        # 模拟信号强度条
        width = self.signal_canvas.winfo_width()
        height = self.signal_canvas.winfo_height()
        
        if width > 0 and height > 0:  # 确保窗口已经创建
            bar_width = width / 5
            for i in range(5):
                # 随机生成信号强度
                strength = random.random() if self.current_station else 0.2
                bar_height = height * strength
                
                x1 = i * bar_width + 2
                y1 = height - bar_height
                x2 = (i + 1) * bar_width - 2
                y2 = height
                
                # 根据信号强度设置颜色
                color = f"#{int(strength * 255):02x}ff00"
                self.signal_canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        
        # 每秒更新一次
        window.after(1000, lambda: self.update_signal_strength(window))

    def on_radio_window_close(self, window):
        """关闭收音机窗口时的处理"""
        self.stop_radio()
        window.destroy()
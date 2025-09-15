# ---------- 第一部分：基础导入和全局配置 ----------
from collections import defaultdict  # 添加这一行
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
import json
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- 第二部分：主应用类框架 ----------
class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("个人理财助手")
        self.current_date = datetime.now()
        self.records = {}
        self.budget = 0
        self.load_data()

        # 初始化界面组件
        self.setup_main_window()
        self.create_calendar()
        self.create_budget_section()
        self.create_stat_button()

    # ---------- 第三部分：主界面布局 ----------
    def setup_main_window(self):
        # 头部日期显示
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(pady=10)
        self.date_label = ttk.Label(self.header_frame, font=('Times New Roman', 14))
        self.date_label.pack()

        # 日历主体
        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack(padx=20, pady=10)

        # 翻页按钮
        self.nav_frame = ttk.Frame(self.root)
        self.nav_frame.pack(pady=10)
        ttk.Button(self.nav_frame, text="← 上一月", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="下一月 →", command=self.next_month).pack(side=tk.LEFT, padx=5)

    # ---------- 新增：统计按钮 ----------
    def create_stat_button(self):
        self.stat_button = ttk.Button(self.root, text="统计", command=self.open_stats)
        self.stat_button.pack(side=tk.LEFT, padx=10, pady=10)

    # ---------- 第四部分：日历生成核心逻辑 ----------
    def create_calendar(self):
        # 清除旧日历
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # 设置表头
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        for i, day in enumerate(weekdays):
            ttk.Label(self.calendar_frame, text=day).grid(row=0, column=i, padx=5, pady=5)

        # 获取当月信息
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_days = cal.monthdayscalendar(self.current_date.year, self.current_date.month)

        # 生成日期按钮
        for week_num, week in enumerate(month_days, start=1):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = tk.Button(self.calendar_frame, text=str(day), width=5,
                                    bg='white', relief='flat',
                                    command=lambda d=day: self.open_accounting(d))
                    btn.grid(row=week_num, column=day_num, padx=5, pady=5)

                    # 设置周末颜色
                    if day_num >= 5:
                        btn.config(fg='red')

                    # 绑定鼠标悬停事件
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#e0e0e0'))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg='white'))

        # 更新头部日期显示
        self.date_label.config(text=f"{self.current_date.year}-{self.current_date.month:02d}")

    # ---------- 新增：打开统计窗口 ----------
    def open_stats(self):
        self.StatsWindow(self.root, self)

    # ---------- 新增：打开记账窗口 ----------
    def open_accounting(self, day):
        date = datetime(self.current_date.year, self.current_date.month, day)
        self.AccountingWindow(self.root, date, self)  # 保持原调用方式，但需要修复类定义

    # ---------- 第五部分：翻页功能 ----------
    def prev_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.create_calendar()

    def next_month(self):
        self.current_date = (self.current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        self.create_calendar()

    # ---------- 第六部分：预算模块 ----------
    def create_budget_section(self):
        self.budget_frame = ttk.Frame(self.root)
        self.budget_frame.pack(pady=10, anchor=tk.NE, padx=20)

        # 预算显示组件
        ttk.Label(self.budget_frame, text="预算管理", font=('微软雅黑', 12)).grid(row=0, columnspan=2, pady=5)

        self.budget_label = ttk.Label(self.budget_frame, text="本月支出预算：0元")
        self.budget_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        self.remain_label = ttk.Label(self.budget_frame, text="本月剩余预算：0元")
        self.remain_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # 操作按钮
        ttk.Button(self.budget_frame, text="修改预算", command=self.show_edit_budget, width=10).grid(row=3, column=0, pady=5)
        ttk.Button(self.budget_frame, text="刷新数据", command=self.update_budget_display, width=10).grid(row=3, column=1, pady=5)

        self.update_budget_display()

    class EditBudgetDialog:
        def __init__(self, parent, main_app):
            self.top = tk.Toplevel(parent)
            self.main_app = main_app
            self.top.title("修改预算设置")
            self.top.geometry("300x150")

            # 输入组件
            ttk.Label(self.top, text="请输入新的月度支出预算（元）:").pack(pady=10)
            self.amount_var = tk.StringVar(value=str(self.main_app.budget))
            self.amount_entry = ttk.Entry(self.top, textvariable=self.amount_var, width=15)
            self.amount_entry.pack()

            # 操作按钮
            btn_frame = ttk.Frame(self.top)
            btn_frame.pack(pady=15)
            ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="取消", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

        def save(self):
            try:
                new_budget = float(self.amount_var.get())
                if new_budget < 0:
                    raise ValueError
                self.main_app.budget = new_budget
                self.main_app.save_data()
                self.main_app.update_budget_display()
                messagebox.showinfo("成功", "预算设置已更新！")
                self.top.destroy()
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的正数金额", parent=self.top)

    def show_edit_budget(self):
            self.EditBudgetDialog(self.root, self)

    def update_budget_display(self):
        # 计算当月总支出
        month_key = f"{self.current_date.year}-{self.current_date.month:02d}"
        total_expense = sum(
            float(record['amount'])
            for date_str, records in self.records.items()
            if date_str.startswith(month_key)
            for record in records
            if record['type'] == '支出'
        )

        # 计算剩余预算
        remaining = self.budget - total_expense

        # 更新显示样式
        budget_text = f"本月支出预算：{self.budget:.2f}元"
        remain_text = f"本月剩余预算：{remaining:.2f}元"

        # 设置颜色逻辑
        self.remain_label.config(foreground='black')  # 重置颜色
        if self.budget > 0:
            remaining_percent = remaining / self.budget
            if remaining_percent < 0.3:
                self.remain_label.config(foreground='red')
            if remaining < 0:  # 处理超支情况
                remain_text = f"本月超支预算：{-remaining:.2f}元"
                self.remain_label.config(foreground='red')

        # 更新显示内容
        self.budget_label.config(text=budget_text)
        self.remain_label.config(text=remain_text)

        # ---------- 第七部分：记账窗口类 ----------
    class AccountingWindow:
        def __init__(self, parent, date, main_app):  # 注意第三个参数
            self.top = tk.Toplevel(parent)
            self.main_app = main_app  # 保存主应用引用
            self.date = date
            self.top.grab_set()

            # 金额输入（添加输入验证）
            ttk.Label(self.top, text="金额（元）:").grid(row=0, column=0, padx=5, pady=5)
            self.amount = ttk.Entry(self.top)
            self.amount.grid(row=0, column=1, padx=5, pady=5)

            # 收支类型（添加默认选择）
            self.type_var = tk.StringVar(value="支出")
            ttk.Radiobutton(self.top, text="支出", variable=self.type_var, value="支出").grid(row=1, column=0, sticky=tk.W)
            ttk.Radiobutton(self.top, text="收入", variable=self.type_var, value="收入").grid(row=1, column=1, sticky=tk.W)

            # 消费类型（设置默认选项）
            ttk.Label(self.top, text="消费类型:").grid(row=2, column=0, sticky=tk.W, padx=5)
            self.category = ttk.Combobox(self.top, values=["饮食", "娱乐", "交通", "学习", "其他", "购物"], state="readonly")
            self.category.grid(row=2, column=1, padx=5)
            self.category.current(0)  # 默认选择第一个选项

            # 备注栏（始终显示）
            ttk.Label(self.top, text="备注:").grid(row=3, column=0, sticky=tk.W, padx=5)
            self.note = ttk.Entry(self.top)
            self.note.grid(row=3, column=1, padx=5)

            # 按钮布局优化
            btn_frame = ttk.Frame(self.top)
            btn_frame.grid(row=4, columnspan=2, pady=10)
            ttk.Button(btn_frame, text="确认", command=self.save).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="取消", command=self.top.destroy).pack(side=tk.RIGHT, padx=10)

        def save(self):
            try:
                # 输入验证
                amount = float(self.amount.get())
                if amount <= 0:
                    raise ValueError("金额必须大于0")

                # 构建记录
                record = {
                    'type': self.type_var.get(),
                    'amount': amount,
                    'category': self.category.get(),
                    'note': self.note.get()
                }

                # 保存到主应用数据
                date_str = self.date.strftime("%Y-%m-%d")
                if date_str not in self.main_app.records:
                    self.main_app.records[date_str] = []
                self.main_app.records[date_str].append(record)
                self.main_app.save_data()
                self.main_app.update_budget_display()  # 刷新预算显示

                messagebox.showinfo("提示", "记账成功！")
                self.top.destroy()
            except ValueError as e:
                messagebox.showerror("输入错误", str(e))
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

        # ---------- 第八部分：统计窗口类（修复版） ----------
    class StatsWindow:
        def __init__(self, parent, main_app):
            self.top = tk.Toplevel(parent)
            self.main_app = main_app
            self.top.title("收支统计")
            self.top.geometry("680x520")

            # 主容器布局
            main_frame = ttk.Frame(self.top)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

            # 控制面板
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(side=tk.LEFT, fill=tk.Y)

            # 统计类型选择
            type_frame = ttk.LabelFrame(control_frame, text="统计类型")
            type_frame.pack(pady=5, fill=tk.X)
            self.type_var = tk.StringVar(value="支出")
            ttk.Radiobutton(type_frame, text="支出", variable=self.type_var, value="支出").pack(anchor=tk.W)
            ttk.Radiobutton(type_frame, text="收入", variable=self.type_var, value="收入").pack(anchor=tk.W)

            # 日期范围选择
            date_frame = ttk.LabelFrame(control_frame, text="日期范围")
            date_frame.pack(pady=10, fill=tk.X)
            ttk.Label(date_frame, text="开始日期:").grid(row=0, column=0, sticky=tk.W)
            self.start_date = ttk.Entry(date_frame, width=12)
            self.start_date.grid(row=0, column=1, pady=2)

            ttk.Label(date_frame, text="结束日期:").grid(row=1, column=0, sticky=tk.W)
            self.end_date = ttk.Entry(date_frame, width=12)
            self.end_date.grid(row=1, column=1, pady=2)

            # 操作按钮
            btn_frame = ttk.Frame(control_frame)
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="查询", command=self.show_stats, width=10).pack(pady=5)
            ttk.Button(btn_frame, text="关闭", command=self.top.destroy, width=10).pack(pady=5)

            # 金额显示
            amount_frame = ttk.LabelFrame(control_frame, text="统计结果")
            amount_frame.pack(fill=tk.X)
            bold_font = ('Arial', 11, 'bold')
            self.income_label = ttk.Label(amount_frame, text="收入总额：0.00元", foreground='red', font=bold_font)
            self.income_label.pack(anchor=tk.W, pady=2)
            self.expense_label = ttk.Label(amount_frame, text="支出总额：0.00元", foreground='green', font=bold_font)
            self.expense_label.pack(anchor=tk.W, pady=2)

            # 图表区域
            chart_frame = ttk.Frame(main_frame)
            chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.figure = plt.Figure(figsize=(6, 5), dpi=100)
            self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def show_stats(self):
            try:
                # 日期验证
                start_date = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
                end_date = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
                if start_date > end_date:
                    raise ValueError("开始日期不能晚于结束日期")

                # 数据收集
                income_data = defaultdict(float)
                expense_data = defaultdict(float)

                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.strftime("%Y-%m-%d")
                    if date_str in self.main_app.records:
                        for record in self.main_app.records[date_str]:
                            amount = float(record['amount'])
                            category = record['category']
                            if record['type'] == '收入':
                                income_data[category] += amount
                            else:
                                expense_data[category] += amount
                    current_date += timedelta(days=1)

                # 更新显示
                self.figure.clf()
                ax = self.figure.add_subplot(111)

                if self.type_var.get() == '收入':
                    data = income_data
                    title = "收入构成"
                else:
                    data = expense_data
                    title = "支出构成"

                if not data:
                    messagebox.showinfo("提示", "没有找到相关记录")
                    return

                # 绘制饼图
                labels = list(data.keys())
                sizes = list(data.values())
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.set_title(title, fontsize=12)
                self.canvas.draw()

                # 更新金额显示
                self.income_label.config(text=f"收入总额：{sum(income_data.values()):.2f}元")
                self.expense_label.config(text=f"支出总额：{sum(expense_data.values()):.2f}元")

            except ValueError as e:
                messagebox.showerror("输入错误", str(e))
            except Exception as e:
                messagebox.showerror("错误", f"查询失败：{str(e)}")

    # ---------- 第九部分：数据持久化 ----------
    def load_data(self):
        try:
            with open('data.json', 'r') as f:
                data = json.load(f)
                self.records = data.get('records', {})
                self.budget = data.get('budget', 0)
        except FileNotFoundError:
            pass

    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump({
                'records': self.records,
                'budget': self.budget
            }, f)

    # ---------- 第十部分：运行程序 ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
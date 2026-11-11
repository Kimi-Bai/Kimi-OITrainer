import tkinter as tk
from tkinter import messagebox
import KimiTools as kt
import os

def center_fixed(win,height,width) :
    """
    让窗口居中显示，并固定其大小（禁止用户拖动缩放）。

    参数:
        win    : 要设置的窗口对象（如 tk.Tk() 或 tk.Toplevel()）
        height : 窗口高度（像素）
        width  : 窗口宽度（像素）
    """
    # 获取屏幕的宽度和高度（主屏分辨率）
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    # 计算窗口左上角坐标，使其在屏幕上水平、垂直居中
    # 用整除 // 2 得到整数坐标，避免浮点数问题
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 设置窗口大小和位置，格式为 "宽x高+左上角x+左上角y"
    win.geometry(f"{width}x{height}+{x}+{y}")

    # 禁止调整窗口大小：第一个参数控制宽度，第二个控制高度
    win.resizable(False, False)

def Login() :
    os.makedirs("OI-Data", exist_ok=True)
    def Is_acc() :
        acc = entry_account.get()
        pwd = entry_pwd.get()
        if not acc or not pwd:
            messagebox.showwarning("警告", "账号和密码不能为空")
            return

        result = kt.IsAcc(acc, pwd)

        if result == 1:
            messagebox.showinfo("成功", "登录成功")
            # 登录成功后的操作
            acc_pwd.destroy()
        elif result == 0:
            messagebox.showerror("错误", "密码错误")
        else:
            messagebox.showerror("错误", "账号不存在")

    def Register() :
        acc = entry_account.get()
        pwd = entry_pwd.get()
        
        if not acc or not pwd:
            messagebox.showwarning("警告", "账号和密码不能为空")
            return
        if kt.RegisterAcc(acc,pwd) == 1 :
            messagebox.showinfo("成功", "创建成功")
        else :
            messagebox.showerror("错误", "创建失败")

    acc_pwd = tk.Tk()
    acc_pwd.title("OI教练模拟器")
    
    center_fixed(acc_pwd,300,300)

    warning = tk.Label(acc_pwd,text="不要用空格和中文！！！")
    warning.grid(row=0,column=1)
    
    label_account = tk.Label(acc_pwd,text="账号")
    label_account.grid(row=1,column=0)
    entry_account = tk.Entry(acc_pwd)
    entry_account.grid(row=1,column=1)
    
    label_pwd = tk.Label(acc_pwd,text="密码")
    label_pwd.grid(row=2,column=0)
    entry_pwd = tk.Entry(acc_pwd)
    entry_pwd.grid(row=2,column=1)
    
    button1 = tk.Button(acc_pwd,text="登录",command=Is_acc)
    button1.grid(row=2,column=2)
    
    button2 = tk.Button(acc_pwd,text="创建一个账号",command=Register)
    button2.grid(row=3,column=1)
    
    acc_pwd.mainloop()

def Start() :
    game = tk.Tk()
    game.title("OI教练模拟器")
    

Login()

Start()

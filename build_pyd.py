import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


def find_vcvars64():
    """自动查找 vcvars64.bat 的常见位置"""
    candidates = []
    # VS 2022 / 2019 常见安装路径
    for ver in ("2022", "2019"):
        for edition in ("BuildTools", "Community", "Professional", "Enterprise"):
            base = rf"C:\Program Files\Microsoft Visual Studio\{ver}\{edition}\VC\Auxiliary\Build\vcvars64.bat"
            candidates.append(base)
            base_x86 = rf"C:\Program Files (x86)\Microsoft Visual Studio\{ver}\{edition}\VC\Auxiliary\Build\vcvars64.bat"
            candidates.append(base_x86)
    # 也问一下 VS Installer（如果 vswhere 存在）
    vswhere = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    if os.path.isfile(vswhere):
        try:
            out = subprocess.check_output(
                [vswhere, "-latest", "-products", "*",
                 "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                 "-property", "installationPath"],
                text=True, encoding="gbk", errors="replace"
            ).strip()
            if out:
                candidates.insert(0, os.path.join(out, r"VC\Auxiliary\Build\vcvars64.bat"))
        except Exception:
            pass
    for c in candidates:
        if os.path.isfile(c):
            return c
    return ""


def run_in_msvc_env(cmd_list, cwd, log_fn):
    """在已加载 vcvars64 环境的 cmd 里执行命令，实时输出"""
    vcvars = find_vcvars64()
    if not vcvars:
        log_fn("未找到 vcvars64.bat，请安装 Visual Studio Build Tools（C++ 桌面开发）\n")
        return 1

    log_fn(f"使用环境: {vcvars}\n")

    # 把命令拼成一行，用 && 保证 vcvars 成功后执行
    # 注意：用 list2cmdline 处理带空格的参数
    cmdline = subprocess.list2cmdline(cmd_list)
    full = f'call "{vcvars}" >nul && {cmdline}'
    log_fn(f"执行: {full}\n")
    log_fn("=" * 60 + "\n")

    proc = subprocess.Popen(
        full,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="gbk",
        errors="replace",
        shell=True,          # 必须 shell=True 才能用 call 和 &&
    )
    for line in proc.stdout:
        log_fn(line)
    proc.wait()
    return proc.returncode


class PydBuilder:
    def __init__(self, root):
        self.root = root
        root.title("C++ → PYD 编译工具")
        root.geometry("780x580")

        self.v_cpp = tk.StringVar()
        self.v_py_include = tk.StringVar(value=r"D:\Python 3.14\include")
        self.v_py_libs = tk.StringVar(value=r"D:\Python 3.14\libs")
        self.v_py_lib = tk.StringVar(value="python314.lib")
        self.v_pybind11 = tk.StringVar(
            value=r"D:\Python 3.14\Lib\site-packages\pybind11\include"
        )
        self.v_output = tk.StringVar()

        self._row(0, "源文件 (.cpp)：", self.v_cpp, self._pick_cpp)
        self._row(1, "pybind11 include：", self.v_pybind11, self._pick_dir)
        self._row(2, "Python include：", self.v_py_include, self._pick_dir)
        self._row(3, "Python libs：", self.v_py_libs, self._pick_dir)
        self._row(4, "Python 库文件名：", self.v_py_lib, None)
        self._row(5, "输出 .pyd：", self.v_output, self._pick_output)

        bf = tk.Frame(root)
        bf.pack(fill="x", padx=10, pady=6)
        tk.Button(bf, text="开始编译", width=14, command=self.build).pack(side="left", padx=4)
        tk.Button(bf, text="清空输出", width=10, command=self.clear_log).pack(side="left", padx=4)
        tk.Button(bf, text="打开输出目录", width=12, command=self.open_outdir).pack(side="left", padx=4)

        self.log = ScrolledText(root, wrap="word", height=18)
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 启动时把 vcvars 查找结果写进日志，方便排查
        v = find_vcvars64()
        self._append("vcvars64.bat: " + (v if v else "未找到！") + "\n")
        self._append("可直接双击运行；若失败，请检查上方路径。\n\n")

    def _row(self, r, label, var, browse_cmd):
        f = tk.Frame(self.root)
        f.pack(fill="x", padx=10, pady=3)
        tk.Label(f, text=label, width=18, anchor="e").pack(side="left")
        tk.Entry(f, textvariable=var).pack(side="left", fill="x", expand=True, padx=4)
        if browse_cmd:
            tk.Button(f, text="浏览", width=6,
                      command=lambda: browse_cmd(var)).pack(side="left")

    def _pick_cpp(self, var):
        p = filedialog.askopenfilename(
            title="选择 C++ 源文件",
            filetypes=[("C++ 源文件", "*.cpp"), ("所有文件", "*.*")],
        )
        if p:
            var.set(p)
            base = os.path.splitext(os.path.basename(p))[0]
            self.v_output.set(os.path.join(os.path.dirname(p), base + ".pyd"))

    def _pick_dir(self, var):
        p = filedialog.askdirectory(title="选择目录")
        if p:
            var.set(p)

    def _pick_output(self, var):
        p = filedialog.asksaveasfilename(
            title="保存为 .pyd", defaultextension=".pyd",
            filetypes=[("Python 扩展", "*.pyd")],
        )
        if p:
            var.set(p)

    def build(self):
        cpp = self.v_cpp.get().strip()
        if not cpp or not os.path.isfile(cpp):
            messagebox.showerror("错误", "请选择有效的 .cpp 源文件")
            return
        out = self.v_output.get().strip()
        if not out:
            messagebox.showerror("错误", "请指定输出 .pyd 路径")
            return

        py_inc = self.v_py_include.get().strip()
        py_libs = self.v_py_libs.get().strip()
        py_lib = self.v_py_lib.get().strip()
        pybind = self.v_pybind11.get().strip()

        for path, name in [(py_inc, "Python include"), (py_libs, "Python libs"),
                           (pybind, "pybind11 include")]:
            if not os.path.isdir(path):
                messagebox.showerror("错误", f"{name} 目录不存在：\n{path}")
                return

        out_dir = os.path.dirname(out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        cmd = [
            "cl",
            "/LD", "/EHsc", "/std:c++17", "/utf-8",
            f"/I{pybind}",
            f"/I{py_inc}",
            cpp,
            "/link",
            f"/LIBPATH:{py_libs}",
            py_lib,
            f"/OUT:{out}",
        ]

        self.clear_log()
        rc = run_in_msvc_env(cmd, os.path.dirname(cpp), self._append)
        self._append("=" * 60 + "\n")

        if rc == 0:
            self._fix_output_name(out)
            self._append("编译成功！\n")
            messagebox.showinfo("完成", f"已生成：\n{out}")
        else:
            self._append(f"编译失败，返回码 {rc}\n")
            messagebox.showerror("失败", "编译失败，请查看日志")

    def _fix_output_name(self, out):
        d = os.path.dirname(out)
        base = os.path.splitext(os.path.basename(out))[0]
        dll = os.path.join(d, base + ".dll")
        if not os.path.isfile(out) and os.path.isfile(dll):
            try:
                os.replace(dll, out)
                self._append(f"已将 {os.path.basename(dll)} 改名为 {os.path.basename(out)}\n")
            except OSError as e:
                self._append(f"改名失败：{e}\n")

    def _append(self, text):
        self.log.insert("end", text)
        self.log.see("end")
        self.root.update_idletasks()

    def clear_log(self):
        self.log.delete("1.0", "end")

    def open_outdir(self):
        out = self.v_output.get().strip()
        d = os.path.dirname(out) if out else ""
        if d and os.path.isdir(d):
            os.startfile(d)
        else:
            messagebox.showinfo("提示", "输出目录不存在")


if __name__ == "__main__":
    root = tk.Tk()
    PydBuilder(root)
    root.mainloop()
import subprocess
import ctypes
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# بررسی دسترسی ادمین
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# لیست DNSها
providers = [
    "Shecan", "Electro", "Begzar", "DNS Pro", "Google", "Cloudflare", "Reset to Default"
]
dns_servers = {
    "Shecan": ["178.22.122.100", "185.51.200.2"],
    "Electro": ["78.157.42.100", "78.157.42.101"],
    "Begzar": ["185.55.226.26", "185.55.226.25"],
    "DNS Pro": ["87.107.110.109", "87.107.110.110"],
    "Google": ["8.8.8.8", "8.8.4.4"],
    "Cloudflare": ["1.1.1.1", "1.0.0.1"],
    "Reset to Default": []
}

# پیدا کردن کارت شبکه متصل
def get_active_interface():
    result = subprocess.run("netsh interface show interface", capture_output=True, text=True, shell=True)
    for line in result.stdout.splitlines():
        if "Connected" in line and "Dedicated" in line:
            return line.split()[-1]
    return None

# نمایش DNS فعلی
def get_current_dns(interface):
    result = subprocess.run(f'netsh interface ip show dns "{interface}"', capture_output=True, text=True, shell=True)
    return result.stdout.strip()

# تنظیم DNS
def apply_dns():
    provider = dns_choice.get()
    dns_list = dns_servers[provider]

    if not interface_name:
        messagebox.showerror("Error", "No active network interface found.")
        return

    try:
        if not dns_list:
            subprocess.run(f'netsh interface ip set dns name="{interface_name}" source=dhcp', shell=True)
        else:
            subprocess.run(f'netsh interface ip set dns name="{interface_name}" static {dns_list[0]}', shell=True)
            for i, dns in enumerate(dns_list[1:], 2):
                subprocess.run(f'netsh interface ip add dns name="{interface_name}" {dns} index={i}', shell=True)

        current_dns.set(get_current_dns(interface_name))
        messagebox.showinfo("Success", f"DNS updated to {provider}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
if not is_admin():
    messagebox.showerror("Permission Denied", "Please run this script as administrator.")
    sys.exit(1)

interface_name = get_active_interface()
if not interface_name:
    messagebox.showerror("Error", "No active network interface found.")
    sys.exit(1)

root = tk.Tk()
root.title("DNS Switcher")
root.geometry("400x300")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="حکومتی که به قانون اساسی پایبند نباشه را باید برانداخت").pack(pady=(1, 11))
ttk.Label(frame, text="Select DNS Provider:").pack(pady=(0, 10))

dns_choice = ttk.Combobox(frame, values=providers, state="readonly")
dns_choice.set(providers[0])
dns_choice.pack()

ttk.Button(frame, text="Apply DNS", command=apply_dns).pack(pady=10)

ttk.Label(frame, text="Current DNS Settings:").pack(pady=(10, 2))
current_dns = tk.StringVar(value=get_current_dns(interface_name))
dns_display = ttk.Label(frame, textvariable=current_dns, background="white", relief="sunken", anchor="w", padding=5)
dns_display.pack(fill="x")

ttk.Label(frame, text=f"Interface: {interface_name}", font=("Segoe UI", 9, "italic")).pack(pady=(10, 0))

root.mainloop()

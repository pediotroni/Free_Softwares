import socket
import requests

def get_local_ip():
    try:
        # این فقط IP لوکال شما را نشان می‌دهد (در شبکه داخلی)
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        return f"Error: {str(e)}"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return "Unable to fetch IP"
    except Exception as e:
        return f"Error: {str(e)}"

local_ip = get_local_ip()
public_ip = get_public_ip()

print(f"آدرس IP لوکال شما: {local_ip}")
print(f"آدرس IP واقعی (عمومی) شما: {public_ip}")

# ذخیره در فایل
with open('my_ips.txt', 'w', encoding='utf-8') as file:
    file.write(f"آدرس IP لوکال: {local_ip}\n")
    file.write(f"آدرس IP عمومی: {public_ip}\n")

print("اطلاعات IP با موفقیت در فایل 'my_ips.txt' ذخیره شد.")
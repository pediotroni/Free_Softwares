import socket
import threading
import pyautogui
import zlib
import pickle
import cv2
import numpy as np
from mss import mss
from PIL import Image

class RemoteServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = False
        self.quality = 50  # کیفیت تصویر (0-100)
        
        # تنظیمات pyautogui
        pyautogui.FAILSAFE = False
        
    def start(self):
        self.running = True
        print(f"سرور در حال گوش دادن روی {self.host}:{self.port}")
        
        conn, addr = self.server_socket.accept()
        print(f"اتصال برقرار شد از {addr}")
        
        # شروع thread برای ارسال اسکرین شات
        screen_thread = threading.Thread(target=self.send_screen, args=(conn,))
        screen_thread.daemon = True
        screen_thread.start()
        
        # دریافت دستورات ماوس و کیبورد
        while self.running:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                    
                self.handle_command(data, conn)
                
            except (ConnectionResetError, BrokenPipeError):
                print("اتصال قطع شد")
                break
                
        conn.close()
        self.running = False
        
    def handle_command(self, command, conn):
        try:
            parts = command.split(',')
            cmd = parts[0]
            
            if cmd == 'MOUSE_MOVE':
                x, y = map(int, parts[1:3])
                pyautogui.moveTo(x, y)
                
            elif cmd == 'MOUSE_CLICK':
                x, y, button, action = parts[1:5]
                x, y = int(x), int(y)
                
                if action == 'DOWN':
                    pyautogui.mouseDown(x, y, button=button)
                elif action == 'UP':
                    pyautogui.mouseUp(x, y, button=button)
                    
            elif cmd == 'KEYBOARD':
                key = parts[1]
                action = parts[2]
                
                if action == 'DOWN':
                    pyautogui.keyDown(key)
                elif action == 'UP':
                    pyautogui.keyUp(key)
                    
            elif cmd == 'QUALITY':
                self.quality = int(parts[1])
                conn.sendall(b"OK")
                
        except Exception as e:
            print(f"خطا در پردازش دستور: {e}")
            
    def send_screen(self, conn):
        sct = mss()
        monitor = sct.monitors[1]  # مانیتور اصلی
        
        while self.running:
            try:
                # گرفتن اسکرین شات
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
                
                # تبدیل به numpy array و سپس به JPEG با کیفیت تنظیم شده
                frame = np.array(img)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                # فشرده سازی و ارسال
                compressed = zlib.compress(buffer.tobytes())
                size = len(compressed)
                conn.sendall(size.to_bytes(4, 'big') + compressed)
                
            except Exception as e:
                print(f"خطا در ارسال اسکرین: {e}")
                break
                
    def stop(self):
        self.running = False
        self.server_socket.close()

if __name__ == "__main__":
    server = RemoteServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("سرور متوقف شد")
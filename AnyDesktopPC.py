import socket
import cv2
import numpy as np
import zlib
import pygame
import threading
import sys
import pyautogui
from pygame.locals import *

class RemoteClient:
    def __init__(self, server_ip='localhost', server_port=5000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.remote_screen_size = (1024, 768)  # اندازه پیش فرض
        self.scaling_factor = 1.0
        self.mouse_down = False
        self.current_button = None
        
    def connect(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.running = True
            print(f"متصل به سرور در {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"خطا در اتصال به سرور: {e}")
            return False
            
    def start(self):
        # راه اندازی pygame برای نمایش تصویر و کنترل
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768), RESIZABLE)
        pygame.display.set_caption('Remote Desktop Client')
        
        # شروع thread برای دریافت اسکرین شات
        screen_thread = threading.Thread(target=self.receive_screen)
        screen_thread.daemon = True
        screen_thread.start()
        
        # حلقه اصلی برای کنترل
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
                    
                # کنترل ماوس
                self.handle_mouse_events(event)
                
                # کنترل کیبورد
                self.handle_keyboard_events(event)
                
            pygame.display.flip()
            clock.tick(30)
            
        self.client_socket.close()
        pygame.quit()
        
    def handle_mouse_events(self, event):
        if event.type == MOUSEMOTION:
            # محاسبه موقعیت ماوس نسبت به صفحه ریموت
            mouse_x, mouse_y = event.pos
            remote_x = int(mouse_x / self.scaling_factor)
            remote_y = int(mouse_y / self.scaling_factor)
            
            # ارسال حرکت ماوس به سرور
            if 0 <= remote_x < self.remote_screen_size[0] and 0 <= remote_y < self.remote_screen_size[1]:
                self.send_command(f'MOUSE_MOVE,{remote_x},{remote_y}')
                
        elif event.type == MOUSEBUTTONDOWN:
            self.mouse_down = True
            if event.button == 1:
                self.current_button = 'left'
            elif event.button == 3:
                self.current_button = 'right'
                
            mouse_x, mouse_y = event.pos
            remote_x = int(mouse_x / self.scaling_factor)
            remote_y = int(mouse_y / self.scaling_factor)
            self.send_command(f'MOUSE_CLICK,{remote_x},{remote_y},{self.current_button},DOWN')
            
        elif event.type == MOUSEBUTTONUP:
            self.mouse_down = False
            mouse_x, mouse_y = event.pos
            remote_x = int(mouse_x / self.scaling_factor)
            remote_y = int(mouse_y / self.scaling_factor)
            self.send_command(f'MOUSE_CLICK,{remote_x},{remote_y},{self.current_button},UP')
            self.current_button = None
            
    def handle_keyboard_events(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.running = False
            else:
                key_name = pygame.key.name(event.key)
                self.send_command(f'KEYBOARD,{key_name},DOWN')
                
        elif event.type == KEYUP:
            key_name = pygame.key.name(event.key)
            self.send_command(f'KEYBOARD,{key_name},UP')
            
    def send_command(self, command):
        try:
            self.client_socket.sendall(command.encode())
        except Exception as e:
            print(f"خطا در ارسال دستور: {e}")
            self.running = False
            
    def receive_screen(self):
        try:
            while self.running:
                # دریافت اندازه داده
                size_bytes = self.client_socket.recv(4)
                if not size_bytes:
                    break
                    
                size = int.from_bytes(size_bytes, 'big')
                
                # دریافت داده فشرده شده
                compressed_data = b''
                while len(compressed_data) < size:
                    chunk = self.client_socket.recv(size - len(compressed_data))
                    if not chunk:
                        break
                    compressed_data += chunk
                    
                # از حالت فشرده خارج کردن
                buffer = zlib.decompress(compressed_data)
                
                # تبدیل به تصویر
                np_arr = np.frombuffer(buffer, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # ذخیره اندازه واقعی صفحه ریموت
                    self.remote_screen_size = (frame.shape[1], frame.shape[0])
                    
                    # محاسبه فاکتور مقیاس
                    win_width, win_height = self.screen.get_size()
                    self.scaling_factor = min(win_width / frame.shape[1], win_height / frame.shape[0])
                    
                    # تغییر اندازه تصویر برای نمایش
                    display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    display_frame = cv2.resize(display_frame, (int(frame.shape[1] * self.scaling_factor), 
                                                           int(frame.shape[0] * self.scaling_factor)))
                    
                    # نمایش تصویر در pygame
                    pygame_frame = pygame.surfarray.make_surface(display_frame.swapaxes(0, 1))
                    self.screen.blit(pygame_frame, (0, 0))
                    
        except Exception as e:
            print(f"خطا در دریافت اسکرین: {e}")
            self.running = False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = input("آدرس IP سرور را وارد کنید: ")
        
    client = RemoteClient(server_ip)
    if client.connect():
        client.start()
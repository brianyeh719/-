try:
    import ddddocr # Import ddddocr
    HAS_DDDDOCR = True
except ImportError:
    print("Warning: ddddocr not found or failed to import. Auto-captcha will be disabled.")
    HAS_DDDDOCR = False

import tkinter as tk
from tkinter import ttk
from bot import THSRBot
import threading
from PIL import Image, ImageTk
import io

class THSRApp:
    def __init__(self, root):
        global HAS_DDDDOCR
        self.root = root
        self.root.title("THSR Booking Bot")
        self.root.geometry("600x600")
        self.bot = THSRBot()
        self.captcha_event = threading.Event()
        self.captcha_solution = ""
        
        # Initialize OCR
        if HAS_DDDDOCR:
            print("Initializing OCR model...")
            try:
                self.ocr = ddddocr.DdddOcr(show_ad=False)
                print("OCR model initialized.")
            except Exception as e:
                print(f"Failed to init ddddocr: {e}")
                
                HAS_DDDDOCR = False
        else:
            print("OCR disabled.")

        print("Calling create_widgets...")
        self.create_widgets()
        print("create_widgets finished.")

    def create_widgets(self):
        # Title
        ttk.Label(self.root, text="台灣高鐵訂票機器人", font=("Helvetica", 16)).pack(pady=10)

        # Form Frame
        form_frame = ttk.Frame(self.root, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Start Station
        ttk.Label(form_frame, text="出發站:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_station_var = tk.StringVar(value="台北") # Default
        self.start_station_cb = ttk.Combobox(form_frame, textvariable=self.start_station_var)
        # Use Chinese station names as found on the website
        stations = ("南港", "台北", "板橋", "桃園", "新竹", "苗栗", "台中", "彰化", "雲林", "嘉義", "台南", "左營")
        self.start_station_cb['values'] = stations
        self.start_station_cb.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # Dest Station
        ttk.Label(form_frame, text="到達站:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_station_var = tk.StringVar(value="台南") # Default
        self.dest_station_cb = ttk.Combobox(form_frame, textvariable=self.dest_station_var)
        self.dest_station_cb['values'] = stations
        self.dest_station_cb.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Date
        ttk.Label(form_frame, text="日期 (YYYY/MM/DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value="2026/03/01")
        self.date_entry = ttk.Entry(form_frame, textvariable=self.date_var)
        self.date_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)

        # Time
        ttk.Label(form_frame, text="時間:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar(value="12:00")
        self.time_cb = ttk.Combobox(form_frame, textvariable=self.time_var)
        # Generate time values 00:00 to 23:30
        times = []
        for h in range(24):
            times.append(f"{h:02d}:00")
            times.append(f"{h:02d}:30")
        self.time_cb['values'] = times
        self.time_cb.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Ticket Amount
        ttk.Label(form_frame, text="車票張數:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ticket_amount_var = tk.StringVar(value="1") 
        self.ticket_amount_cb = ttk.Combobox(form_frame, textvariable=self.ticket_amount_var)
        # Website uses simple numbers for labels
        self.ticket_amount_cb['values'] = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
        self.ticket_amount_cb.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # ID Number
        ttk.Label(form_frame, text="身分證字號:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.id_var = tk.StringVar(value="A123456789") # Default Test ID
        self.id_entry = ttk.Entry(form_frame, textvariable=self.id_var)
        self.id_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)

        # Phone
        ttk.Label(form_frame, text="手機號碼:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar(value="0912345678") # Default Test Phone
        self.phone_entry = ttk.Entry(form_frame, textvariable=self.phone_var)
        self.phone_entry.grid(row=6, column=1, sticky=tk.EW, pady=5)

        # Email
        ttk.Label(form_frame, text="電子郵件:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar(value="")  # Optional email
        self.email_entry = ttk.Entry(form_frame, textvariable=self.email_var)
        self.email_entry.grid(row=7, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="(選填，可收取訂位確認信)").grid(row=7, column=2, sticky=tk.W, padx=5)

        # Priority Time Ranges
        ttk.Label(form_frame, text="優先時段 (格式 HH:MM-HH:MM, ...):").grid(row=8, column=0, sticky=tk.W, pady=5)
        # Default empty means no priority (take first available)
        self.time_ranges_var = tk.StringVar(value="12:00-22:00") 
        self.range_entry = ttk.Entry(form_frame, textvariable=self.time_ranges_var)
        self.range_entry.grid(row=8, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="(留空則選擇最早班次)").grid(row=8, column=2, sticky=tk.W, padx=5)

        # Retry Settings
        ttk.Label(form_frame, text="搜尋循環次數:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.retry_cycles_var = tk.StringVar(value="10")
        self.retry_cycles_entry = ttk.Entry(form_frame, textvariable=self.retry_cycles_var)
        self.retry_cycles_entry.grid(row=9, column=1, sticky=tk.EW, pady=5)

        self.until_success_var = tk.BooleanVar(value=False)
        def toggle_retry_entry():
            if self.until_success_var.get():
                self.retry_cycles_entry.config(state='disabled')
            else:
                self.retry_cycles_entry.config(state='normal')

        self.until_success_cb = ttk.Checkbutton(
            form_frame,
            text="直到成功訂到為止",
            variable=self.until_success_var,
            command=toggle_retry_entry
        )
        self.until_success_cb.grid(row=9, column=2, sticky=tk.W, padx=5)

        # Test Mode Checkbox
        self.test_mode_var = tk.BooleanVar(value=True)  # Default: Test mode ON (won't submit)
        self.test_mode_cb = ttk.Checkbutton(
            form_frame, 
            text="測試模式 (不送出最終訂位)", 
            variable=self.test_mode_var
        )
        self.test_mode_cb.grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=10)
        ttk.Label(form_frame, text="⚠️ 取消勾選將實際完成訂位！", foreground="red").grid(row=10, column=2, sticky=tk.W, padx=5)

        # Start Button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="開始訂票", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="停止訂票", command=self.stop_bot)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.config(state='disabled')

        # CAPTCHA Section
        captcha_frame = ttk.LabelFrame(self.root, text="驗證碼處理", padding="10")
        captcha_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.captcha_img_label = ttk.Label(captcha_frame, text="驗證碼將自動辨識")
        self.captcha_img_label.pack(pady=5)
        
        self.captcha_var = tk.StringVar()
        self.captcha_entry = ttk.Entry(captcha_frame, textvariable=self.captcha_var)
        self.captcha_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.captcha_entry.config(state='disabled') # Purely output/log

        self.submit_captcha_btn = ttk.Button(captcha_frame, text="送出驗證碼", command=self.submit_captcha_code)
        self.submit_captcha_btn.pack(side=tk.RIGHT, padx=5)
        self.submit_captcha_btn.config(state='disabled')

    def start_bot(self):
        print("Bot starting...")
        self.stop_event = threading.Event()
        
        # Toggle Buttons
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # Get values here
        start = self.start_station_var.get()
        dest = self.dest_station_var.get()
        date = self.date_var.get()
        time_str = self.time_var.get()
        qty = self.ticket_amount_var.get()
        pid = self.id_var.get()
        phone = self.phone_var.get()
        email = self.email_var.get()
        test_mode = self.test_mode_var.get()
        until_success = self.until_success_var.get()

        max_cycles = None
        if not until_success:
            try:
                max_cycles = int(self.retry_cycles_var.get())
                if max_cycles <= 0:
                    max_cycles = 1
            except Exception:
                max_cycles = 10
        
        # Parse Time Ranges
        raw_ranges = self.time_ranges_var.get()
        time_ranges = []
        if raw_ranges.strip():
            try:
                # Format: "09:00-10:00, 14:00-15:00"
                parts = raw_ranges.split(',')
                for p in parts:
                    if '-' in p:
                        s, e = p.split('-')
                        time_ranges.append((s.strip(), e.strip()))
            except:
                print("Error parsing time ranges, ignoring.")
        
        
        def normalize_time(t):
            if not t:
                return t
            t = t.strip()
            if ':' in t:
                parts = t.split(':')
                hour = parts[0].zfill(2)  # Pad hour to 2 digits
                minute = parts[1].zfill(2) if len(parts) > 1 else "00"
                return f"{hour}:{minute}"
            return t
        
        # Normalize time ranges
        time_ranges = [(normalize_time(s), normalize_time(e)) for s, e in time_ranges]
        
        # Normalize time_str
        time_str = normalize_time(time_str)
        
        # AUTO-SYNC: If priority ranges are specified, use the start of the first range
        # as the search time for Step 1. This ensures the search results include trains
        # within the user's preferred time window.
        if time_ranges:
            first_range_start = time_ranges[0][0]
            print(f"優先時段已設定: {time_ranges}")
            print(f"自動將 Step 1 搜尋時間調整為: {first_range_start} (優先時段起始時間)")
            time_str = first_range_start
        else:
            print(f"未設定優先時段，使用原始搜尋時間: {time_str}")
        
        # Log test mode status
        if test_mode:
            print("⚠️ 測試模式啟用：將不會送出最終訂位")
        else:
            print("🔴 正式模式：將送出最終訂位！")
        
        threading.Thread(
            target=self.run_browser,
            args=(start, dest, date, time_str, qty, pid, phone, email, time_ranges, test_mode, max_cycles, until_success),
            daemon=True
        ).start()



    def stop_bot(self):
        print("Stopping bot...")
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
        self.stop_btn.config(state='disabled')
        self.start_btn.config(state='normal')

    def run_browser(self, start, dest, date, time_str, qty, pid, phone, email, time_ranges, test_mode, max_cycles, until_success):
        retry_count = 0
        
        try:
            self.bot.start_browser()

            while True:
                if max_cycles is not None and retry_count >= max_cycles:
                    break

                retry_count += 1
                print(f"\n{'='*50}")
                if max_cycles is None:
                    print(f"搜尋循環 第 {retry_count} 次 (直到成功)")
                else:
                    print(f"搜尋循環 第 {retry_count}/{max_cycles} 次")
                print(f"{'='*50}")
                
                # Check stop event
                if hasattr(self, 'stop_event') and self.stop_event.is_set():
                    print(">> 用戶已停止訂票")
                    break
                
                # Pass stop_event to submit_search
                if self.bot.submit_search(start, dest, date, time_str, qty, self.solve_captcha, self.stop_event):
                    # Successfully reached Step 2, try booking
                    result = self.bot.submit_booking(pid, phone, email, time_ranges, test_mode)
                    
                    if result == "RETRY":
                        print(">> 沒有符合時段的班次，等待 5 秒後重新搜尋...")
                        import time
                        time.sleep(5)
                        continue  # Retry the search loop
                    else:
                        # Booking process completed (success or error)
                        break
                else:
                    # submit_search failed (probably stopped by user)
                    break
            
            if max_cycles is not None and retry_count >= max_cycles:
                print(f">> 已達最大重試次數 ({max_cycles})，停止搜尋")
                
        except Exception as e:
            print(f"Browser error: {e}")

            import traceback
            traceback.print_exc()
        finally:
            print("Browser thread finished.")
            # Ensure buttons reset even if crashed
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))


    def solve_captcha(self, img_bytes):
        # Update UI in main thread just for visual feedback
        try:
            image = Image.open(io.BytesIO(img_bytes))
            photo = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error processing image for UI: {e}")
            photo = None

        res = ""
        if HAS_DDDDOCR:
            # Do OCR
            print("Solving Captcha...")
            try:
                res = self.ocr.classification(img_bytes)
                print(f"OCR Result: {res}")
                self.captcha_solution = res
            except Exception as e:
                print(f"OCR Error: {e}")
                self.captcha_solution = "" # Fail gracefully
        else:
            print("OCR not available. Please enter captcha manually if enabled.")

        def update_ui():
            if photo:
                if HAS_DDDDOCR:
                    self.captcha_img_label.config(image=photo, text=f"辨識結果: {res}")
                else:
                    self.captcha_img_label.config(image=photo, text="請手動輸入(自動辨識失敗)")
                    self.captcha_entry.config(state='normal')
                    self.submit_captcha_btn.config(state='normal')
                    
                self.captcha_img_label.image = photo # Keep reference
            
            if HAS_DDDDOCR:
                self.captcha_var.set(res)
            
        self.root.after(0, update_ui)
        
        if not HAS_DDDDOCR:
            # If manual, we need to wait for event
            print("Waiting for manual captcha input...")
            self.captcha_event.clear()
            self.captcha_event.wait()
            # Disable inputs again
            def disable_ui():
                self.captcha_entry.config(state='disabled')
                self.submit_captcha_btn.config(state='disabled')
            self.root.after(0, disable_ui)
            return self.captcha_solution
        
        return self.captcha_solution

    def submit_captcha_code(self):
        self.captcha_solution = self.captcha_var.get()
        self.captcha_event.set()

def main():
    print("Starting Main...")
    try:
        root = tk.Tk()
        print("Tkinter root created.")
        app = THSRApp(root)
        print("THSRApp initialized. Starting mainloop...")
        root.mainloop()
    except Exception as e:
        print(f"CRITICAL ERROR MAIN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

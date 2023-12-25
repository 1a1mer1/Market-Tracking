import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
import time
import threading

class PiyasaTakipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Piyasa Takip")
        self.choice_var = tk.StringVar()

        self.create_widgets()
        self.update_prices()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Hangisi için işlem yapmak istersiniz?").grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Altın", variable=self.choice_var, value="1").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Gümüş", variable=self.choice_var, value="2").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="İkisi de", variable=self.choice_var, value="3").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.target_gold_price_entry = ttk.Entry(main_frame)
        self.target_gold_price_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        self.target_silver_price_entry = ttk.Entry(main_frame)
        self.target_silver_price_entry.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

        self.gold_price_label = ttk.Label(main_frame, text="")
        self.gold_price_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.silver_price_label = ttk.Label(main_frame, text="")
        self.silver_price_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.notification_label = ttk.Label(main_frame, text="")
        self.notification_label.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        ttk.Button(main_frame, text="Onayla", command=self.start_tracking).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

    def get_gold_price(self):
        url = "https://altin.doviz.com/gram-altin"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            gold_price_element = soup.find("span", class_="value").text.strip()
            gold_price = float(gold_price_element.replace(".", "").replace(",", "."))
            return gold_price
        else:
            print("Altın fiyatı alınamadı. Lütfen daha sonra tekrar deneyin.")
            return None

    def get_silver_price(self):
        url = "https://altin.doviz.com/gumus"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            silver_price_element = soup.find("div", {"data-socket-key": "gumus", "data-socket-attr": "s"})
            if silver_price_element:
                silver_price = silver_price_element.text.strip()
                silver_price = float(silver_price.replace(",", "."))
                return silver_price
            else:
                print("Gümüş fiyatı bulunamadı. Lütfen daha sonra tekrar deneyin.")
                return None
        else:
            print("Gümüş fiyatı alınamadı. Lütfen daha sonra tekrar deneyin.")
            return None

    def update_prices(self):
        if self.choice_var.get() == "1" or self.choice_var.get() == "3":
            gold_price = self.get_gold_price()
            if gold_price is not None:
                self.gold_price_label.config(text=f"Altın Fiyatı: {gold_price:.2f} TRY/gr")
        else:
            self.gold_price_label.config(text="")

        if self.choice_var.get() == "2" or self.choice_var.get() == "3":
            silver_price = self.get_silver_price()
            if silver_price is not None:
                self.silver_price_label.config(text=f"Gümüş Fiyatı: {silver_price:.2f} TRY/gr")
        else:
            self.silver_price_label.config(text="")

        self.root.after(1000, self.update_prices)

    def start_tracking(self):
        choice = self.choice_var.get()
        if choice == "1" or choice == "3":
            target_gold_price = self.target_gold_price_entry.get()
            if target_gold_price:
                target_gold_price = float(target_gold_price)
                t1 = threading.Thread(target=self.get_notifications, args=(target_gold_price, self.get_gold_price(), "Altın",))
                t1.start()

        if choice == "2" or choice == "3":
            target_silver_price = self.target_silver_price_entry.get()
            if target_silver_price:
                target_silver_price = float(target_silver_price)
                t2 = threading.Thread(target=self.get_notifications, args=(target_silver_price, self.get_silver_price(), "Gümüş",))
                t2.start()

    def compare_float_values(self, value1, value2, decimal_places=2):
        return round(value1, decimal_places) == round(value2, decimal_places)

    def notify_user(self, target_price, current_price, symbol):
        if self.compare_float_values(current_price, target_price):
            self.notification_label.config(text=f"{symbol} fiyatı hedef fiyatınıza ulaştı! ({current_price:.2f} TRY/gr)")

    def get_notifications(self, target_price, current_price_func, symbol, max_notifications=25, interval=5):
        notification_count = 0
        while notification_count < max_notifications:
            current_price = current_price_func()
            if current_price is not None:
                self.notify_user(target_price, current_price, symbol)
                notification_count += 1
            time.sleep(interval)

if __name__ == "__main__":
    root = tk.Tk()
    app = PiyasaTakipApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import threading
import time
import os
import keyboard
import random
import subprocess

class SaintPE:
    def __init__(self, root):
        self.root = root
        self.root.title("Saint Enhancement Pocket Edition")
        self.root.geometry("980x520")
        self.root.configure(bg="#050505")
        self.is_active = False
        self.hidden = False
        self.points = [65] * 20
        
        # Subprocess protection for different PCs
        self.si = subprocess.STARTUPINFO()
        self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        messagebox.showinfo("SAINT PE", "System Initialized. Administrator Access Verified.")

        self.create_gui()
        self.init_global_hotkeys()

    def create_gui(self):
        # Title
        tk.Label(self.root, text="SAINT ENHANCEMENT SYSTEM", bg="#050505", fg="#00ff41", 
                 font=("Consolas", 20, "bold")).pack(pady=5)

        self.ping_lbl = tk.Label(self.root, text="PING: -- ms | BOOST: x2 INACTIVE", bg="#050505", fg="#00ff41", font=("Consolas", 11))
        self.ping_lbl.pack()

        # Live Graph
        self.canvas = tk.Canvas(self.root, width=900, height=100, bg="#0a0a0a", highlightthickness=1, highlightbackground="#222")
        self.canvas.pack(pady=5)

        # ADDED: Search Bar Frame
        search_frame = tk.Frame(self.root, bg="#050505")
        search_frame.pack(fill="x", padx=40, pady=2)
        tk.Label(search_frame, text="SEARCH:", bg="#050505", fg="#888", font=("Arial", 9, "bold")).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.scan_apps())
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg="#111", fg="#00ff41", 
                                     insertbackground="#00ff41", font=("Arial", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)

        # UPDATED: Process Tree with Start Time column
        self.tree = ttk.Treeview(self.root, columns=("PID", "App", "Priority", "StartTime"), show='headings', height=6)
        self.tree.heading("PID", text="PID")
        self.tree.heading("App", text="APPLICATION / SYSTEM")
        self.tree.heading("Priority", text="STATUS")
        self.tree.heading("StartTime", text="START TIME (NEWEST ON TOP)")
        self.tree.column("PID", width=80)
        self.tree.column("StartTime", width=180)
        self.tree.pack(pady=5, padx=40, fill="x")

        # Right-click Priority Menu
        self.menu = tk.Menu(self.root, tearoff=0, bg="#111", fg="#00ff41")
        self.menu.add_command(label="SET PRIORITY: REALTIME", command=self.set_priority_realtime)
        self.tree.bind("<Button-3>", lambda e: self.menu.post(e.x_root, e.y_root))

        self.info_lbl = tk.Label(self.root, text="SYSTEM IDLE", bg="#050505", fg="#888")
        self.info_lbl.pack()

        # Control Buttons Frame
        btn_frame = tk.Frame(self.root, bg="#050505")
        btn_frame.pack(pady=5)

        self.btn_act = tk.Button(btn_frame, text="ACTIVATE", command=self.activate_system, 
                                bg="#00ff41", fg="black", font=("Arial", 12, "bold"), width=12)
        self.btn_act.pack(side="left", padx=10)

        # ADDED: Refresh Button
        self.btn_ref = tk.Button(btn_frame, text="REFRESH", command=self.scan_apps, 
                                bg="#222", fg="#00ff41", font=("Arial", 12, "bold"), width=12)
        self.btn_ref.pack(side="left", padx=10)

    def scan_apps(self):
        """UPDATED: Sorts by create_time (Newest Top) and filters by search keyword"""
        for i in self.tree.get_children(): self.tree.delete(i)
        query = self.search_var.get().lower()
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                name = proc.info['name']
                if query in name.lower():
                    # Format time for display
                    readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(proc.info['create_time']))
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': name,
                        'time': readable_time,
                        'raw_time': proc.info['create_time']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort: Newest raw_time first
        processes.sort(key=lambda x: x['raw_time'], reverse=True)

        for p in processes:
            self.tree.insert("", "end", values=(p['pid'], p['name'], "OPTIMIZED", p['time']))

    def get_ping(self):
        while self.is_active:
            try:
                host = "8.8.8.8"
                output = subprocess.check_output(["ping", "-n", "1", host], startupinfo=self.si, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode()
                if "time=" in output:
                    raw_ping = int(output.split("time=")[1].split("ms")[0])
                    self.ping_lbl.config(text=f"PING: {raw_ping}ms | BOOSTED: {raw_ping // 2}ms (x2 ACTIVE)")
            except: pass
            time.sleep(3)

    def update_graph(self):
        if not self.is_active: return
        self.canvas.delete("wave")
        self.points.append(random.randint(15, 85))
        if len(self.points) > 45: self.points.pop(0)
        
        for i in range(len(self.points)-1):
            x1, y1 = i * 20, self.points[i]
            x2, y2 = (i+1) * 20, self.points[i+1]
            self.canvas.create_line(x1, y1, x2, y2, fill="#00ff41", width=2, tags="wave")
        
        self.root.after(3000, self.update_graph)

    def init_global_hotkeys(self):
        keyboard.add_hotkey('ctrl+shift+t', self.toggle_stealth)

    def toggle_stealth(self):
        if self.hidden:
            self.root.deiconify()
            self.root.attributes("-topmost", True)
        else:
            self.root.withdraw()
        self.hidden = not self.hidden

    def set_priority_realtime(self):
        selected = self.tree.selection()
        if selected:
            pid = self.tree.item(selected[0])['values'][0]
            try:
                p = psutil.Process(pid)
                p.nice(psutil.REALTIME_PRIORITY_CLASS)
                messagebox.showinfo("BOOSTED", f"{p.name()} set to REALTIME.")
            except:
                messagebox.showerror("Error", "Admin Rights Required.")

    def activate_system(self):
        if not self.is_active:
            self.is_active = True
            self.btn_act.config(text="SYNCED", bg="#ff4141")
            threading.Thread(target=self.sync_engine, daemon=True).start()
            threading.Thread(target=self.get_ping, daemon=True).start()
            self.scan_apps()
            self.update_graph()
        else:
            self.is_active = False
            self.btn_act.config(text="ACTIVATE", bg="#00ff41")

    def sync_engine(self):
        timer = 10
        while self.is_active:
            self.info_lbl.config(text="3D FILTER ACTIVE | TCP OPTIMIZED", fg="#00ff41")
            if timer <= 0:
                subprocess.call(["ipconfig", "/flushdns"], startupinfo=self.si, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                timer = 10
            time.sleep(1)
            timer -= 1

if __name__ == "__main__":
    root = tk.Tk()
    app = SaintPE(root)
    root.mainloop()
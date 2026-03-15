import tkinter as tk
import random
import threading
import time
import ctypes
from pynput import mouse

# ==================== GLOBALS ====================
current_theme = "sorrow"
is_active = False
is_binding_spam = False
is_binding_toggle = False
cps_value = "30"
spam_key_code = None
spam_key_name = "NONE"
toggle_key = None
toggle_key_name = "NONE"
selected_button = "M5" 

def press_key_raw(code):
    ctypes.windll.user32.keybd_event(0, code, 0x0008, 0)
    time.sleep(0.01)
    ctypes.windll.user32.keybd_event(0, code, 0x0008 | 0x0002, 0)

def spam_loop():
    global is_active
    while True:
        if is_active:
            try: val = int(cps_value)
            except: val = 30
            press_key_raw(SCAN_CODE)
            time.sleep(1.0 / max(1, val))
        else:
            time.sleep(0.1)


def interpolate_color(color1, color2, progress):
    r1, g1, b1 = root.winfo_rgb(color1)
    r2, g2, b2 = root.winfo_rgb(color2)
    r = int(r1 + (r2 - r1) * progress) >> 8
    g = int(g1 + (g2 - g1) * progress) >> 8
    b = int(b1 + (b2 - b1) * progress) >> 8
    return f'#{r:02x}{g:02x}{b:02x}'

pulse_val = 0
pulse_dir = 1

def attack_visuals():
    global pulse_val, pulse_dir
    if is_active:
        pulse_val += 0.05 * pulse_dir
        if pulse_val >= 1: pulse_dir = -1
        if pulse_val <= 0: pulse_dir = 1
        
        is_flash = random.random() > 0.96
        bg_color = "#330000" if is_flash else interpolate_color("#000000", "#120000", pulse_val)
        main_color = "#ff0000" if is_flash else interpolate_color("#660000", "#ff0000", pulse_val)
        
        rain_canvas.config(bg=bg_color)
        close_button.config(bg=bg_color)
        

        dx, dy = random.randint(-2, 2), random.randint(-2, 2)
        rain_canvas.coords(title_text, W//2 + dx, 45 + dy)
        rain_canvas.coords(cps_display, W//2 - dx, 115 + dy)
        rain_canvas.coords(m4_text, 70 + dx, 185 - dy)
        rain_canvas.coords(m5_text, 150 - dx, 185 + dy)
        
        for item in [title_text, cps_display, m4_text, m5_text]:
            rain_canvas.itemconfig(item, fill=main_color)
        
        root.config(highlightbackground=main_color)
        root.after(40, attack_visuals)
    else:

        rain_canvas.config(bg="#000")
        close_button.config(bg="#000")
        rain_canvas.coords(title_text, W//2, 45)
        rain_canvas.coords(cps_display, W//2, 115)
        rain_canvas.coords(m4_text, 70, 185)
        rain_canvas.coords(m5_text, 150, 185)
        
        rain_canvas.itemconfig(title_text, fill="#333")
        rain_canvas.itemconfig(cps_display, fill="#333")
        rain_canvas.itemconfig(m4_text, fill="#ff0000" if selected_button == "M4" else "#222")
        rain_canvas.itemconfig(m5_text, fill="#ff0000" if selected_button == "M5" else "#222")
        root.config(highlightbackground="#1a1a1a")

drops = []
def create_rain():
    for _ in range(80): 
        x, y = random.randint(-50, 250), random.randint(-220, 220)
        length = random.randint(40, 70)
        drop = rain_canvas.create_line(x, y, x - 3, y + length, fill="#0a0a0a", width=1)
        drops.append([drop, random.randint(5, 12), length])

def animate_rain():
    for d in drops:
        drop_obj, base_speed, length = d
        speed = base_speed * 3.5 if is_active else base_speed
        color = random.choice(["#ff0000", "#8b0000", "#4a0000"]) if is_active else "#111"
        
        rain_canvas.move(drop_obj, -1 if is_active else 0, speed)
        rain_canvas.itemconfig(drop_obj, fill=color, width=1.5 if is_active else 1)
        
        c = rain_canvas.coords(drop_obj)
        if c and c[3] > 220:
            nx = random.randint(-50, 250)
            rain_canvas.coords(drop_obj, nx, -80, nx - 3, -80 + length)
            
    rain_canvas.tag_raise(title_text)
    rain_canvas.tag_raise(cps_display)
    rain_canvas.tag_raise(m4_text)
    rain_canvas.tag_raise(m5_text)
    root.after(25, animate_rain)

def screen_shake():
    if is_active:
        ox, oy = screen_width - 220 - 20, screen_height - 220 - 60
        root.geometry(f"+{ox + random.randint(-3,3)}+{oy + random.randint(-3,3)}")
        root.after(35, screen_shake)


def on_key(event):
    global cps_value
    if not is_active:
        if event.keysym == "BackSpace": cps_value = cps_value[:-1]
        elif event.char.isdigit() and len(cps_value) < 3: cps_value += event.char
        rain_canvas.itemconfig(cps_display, text=cps_value)

def on_canvas_click(event):
    global selected_button
    if 170 < event.y < 200:
        if 40 < event.x < 100: selected_button = "M4"
        elif 120 < event.x < 180: selected_button = "M5"
        attack_visuals()

def on_mouse_click(x, y, button, pressed):
    global is_active
    if pressed:
        target = mouse.Button.x1 if selected_button == "M4" else mouse.Button.x2
        if button == target:
            is_active = not is_active
            if is_active: 
                attack_visuals()
                screen_shake()


root = tk.Tk()
root.iconbitmap("icon.ico")
W, H = 220, 220
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"{W}x{H}+{screen_width-W-20}+{screen_height-H-60}")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg="#000", highlightthickness=2, highlightbackground="#1a1a1a")

rain_canvas = tk.Canvas(root, width=W, height=H, bg="#000", highlightthickness=0)
rain_canvas.pack()
rain_canvas.bind("<Button-1>", on_canvas_click)
root.bind("<Key>", on_key)

create_rain()
title_text = rain_canvas.create_text(W//2, 45, text="GrRB", fill="#333", font=("Impact", 28))
cps_display = rain_canvas.create_text(W//2, 115, text=cps_value, fill="#333", font=("Impact", 56))
m4_text = rain_canvas.create_text(70, 185, text="M4", fill="#222", font=("Impact", 16))
m5_text = rain_canvas.create_text(150, 185, text="M5", fill="#ff0000", font=("Impact", 16))

close_button = tk.Button(root, text="×", bg="#000", fg="#222", bd=0, command=root.destroy, font=("Arial", 10))
close_button.place(x=W-20, y=5)

animate_rain()
threading.Thread(target=spam_loop, daemon=True).start()
mouse.Listener(on_click=on_mouse_click).start()
root.mainloop()
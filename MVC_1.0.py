import cv2
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
# Risoluzioni comuni ordinate dalla più grande alla più piccola
COMMON_RESOLUTIONS = [
    (3840, 2160),  # 4K
    (2560, 1440),
    (1920, 1080),
    (1280, 800),
    (1280, 720),
    (1024, 768),
    (800, 600),
    (640, 480)
]
preview_threads = []
preview_stop_event = threading.Event()
webcam_configs = []
threads = []
stop_event = threading.Event()
# ---------------- PREVIEW WEBCAM ----------------
def preview_webcam(cam, preview_label):
    ret, frame = cam.read()
    if not ret:
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (240, 180))
    img = ImageTk.PhotoImage(Image.fromarray(frame))

    preview_label.imgtk = img
    preview_label.configure(image=img)

    preview_label.after(30, lambda: preview_webcam(cam, preview_label))

# ---------------- AVVIO ANTEPRIMA ----------------
preview_cams = []

def start_preview():
    preview_cams.clear()

    for entries, preview in webcam_configs:
        try:
            cam_index = int(entries["cam_index"].get())
        except ValueError:
            continue

        cam = cv2.VideoCapture(cam_index)
        if cam.isOpened():
            preview_cams.append(cam)
            preview_webcam(cam, preview)

# ---------------- STOP ANTEPRIMA ANTEPRIMA ----------------
def stop_preview():
    for cam in preview_cams:
        cam.release()
    preview_cams.clear()

# ---------------- MAX RESOLUTION FUNCTION ----------------
def set_max_resolution(cam):
    """
    Imposta automaticamente la massima risoluzione supportata dalla webcam
    """
    for width, height in COMMON_RESOLUTIONS:
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        time.sleep(0.2)

        actual_w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if actual_w == width and actual_h == height:
            print(f"Risoluzione impostata: {actual_w}x{actual_h}")
            return actual_w, actual_h

    # fallback finale
    w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Risoluzione fallback: {w}x{h}")
    return w, h


# ---------------- CAPTURE FUNCTION ----------------
def capture_webcam(cfg, preview_label):
    cam = cv2.VideoCapture(cfg["cam_index"])
    # imposta automaticamente la massima risoluzione
    max_w, max_h = set_max_resolution(cam)
    print(f"Webcam {cfg['cam_index']} → {max_w}x{max_h}")
    if not cam.isOpened():
        messagebox.showerror("Errore", f"Webcam {cfg['cam_index']} non disponibile")
        return
    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Risoluzione webcam {cfg['cam_index']}: {int(width)}x{int(height)}")


    time.sleep(2)
    start_time = time.time()
    count = 1

    os.makedirs(cfg["folder"], exist_ok=True)

    while not stop_event.is_set():
        if time.time() - start_time >= cfg["duration"]:
            break

        ret, frame = cam.read()
        if not ret or frame is None:
            break

        filename = os.path.join(
            cfg["folder"],
            f"{cfg['base_name']}_{count}.jpg"
        )
        cv2.imwrite(filename, frame)
        count += 1

        # preview
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (240, 180))
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        preview_label.imgtk = img
        preview_label.configure(image=img)

        for _ in range(cfg["interval"]):
            if stop_event.is_set():
                break
            time.sleep(1)

    cam.release()

# ---------------- GUI LOGIC ----------------
def build_webcam_inputs():
    for widget in cams_frame.winfo_children():
        widget.destroy()

    webcam_configs.clear()

    try:
        num = int(num_cams_entry.get())
    except ValueError:
        return

    for i in range(num):
        frame = ttk.LabelFrame(cams_frame, text=f"Webcam {i}")
        frame.grid(row=i//4, column=i%4, padx=10, pady=10, sticky="n")

        entries = {}

        labels = [
            ("Indice webcam", "cam_index"),
            ("Intervallo (sec)", "interval"),
            ("Durata (min)", "duration"),
            ("Cartella", "folder"),
            ("Nome immagini", "base_name")
        ]

        for lbl, key in labels:
            ttk.Label(frame, text=lbl).pack()
            e = ttk.Entry(frame)
            e.pack()
            entries[key] = e

        preview = ttk.Label(frame)
        preview.pack(pady=5)

        webcam_configs.append((entries, preview))

def start_all():
    stop_event.clear()
    threads.clear()

    for entries, preview in webcam_configs:
        try:
            cfg = {
                "cam_index": int(entries["cam_index"].get()),
                "interval": int(entries["interval"].get()),
                "duration": int(entries["duration"].get()) * 60,
                "folder": entries["folder"].get(),
                "base_name": entries["base_name"].get()
            }
        except ValueError:
            messagebox.showerror("Errore", "Valori non validi")
            return

        t = threading.Thread(
            target=capture_webcam,
            args=(cfg, preview),
            daemon=True
        )
        threads.append(t)
        t.start()

def stop_all():
    stop_event.set()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Multi Webcam Capture - Fabio Guida")
root.geometry("640x480")

# Icona app
try:
    root.iconbitmap("icon.ico")
except:
    pass

style = ttk.Style()
style.theme_use("default")

# -------- HEADER --------
header = ttk.Frame(root)
header.pack(fill="x", pady=15)

title_label = tk.Label(
    header,
    text="🎥 Multi Webcam Capture System",
    font=("Segoe UI", 22, "bold"),
    fg="#1F4E79",      # blu corporate
    bg=root["bg"]
)
title_label.pack()

subtitle = tk.Label(
    header,
    text="Professional Multi-Camera Acquisition Platform",
    font=("Segoe UI", 10),
    fg="#4F4F4F",
    bg=root["bg"]
)
subtitle.pack()

line = tk.Frame(header, height=2, bg="#1F4E79")
line.pack(fill="x", padx=300, pady=8)


# -------- CONFIG --------
config_frame = ttk.LabelFrame(root, text="Configurazione")
config_frame.pack(fill="x", padx=15, pady=10)

ttk.Label(config_frame, text="Numero di webcam da usare:").pack(anchor="w", padx=10, pady=2)
num_cams_entry = ttk.Entry(config_frame)
num_cams_entry.pack(anchor="w", padx=10)

ttk.Button(
    config_frame,
    text="Configura webcam",
    command=build_webcam_inputs
).pack(pady=10)

# -------- WEBCAMS --------
# cams_frame = ttk.Frame(root)
# cams_frame.pack(fill="both", expand=True, padx=10)
# -------- SCROLL AREA WEBCAMS --------
# -------- SCROLL AREA WEBCAMS --------
container = ttk.Frame(root)
container.pack(fill="both", expand=True, padx=10, pady=5)

canvas = tk.Canvas(container, highlightthickness=0)

v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)

cams_frame = ttk.Frame(canvas)

cams_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=cams_frame, anchor="nw")
canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

canvas.grid(row=0, column=0, sticky="nsew")
v_scrollbar.grid(row=0, column=1, sticky="ns")
h_scrollbar.grid(row=1, column=0, sticky="ew")

container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Mousewheel
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)


# -------- CONTROLS --------
controls = ttk.Frame(root)
controls.pack(pady=15)
ttk.Button(
    controls,
    text="👁 ATTIVA ANTEPRIMA",
    command=start_preview
).grid(row=1, column=0, padx=20, pady=10)

ttk.Button(
    controls,
    text="🛑 STOP ANTEPRIMA",
    command=stop_preview
).grid(row=1, column=1, padx=20, pady=10)

ttk.Button(
    controls,
    text="▶ AVVIA TUTTE",
    command=start_all
).grid(row=0, column=0, padx=20)

ttk.Button(
    controls,
    text="⏹ STOP TUTTE",
    command=stop_all
).grid(row=0, column=1, padx=20)

# -------- FOOTER --------
footer = ttk.Frame(root)
footer.pack(side="bottom", fill="x")

creator_label = ttk.Label(
    footer,
    text="Developed by Fabio Guida © 2026",
    anchor="center",
    font=("Segoe UI", 9)
)
creator_label.pack(pady=5)

root.mainloop()

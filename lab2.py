import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
from PIL import ImageDraw

original_img = None
processed_img = None

root = tk.Tk()
root.title("Лаба 2")
root.geometry("900x700")
root.state('zoomed')

def load_image():
    global original_img
    path = filedialog.askopenfilename()
    if not path:
        return
    original_img = Image.open(path).convert("RGB")
    display_img = original_img.copy()
    display_img.thumbnail((550, 550))
    tk_img = ImageTk.PhotoImage(display_img)
    original_canvas.image = tk_img
    original_canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

def process_image():
    global processed_img
    try:
        new_width = int(width_entry.get())
        new_height = int(height_entry.get())
    except ValueError:
        return

    resized = original_img.resize((new_width, new_height))

    points_math = [(3, 3), (-3, -3), (6, 0), (0, -6)]

    cx = new_width / 2
    cy = new_height / 2
    points_px = []
    for x, y in points_math:
        px = cx + (x / 10) * (new_width / 2)
        py = cy - (y / 10) * (new_height / 2)
        points_px.append((px, py))

    poly_cx = sum(p[0] for p in points_px) / 4
    poly_cy = sum(p[1] for p in points_px) / 4
    points_px.sort(key=lambda p: math.atan2(p[1] - poly_cy, p[0] - poly_cx))

    def point_in_polygon(x, y, poly):
        inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if (yi > y) != (yj > y):
                x_intersect = (xj - xi) * (y - yi) / (yj - yi) + xi
                if x < x_intersect:
                    inside = not inside
            j = i
        return inside

    processed_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    for y in range(new_height):
        for x in range(new_width):
            if point_in_polygon(x, y, points_px):
                processed_img.putpixel((x, y), resized.getpixel((x, y)))
                
    draw = ImageDraw.Draw(processed_img)

    def to_px(x, y):
        px = cx + (x / 10) * (new_width / 2)
        py = cy - (y / 10) * (new_height / 2)
        return (px, py)

    draw.line([to_px(-10, 0), to_px(10, 0)], fill=(0, 0, 0), width=2)
    draw.line([to_px(0, -10), to_px(0, 10)], fill=(0, 0, 0), width=2)

    graph_points = []
    x = -10
    while x <= 10:
        y = math.cos(x) * 3
        graph_points.append(to_px(x, y))
        x += 0.05

    draw.line(graph_points, fill=(255, 0, 0), width=2)

    display_img = processed_img.copy()
    display_img.thumbnail((550, 550))
    tk_img = ImageTk.PhotoImage(display_img)
    processed_canvas.image = tk_img
    processed_canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

def save_bmp():
    path = filedialog.asksaveasfilename(defaultextension=".bmp")
    if not path:
        return
    processed_img.save(path)

def save_pbm():
    path = filedialog.asksaveasfilename(defaultextension=".pbm")
    if not path:
        return
    width, height = processed_img.size
    with open(path, "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = processed_img.getpixel((x, y))
                row.append(f"{r} {g} {b}")
            f.write(" ".join(row) + "\n")

top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, pady=10)

left_frame = tk.Frame(top_frame)
left_frame.pack(side=tk.LEFT, padx=20)

center_frame = tk.Frame(top_frame)
center_frame.pack(side=tk.LEFT, padx=20)

right_frame = tk.Frame(top_frame)
right_frame.pack(side=tk.LEFT, padx=20)

tk.Button(left_frame, text="Открыть", command=load_image, width=20).pack(pady=5)
tk.Button(left_frame, text="Обработать", command=process_image, width=20).pack(pady=5)

tk.Label(center_frame, text="Ширина:").pack()
width_entry = tk.Entry(center_frame)
width_entry.pack(pady=5)

tk.Label(center_frame, text="Высота:").pack()
height_entry = tk.Entry(center_frame)
height_entry.pack(pady=5)

tk.Button(right_frame, text="Сохранить в BMP", command=save_bmp, width=20).pack(pady=5)
tk.Button(right_frame, text="Сохранить в PBM", command=save_pbm, width=20).pack(pady=5)

canvas_frame = tk.Frame(root)
canvas_frame.pack()

original_canvas = tk.Canvas(canvas_frame, width=550, height=550, bg="gray", highlightthickness=0, bd=0)
original_canvas.pack(side=tk.LEFT, padx=10)
processed_canvas = tk.Canvas(canvas_frame, width=550, height=550, bg="gray", highlightthickness=0, bd=0)
processed_canvas.pack(side=tk.LEFT, padx=10)

root.mainloop()
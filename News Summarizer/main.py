import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser

from fetch_news import fetch_multiple_sources, PERSIAN_SOURCES, ENGLISH_SOURCES
from summarizer import summarize_text

source_vars = {}
link_map = {}

# Theme 
BG = "#1e293b"       
CARD_BG = "#334155"   
FG = "#f8fafc"
ACCENT = "#38bdf8"
MUTED = "#94a3b8"

FONT_MAIN = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")

def center_window(win, width, height):
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def update_sources():
    for w in sources_frame.winfo_children():
        w.destroy()
    source_vars.clear()
    
    sources = PERSIAN_SOURCES if lang_var.get() == "fa" else ENGLISH_SOURCES
    for key, name in sources.items():
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(sources_frame, text=name, variable=var, 
                           bg=CARD_BG, fg=FG, selectcolor=BG, font=FONT_MAIN)
        cb.pack(anchor="w", padx=10)
        source_vars[key] = var

def open_link_label(event):
    idx = text_box.index(f"@{event.x},{event.y}")
    for (start, end), url in link_map.items():
        if text_box.compare(start, "<=", idx) and text_box.compare(idx, "<", end):
            webbrowser.open_new_tab(url)
            break

def fetch_and_show():
    selected = [k for k, v in source_vars.items() if v.get()]
    if not selected:
        messagebox.showwarning("خطا", "لطفاً حداقل یک منبع انتخاب کنید.")
        return

    try:
        n = int(entry_count.get())
    except:
        n = 5

    fetch_btn.config(state="disabled", text="در حال دریافت...")
    window.update()

    articles = fetch_multiple_sources(selected)
    
    text_box.config(state="normal")
    text_box.delete("1.0", tk.END)
    link_map.clear()

    if not articles:
        text_box.insert(tk.END, "هیچ خبری یافت نشد.")
    else:
        for art in articles[:n]:
            text_box.insert(tk.END, f"📰 {art['title']}\n", "title")
            if art.get("pub_date"):
                text_box.insert(tk.END, f"📅 {art['pub_date'].strftime('%Y-%m-%d %H:%M')}\n", "date")
            
            summary = summarize_text(art.get("description", ""), 2)
            text_box.insert(tk.END, f"📄 خلاصه: {summary}\n")
            
            start = text_box.index(tk.INSERT)
            text_box.insert(tk.END, "🔗 جزئیات بیشتر", "link_click")
            end = text_box.index(tk.INSERT)
            link_map[(start, end)] = art['link']
            text_box.insert(tk.END, "\n\n" + "-"*50 + "\n\n")

    text_box.config(state="disabled")
    fetch_btn.config(state="normal", text="دریافت و خلاصه‌سازی")

# window
window = tk.Tk()
window.title("News Summarizer")
window.configure(bg=BG)
center_window(window, 820, 720)

# controls
controls = tk.Frame(window, bg=CARD_BG, pady=10)
controls.pack(fill="x", padx=20, pady=20)

lang_var = tk.StringVar(value="fa")
tk.Radiobutton(controls, text="فارسی", variable=lang_var, value="fa", command=update_sources, bg=CARD_BG, fg=FG, selectcolor=BG).pack()
tk.Radiobutton(controls, text="English", variable=lang_var, value="en", command=update_sources, bg=CARD_BG, fg=FG, selectcolor=BG).pack()

sources_frame = tk.Frame(controls, bg=CARD_BG)
sources_frame.pack()

entry_count = tk.Entry(controls, width=10)
entry_count.insert(0, "5")
entry_count.pack(pady=5)

fetch_btn = tk.Button(controls, text="دریافت و خلاصه‌سازی", command=fetch_and_show, bg=ACCENT)
fetch_btn.pack(pady=10)

# output
text_box = scrolledtext.ScrolledText(window, bg=BG, fg=FG, font=FONT_MAIN, state="disabled")
text_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
text_box.tag_config("link_click", foreground=ACCENT, underline=True)
text_box.tag_bind("link_click", "<Button-1>", open_link_label)

update_sources()
window.mainloop()
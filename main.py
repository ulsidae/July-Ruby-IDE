import tkinter as tk
from tkinter import filedialog, font
import subprocess
import os


class RubyIDLE:
    def __init__(self, root):
        self.root = root
        self.root.title("July Ruby IDE - by ulsidae")
        self.root.geometry("800x600")

        # 1. button
        btn_frame = tk.Frame(root, bg="#eee")
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="▶ Run", command=self.run_ruby, fg="green").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Load", command=self.load_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Font+", command=lambda: self.change_font(1)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text="Font-", command=lambda: self.change_font(-1)).pack(side=tk.LEFT, padx=5, pady=5)

        # 2. main editor
        self.editor_font = font.Font(family="MS Gothic", size=12)
        self.editor = tk.Text(root, bg="#2d2d2d", fg="white",
                              insertbackground="white",
                              font=self.editor_font,
                              undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind('<KeyRelease>', self.show_suggestions)

        # 3. simple code suggestion
        self.suggestions = ["puts", "gets", "if","elsif","else", "end", "def", "class", "require", "times", "loop do"]
        self.suggestion_list = tk.Listbox(root, height=5, width=15, font=("MS Gothic", 12))
        self.suggestion_list.bind('<Double-Button-1>', self.insert_suggestion)

    def show_suggestions(self, event):
        try:
            x, y, _, height = self.editor.bbox("insert")
            word = self.editor.get("insert-1c wordstart", "insert")
            matches = [s for s in self.suggestions if s.startswith(word)]

            if matches and word:
                self.suggestion_list.delete(0, tk.END)
                for m in matches: self.suggestion_list.insert(tk.END, m)
                self.suggestion_list.place(x=self.editor.winfo_x() + x, y=self.editor.winfo_y() + y + height)
            else:
                self.suggestion_list.place_forget()
        except:
            pass

    def insert_suggestion(self, event):
        word = self.suggestion_list.get(self.suggestion_list.curselection())
        self.editor.insert(tk.INSERT, word[len(self.editor.get("insert-1c wordstart", "insert")):])
        self.suggestion_list.place_forget()

    def change_font(self, delta):
        size = self.editor_font.cget("size")
        self.editor_font.configure(size=max(8, size + delta))

    def run_ruby(self):
        # temporary file-save
        code = self.editor.get("1.0", tk.END)
        with open("temp.rb", "w", encoding="utf-8") as f:
            f.write(code)

        # execute by running cmd
        os.system('start cmd /k "ruby temp.rb && pause"')

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".rb", filetypes=[("Ruby files", "*.rb")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Ruby files", "*.rb")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, f.read())


root = tk.Tk()
RubyIDLE(root)
root.mainloop()

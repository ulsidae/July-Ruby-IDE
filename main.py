import tkinter as tk
from tkinter import filedialog, font
import subprocess
import tempfile
import os
import shutil
import glob
import re
import threading
import queue


class RubyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("July Ruby IDE - by ulsidae")
        self.root.geometry("1100x750")
        self.root.minsize(800, 500)

        self.ruby_path = self.find_ruby_path()

        self.ruby_process = None
        self.process_thread = None
        self.output_queue = queue.Queue()
        self.temp_path = None

        self.ruby_keywords = {
            "def", "class", "module",
            "if", "elsif", "else", "unless",
            "case", "when", "then",
            "while", "until", "for", "in",
            "do", "end",
            "return", "yield",
            "break", "next", "redo", "retry",
            "begin", "rescue", "ensure", "raise",
            "super", "self",
            "nil", "true", "false",
            "and", "or", "not"
        }

        self.ruby_oop = {
            "initialize",
            "attr_reader", "attr_writer", "attr_accessor",
            "public", "private", "protected",
            "include", "extend", "prepend"
        }

        self.ruby_io = {
            "puts", "print", "p",
            "gets", "chomp",
            "format", "sprintf"
        }

        self.ruby_enumerable = {
            "each",
            "each_with_index",
            "each_with_object",
            "map",
            "collect",
            "select",
            "filter",
            "reject",
            "find",
            "find_all",
            "reduce",
            "inject",
            "any?",
            "all?",
            "none?",
            "one?",
            "count",
            "first",
            "take",
            "drop",
            "sort",
            "sort_by",
            "group_by",
            "flat_map",
            "zip"
        }

        self.ruby_string = {
            "length", "size", "empty?",
            "include?",
            "split", "join", "strip",
            "start_with?", "end_with?",
            "upcase", "downcase", "capitalize",
            "replace", "sub", "gsub",
            "chars", "bytes"
        }

        self.ruby_array = {
            "push", "pop",
            "shift", "unshift",
            "slice", "concat",
            "reverse", "reverse!",
            "uniq", "uniq!",
            "compact", "compact!",
            "flatten", "flatten!",
            "index", "rindex",
            "first", "last"
        }

        self.ruby_hash = {
            "keys", "values",
            "fetch",
            "has_key?", "key?", "value?",
            "merge", "merge!",
            "delete",
            "each_key", "each_value", "each_pair"
        }

        self.ruby_numeric = {
            "times",
            "upto",
            "downto",
            "step",
            "even?",
            "odd?",
            "zero?",
            "positive?",
            "negative?",
            "abs",
            "round",
            "floor",
            "ceil"
        }

        self.ruby_conversion = {
            "to_i",
            "to_s",
            "to_a"
        }

        self.ruby_proc = {
            "Proc",
            "lambda",
            "proc",
            "call"
        }

        self.ruby_misc = {
            "require",
            "require_relative",
            "load",
            "loop",
            "defined?"
        }

        self.suggestions = sorted(
            self.ruby_keywords
            | self.ruby_oop
            | self.ruby_io
            | self.ruby_enumerable
            | self.ruby_string
            | self.ruby_array
            | self.ruby_hash
            | self.ruby_numeric
            | self.ruby_conversion
            | self.ruby_proc
            | self.ruby_misc
        )

        btn_frame = tk.Frame(root, bg="#252526")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.run_button = tk.Button(
            btn_frame,
            text="▶ Run",
            command=self.run_ruby,
            bg="#333333",
            fg="#4EC9B0",
            relief=tk.FLAT
        )
        self.run_button.pack(side=tk.LEFT, padx=2)

        self.stop_button = tk.Button(
            btn_frame,
            text="■ Stop",
            command=self.stop_ruby,
            bg="#333333",
            fg="#F44747",
            relief=tk.FLAT
        )
        self.stop_button.pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Save",
            command=self.save_file,
            bg="#333333",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Load",
            command=self.load_file,
            bg="#333333",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Font+",
            command=lambda: self.change_font(1),
            bg="#333333",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Font-",
            command=lambda: self.change_font(-1),
            bg="#333333",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="TermFont+",
            command=lambda: self.change_terminal_font(1),
            bg="#333333",
            fg="#ce9178",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame,
            text="TermFont-",
            command=lambda: self.change_terminal_font(-1),
            bg="#333333",
            fg="#ce9178",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Detach Terminal",
            command=self.detach_terminal,
            bg="#333333",
            fg="#dcdcaa",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=8)

        self.status_label = tk.Label(
            btn_frame,
            text=f"Ruby: {self.ruby_path} | Ready",
            bg="#252526",
            fg="#858585",
            font=("Consolas", 9)
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)

        self.pane = tk.PanedWindow(
            root,
            orient=tk.VERTICAL,
            bg="#3f3f46",
            sashwidth=6,
            bd=0
        )
        self.pane.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )

        self.editor_font = font.Font(
            family="Consolas",
            size=12
        )

        self.editor = tk.Text(
            self.pane,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            font=self.editor_font,
            undo=True,
            wrap=tk.NONE
        )

        self.pane.add(
            self.editor,
            minsize=200
        )

        self.editor.tag_configure(
            "keyword",
            foreground="#569CD6"
        )

        self.editor.tag_configure(
            "oop",
            foreground="#C586C0"
        )

        self.editor.tag_configure(
            "io",
            foreground="#4EC9B0"
        )

        self.editor.tag_configure(
            "enumerable",
            foreground="#DCDCAA"
        )

        self.editor.tag_configure(
            "string_method",
            foreground="#CE9178"
        )

        self.editor.tag_configure(
            "array_method",
            foreground="#9CDCFE"
        )

        self.editor.tag_configure(
            "hash_method",
            foreground="#4FC1FF"
        )

        self.editor.tag_configure(
            "numeric",
            foreground="#B5CEA8"
        )

        self.editor.tag_configure(
            "conversion",
            foreground="#D7BA7D"
        )

        self.editor.tag_configure(
            "proc",
            foreground="#C586C0"
        )

        self.editor.tag_configure(
            "misc",
            foreground="#4EC9B0"
        )

        self.editor.tag_configure(
            "string",
            foreground="#CE9178"
        )

        self.editor.tag_configure(
            "comment",
            foreground="#6A9955"
        )

        self.editor.tag_configure(
            "number",
            foreground="#B5CEA8"
        )

        self.editor.tag_configure(
            "constant",
            foreground="#4FC1FF"
        )

        self.editor.bind(
            "<KeyRelease>",
            self.handle_key_release
        )

        self.editor.bind(
            "<Tab>",
            self.handle_tab
        )

        self.editor.bind(
            "<Down>",
            self.handle_editor_arrow
        )

        self.editor.bind(
            "<Up>",
            self.handle_editor_arrow
        )

        terminal_frame = tk.Frame(
            self.pane,
            bg="#111111"
        )

        terminal_frame.grid_rowconfigure(
            0,
            weight=1
        )

        terminal_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.terminal_font = font.Font(
            family="Consolas",
            size=10
        )

        self.terminal = tk.Text(
            terminal_frame,
            bg="#111111",
            fg="#00ff00",
            insertbackground="white",
            font=self.terminal_font,
            state=tk.DISABLED,
            wrap=tk.NONE
        )

        self.terminal.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.input_frame = tk.Frame(
            terminal_frame,
            bg="#181818"
        )

        self.input_frame.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.input_frame.grid_columnconfigure(
            1,
            weight=1
        )

        tk.Label(
            self.input_frame,
            text=">",
            bg="#181818",
            fg="#4EC9B0",
            font=self.terminal_font
        ).grid(
            row=0,
            column=0,
            padx=(8, 4),
            pady=6
        )

        self.input_entry = tk.Entry(
            self.input_frame,
            bg="#181818",
            fg="#d4d4d4",
            insertbackground="white",
            relief=tk.FLAT,
            font=self.terminal_font
        )

        self.input_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 8),
            pady=6
        )

        self.input_entry.bind(
            "<Return>",
            self.send_input
        )

        self.pane.add(
            terminal_frame,
            minsize=100
        )

        self.terminal_frame = terminal_frame

        self.pane.sash_place(
            0,
            0,
            450
        )

        self.terminal_window = None
        self.detached_terminal = None
        self.detached_input_entry = None

        self.suggestion_list = tk.Listbox(
            root,
            height=8,
            width=25,
            font=("Consolas", 11),
            bg="#252526",
            fg="white",
            selectbackground="#37373d",
            relief=tk.FLAT,
            borderwidth=0
        )

        self.suggestion_list.bind(
            "<Double-Button-1>",
            self.insert_suggestion
        )

        self.suggestion_list.bind(
            "<Return>",
            self.insert_suggestion
        )

        self.root.after(
            50,
            self.process_output_queue
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

    def find_ruby_path(self):
        ruby = shutil.which("ruby")

        if ruby:
            return ruby

        pattern = r"C:\Ruby*\bin\ruby.exe"
        matches = glob.glob(pattern)

        if matches:
            return matches[0]

        common_paths = [
            r"C:\Ruby40-x64\bin\ruby.exe",
            r"C:\Ruby33-x64\bin\ruby.exe",
            r"C:\Ruby32-x64\bin\ruby.exe",
            r"C:\Ruby31-x64\bin\ruby.exe",
            r"C:\Ruby30-x64\bin\ruby.exe",
            r"C:\Ruby27-x64\bin\ruby.exe",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return "ruby"

    def highlight_syntax(self):
        code = self.editor.get("1.0", tk.END)

        tags = [
            "keyword",
            "oop",
            "io",
            "enumerable",
            "string_method",
            "array_method",
            "hash_method",
            "numeric",
            "conversion",
            "proc",
            "misc",
            "string",
            "comment",
            "number",
            "constant"
        ]

        for tag in tags:
            self.editor.tag_remove(
                tag,
                "1.0",
                tk.END
            )

        self.apply_regex_tag(
            r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
            "string"
        )

        self.apply_regex_tag(
            r"#.*",
            "comment"
        )

        self.apply_regex_tag(
            r"\b(?:0x[0-9a-fA-F]+|\d+(?:\.\d+)?)\b",
            "number"
        )

        categories = [
            (self.ruby_keywords, "keyword"),
            (self.ruby_oop, "oop"),
            (self.ruby_io, "io"),
            (self.ruby_enumerable, "enumerable"),
            (self.ruby_string, "string_method"),
            (self.ruby_array, "array_method"),
            (self.ruby_hash, "hash_method"),
            (self.ruby_numeric, "numeric"),
            (self.ruby_conversion, "conversion"),
            (self.ruby_proc, "proc"),
            (self.ruby_misc, "misc")
        ]

        for words, tag in categories:
            for word in words:
                pattern = (
                    r"(?<![\w?])"
                    + re.escape(word)
                    + r"(?![\w?])"
                )

                self.apply_regex_tag(
                    pattern,
                    tag
                )

        self.apply_regex_tag(
            r"\b[A-Z][A-Za-z0-9_]*\b",
            "constant"
        )

    def apply_regex_tag(self, pattern, tag):
        code = self.editor.get("1.0", tk.END)

        for match in re.finditer(
            pattern,
            code
        ):
            start = "1.0 + %dc" % match.start()
            end = "1.0 + %dc" % match.end()

            self.editor.tag_add(
                tag,
                start,
                end
            )

    def handle_key_release(self, event):
        if event.keysym in (
            "Up",
            "Down",
            "Left",
            "Right",
            "Return",
            "Tab",
            "Shift_L",
            "Shift_R"
        ):
            return

        self.highlight_syntax()
        self.show_suggestions()

    def show_suggestions(self):
        try:
            word = self.editor.get(
                "insert-1c wordstart",
                "insert"
            )

            if not word or not word.strip():
                self.suggestion_list.place_forget()
                return

            matches = [
                s for s in self.suggestions
                if s.startswith(word)
            ]

            if matches:
                bbox = self.editor.bbox("insert")

                if not bbox:
                    return

                x, y, _, height = bbox

                self.suggestion_list.delete(
                    0,
                    tk.END
                )

                for match in matches:
                    self.suggestion_list.insert(
                        tk.END,
                        match
                    )

                self.suggestion_list.selection_set(0)

                self.suggestion_list.place(
                    x=self.editor.winfo_x() + x,
                    y=self.editor.winfo_y() + y + height
                )

            else:
                self.suggestion_list.place_forget()

        except Exception:
            self.suggestion_list.place_forget()

    def handle_editor_arrow(self, event):
        if self.suggestion_list.winfo_ismapped():
            try:
                current_selection = (
                    self.suggestion_list.curselection()
                )

                index = (
                    current_selection[0]
                    if current_selection
                    else 0
                )

                if event.keysym == "Down":
                    index = min(
                        index + 1,
                        self.suggestion_list.size() - 1
                    )

                elif event.keysym == "Up":
                    index = max(
                        index - 1,
                        0
                    )

                self.suggestion_list.selection_clear(
                    0,
                    tk.END
                )

                self.suggestion_list.selection_set(
                    index
                )

                self.suggestion_list.see(index)

                return "break"

            except Exception:
                pass

    def handle_tab(self, event):
        if self.suggestion_list.winfo_ismapped():
            self.insert_suggestion()
            return "break"

        self.editor.insert(
            tk.INSERT,
            "  "
        )

        return "break"

    def insert_suggestion(self, event=None):
        try:
            selection = (
                self.suggestion_list.curselection()
            )

            if not selection:
                return

            word = self.suggestion_list.get(
                selection[0]
            )

            current_word = self.editor.get(
                "insert-1c wordstart",
                "insert"
            )

            self.editor.insert(
                tk.INSERT,
                word[len(current_word):]
            )

            self.suggestion_list.place_forget()
            self.editor.focus()
            self.highlight_syntax()

        except Exception:
            pass

    def change_font(self, delta):
        size = self.editor_font.cget("size")

        self.editor_font.configure(
            size=max(8, size + delta)
        )

    def change_terminal_font(self, delta):
        size = self.terminal_font.cget("size")

        self.terminal_font.configure(
            size=max(6, size + delta)
        )

    def append_terminal(self, text):
        self.terminal.config(
            state=tk.NORMAL
        )

        self.terminal.insert(
            tk.END,
            text
        )

        self.terminal.see(
            tk.END
        )

        self.terminal.config(
            state=tk.DISABLED
        )

        if (
            self.detached_terminal is not None
            and self.terminal_window is not None
            and self.terminal_window.winfo_exists()
        ):
            self.detached_terminal.config(
                state=tk.NORMAL
            )

            self.detached_terminal.insert(
                tk.END,
                text
            )

            self.detached_terminal.see(
                tk.END
            )

            self.detached_terminal.config(
                state=tk.DISABLED
            )

    def clear_terminal(self):
        self.terminal.config(
            state=tk.NORMAL
        )

        self.terminal.delete(
            "1.0",
            tk.END
        )

        self.terminal.config(
            state=tk.DISABLED
        )

        if (
            self.detached_terminal is not None
            and self.terminal_window is not None
            and self.terminal_window.winfo_exists()
        ):
            self.detached_terminal.config(
                state=tk.NORMAL
            )

            self.detached_terminal.delete(
                "1.0",
                tk.END
            )

            self.detached_terminal.config(
                state=tk.DISABLED
            )

    def run_ruby(self):
        if (
            self.ruby_process is not None
            and self.ruby_process.poll() is None
        ):
            self.append_terminal(
                "\n[Process is already running]\n"
            )
            return

        code = self.editor.get(
            "1.0",
            tk.END
        )

        code = "$stdout.sync = true\n$stderr.sync = true\n" + code

        try:
            if self.temp_path and os.path.exists(self.temp_path):
                os.remove(self.temp_path)
        except Exception:
            pass

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".rb",
                delete=False,
                encoding="utf-8"
            ) as f:
                f.write(code)
                self.temp_path = f.name

            env = os.environ.copy()
            env["RUBYOPT"] = "-Eutf-8"

            self.ruby_process = subprocess.Popen(
                [
                    self.ruby_path,
                    self.temp_path
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env
            )

            self.clear_terminal()

            self.append_terminal(
                "[Ruby process started]\n"
            )

            self.status_label.config(
                text=f"Ruby: {self.ruby_path} | Running"
            )

            self.run_button.config(
                state=tk.DISABLED
            )

            self.input_entry.config(
                state=tk.NORMAL
            )

            self.input_entry.focus_set()

            self.process_thread = threading.Thread(
                target=self.read_process_output,
                daemon=True
            )

            self.process_thread.start()

        except FileNotFoundError:
            self.append_terminal(
                f"Error: Ruby executable not found "
                f"({self.ruby_path}).\n"
            )

            self.status_label.config(
                text=f"Ruby: {self.ruby_path} | Error"
            )

            self.cleanup_process()

        except Exception as e:
            self.append_terminal(
                f"Error: {str(e)}\n"
            )

            self.status_label.config(
                text=f"Ruby: {self.ruby_path} | Error"
            )

            self.cleanup_process()

    def read_process_output(self):
        process = self.ruby_process

        if process is None:
            return

        try:
            while True:
                char = process.stdout.read(1)

                if char == "":
                    break

                self.output_queue.put(
                    ("output", char)
                )

        except Exception as e:
            self.output_queue.put(
                ("error", str(e))
            )

        finally:
            return_code = process.wait()

            self.output_queue.put(
                ("exit", return_code)
            )

    def process_output_queue(self):
        try:
            while True:
                item_type, value = (
                    self.output_queue.get_nowait()
                )

                if item_type == "output":
                    self.append_terminal(value)

                elif item_type == "error":
                    self.append_terminal(
                        f"\n[Output error: {value}]\n"
                    )

                elif item_type == "exit":
                    self.append_terminal(
                        f"\n[Process exited: {value}]\n"
                    )

                    self.status_label.config(
                        text=f"Ruby: {self.ruby_path} | Ready"
                    )

                    self.run_button.config(
                        state=tk.NORMAL
                    )

                    self.ruby_process = None

                    if self.temp_path:
                        try:
                            if os.path.exists(self.temp_path):
                                os.remove(self.temp_path)
                        except Exception:
                            pass

                        self.temp_path = None

        except queue.Empty:
            pass

        self.root.after(
            50,
            self.process_output_queue
        )

    def send_input(self, event=None):
        if (
            self.ruby_process is None
            or self.ruby_process.poll() is not None
        ):
            return "break"

        entry = self.input_entry

        if event is not None:
            if event.widget is self.detached_input_entry:
                entry = self.detached_input_entry

        text = entry.get()

        try:
            self.ruby_process.stdin.write(
                text + "\n"
            )

            self.ruby_process.stdin.flush()

            self.append_terminal(
                f"> {text}\n"
            )

            entry.delete(
                0,
                tk.END
            )

        except Exception as e:
            self.append_terminal(
                f"\n[Input error: {e}]\n"
            )

        return "break"

    def stop_ruby(self):
        if (
            self.ruby_process is None
            or self.ruby_process.poll() is not None
        ):
            return

        try:
            self.ruby_process.terminate()

            self.append_terminal(
                "\n[Process terminated]\n"
            )

        except Exception as e:
            self.append_terminal(
                f"\n[Stop error: {e}]\n"
            )

    def cleanup_process(self):
        self.ruby_process = None

        self.run_button.config(
            state=tk.NORMAL
        )

    def detach_terminal(self):
        if (
            self.terminal_window is not None
            and self.terminal_window.winfo_exists()
        ):
            self.terminal_window.lift()
            self.terminal_window.focus_force()
            return

        try:
            self.pane.forget(
                self.terminal_frame
            )
        except Exception:
            pass

        self.terminal_window = tk.Toplevel(
            self.root
        )

        self.terminal_window.title(
            "July Ruby IDE - Terminal"
        )

        self.terminal_window.geometry(
            "850x500"
        )

        self.terminal_window.configure(
            bg="#111111"
        )

        top = tk.Frame(
            self.terminal_window,
            bg="#252526"
        )

        top.pack(
            fill=tk.X
        )

        tk.Label(
            top,
            text="Ruby Terminal",
            bg="#252526",
            fg="#4EC9B0",
            font=("Consolas", 10, "bold")
        ).pack(
            side=tk.LEFT,
            padx=10,
            pady=6
        )

        tk.Button(
            top,
            text="Attach Terminal",
            command=self.attach_terminal,
            bg="#333333",
            fg="white",
            relief=tk.FLAT
        ).pack(
            side=tk.RIGHT,
            padx=8,
            pady=4
        )

        self.detached_terminal = tk.Text(
            self.terminal_window,
            bg="#111111",
            fg="#00ff00",
            insertbackground="white",
            font=self.terminal_font,
            state=tk.DISABLED,
            wrap=tk.NONE
        )

        self.detached_terminal.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=(5, 0)
        )

        detached_input_frame = tk.Frame(
            self.terminal_window,
            bg="#181818"
        )

        detached_input_frame.pack(
            fill=tk.X,
            padx=5,
            pady=5
        )

        tk.Label(
            detached_input_frame,
            text=">",
            bg="#181818",
            fg="#4EC9B0",
            font=self.terminal_font
        ).pack(
            side=tk.LEFT,
            padx=(8, 4)
        )

        self.detached_input_entry = tk.Entry(
            detached_input_frame,
            bg="#181818",
            fg="#d4d4d4",
            insertbackground="white",
            relief=tk.FLAT,
            font=self.terminal_font
        )

        self.detached_input_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 8),
            pady=6
        )

        self.detached_input_entry.bind(
            "<Return>",
            self.send_input
        )

        current_output = self.terminal.get(
            "1.0",
            tk.END
        )

        self.detached_terminal.config(
            state=tk.NORMAL
        )

        self.detached_terminal.insert(
            tk.END,
            current_output
        )

        self.detached_terminal.see(
            tk.END
        )

        self.detached_terminal.config(
            state=tk.DISABLED
        )

        self.terminal_window.protocol(
            "WM_DELETE_WINDOW",
            self.attach_terminal
        )

        self.terminal_window.focus_force()

    def attach_terminal(self):
        if (
            self.terminal_window is None
            or not self.terminal_window.winfo_exists()
        ):
            return

        self.terminal_window.destroy()

        self.terminal_window = None
        self.detached_terminal = None
        self.detached_input_entry = None

        self.pane.add(
            self.terminal_frame,
            minsize=100
        )

        self.pane.sash_place(
            0,
            0,
            450
        )

    def save_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".rb",
            filetypes=[
                ("Ruby files", "*.rb")
            ]
        )

        if path:
            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(
                    self.editor.get(
                        "1.0",
                        tk.END
                    )
                )

    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Ruby files", "*.rb")
            ]
        )

        if path:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                self.editor.delete(
                    "1.0",
                    tk.END
                )

                self.editor.insert(
                    tk.END,
                    f.read()
                )

            self.highlight_syntax()

    def on_close(self):
        if (
            self.ruby_process is not None
            and self.ruby_process.poll() is None
        ):
            try:
                self.ruby_process.terminate()
            except Exception:
                pass

        if self.temp_path:
            try:
                if os.path.exists(self.temp_path):
                    os.remove(self.temp_path)
            except Exception:
                pass

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RubyIDE(root)
    root.mainloop()

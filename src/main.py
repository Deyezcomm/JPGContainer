import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "JPG Container"
VERSION = "v1.0"

BG = "#0f1117"
CARD = "#171a21"
CARD_2 = "#1d212b"
BORDER = "#292e39"

TEXT = "#f5f7fa"
MUTED = "#8b93a3"

ACCENT = "#6c63ff"
ACCENT_HOVER = "#7d75ff"

GREEN = "#35d07f"
RED = "#ff5c70"

FONT = "Segoe UI"


# ============================================================
# FILE FUNCTIONS
# ============================================================

def is_jpeg(path):
    try:
        with open(path, "rb") as f:
            return f.read(2) == b"\xff\xd8"
    except Exception:
        return False


def has_zip_payload(path):
    try:
        with open(path, "rb") as f:
            data = f.read()

        return (
            b"PK\x03\x04" in data
            and b"PK\x05\x06" in data
        )

    except Exception:
        return False


def create_container(jpg_path, files, output_path):

    if not is_jpeg(jpg_path):
        raise ValueError("File carrier bukan JPG/JPEG yang valid.")

    if not files:
        raise ValueError("Tidak ada file yang dipilih.")

    if os.path.abspath(jpg_path) == os.path.abspath(output_path):
        raise ValueError(
            "File output tidak boleh sama dengan JPG sumber."
        )

    temp_zip = output_path + ".tmp.zip"

    try:

        with zipfile.ZipFile(
            temp_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            for file_path in files:

                if os.path.isfile(file_path):

                    archive.write(
                        file_path,
                        arcname=os.path.basename(file_path)
                    )

        with open(jpg_path, "rb") as f:
            jpg_data = f.read()

        with open(temp_zip, "rb") as f:
            zip_data = f.read()

        with open(output_path, "wb") as f:
            f.write(jpg_data)
            f.write(zip_data)

    finally:

        if os.path.exists(temp_zip):
            os.remove(temp_zip)


def extract_container(container_path, output_dir):

    with open(container_path, "rb") as f:
        data = f.read()

    zip_start = data.find(b"PK\x03\x04")

    if zip_start == -1:
        raise ValueError(
            "Payload tidak ditemukan di dalam JPG."
        )

    zip_data = data[zip_start:]

    temp_zip = os.path.join(
        output_dir,
        ".jpgcontainer_temp.zip"
    )

    try:

        with open(temp_zip, "wb") as f:
            f.write(zip_data)

        with zipfile.ZipFile(
            temp_zip,
            "r"
        ) as archive:

            bad_file = archive.testzip()

            if bad_file:
                raise ValueError(
                    f"ZIP rusak: {bad_file}"
                )

            archive.extractall(output_dir)

    finally:

        if os.path.exists(temp_zip):
            os.remove(temp_zip)


# ============================================================
# MODERN BUTTON
# ============================================================

class ModernButton(tk.Frame):

    def __init__(
        self,
        parent,
        text,
        command,
        color=ACCENT,
        width=150
    ):

        super().__init__(
            parent,
            bg=color,
            cursor="hand2"
        )

        self.command = command
        self.color = color
        self.hover = ACCENT_HOVER
        self.width = width

        self.label = tk.Label(
            self,
            text=text,
            bg=color,
            fg="white",
            font=(FONT, 9, "bold"),
            width=width // 10,
            height=1,
            cursor="hand2"
        )

        self.label.pack(
            padx=16,
            pady=9
        )

        self.bind("<Button-1>", self.clicked)
        self.label.bind("<Button-1>", self.clicked)

        self.bind("<Enter>", self.enter)
        self.label.bind("<Enter>", self.enter)

        self.bind("<Leave>", self.leave)
        self.label.bind("<Leave>", self.leave)

    def clicked(self, event=None):
        self.command()

    def enter(self, event=None):

        self.configure(
            bg=self.hover
        )

        self.label.configure(
            bg=self.hover
        )

    def leave(self, event=None):

        self.configure(
            bg=self.color
        )

        self.label.configure(
            bg=self.color
        )


# ============================================================
# APPLICATION
# ============================================================

class JPGContainerApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.selected_files = []

        self.title(
            f"{APP_NAME} {VERSION}"
        )

        self.geometry("520x430")

        self.resizable(
            False,
            False
        )

        self.configure(
            bg=BG
        )

        self.setup_window()

        self.create_ui()


    # ========================================================
    # WINDOW
    # ========================================================

    def setup_window(self):

        # Center window
        self.update_idletasks()

        width = 520
        height = 430

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (
            screen_width - width
        ) // 2

        y = (
            screen_height - height
        ) // 2

        self.geometry(
            f"{width}x{height}+{x}+{y}"
        )


    # ========================================================
    # UI
    # ========================================================

    def create_ui(self):

        # Main container
        main = tk.Frame(
            self,
            bg=BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20
        )


        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            main,
            bg=BG
        )

        header.pack(
            fill="x"
        )


        icon = tk.Label(
            header,
            text="◆",
            bg=BG,
            fg=ACCENT,
            font=(FONT, 20, "bold")
        )

        icon.pack(
            side="left",
            padx=(0, 10)
        )


        title_frame = tk.Frame(
            header,
            bg=BG
        )

        title_frame.pack(
            side="left"
        )


        tk.Label(
            title_frame,
            text="JPG Container",
            bg=BG,
            fg=TEXT,
            font=(FONT, 17, "bold")
        ).pack(
            anchor="w"
        )


        tk.Label(
            title_frame,
            text="Embed files inside JPG",
            bg=BG,
            fg=MUTED,
            font=(FONT, 8)
        ).pack(
            anchor="w"
        )


        # ----------------------------------------------------
        # DIVIDER
        # ----------------------------------------------------

        tk.Frame(
            main,
            bg=BORDER,
            height=1
        ).pack(
            fill="x",
            pady=(17, 14)
        )


        # ----------------------------------------------------
        # EMBED CARD
        # ----------------------------------------------------

        embed_card = self.card(main)

        embed_card.pack(
            fill="x",
            pady=(0, 10)
        )


        tk.Label(
            embed_card,
            text="EMBED",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(13, 2)
        )


        tk.Label(
            embed_card,
            text="Simpan file ke dalam JPG",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 11, "bold")
        ).pack(
            anchor="w",
            padx=15
        )


        self.file_status = tk.Label(
            embed_card,
            text="Belum ada file dipilih",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8)
        )

        self.file_status.pack(
            anchor="w",
            padx=15,
            pady=(3, 10)
        )


        button_row = tk.Frame(
            embed_card,
            bg=CARD
        )

        button_row.pack(
            fill="x",
            padx=15,
            pady=(0, 14)
        )


        ModernButton(
            button_row,
            "Choose Files",
            self.select_files,
            color=CARD_2,
            width=130
        ).pack(
            side="left"
        )


        ModernButton(
            button_row,
            "Embed →",
            self.embed,
            color=ACCENT,
            width=130
        ).pack(
            side="right"
        )


        # ----------------------------------------------------
        # EXTRACT CARD
        # ----------------------------------------------------

        extract_card = self.card(main)

        extract_card.pack(
            fill="x",
            pady=(0, 10)
        )


        extract_left = tk.Frame(
            extract_card,
            bg=CARD
        )

        extract_left.pack(
            side="left",
            padx=15,
            pady=13
        )


        tk.Label(
            extract_left,
            text="EXTRACT",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8, "bold")
        ).pack(
            anchor="w"
        )


        tk.Label(
            extract_left,
            text="Keluarkan file dari JPG",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 10, "bold")
        ).pack(
            anchor="w"
        )


        ModernButton(
            extract_card,
            "Extract",
            self.extract,
            color=CARD_2,
            width=100
        ).pack(
            side="right",
            padx=15,
            pady=14
        )


        # ----------------------------------------------------
        # CHECK CARD
        # ----------------------------------------------------

        check_card = self.card(main)

        check_card.pack(
            fill="x"
        )


        check_left = tk.Frame(
            check_card,
            bg=CARD
        )

        check_left.pack(
            side="left",
            padx=15,
            pady=13
        )


        tk.Label(
            check_left,
            text="CHECK",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8, "bold")
        ).pack(
            anchor="w"
        )


        tk.Label(
            check_left,
            text="Periksa JPG Container",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 10, "bold")
        ).pack(
            anchor="w"
        )


        ModernButton(
            check_card,
            "Check",
            self.check,
            color=CARD_2,
            width=100
        ).pack(
            side="right",
            padx=15,
            pady=14
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status_frame = tk.Frame(
            main,
            bg=BG
        )

        status_frame.pack(
            fill="x",
            pady=(14, 0)
        )


        self.status_dot = tk.Label(
            status_frame,
            text="●",
            bg=BG,
            fg=GREEN,
            font=(FONT, 8)
        )

        self.status_dot.pack(
            side="left"
        )


        self.status = tk.Label(
            status_frame,
            text="Ready",
            bg=BG,
            fg=MUTED,
            font=(FONT, 8)
        )

        self.status.pack(
            side="left",
            padx=6
        )


        tk.Label(
            status_frame,
            text=VERSION,
            bg=BG,
            fg="#555c6b",
            font=(FONT, 8)
        ).pack(
            side="right"
        )


    # ========================================================
    # CARD
    # ========================================================

    def card(self, parent):

        frame = tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        return frame


    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text,
        color=MUTED
    ):

        self.status.config(
            text=text
        )

        self.status_dot.config(
            fg=color
        )


    # ========================================================
    # SELECT
    # ========================================================

    def select_files(self):

        files = filedialog.askopenfilenames(
            title="Select files"
        )

        if not files:
            return

        self.selected_files = list(files)

        if len(files) == 1:

            text = os.path.basename(
                files[0]
            )

        else:

            text = (
                f"{len(files)} files selected"
            )

        self.file_status.config(
            text=text,
            fg=TEXT
        )

        self.set_status(
            "Files ready to embed.",
            GREEN
        )


    # ========================================================
    # EMBED
    # ========================================================

    def embed(self):

        if not self.selected_files:

            messagebox.showwarning(
                APP_NAME,
                "Please choose at least one file."
            )

            return


        jpg = filedialog.askopenfilename(

            title="Select JPG carrier",

            filetypes=[
                (
                    "JPEG files",
                    "*.jpg *.jpeg"
                )
            ]
        )


        if not jpg:
            return


        output = filedialog.asksaveasfilename(

            title="Save JPG Container",

            defaultextension=".jpg",

            filetypes=[
                (
                    "JPEG files",
                    "*.jpg"
                )
            ],

            initialfile=(
                os.path.splitext(
                    os.path.basename(jpg)
                )[0]
                + "_container.jpg"
            )
        )


        if not output:
            return


        try:

            self.set_status(
                "Creating container...",
                ACCENT
            )

            self.update()


            create_container(
                jpg,
                self.selected_files,
                output
            )


            size = (
                os.path.getsize(output)
                / 1024
                / 1024
            )


            self.set_status(
                "Container created successfully.",
                GREEN
            )


            messagebox.showinfo(
                APP_NAME,
                "JPG Container berhasil dibuat.\n\n"
                f"{output}\n\n"
                f"Size: {size:.2f} MB"
            )


        except Exception as error:

            self.set_status(
                "Failed.",
                RED
            )

            messagebox.showerror(
                APP_NAME,
                str(error)
            )


    # ========================================================
    # EXTRACT
    # ========================================================

    def extract(self):

        container = filedialog.askopenfilename(

            title="Select JPG Container",

            filetypes=[
                (
                    "JPEG files",
                    "*.jpg *.jpeg"
                )
            ]
        )


        if not container:
            return


        output_dir = filedialog.askdirectory(
            title="Select destination folder"
        )


        if not output_dir:
            return


        try:

            self.set_status(
                "Extracting files...",
                ACCENT
            )

            self.update()


            extract_container(
                container,
                output_dir
            )


            self.set_status(
                "Extraction completed.",
                GREEN
            )


            messagebox.showinfo(
                APP_NAME,
                "Files berhasil diekstrak."
            )


        except Exception as error:

            self.set_status(
                "Extraction failed.",
                RED
            )

            messagebox.showerror(
                APP_NAME,
                str(error)
            )


    # ========================================================
    # CHECK
    # ========================================================

    def check(self):

        path = filedialog.askopenfilename(

            title="Select JPG",

            filetypes=[
                (
                    "JPEG files",
                    "*.jpg *.jpeg"
                )
            ]
        )


        if not path:
            return


        if has_zip_payload(path):

            self.set_status(
                "Container detected.",
                GREEN
            )

            messagebox.showinfo(
                APP_NAME,
                "JPG Container terdeteksi."
            )

        else:

            self.set_status(
                "No container found.",
                RED
            )

            messagebox.showinfo(
                APP_NAME,
                "Tidak ditemukan payload."
            )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app = JPGContainerApp()

    app.mainloop()

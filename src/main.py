import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_NAME = "JPG Container"


def is_jpeg(path):
    """Memeriksa header dasar file JPEG."""
    try:
        with open(path, "rb") as f:
            header = f.read(2)

        return header == b"\xFF\xD8"

    except Exception:
        return False


def has_zip_payload(path):
    """Memeriksa apakah JPG memiliki payload ZIP."""
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
        raise ValueError(
            "File carrier bukan JPG/JPEG yang valid."
        )

    if not files:
        raise ValueError(
            "Tidak ada file yang dipilih."
        )

    if os.path.abspath(jpg_path) == os.path.abspath(output_path):
        raise ValueError(
            "File output tidak boleh sama dengan file JPG sumber."
        )

    temp_zip = output_path + ".payload.zip"

    try:

        # Buat ZIP payload
        with zipfile.ZipFile(
            temp_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            for file_path in files:

                if not os.path.isfile(file_path):
                    continue

                archive.write(
                    file_path,
                    arcname=os.path.basename(file_path)
                )

        # Baca JPG asli
        with open(jpg_path, "rb") as f:
            jpg_data = f.read()

        # Baca ZIP
        with open(temp_zip, "rb") as f:
            zip_data = f.read()

        # Gabungkan JPG + ZIP
        with open(output_path, "wb") as f:
            f.write(jpg_data)
            f.write(zip_data)

    finally:

        if os.path.exists(temp_zip):
            os.remove(temp_zip)


def extract_container(container_path, output_dir):

    with open(container_path, "rb") as f:
        data = f.read()

    # Cari awal ZIP
    zip_start = data.find(b"PK\x03\x04")

    if zip_start == -1:
        raise ValueError(
            "Payload ZIP tidak ditemukan."
        )

    zip_data = data[zip_start:]

    temp_zip = os.path.join(
        output_dir,
        "__jpgcontainer_payload.zip"
    )

    try:

        with open(temp_zip, "wb") as f:
            f.write(zip_data)

        with zipfile.ZipFile(
            temp_zip,
            "r"
        ) as archive:

            # Periksa kerusakan ZIP
            bad_file = archive.testzip()

            if bad_file:
                raise ValueError(
                    "ZIP rusak: " + bad_file
                )

            archive.extractall(output_dir)

    finally:

        if os.path.exists(temp_zip):
            os.remove(temp_zip)


class JPGContainerApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(APP_NAME)

        self.geometry("650x480")

        self.resizable(
            False,
            False
        )

        self.selected_files = []

        self.setup_style()

        self.create_interface()


    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("vista")
        except:
            pass


    def create_interface(self):

        # =========================
        # TITLE
        # =========================

        title = ttk.Label(
            self,
            text="JPG Container",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        )

        title.pack(
            pady=(25, 5)
        )


        subtitle = ttk.Label(
            self,
            text="Simpan file ke dalam JPG",
            font=(
                "Segoe UI",
                10
            )
        )

        subtitle.pack(
            pady=(0, 20)
        )


        # =========================
        # EMBED
        # =========================

        embed_frame = ttk.LabelFrame(
            self,
            text=" Embed File "
        )

        embed_frame.pack(
            fill="x",
            padx=35,
            pady=10
        )


        ttk.Button(
            embed_frame,
            text="1. Pilih File",
            command=self.select_files
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=15
        )


        self.file_status = ttk.Label(
            embed_frame,
            text="Belum ada file."
        )

        self.file_status.grid(
            row=0,
            column=1,
            padx=10,
            pady=15,
            sticky="w"
        )


        ttk.Button(
            embed_frame,
            text="2. Embed ke JPG",
            command=self.embed
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            pady=(0, 15)
        )


        # =========================
        # EXTRACT
        # =========================

        extract_frame = ttk.LabelFrame(
            self,
            text=" Extract File "
        )

        extract_frame.pack(
            fill="x",
            padx=35,
            pady=10
        )


        ttk.Button(
            extract_frame,
            text="Pilih JPG Container",
            command=self.extract
        ).pack(
            padx=15,
            pady=15
        )


        # =========================
        # CHECK
        # =========================

        check_frame = ttk.LabelFrame(
            self,
            text=" Check Container "
        )

        check_frame.pack(
            fill="x",
            padx=35,
            pady=10
        )


        ttk.Button(
            check_frame,
            text="Periksa JPG",
            command=self.check
        ).pack(
            padx=15,
            pady=15
        )


        # =========================
        # STATUS
        # =========================

        self.status = tk.StringVar()

        self.status.set(
            "Ready"
        )

        ttk.Label(
            self,
            textvariable=self.status,
            foreground="#555555"
        ).pack(
            pady=20
        )


    def select_files(self):

        files = filedialog.askopenfilenames(
            title="Pilih file"
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
                str(len(files))
                + " file dipilih"
            )

        self.file_status.config(
            text=text
        )

        self.status.set(
            "File siap di-embed."
        )


    def embed(self):

        if not self.selected_files:

            messagebox.showwarning(
                APP_NAME,
                "Pilih file terlebih dahulu."
            )

            return


        jpg = filedialog.askopenfilename(

            title="Pilih JPG Carrier",

            filetypes=[
                (
                    "JPEG Image",
                    "*.jpg *.jpeg"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )


        if not jpg:
            return


        output = filedialog.asksaveasfilename(

            title="Simpan JPG Container",

            defaultextension=".jpg",

            filetypes=[
                (
                    "JPEG Image",
                    "*.jpg"
                ),
                (
                    "All Files",
                    "*.*"
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

            self.status.set(
                "Container berhasil dibuat."
            )

            messagebox.showinfo(
                APP_NAME,
                "Berhasil!\n\n"
                "JPG Container:\n"
                + output
                + "\n\n"
                + f"Ukuran: {size:.2f} MB"
            )

        except Exception as error:

            messagebox.showerror(
                APP_NAME,
                "Gagal membuat container:\n\n"
                + str(error)
            )


    def extract(self):

        container = filedialog.askopenfilename(

            title="Pilih JPG Container",

            filetypes=[
                (
                    "JPEG Image",
                    "*.jpg *.jpeg"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )


        if not container:
            return


        output_dir = filedialog.askdirectory(

            title="Pilih folder tujuan"
        )


        if not output_dir:
            return


        try:

            extract_container(
                container,
                output_dir
            )

            self.status.set(
                "Extract berhasil."
            )

            messagebox.showinfo(
                APP_NAME,
                "File berhasil diekstrak ke:\n\n"
                + output_dir
            )

        except Exception as error:

            messagebox.showerror(
                APP_NAME,
                "Gagal extract:\n\n"
                + str(error)
            )


    def check(self):

        path = filedialog.askopenfilename(

            title="Pilih JPG",

            filetypes=[
                (
                    "JPEG Image",
                    "*.jpg *.jpeg"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )


        if not path:
            return


        if has_zip_payload(path):

            self.status.set(
                "Payload ditemukan."
            )

            messagebox.showinfo(
                APP_NAME,
                "Container terdeteksi!\n\n"
                "Payload ZIP ditemukan di dalam JPG."
            )

        else:

            self.status.set(
                "Tidak ada payload."
            )

            messagebox.showinfo(
                APP_NAME,
                "Tidak ditemukan payload ZIP."
            )


if __name__ == "__main__":

    app = JPGContainerApp()

    app.mainloop()

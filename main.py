import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import numpy as np
from PIL import Image, ImageTk
import sys

PREVIEW_SIZE = (300, 300)

# Словари локализации интерфейса
LOCALIZATION = {
    'ru': {
        'title': "Minecraft Figma-Scale Mosaic v1.0",
        'btn_photo': "1. Выбрать фото",
        'status_photo_empty': "Фото не выбрано",
        'btn_folder': "2. Выбрать папку блоков",
        'status_folder_empty': "Папка не выбрана",
        'frame_export': " Параметры экспорта ",
        'lbl_scale': "Масштаб блоков / Качество:",
        'chk_ultra': "Повысить качество (влияние < 16)",
        'chk_alpha': "Прозрачный фон альфа-каналов",
        'chk_skip_alpha': "Пропускать прозрачные пиксели (Alpha 100%)",
        'lbl_log': "Лог системы:",
        'log_ready': "Система готова к работе.",
        'btn_start': "🔥 СОЗДАТЬ",
        'btn_start_progress': "⏳ СБОРКА...",
        'btn_cancel': "🛑 ОТМЕНА",
        'btn_cancel_progress': "⏳ ОТМЕНА...",
        'lbl_preview': "Исходное изображение",
        'preview_placeholder': "Тут будет фото",
        'err_title': "Ошибка",
        'err_select': "Выберите фото и папку с текстурами!",
        'err_scale_val': "Значение должно быть целым числом больше 0!",
        'log_cancel_export': "Экспорт отменен.",
        'log_scanning': "Сканирование текстур...",
        'status_folder_found': "Текстур найдено: {count}",
        'log_folder_success': "Успех! Найдено блоков: {count}",
        'status_folder_fail': "Текстуры не найдены!",
        'log_folder_fail': "❌ ОШИБКА: Нет подходящих картинок!",
        'log_photo_loaded': "Загружено фото: {name} ({w}x{h} пикселей)",
        'err_preview': "Не удалось обновить предпросмотр:\n{e}",
        'log_cancel_req': "Запрос на отмену отправлен. Ожидайте остановки...",
        'dialog_title_save': "Выберите место для сохранения готовой мозаики",
        'log_analyzing': "Анализ папки блоков...",
        'err_folder_empty': "Папка с блоками пуста!",
        'log_building': "Сборка figma-мозаики {w}x{h} блоков (Ячейка: {rw}x{rh}px)...",
        'log_interrupted': "❌ Генерация прервана пользователем.",
        'log_saving': "Сохранение финального изображения...",
        'log_success': "🎉 Сборка завершена успешно!",
        'msg_success_img': "Картинка успешно сохранена:\n-> {name}",
        'msg_success_title': "Успех!",
        'preview_exported': "Исходник (Экспортировано)"
    },
    'en': {
        'title': "Minecraft Figma-Scale Mosaic v1.0",
        'btn_photo': "1. Select Photo",
        'status_photo_empty': "No photo selected",
        'btn_folder': "2. Select Block Folder",
        'status_folder_empty': "No folder selected",
        'frame_export': " Export Parameters ",
        'lbl_scale': "Block Scale / Quality:",
        'chk_ultra': "Enhance Quality (effects < 16)",
        'chk_alpha': "Transparent Alpha-Channel Background",
        'chk_skip_alpha': "Skip transparent pixels (Alpha 100%)",
        'lbl_log': "System Log:",
        'log_ready': "System is ready.",
        'btn_start': "🔥 CREATE",
        'btn_start_progress': "⏳ BUILDING...",
        'btn_cancel': "🛑 CANCEL",
        'btn_cancel_progress': "⏳ CANCELLING...",
        'lbl_preview': "Original Image",
        'preview_placeholder': "Photo preview here",
        'err_title': "Error",
        'err_select': "Please select both a photo and a textures folder!",
        'err_scale_val': "The scale value must be an integer greater than 0!",
        'log_cancel_export': "Export cancelled.",
        'log_scanning': "Scanning textures...",
        'status_folder_found': "Textures found: {count}",
        'log_folder_success': "Success! Found blocks: {count}",
        'status_folder_fail': "No textures found!",
        'log_folder_fail': "❌ ERROR: No valid images found!",
        'log_photo_loaded': "Loaded photo: {name} ({w}x{h} px)",
        'err_preview': "Failed to update preview:\n{e}",
        'log_cancel_req': "Cancellation request sent. Waiting to stop...",
        'dialog_title_save': "Select destination to save your mosaic",
        'log_analyzing': "Analyzing blocks folder...",
        'err_folder_empty': "Blocks folder is empty!",
        'log_building': "Assembling figma-mosaic {w}x{h} blocks (Cell: {rw}x{rh}px)...",
        'log_interrupted': "❌ Generation cancelled by user.",
        'log_saving': "Saving final image...",
        'log_success': "🎉 Assembly finished successfully!",
        'msg_success_img': "Image successfully saved:\n-> {name}",
        'msg_success_title': "Success!",
        'preview_exported': "Source (Exported)"
    }
}


def get_average_color(img):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    np_img = np.array(img)
    visible_mask = np_img[:, :, 3] > 128
    visible_pixels = np_img[visible_mask]
    if len(visible_pixels) == 0:
        return None
    return tuple(visible_pixels[:, :3].mean(axis=0).astype(int))


def load_textures_recursive(folder_path):
    textures = []
    if not folder_path or not os.path.exists(folder_path):
        return textures
    for root_dir, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(root_dir, file)
                try:
                    with Image.open(path) as img:
                        img_rgba = img.convert('RGBA')
                        avg_color = get_average_color(img_rgba)
                        if avg_color is not None:
                            block_name = os.path.splitext(file)[0]
                            textures.append({
                                'name': block_name,
                                'image': img_rgba.copy(),
                                'color': np.array(avg_color)
                            })
                except Exception:
                    continue
    return textures


class LanguageSelectDialog(tk.Toplevel):
    """Окно выбора языка, появляющееся перед запуском основного интерфейса."""

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Select Language / Выбор языка")
        self.geometry("320x130")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        lbl = tk.Label(self, text="Choose your language:\nВыберите язык интерфейса:", font=("Arial", 10, "bold"),
                       pady=10)
        lbl.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        btn_ru = tk.Button(btn_frame, text="Русский (RU)", width=12, font=("Arial", 9, "bold"),
                           command=lambda: self.set_lang('ru'))
        btn_ru.pack(side=tk.LEFT, padx=10)

        btn_en = tk.Button(btn_frame, text="English (EN)", width=12, font=("Arial", 9, "bold"),
                           command=lambda: self.set_lang('en'))
        btn_en.pack(side=tk.RIGHT, padx=10)

        self.transient(parent)
        self.grab_set()

    def set_lang(self, lang):
        self.callback(lang)
        self.destroy()

    def on_close(self):
        self.master.destroy()


class MinecraftCancelApp:
    def __init__(self, root):
        self.root = root
        self.photo_path = ""
        self.folder_path = ""
        self.orig_w = 0
        self.orig_h = 0
        self.cancel_requested = False

        try:
            self.lang = 'en'
            if sys.platform == 'darwin':
                import subprocess
                cmd = ["defaults", "read", "-g", "AppleLanguages"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if result.returncode == 0 and 'ru' in result.stdout.lower()[:30]:
                    self.lang = 'ru'
            else:
                import locale
                current_locale = locale.getlocale()
                if current_locale and current_locale.lower().startswith('ru'):
                    self.lang = 'ru'
        except Exception:
            self.lang = 'en'

        self.root.title(LOCALIZATION[self.lang]['title'])
        self.root.geometry("780x520")
        self.root.minsize(750, 480)

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Minecraft.Horizontal.TProgressbar", thickness=15, troughcolor='#2c2c2c', background='#55ff55')

        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=260)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.lang_frame = tk.Frame(self.left_frame)
        self.lang_frame.pack(anchor="ne", fill=tk.X, pady=(0, 5))
        self.btn_lang_toggle = tk.Button(self.lang_frame, text="🌐 RU / EN", font=("Arial", 8, "bold"), command=self.toggle_language)
        self.btn_lang_toggle.pack(side=tk.RIGHT)

        self.right_frame = tk.Frame(self.main_frame, bg="#e0e0e0", bd=1, relief=tk.SOLID)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.btn_photo = tk.Button(self.left_frame, text="", width=24, command=self.select_photo)
        self.btn_photo.pack(pady=(5, 2))
        self.lbl_photo_status = tk.Label(self.left_frame, text="", fg="red", wraplength=220)
        self.lbl_photo_status.pack(pady=(0, 10))

        self.btn_folder = tk.Button(self.left_frame, text="", width=24, command=self.select_folder)
        self.btn_folder.pack(pady=(5, 2))
        self.lbl_folder_status = tk.Label(self.left_frame, text="", fg="red", wraplength=220)
        self.lbl_folder_status.pack(pady=(0, 10))

        self.size_frame = tk.LabelFrame(self.left_frame, text="", padx=5, pady=5)
        self.size_frame.pack(fill=tk.X, pady=5)

        self.lbl_scale = tk.Label(self.size_frame, text="")
        self.lbl_scale.pack(anchor="w")
        self.block_render_size = tk.Entry(self.size_frame, width=10)
        self.block_render_size.insert(0, "16")
        self.block_render_size.pack(anchor="w", pady=(0, 5))
        self.ultra_res_var = tk.BooleanVar(value=True)
        self.chk_ultra = tk.Checkbutton(self.size_frame, text="", variable=self.ultra_res_var)
        self.chk_ultra.pack(anchor="w")

        self.use_alpha_var = tk.BooleanVar(value=True)
        self.chk_alpha = tk.Checkbutton(self.size_frame, text="", variable=self.use_alpha_var)
        self.chk_alpha.pack(anchor="w")

        self.skip_alpha_var = tk.BooleanVar(value=True)
        self.chk_skip_alpha = tk.Checkbutton(self.size_frame, text="", variable=self.skip_alpha_var)
        self.chk_skip_alpha.pack(anchor="w")

        self.lbl_log = tk.Label(self.left_frame, text="")
        self.lbl_log.pack(anchor="w", pady=(5, 0))
        self.log_box = scrolledtext.ScrolledText(self.left_frame, width=28, height=4, font=("Arial", 8))
        self.log_box.pack(fill=tk.X, pady=2)

        self.progress_frame = tk.Frame(self.left_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate", style="Minecraft.Horizontal.TProgressbar")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_percentage = tk.Label(self.progress_frame, text="0%", font=("Arial", 9, "bold"), width=5)
        self.lbl_percentage.pack(side=tk.RIGHT, padx=(5, 0))

        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(5, 0))

        self.btn_start = tk.Button(self.buttons_frame, text="", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=12, command=self.start_generation_thread)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2), ipady=5)

        self.btn_cancel = tk.Button(self.buttons_frame, text="", bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=12, state=tk.DISABLED, command=self.request_cancel)
        self.btn_cancel.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0), ipady=5)

        self.lbl_preview_title = tk.Label(self.right_frame, text="", bg="#e0e0e0", font=("Arial", 10, "bold"))
        self.lbl_preview_title.pack(pady=5)
        self.canvas_preview = tk.Label(self.right_frame, text="", bg="white")
        self.canvas_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.apply_language_strings()
        self.log(LOCALIZATION[self.lang]['log_ready'])

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'ru' else 'ru'
        self.apply_language_strings()

    def apply_language_strings(self):
        t = LOCALIZATION[self.lang]
        self.root.title(t['title'])
        self.btn_photo.config(text=t['btn_photo'])
        if not self.photo_path:
            self.lbl_photo_status.config(text=t['status_photo_empty'])
        self.btn_folder.config(text=t['btn_folder'])
        if not self.folder_path:
            self.lbl_folder_status.config(text=t['status_folder_empty'])
        self.size_frame.config(text=t['frame_export'])
        self.lbl_scale.config(text=t['lbl_scale'])
        self.chk_ultra.config(text=t['chk_ultra'])
        self.chk_alpha.config(text=t['chk_alpha'])
        self.chk_skip_alpha.config(text=t['chk_skip_alpha'])
        self.lbl_log.config(text=t['lbl_log'])
        if self.btn_start['state'] == tk.NORMAL:
            self.btn_start.config(text=t['btn_start'])
        else:
            self.btn_start.config(text=t['btn_start_progress'])
        if self.btn_cancel['state'] == tk.NORMAL:
            self.btn_cancel.config(text=t['btn_cancel'])
        else:
            self.btn_cancel.config(text=t['btn_cancel_progress'])
        if self.lbl_preview_title['text'] not in [LOCALIZATION['ru']['preview_exported'],
                                                  LOCALIZATION['en']['preview_exported']]:
            self.lbl_preview_title.config(text=t['lbl_preview'])
        else:
            self.lbl_preview_title.config(text=t['preview_exported'])
        if self.canvas_preview['image'] == '':
            self.canvas_preview.config(text=t['preview_placeholder'])

    def log(self, text):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def select_photo(self):
        t = LOCALIZATION[self.lang]
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if path:
            self.photo_path = path
            with Image.open(path) as img:
                self.orig_w, self.orig_h = img.size
                self.lbl_photo_status.config(text=f"{os.path.basename(path)} ({self.orig_w}x{self.orig_h} px)",
                                             fg="green")
                self.show_preview(path)
                self.log(t['log_photo_loaded'].format(name=os.path.basename(path), w=self.orig_w, h=self.orig_h))

    def select_folder(self):
        t = LOCALIZATION[self.lang]
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.log(t['log_scanning'])
            self.root.update_idletasks()
            textures = load_textures_recursive(path)
            if textures:
                self.lbl_folder_status.config(text=t['status_folder_found'].format(count=len(textures)), fg="green")
                self.log(t['log_folder_success'].format(count=len(textures)))
            else:
                self.lbl_folder_status.config(text=t['status_folder_fail'], fg="red")
                self.log(t['log_folder_fail'])

    def show_preview(self, image_path_or_obj):
        try:
            img = Image.open(image_path_or_obj) if isinstance(image_path_or_obj, str) else image_path_or_obj
            ratio = min(PREVIEW_SIZE[0] / img.width, PREVIEW_SIZE[1] / img.height)
            new_w, new_h = int(img.width * ratio), int(img.height * ratio)
            img_resized = img.resize((new_w, new_h), Image.Resampling.NEAREST)
            background = Image.new("RGB", (PREVIEW_SIZE[0], PREVIEW_SIZE[1]), (255, 255, 255))
            background.paste(img_resized, ((PREVIEW_SIZE[0] - new_w) // 2, (PREVIEW_SIZE[1] - new_h) // 2))
            self.img_tk = ImageTk.PhotoImage(background)
            self.canvas_preview.config(image=self.img_tk, text="")
        except Exception as e:
            messagebox.showerror(LOCALIZATION[self.lang]['err_title'],
                                 LOCALIZATION[self.lang]['err_preview'].format(e=e))

    def request_cancel(self):
        t = LOCALIZATION[self.lang]
        self.cancel_requested = True
        self.btn_cancel.config(state=tk.DISABLED, text=t['btn_cancel_progress'])
        self.log(t['log_cancel_req'])

    def start_generation_thread(self):
        t = LOCALIZATION[self.lang]
        if not self.photo_path or not self.folder_path:
            messagebox.showerror(t['err_title'], t['err_select'])
            return
        try:
            scale_factor = int(self.block_render_size.get())
            if scale_factor <= 0: raise ValueError
        except ValueError:
            messagebox.showerror(t['err_title'], t['err_scale_val'])
            return

        export_png_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")],
                                                       title=t['dialog_title_save'])
        if not export_png_path:
            self.log(t['log_cancel_export'])
            return

        self.cancel_requested = False
        self.btn_start.config(state=tk.DISABLED, text=t['btn_start_progress'])
        self.btn_cancel.config(state=tk.NORMAL, text=t['btn_cancel'])

        thread = threading.Thread(
            target=self.generate_and_export,
            args=(scale_factor, export_png_path, self.use_alpha_var.get(), self.ultra_res_var.get(),
                  self.skip_alpha_var.get()),
            daemon=True
        )
        thread.start()

    def generate_and_export(self, scale_factor, export_png_path, use_alpha, ultra_res, skip_alpha):
        t = LOCALIZATION[self.lang]
        self.log(t['log_analyzing'])
        textures = load_textures_recursive(self.folder_path)

        if not textures:
            self.root.after(0, lambda: messagebox.showerror(t['err_title'], t['err_folder_empty']))
            self.root.after(0, self.reset_buttons_ui)
            return

        block_colors = np.array([tex['color'] for tex in textures])
        target_img = Image.open(self.photo_path).convert('RGBA')

        if ultra_res and scale_factor < 16:
            upscale_multiplier = 16 // scale_factor
            w_blocks = self.orig_w * upscale_multiplier
            h_blocks = self.orig_h * upscale_multiplier
            render_w = render_h = 16
        else:
            w_blocks = max(1, self.orig_w // scale_factor)
            h_blocks = max(1, self.orig_h // scale_factor)
            render_w = render_h = scale_factor

        target_rescaled = target_img.resize((w_blocks, h_blocks), Image.Resampling.BOX)
        np_target = np.array(target_rescaled)
        output_image = Image.new('RGBA' if use_alpha else 'RGB', (w_blocks * render_w, h_blocks * render_h),
                                 (0, 0, 0, 0) if use_alpha else (0, 0, 0))

        self.log(t['log_building'].format(w=w_blocks, h=h_blocks, rw=render_w, rh=render_h))
        interrupted = False

        try:
            for y in range(h_blocks):
                if self.cancel_requested:
                    interrupted = True
                    break
                for x in range(w_blocks):
                    pixel_color = np_target[y, x]

                    if skip_alpha and len(pixel_color) == 4 and pixel_color[3] == 0:
                        continue

                    rgb_part = pixel_color[:3]
                    if rgb_part[0] > 245 and rgb_part[1] > 245 and rgb_part[2] > 245:
                        continue

                    distances = np.sum((block_colors - rgb_part) ** 2, axis=1)
                    closest_idx = np.argmin(distances)
                    chosen_tex = textures[closest_idx]

                    block_resized = chosen_tex['image'].resize((render_w, render_h), Image.Resampling.NEAREST)
                    output_image.paste(block_resized, (x * render_w, y * render_h),
                                       block_resized if use_alpha else None)

                self.root.after(0, self.update_progress_ui, int((y + 1) / h_blocks * 100))

            if interrupted:
                self.log(t['log_interrupted'])
                self.root.after(0, self.reset_buttons_ui)
                return

            self.log(t['log_saving'])
            if ultra_res and scale_factor < 16:
                output_image.save(export_png_path, "PNG")
            else:
                output_image.resize((self.orig_w, self.orig_h), Image.Resampling.NEAREST).save(export_png_path, "PNG")
            self.root.after(0, self.generation_complete, export_png_path)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(t['err_title'], f"Fail:\n{e}"))
            self.root.after(0, self.reset_buttons_ui)

    def update_progress_ui(self, percent):
        self.progress['value'] = percent
        self.lbl_percentage.config(text=f"{percent}%")

    def reset_buttons_ui(self):
        t = LOCALIZATION[self.lang]
        self.progress['value'] = 0
        self.lbl_percentage.config(text="0%")
        self.btn_start.config(state=tk.NORMAL, text=t['btn_start'])
        self.btn_cancel.config(state=tk.DISABLED, text=t['btn_cancel'])

    def generation_complete(self, png_path):
        self.reset_buttons_ui()
        self.lbl_preview_title.config(text=LOCALIZATION[self.lang]['preview_exported'])
        self.log(LOCALIZATION[self.lang]['log_success'])
        msg = LOCALIZATION[self.lang]['msg_success_img'].format(name=os.path.basename(png_path))
        messagebox.showinfo(LOCALIZATION[self.lang]['msg_success_title'], msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftCancelApp(root)
    root.bind("<Escape>", lambda event: app.request_cancel() if app.btn_cancel['state'] == tk.NORMAL else None)
    root.mainloop()

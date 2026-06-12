"""
Audio Downloader v6
─────────────────────────────────────────────
Hecho por Maken · Licencia MIT · Código bierto
─────────────────────────────────────────────
pip install yt-dlp plyer pygame Pillow requests tkinterdnd2
FFmpeg: https://ffmpeg.org/download.html
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import threading, os, sys, json, datetime, csv, subprocess, io
from collections import Counter
from urllib.request import urlopen

try:
    import yt_dlp
except ImportError:
    import tkinter.messagebox as _mb
    _mb.showerror("Error", "Falta yt-dlp.\nEjecuta: pip install yt-dlp"); sys.exit(1)

try:
    from plyer import notification as _notif; HAS_NOTIF = True
except ImportError:
    HAS_NOTIF = False

try:
    from PIL import Image, ImageTk; HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pygame; pygame.mixer.init(); HAS_PYGAME = True
except Exception:
    HAS_PYGAME = False

try:
    from tkinterdnd2 import TkinterDnD, DND_TEXT; HAS_DND = True
except ImportError:
    HAS_DND = False


# ─── FFmpeg empaquetado (PyInstaller) ─────────────────────────────────────────
def _setup_ffmpeg():
    """
    Si la app corre como .exe (frozen), añade la carpeta 'ffmpeg' que PyInstaller
    extrajo en sys._MEIPASS al PATH para que yt-dlp encuentre ffmpeg.exe/ffprobe.exe
    automáticamente, sin que el usuario tenga que instalar nada.
    """
    if getattr(sys, "frozen", False):
        ffmpeg_dir = os.path.join(sys._MEIPASS, "ffmpeg")
        if os.path.isdir(ffmpeg_dir):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

_setup_ffmpeg()

# ─── Archivos de config ───────────────────────────────────────────────────────
CONFIG_FILE  = os.path.join(os.path.expanduser("~"), ".config.json")
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".dl_history.json")

FORMATS = {
    "MP3":  {"codec": "mp3",    "lossy": True},
    "AAC":  {"codec": "aac",    "lossy": True},
    "FLAC": {"codec": "flac",   "lossy": False},
    "WAV":  {"codec": "wav",    "lossy": False},
    "OGG":  {"codec": "vorbis", "lossy": True},
}

PLATFORMS = "YouTube · SoundCloud · Vimeo · Bandcamp · Twitter/X · Twitch · +1000 sitios"

# ─── Temas ────────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG":"#1a1a2e","PANEL":"#16213e","PANEL2":"#1e2a45",
        "ACCENT":"#e94560","ACCENT2":"#0f3460",
        "TEXT":"#eaeaea","SUBTEXT":"#a0a0b0",
        "SUCCESS":"#4ade80","WARNING":"#facc15","ERROR":"#f87171",
        "HIST_BG":"#111827",
    },
    "light": {
        "BG":"#f0f2f5","PANEL":"#ffffff","PANEL2":"#e4e8ef",
        "ACCENT":"#e94560","ACCENT2":"#2563eb",
        "TEXT":"#111827","SUBTEXT":"#6b7280",
        "SUCCESS":"#16a34a","WARNING":"#d97706","ERROR":"#dc2626",
        "HIST_BG":"#f9fafb",
    },
}

# ─── Strings i18n ─────────────────────────────────────────────────────────────
STRINGS = {
    "es": {
        "app_title":"Audio Downloader",
        "tab_download":"  ⬇ Descargar  ","tab_history":"  📋 Historial  ",
        "tab_settings":"  ⚙ Ajustes  ",
        "url_label":"URL  (una por línea — arrastra desde el navegador o pega aquí)",
        "btn_info":"✦ Ver Info","btn_add":"＋ Añadir a cola","btn_clear_url":"🗑 Limpiar",
        "folder_lbl":"📁 Carpeta:","btn_change":"Cambiar","btn_open_folder":"📂 Abrir carpeta",
        "fmt_lbl":"Formato:","quality_lbl":"Calidad:","template_lbl":"Nombre archivo:",
        "queue_lbl":"Cola de descarga","btn_remove":"✕ Eliminar",
        "btn_clear_q":"🗑 Vaciar cola","in_queue":"{n} en cola",
        "btn_cancel":"⏹ Cancelar","btn_download":"⬇  DESCARGAR COLA",
        "downloading":"Descargando…","log_lbl":"Log",
        "status_paste":"Pega URLs o arrástralas desde el navegador",
        "status_fetching":"Obteniendo información…","status_info_ok":"Info cargada.",
        "status_added":"{n} URL(s) añadidas.","status_converting":"Convirtiendo…",
        "status_done":"✅ {n} archivo(s) {fmt} en: {folder}",
        "status_cancelled":"⏹ Cancelada.","status_eta":"[{i}/{t}] {pct:.1f}%  {speed}  ETA {eta}",
        "warn_empty_queue":"Añade al menos una URL.","warn_empty_q_title":"Cola vacía",
        "notif_title":"Audio Downloader — ¡Listo!","notif_msg":"{n} archivo(s) {fmt} descargados.",
        "hist_search":"Buscar…","btn_clear_hist":"🗑 Borrar historial",
        "btn_export_csv":"📥 Exportar CSV","hist_entries":"{n} entrada(s)",
        "col_title":"Título","col_channel":"Canal","col_fmt":"Fmt",
        "col_dur":"Dur.","col_date":"Fecha","col_folder":"Carpeta",
        "dblclick_hint":"Doble click → abrir carpeta  |  Seleccionar + ▶ para escuchar",
        "btn_play":"▶ Reproducir","btn_stop":"⏹ Parar",
        "stats_total":"Total:","stats_fmt":"Formato top:","stats_platform":"Canal top:","stats_mb":"MB estimados:",
        "confirm_clear":"¿Borrar todo el historial?","confirm_title":"Confirmar",
        "lang_lbl":"Idioma:","csv_saved":"CSV exportado: {path}",
        "cancelled_log":"⏹ Cancelado.","retry_log":"↩ Reintentando ({n}/{max})…",
        "settings_title":"Ajustes","proxy_lbl":"Proxy:","throttle_lbl":"Velocidad máxima:",
        "cookies_lbl":"Cookies del navegador:","cookies_none":"Ninguno",
        "concurrent_lbl":"Paralelo:","retries_lbl":"Reintentos auto:",
        "theme_lbl":"Tema:","theme_dark":"Oscuro","theme_light":"Claro",
        "accent_lbl":"Color de acento:","btn_pick_accent":"🎨 Elegir color",
        "btn_save_settings":"💾 Guardar ajustes","settings_saved":"✅ Guardado.",
        "btn_update_ytdlp":"🔄 Actualizar yt-dlp","updating":"Actualizando…",
        "update_ok":"✅ yt-dlp actualizado.","update_fail":"❌ Error: {err}",
        "no_audio_file":"No se encontró el archivo. ¿Ya fue descargado?",
        "pygame_missing":"Instala pygame:\npip install pygame",
        "ctx_move_up":"⬆ Mover arriba","ctx_move_down":"⬇ Mover abajo",
        "ctx_open_browser":"🌐 Abrir en navegador","ctx_remove":"✕ Eliminar",
        "about_title":"Acerca de","about_text":"Audio Downloader \n\nHecho por Maken\nLicencia MIT · Eres libre de usarlo, modificarlo y redistribuirlo como quieras.\n\nMotor: yt-dlp  |  UI: Python/Tkinter",
        "btn_about":"ℹ Acerca de",
    },
    "en": {
        "app_title":"Audio Downloader",
        "tab_download":"  ⬇ Download  ","tab_history":"  📋 History  ",
        "tab_settings":"  ⚙ Settings  ",
        "url_label":"URL  (one per line — drag from browser or paste here)",
        "btn_info":"✦ Get Info","btn_add":"＋ Add to queue","btn_clear_url":"🗑 Clear",
        "folder_lbl":"📁 Folder:","btn_change":"Change","btn_open_folder":"📂 Open folder",
        "fmt_lbl":"Format:","quality_lbl":"Quality:","template_lbl":"Filename template:",
        "queue_lbl":"Download queue","btn_remove":"✕ Remove",
        "btn_clear_q":"🗑 Clear queue","in_queue":"{n} in queue",
        "btn_cancel":"⏹ Cancel","btn_download":"⬇  DOWNLOAD QUEUE",
        "downloading":"Downloading…","log_lbl":"Log",
        "status_paste":"Paste URLs or drag them from your browser",
        "status_fetching":"Fetching info…","status_info_ok":"Info loaded.",
        "status_added":"{n} URL(s) added.","status_converting":"Converting…",
        "status_done":"✅ {n} {fmt} file(s) in: {folder}",
        "status_cancelled":"⏹ Cancelled.","status_eta":"[{i}/{t}] {pct:.1f}%  {speed}  ETA {eta}",
        "warn_empty_queue":"Add at least one URL.","warn_empty_q_title":"Empty queue",
        "notif_title":"Audio Downloader — Done!","notif_msg":"{n} {fmt} file(s) downloaded.",
        "hist_search":"Search…","btn_clear_hist":"🗑 Clear history",
        "btn_export_csv":"📥 Export CSV","hist_entries":"{n} entries",
        "col_title":"Title","col_channel":"Channel","col_fmt":"Fmt",
        "col_dur":"Dur.","col_date":"Date","col_folder":"Folder",
        "dblclick_hint":"Double click → open folder  |  Select + ▶ to preview",
        "btn_play":"▶ Play","btn_stop":"⏹ Stop",
        "stats_total":"Total:","stats_fmt":"Top format:","stats_platform":"Top channel:","stats_mb":"Est. MB:",
        "confirm_clear":"Delete all history?","confirm_title":"Confirm",
        "lang_lbl":"Language:","csv_saved":"CSV exported: {path}",
        "cancelled_log":"⏹ Cancelled.","retry_log":"↩ Retrying ({n}/{max})…",
        "settings_title":"Settings","proxy_lbl":"Proxy:","throttle_lbl":"Max speed:",
        "cookies_lbl":"Browser cookies:","cookies_none":"None",
        "concurrent_lbl":"Parallel:","retries_lbl":"Auto-retries:",
        "theme_lbl":"Theme:","theme_dark":"Dark","theme_light":"Light",
        "accent_lbl":"Accent color:","btn_pick_accent":"🎨 Pick color",
        "btn_save_settings":"💾 Save settings","settings_saved":"✅ Saved.",
        "btn_update_ytdlp":"🔄 Update yt-dlp","updating":"Updating…",
        "update_ok":"✅ yt-dlp updated.","update_fail":"❌ Error: {err}",
        "no_audio_file":"File not found. Has it been downloaded?",
        "pygame_missing":"Install pygame:\npip install pygame",
        "ctx_move_up":"⬆ Move up","ctx_move_down":"⬇ Move down",
        "ctx_open_browser":"🌐 Open in browser","ctx_remove":"✕ Remove",
        "about_title":"About","about_text":"Audio Downloader \n\nMade by Maken\nMIT License · You are free to use, modify, and redistribute it as you wish.\n\nEngine: yt-dlp  |  UI: Python/Tkinter",
        "btn_about":"ℹ About",
    },
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def load_config():
    d = {"lang":"es","output_dir":os.path.expanduser("~/Downloads"),
         "format":"MP3","quality":"320","template":"%(title)s",
         "proxy":"","throttle":"","cookies":"none","concurrent":1,"retries":3,
         "theme":"dark","accent":"#e94560"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE,"r",encoding="utf-8") as f: d.update(json.load(f))
        except Exception: pass
    return d

def save_config(c):
    try:
        with open(CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(c,f,ensure_ascii=False,indent=2)
    except Exception: pass

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return []

def save_history(h):
    try:
        with open(HISTORY_FILE,"w",encoding="utf-8") as f: json.dump(h[-500:],f,ensure_ascii=False,indent=2)
    except Exception: pass

def desktop_notify(title, msg):
    if not HAS_NOTIF: return
    try: _notif.notify(title=title,message=msg,app_name="Audio Downloader",timeout=6)
    except Exception: pass

def estimate_mb(history):
    KBPS={"MP3":192,"AAC":160,"FLAC":900,"WAV":1400,"OGG":160}
    secs=sum(int(r.get("duracion","0:00").split(":")[0])*60+int(r.get("duracion","0:00").split(":")[1])
             for r in history if ":" in r.get("duracion",""))
    if not history: return 0
    avg=sum(KBPS.get(r.get("formato","MP3"),192) for r in history)/len(history)
    return round(secs*avg/8/1024,1)

def open_folder(path):
    if not os.path.isdir(path): return
    if sys.platform=="win32": os.startfile(path)
    elif sys.platform=="darwin": subprocess.run(["open",path])
    else: subprocess.run(["xdg-open",path])

def open_url_browser(url):
    import webbrowser; webbrowser.open(url)


# ════════════════════════════════════════════════════════════════════════════
_Base = TkinterDnD.Tk if HAS_DND else tk.Tk

class App(_Base):
    def __init__(self):
        super().__init__()
        self.cfg            = load_config()
        self.lang           = self.cfg.get("lang","es")
        self.output_dir     = self.cfg.get("output_dir",os.path.expanduser("~/Downloads"))
        self.history        = load_history()
        self.queue          = []
        self.is_downloading = False
        self._completed     = 0
        self._cancel_evt    = threading.Event()
        self._thumb_img     = None
        self._player_file   = None
        # Carga tema activo
        self.C = self._build_theme()
        self._apply_styles()
        self._build_ui()
        self._refresh_history()
        self._refresh_stats()

    # ── Tema ─────────────────────────────────────────────────────────────────
    def _build_theme(self):
        base   = THEMES.get(self.cfg.get("theme","dark"), THEMES["dark"]).copy()
        accent = self.cfg.get("accent","#e94560")
        base["ACCENT"] = accent
        return base

    def _apply_styles(self):
        C = self.C
        self.configure(bg=C["BG"])
        s = ttk.Style(); s.theme_use("default")
        s.configure("TNotebook",     background=C["BG"],    borderwidth=0)
        s.configure("TNotebook.Tab", background=C["PANEL"], foreground=C["SUBTEXT"],
                    padding=[14,6],  font=("Segoe UI",10))
        s.map("TNotebook.Tab", background=[("selected",C["ACCENT2"])],
                               foreground=[("selected",C["TEXT"])])
        s.configure("TProgressbar", troughcolor=C["PANEL"], background=C["ACCENT"], thickness=8)
        s.configure("Hist.Treeview", background=C["HIST_BG"], foreground=C["TEXT"],
                    rowheight=26, fieldbackground=C["HIST_BG"], borderwidth=0, font=("Segoe UI",9))
        s.configure("Hist.Treeview.Heading", background=C["PANEL"], foreground=C["SUBTEXT"],
                    font=("Segoe UI",9,"bold"), relief="flat")
        s.map("Hist.Treeview", background=[("selected",C["ACCENT2"])])

    def _reload_theme(self):
        self.C = self._build_theme()
        self._apply_styles()
        # Cancelar trace activo antes de destruir widgets
        try:
            for name, _, cb in self.search_var.trace_info():
                self.search_var.trace_remove(name, cb)
        except Exception:
            pass
        for w in self.winfo_children(): w.destroy()
        self._build_ui()
        self._refresh_history()
        self._refresh_stats()

    # ── i18n ─────────────────────────────────────────────────────────────────
    def T(self, k, **kw):
        s = STRINGS[self.lang].get(k,k)
        return s.format(**kw) if kw else s

    # ════════════════════════════════════════════════════════════════════════
    # BUILD UI
    # ════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        C = self.C
        self.title(self.T("app_title"))

        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C["ACCENT2"], height=56)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        tk.Label(hdr, text="⬇ Audio Downloader",
                 font=("Segoe UI",16,"bold"), bg=C["ACCENT2"], fg=C["TEXT"]).pack(side="left",padx=20)

        # Botón Acerca de
        tk.Button(hdr, text=self.T("btn_about"), font=("Segoe UI",9),
                  bg=C["ACCENT2"], fg=C["SUBTEXT"], relief="flat", cursor="hand2",
                  activebackground=C["ACCENT"], activeforeground=C["TEXT"],
                  command=self._show_about).pack(side="right", padx=6)

        # Botón Abrir carpeta (header)
        self.btn_open_folder_hdr = tk.Button(
            hdr, text=self.T("btn_open_folder"), font=("Segoe UI",9),
            bg=C["ACCENT2"], fg=C["TEXT"], relief="flat", cursor="hand2",
            activebackground=C["ACCENT"], activeforeground=C["TEXT"], padx=10,
            command=lambda: open_folder(self.output_dir))
        self.btn_open_folder_hdr.pack(side="right", padx=2)

        # Idioma
        lang_f = tk.Frame(hdr, bg=C["ACCENT2"]); lang_f.pack(side="right", padx=14)
        tk.Label(lang_f, text=self.T("lang_lbl"), font=("Segoe UI",9),
                 bg=C["ACCENT2"], fg=C["SUBTEXT"]).pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang.upper())
        lang_cb = ttk.Combobox(lang_f, textvariable=self.lang_var, values=["ES","EN"],
                               state="readonly", width=4, font=("Segoe UI",9))
        lang_cb.pack(side="left", padx=(4,0))
        lang_cb.bind("<<ComboboxSelected>>", self._change_lang)

        # Sub-header
        sub = tk.Frame(self, bg=C["PANEL2"]); sub.pack(fill="x")
        tk.Label(sub, text=f"🌐  {PLATFORMS}", font=("Segoe UI",8),
                 bg=C["PANEL2"], fg=C["SUBTEXT"]).pack(side="left", pady=3, padx=12)

        # Notebook
        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=True)
        self.tab_dl   = tk.Frame(self.nb, bg=C["BG"])
        self.tab_hist = tk.Frame(self.nb, bg=C["BG"])
        self.tab_cfg  = tk.Frame(self.nb, bg=C["BG"])
        self.nb.add(self.tab_dl,   text=self.T("tab_download"))
        self.nb.add(self.tab_hist, text=self.T("tab_history"))
        self.nb.add(self.tab_cfg,  text=self.T("tab_settings"))
        self._build_tab_download(self.tab_dl)
        self._build_tab_history(self.tab_hist)
        self._build_tab_settings(self.tab_cfg)

    # ════════════════════════════════════════════════════════════════════════
    # TAB DESCARGAR
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_download(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=18, pady=10)
        p.pack(fill="both", expand=True); p.columnconfigure(0, weight=1)

        self.lbl_url = tk.Label(p, text=self.T("url_label"),
                                 font=("Segoe UI",9,"bold"), bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_url.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,4))

        # URL box + thumbnail
        u_out = tk.Frame(p, bg=C["PANEL"]); u_out.grid(row=1, column=0, sticky="ew")
        self.url_text = tk.Text(u_out, height=3, font=("Segoe UI",10),
                                bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                                relief="flat", wrap="word", bd=6)
        u_sb = tk.Scrollbar(u_out, command=self.url_text.yview)
        self.url_text.configure(yscrollcommand=u_sb.set)
        self.url_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        u_sb.pack(side="right", fill="y")
        if HAS_DND:
            self.url_text.drop_target_register(DND_TEXT)
            self.url_text.dnd_bind("<<Drop>>", self._on_dnd_drop)

        self.thumb_frame = tk.Frame(p, bg=C["PANEL"], width=112, height=63)
        self.thumb_frame.grid(row=1, column=1, sticky="nsew", padx=(8,0))
        self.thumb_frame.pack_propagate(False)
        self.lbl_thumb = tk.Label(self.thumb_frame, bg=C["PANEL"], fg=C["SUBTEXT"],
                                   text="🖼", font=("Segoe UI",22))
        self.lbl_thumb.pack(expand=True)

        # Botones URL
        br = tk.Frame(p, bg=C["BG"]); br.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5,0))
        self.btn_info = tk.Button(br, text=self.T("btn_info"), font=("Segoe UI",9,"bold"),
                                   bg=C["ACCENT2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                                   padx=10, pady=3, activebackground=C["ACCENT"],
                                   activeforeground=C["TEXT"], command=self._start_fetch_info)
        self.btn_info.pack(side="left", padx=(0,6))
        self.btn_add = tk.Button(br, text=self.T("btn_add"), font=("Segoe UI",9),
                                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                                  padx=10, pady=3, command=self._add_to_queue)
        self.btn_add.pack(side="left", padx=(0,6))
        self.btn_clr_url = tk.Button(br, text=self.T("btn_clear_url"), font=("Segoe UI",9),
                                      bg=C["PANEL2"], fg=C["SUBTEXT"], relief="flat",
                                      cursor="hand2", padx=10, pady=3, command=self._clear_url)
        self.btn_clr_url.pack(side="left")

        # Info card
        inf = tk.Frame(p, bg=C["PANEL"]); inf.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8,0))
        self.lbl_title    = tk.Label(inf, text="—", font=("Segoe UI",11,"bold"),
                                      bg=C["PANEL"], fg=C["TEXT"], wraplength=740, justify="left")
        self.lbl_title.pack(anchor="w", padx=12, pady=(7,2))
        self.lbl_channel  = tk.Label(inf, text="", font=("Segoe UI",9), bg=C["PANEL"], fg=C["SUBTEXT"])
        self.lbl_channel.pack(anchor="w", padx=12)
        self.lbl_duration = tk.Label(inf, text="", font=("Segoe UI",9), bg=C["PANEL"], fg=C["SUBTEXT"])
        self.lbl_duration.pack(anchor="w", padx=12)
        self.lbl_copyright= tk.Label(inf, text="", font=("Segoe UI",10,"bold"), bg=C["PANEL"], fg=C["SUBTEXT"])
        self.lbl_copyright.pack(anchor="w", padx=12, pady=(0,7))

        # Carpeta
        cr1 = tk.Frame(p, bg=C["BG"]); cr1.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(7,0))
        self.lbl_folder_label = tk.Label(cr1, text=self.T("folder_lbl"), font=("Segoe UI",9),
                                          bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_folder_label.pack(side="left")
        self.lbl_folder = tk.Label(cr1, text=self.output_dir, font=("Segoe UI",9),
                                    bg=C["BG"], fg=C["ACCENT"], cursor="hand2")
        self.lbl_folder.pack(side="left", padx=4)
        self.lbl_folder.bind("<Button-1>", lambda e: self._choose_folder())
        self.btn_change = tk.Button(cr1, text=self.T("btn_change"), font=("Segoe UI",9),
                                     bg=C["PANEL"], fg=C["TEXT"], relief="flat", cursor="hand2",
                                     padx=6, pady=2, command=self._choose_folder)
        self.btn_change.pack(side="left", padx=(0,14))

        # Formato + calidad
        cr2 = tk.Frame(p, bg=C["BG"]); cr2.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5,0))
        self.lbl_fmt = tk.Label(cr2, text=self.T("fmt_lbl"), font=("Segoe UI",9),
                                 bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_fmt.pack(side="left")
        self.format_var = tk.StringVar(value=self.cfg.get("format","MP3"))
        fmt_cb = ttk.Combobox(cr2, textvariable=self.format_var, values=list(FORMATS.keys()),
                               state="readonly", width=6, font=("Segoe UI",9))
        fmt_cb.pack(side="left", padx=(4,12))
        fmt_cb.bind("<<ComboboxSelected>>", self._on_format_change)
        self.qual_frame = tk.Frame(cr2, bg=C["BG"]); self.qual_frame.pack(side="left")
        self.lbl_qual = tk.Label(self.qual_frame, text=self.T("quality_lbl"), font=("Segoe UI",9),
                                  bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_qual.pack(side="left")
        self.quality_var = tk.StringVar(value=self.cfg.get("quality","320"))
        for q in ["128","192","256","320"]:
            tk.Radiobutton(self.qual_frame, text=f"{q}k", variable=self.quality_var, value=q,
                           font=("Segoe UI",9), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=3)

        # Plantilla
        cr3 = tk.Frame(p, bg=C["BG"]); cr3.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4,0))
        self.lbl_tpl = tk.Label(cr3, text=self.T("template_lbl"), font=("Segoe UI",9),
                                 bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_tpl.pack(side="left")
        self.template_var = tk.StringVar(value=self.cfg.get("template","%(title)s"))
        tk.Entry(cr3, textvariable=self.template_var, font=("Consolas",9),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=4, width=32).pack(side="left", padx=(6,0), ipady=3)
        tk.Label(cr3, text="  %(artist)s · %(playlist_index)s · %(uploader)s",
                 font=("Segoe UI",7), bg=C["BG"], fg=C["SUBTEXT"]).pack(side="left", padx=4)

        # Cola
        self.lbl_queue_title = tk.Label(p, text=self.T("queue_lbl"), font=("Segoe UI",9,"bold"),
                                         bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_queue_title.grid(row=7, column=0, columnspan=2, sticky="w", pady=(9,2))
        q_out = tk.Frame(p, bg=C["PANEL"]); q_out.grid(row=8, column=0, columnspan=2, sticky="ew")
        self.queue_list = tk.Listbox(q_out, height=3, font=("Segoe UI",9),
                                      bg=C["PANEL"], fg=C["TEXT"], relief="flat",
                                      selectbackground=C["ACCENT2"], activestyle="none", bd=4)
        q_sb = tk.Scrollbar(q_out, command=self.queue_list.yview)
        self.queue_list.configure(yscrollcommand=q_sb.set)
        self.queue_list.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        q_sb.pack(side="right", fill="y")
        # Menú contextual click derecho en cola
        self.ctx_menu = tk.Menu(self, tearoff=0, bg=C["PANEL"], fg=C["TEXT"],
                                 activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                                 relief="flat", bd=0)
        self.ctx_menu.add_command(label=self.T("ctx_move_up"),      command=self._ctx_move_up)
        self.ctx_menu.add_command(label=self.T("ctx_move_down"),    command=self._ctx_move_down)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=self.T("ctx_open_browser"), command=self._ctx_open_browser)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label=self.T("ctx_remove"),       command=self._remove_from_queue)
        self.queue_list.bind("<Button-3>",          self._show_ctx_menu)   # Windows/Linux
        self.queue_list.bind("<Button-2>",          self._show_ctx_menu)   # macOS

        qr = tk.Frame(p, bg=C["BG"]); qr.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(3,0))
        self.btn_remove = tk.Button(qr, text=self.T("btn_remove"), font=("Segoe UI",8),
                                     bg=C["PANEL"], fg=C["SUBTEXT"], relief="flat", cursor="hand2",
                                     padx=8, pady=2, command=self._remove_from_queue)
        self.btn_remove.pack(side="left")
        self.btn_clr_q = tk.Button(qr, text=self.T("btn_clear_q"), font=("Segoe UI",8),
                                    bg=C["PANEL"], fg=C["SUBTEXT"], relief="flat", cursor="hand2",
                                    padx=8, pady=2, command=self._clear_queue)
        self.btn_clr_q.pack(side="left", padx=(5,0))
        self.lbl_queue_count = tk.Label(qr, text=self.T("in_queue",n=0), font=("Segoe UI",8),
                                         bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_queue_count.pack(side="right")

        # Progreso
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(p, variable=self.progress_var, maximum=100).grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=(10,2))
        self.lbl_status = tk.Label(p, text=self.T("status_paste"), font=("Segoe UI",9),
                                    bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_status.grid(row=11, column=0, columnspan=2)

        # Botones descarga/cancelar
        btn_row = tk.Frame(p, bg=C["BG"]); btn_row.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(7,0))
        btn_row.columnconfigure(0, weight=1)
        self.btn_download = tk.Button(btn_row, text=self.T("btn_download"),
                                       font=("Segoe UI",13,"bold"), bg=C["ACCENT"], fg=C["TEXT"],
                                       relief="flat", cursor="hand2", pady=9,
                                       activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                                       command=self._start_queue)
        self.btn_download.grid(row=0, column=0, sticky="ew")
        self.btn_cancel = tk.Button(btn_row, text=self.T("btn_cancel"),
                                     font=("Segoe UI",10), bg=C["PANEL2"], fg=C["WARNING"],
                                     relief="flat", cursor="hand2", pady=4,
                                     state="disabled", command=self._cancel_download)
        self.btn_cancel.grid(row=1, column=0, sticky="ew", pady=(4,0))

        # Log
        self.lbl_log = tk.Label(p, text=self.T("log_lbl"), font=("Segoe UI",8),
                                 bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_log.grid(row=13, column=0, columnspan=2, sticky="w", pady=(8,2))
        log_out = tk.Frame(p, bg=C["PANEL"]); log_out.grid(row=14, column=0, columnspan=2, sticky="ew")
        self.log_text = tk.Text(log_out, height=3, font=("Consolas",8),
                                 bg=C["PANEL"], fg=C["SUBTEXT"], relief="flat",
                                 state="disabled", wrap="word")
        log_sb = tk.Scrollbar(log_out, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        log_sb.pack(side="right", fill="y")
        self._on_format_change()

    # ════════════════════════════════════════════════════════════════════════
    # TAB HISTORIAL
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_history(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=18, pady=12)
        p.pack(fill="both", expand=True); p.columnconfigure(0, weight=1); p.rowconfigure(2, weight=1)

        sr = tk.Frame(p, bg=C["BG"]); sr.grid(row=0, column=0, sticky="ew", pady=(0,5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_history())
        self.search_entry = tk.Entry(sr, textvariable=self.search_var, font=("Segoe UI",10),
                                      bg=C["PANEL"], fg=C["SUBTEXT"], insertbackground=C["TEXT"],
                                      relief="flat", bd=6)
        self.search_entry.insert(0, self.T("hist_search"))
        self.search_entry.bind("<FocusIn>",  self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.btn_export = tk.Button(sr, text=self.T("btn_export_csv"), font=("Segoe UI",9),
                                     bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                                     padx=8, pady=3, command=self._export_csv)
        self.btn_export.pack(side="right", padx=(5,0))
        self.btn_clr_hist = tk.Button(sr, text=self.T("btn_clear_hist"), font=("Segoe UI",9),
                                       bg=C["PANEL"], fg=C["ERROR"], relief="flat", cursor="hand2",
                                       padx=8, pady=3, command=self._clear_history)
        self.btn_clr_hist.pack(side="right", padx=(5,0))

        self.lbl_hist_count = tk.Label(p, text="", font=("Segoe UI",8), bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_hist_count.grid(row=1, column=0, sticky="w", pady=(0,3))

        tf = tk.Frame(p, bg=C["PANEL"]); tf.grid(row=2, column=0, sticky="nsew")
        cols = ("titulo","canal","formato","duracion","fecha","carpeta")
        self.hist_tree = ttk.Treeview(tf, columns=cols, show="headings", style="Hist.Treeview")
        for cid,w,lbl in [("titulo",248,self.T("col_title")),("canal",108,self.T("col_channel")),
                           ("formato",50,self.T("col_fmt")),  ("duracion",50,self.T("col_dur")),
                           ("fecha",86,self.T("col_date")),   ("carpeta",148,self.T("col_folder"))]:
            self.hist_tree.heading(cid, text=lbl)
            self.hist_tree.column(cid, width=w, anchor="w", stretch=(cid=="titulo"))
        vsb = tk.Scrollbar(tf, orient="vertical",   command=self.hist_tree.yview)
        hsb = tk.Scrollbar(tf, orient="horizontal", command=self.hist_tree.xview)
        self.hist_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.hist_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns"); hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1); tf.columnconfigure(0, weight=1)
        self.hist_tree.bind("<Double-1>", self._open_hist_folder)

        # Reproductor
        pb = tk.Frame(p, bg=C["PANEL2"]); pb.grid(row=3, column=0, sticky="ew", pady=(5,0))
        self.lbl_dblclick = tk.Label(pb, text=self.T("dblclick_hint"), font=("Segoe UI",8),
                                      bg=C["PANEL2"], fg=C["SUBTEXT"])
        self.lbl_dblclick.pack(side="left", padx=10, pady=4)
        self.btn_stop_player = tk.Button(pb, text=self.T("btn_stop"), font=("Segoe UI",9,"bold"),
                                          bg=C["PANEL2"], fg=C["WARNING"], relief="flat",
                                          cursor="hand2", padx=10, pady=3, state="disabled",
                                          command=self._stop_player)
        self.btn_stop_player.pack(side="right", padx=6, pady=3)
        self.btn_play_player = tk.Button(pb, text=self.T("btn_play"), font=("Segoe UI",9,"bold"),
                                          bg=C["SUCCESS"], fg=C["BG"], relief="flat",
                                          cursor="hand2", padx=10, pady=3, command=self._play_selected)
        self.btn_play_player.pack(side="right", padx=(0,4), pady=3)
        self.lbl_now_playing = tk.Label(pb, text="", font=("Segoe UI",8),
                                         bg=C["PANEL2"], fg=C["SUCCESS"])
        self.lbl_now_playing.pack(side="right", padx=6)

        # Stats
        so = tk.Frame(p, bg=C["PANEL2"]); so.grid(row=4, column=0, sticky="ew", pady=(5,0))
        self.stats_labels = {}
        for i,k in enumerate(["stats_total","stats_fmt","stats_platform","stats_mb"]):
            cf = tk.Frame(so, bg=C["PANEL2"]); cf.grid(row=0, column=i, padx=16, pady=7)
            tk.Label(cf, text=self.T(k), font=("Segoe UI",8), bg=C["PANEL2"], fg=C["SUBTEXT"]).pack()
            lbl = tk.Label(cf, text="—", font=("Segoe UI",12,"bold"), bg=C["PANEL2"], fg=C["ACCENT"])
            lbl.pack(); self.stats_labels[k] = lbl

    # ════════════════════════════════════════════════════════════════════════
    # TAB AJUSTES
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_settings(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=30, pady=20)
        p.pack(fill="both", expand=True); p.columnconfigure(1, weight=1)

        def lbl(r, key):
            tk.Label(p, text=self.T(key), font=("Segoe UI",10),
                     bg=C["BG"], fg=C["TEXT"]).grid(row=r, column=0, sticky="w", pady=7, padx=(0,16))

        def sep(r):
            tk.Frame(p, bg=C["PANEL"], height=1).grid(row=r, column=0, columnspan=2,
                                                        sticky="ew", pady=(8,10))

        # Proxy
        lbl(0,"proxy_lbl")
        self.proxy_var = tk.StringVar(value=self.cfg.get("proxy",""))
        tk.Entry(p, textvariable=self.proxy_var, font=("Segoe UI",10),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=6).grid(row=0, column=1, sticky="ew", pady=7)

        # Throttle
        lbl(1,"throttle_lbl")
        thr_f = tk.Frame(p, bg=C["BG"]); thr_f.grid(row=1, column=1, sticky="ew", pady=7)
        self.throttle_var = tk.StringVar(value=self.cfg.get("throttle",""))
        tk.Entry(thr_f, textvariable=self.throttle_var, font=("Segoe UI",10),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=6, width=12).pack(side="left")
        tk.Label(thr_f, text="  e.g. 500K · 2M  (vacío = sin límite)",
                 font=("Segoe UI",8), bg=C["BG"], fg=C["SUBTEXT"]).pack(side="left", padx=6)

        # Cookies
        lbl(2,"cookies_lbl")
        BROWSERS = [self.T("cookies_none"),"chrome","firefox","edge","safari","brave","opera"]
        self.cookies_var = tk.StringVar(value=self.cfg.get("cookies","none"))
        ttk.Combobox(p, textvariable=self.cookies_var, values=BROWSERS,
                      state="readonly", width=14, font=("Segoe UI",10)).grid(
                      row=2, column=1, sticky="w", pady=7)

        # Paralelo
        lbl(3,"concurrent_lbl")
        conc_f = tk.Frame(p, bg=C["BG"]); conc_f.grid(row=3, column=1, sticky="w", pady=7)
        self.concurrent_var = tk.IntVar(value=self.cfg.get("concurrent",1))
        for n in [1,2,3,4]:
            tk.Radiobutton(conc_f, text=str(n), variable=self.concurrent_var, value=n,
                           font=("Segoe UI",10), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=8)

        # Reintentos
        lbl(4,"retries_lbl")
        ret_f = tk.Frame(p, bg=C["BG"]); ret_f.grid(row=4, column=1, sticky="w", pady=7)
        self.retries_var = tk.IntVar(value=self.cfg.get("retries",3))
        for n in [0,1,2,3,5]:
            tk.Radiobutton(ret_f, text=str(n), variable=self.retries_var, value=n,
                           font=("Segoe UI",10), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=8)

        sep(5)

        # Tema
        lbl(6,"theme_lbl")
        theme_f = tk.Frame(p, bg=C["BG"]); theme_f.grid(row=6, column=1, sticky="w", pady=7)
        self.theme_var = tk.StringVar(value=self.cfg.get("theme","dark"))
        for val, key in [("dark","theme_dark"),("light","theme_light")]:
            tk.Radiobutton(theme_f, text=self.T(key), variable=self.theme_var, value=val,
                           font=("Segoe UI",10), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=(0,16))

        # Color de acento
        lbl(7,"accent_lbl")
        acc_f = tk.Frame(p, bg=C["BG"]); acc_f.grid(row=7, column=1, sticky="w", pady=7)
        self.accent_preview = tk.Label(acc_f, bg=self.cfg.get("accent","#e94560"),
                                        width=4, relief="flat")
        self.accent_preview.pack(side="left", padx=(0,8), ipady=8)
        self.accent_var = tk.StringVar(value=self.cfg.get("accent","#e94560"))
        tk.Label(acc_f, textvariable=self.accent_var, font=("Consolas",9),
                 bg=C["BG"], fg=C["TEXT"]).pack(side="left", padx=(0,8))
        tk.Button(acc_f, text=self.T("btn_pick_accent"), font=("Segoe UI",9),
                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=8, pady=3, command=self._pick_accent).pack(side="left")

        sep(8)

        # Guardar
        save_f = tk.Frame(p, bg=C["BG"]); save_f.grid(row=9, column=0, columnspan=2, sticky="w")
        self.btn_save_cfg = tk.Button(save_f, text=self.T("btn_save_settings"),
                                       font=("Segoe UI",11,"bold"), bg=C["ACCENT2"], fg=C["TEXT"],
                                       relief="flat", cursor="hand2", padx=16, pady=8,
                                       command=self._save_settings)
        self.btn_save_cfg.pack(side="left")
        self.lbl_settings_status = tk.Label(save_f, text="", font=("Segoe UI",9),
                                             bg=C["BG"], fg=C["SUCCESS"])
        self.lbl_settings_status.pack(side="left", padx=12)

        sep(10)

        # Actualizar yt-dlp
        upd_f = tk.Frame(p, bg=C["BG"]); upd_f.grid(row=11, column=0, columnspan=2, sticky="w")
        self.btn_update = tk.Button(upd_f, text=self.T("btn_update_ytdlp"),
                                     font=("Segoe UI",11,"bold"), bg=C["PANEL2"], fg=C["TEXT"],
                                     relief="flat", cursor="hand2", padx=16, pady=8,
                                     command=self._update_ytdlp)
        self.btn_update.pack(side="left")
        self.lbl_update_status = tk.Label(upd_f, text="", font=("Segoe UI",9),
                                           bg=C["BG"], fg=C["SUCCESS"])
        self.lbl_update_status.pack(side="left", padx=12)

    # ════════════════════════════════════════════════════════════════════════
    # COLA — helpers + menú contextual
    # ════════════════════════════════════════════════════════════════════════
    def _add_to_queue(self):
        raw = self.url_text.get("1.0","end").strip()
        if not raw: return
        added = 0
        for line in raw.splitlines():
            url = line.strip()
            if url and url not in self.queue:
                self.queue.append(url)
                self.queue_list.insert("end", (url[:74]+"…") if len(url)>74 else url)
                added += 1
        self._update_queue_count()
        if added: self._set_status(self.T("status_added",n=added), self.C["SUCCESS"])
        self._clear_url()

    def _remove_from_queue(self):
        for idx in reversed(self.queue_list.curselection()):
            self.queue.pop(idx); self.queue_list.delete(idx)
        self._update_queue_count()

    def _clear_queue(self):
        self.queue.clear(); self.queue_list.delete(0,"end"); self._update_queue_count()

    def _update_queue_count(self):
        self.lbl_queue_count.configure(text=self.T("in_queue",n=len(self.queue)))

    def _show_ctx_menu(self, event):
        """Selecciona el item bajo el cursor y muestra menú contextual."""
        idx = self.queue_list.nearest(event.y)
        if idx >= 0:
            self.queue_list.selection_clear(0,"end")
            self.queue_list.selection_set(idx)
            self.queue_list.activate(idx)
        try: self.ctx_menu.tk_popup(event.x_root, event.y_root)
        finally: self.ctx_menu.grab_release()

    def _ctx_move_up(self):
        sel = self.queue_list.curselection()
        if not sel or sel[0] == 0: return
        i = sel[0]
        self.queue[i-1], self.queue[i] = self.queue[i], self.queue[i-1]
        txt_i   = self.queue_list.get(i)
        txt_im1 = self.queue_list.get(i-1)
        self.queue_list.delete(i-1, i)
        self.queue_list.insert(i-1, txt_i); self.queue_list.insert(i, txt_im1)
        self.queue_list.selection_set(i-1)

    def _ctx_move_down(self):
        sel = self.queue_list.curselection()
        if not sel or sel[0] >= len(self.queue)-1: return
        i = sel[0]
        self.queue[i], self.queue[i+1] = self.queue[i+1], self.queue[i]
        txt_i   = self.queue_list.get(i)
        txt_ip1 = self.queue_list.get(i+1)
        self.queue_list.delete(i, i+1)
        self.queue_list.insert(i, txt_ip1); self.queue_list.insert(i+1, txt_i)
        self.queue_list.selection_set(i+1)

    def _ctx_open_browser(self):
        sel = self.queue_list.curselection()
        if not sel: return
        open_url_browser(self.queue[sel[0]])

    # ════════════════════════════════════════════════════════════════════════
    # HELPERS UI
    # ════════════════════════════════════════════════════════════════════════
    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg+"\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, msg, color=None):
        if color is None: color = self.C["TEXT"]
        self.lbl_status.configure(text=msg, fg=color)

    def _choose_folder(self):
        d = filedialog.askdirectory(initialdir=self.output_dir)
        if d:
            self.output_dir = d; self.lbl_folder.configure(text=d)
            self.cfg["output_dir"] = d; save_config(self.cfg)

    def _clear_url(self): self.url_text.delete("1.0","end")

    def _on_format_change(self, _=None):
        fmt = self.format_var.get()
        (self.qual_frame.pack_forget if fmt in ("FLAC","WAV") else lambda: self.qual_frame.pack(side="left"))()
        self.cfg["format"] = fmt; save_config(self.cfg)

    def _on_dnd_drop(self, event):
        data = event.data.strip().strip("{}")
        if data:
            cur = self.url_text.get("1.0","end").strip()
            self.url_text.insert("end", ("\n" if cur else "") + data)

    def _search_focus_in(self, e):
        if self.search_entry.get() == self.T("hist_search"):
            self.search_entry.delete(0,"end"); self.search_entry.configure(fg=self.C["TEXT"])

    def _search_focus_out(self, e):
        if not self.search_entry.get():
            self.search_entry.insert(0, self.T("hist_search"))
            self.search_entry.configure(fg=self.C["SUBTEXT"])

    def _change_lang(self, _=None):
        self.lang = self.lang_var.get().lower()
        self.cfg["lang"] = self.lang; save_config(self.cfg)
        self._reload_theme()   # reconstruye UI con nuevos strings

    def _show_about(self):
        messagebox.showinfo(self.T("about_title"), self.T("about_text"))

    # ════════════════════════════════════════════════════════════════════════
    # FETCH INFO + THUMBNAIL
    # ════════════════════════════════════════════════════════════════════════
    def _start_fetch_info(self):
        raw = self.url_text.get("1.0","end").strip()
        urls = [l.strip() for l in raw.splitlines() if l.strip()]
        if not urls: return
        self._set_status(self.T("status_fetching"), self.C["SUBTEXT"])
        threading.Thread(target=self._fetch_info, args=(urls[0],), daemon=True).start()

    def _fetch_info(self, url):
        try:
            with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True,"skip_download":True}) as ydl:
                info = ydl.extract_info(url, download=False)
            thumb_url = None
            if info.get("_type") == "playlist":
                entries = list(info.get("entries",[]))
                title   = f"🎵 Playlist: {info.get('title','—')}  ({len(entries)} tracks)"
                channel = info.get("uploader","—"); dur_str = f"{len(entries)} tracks"
                cr_text,cr_color = "📋 Playlist — todos los tracks serán descargados", self.C["WARNING"]
                thumb_url = (entries[0] or {}).get("thumbnail") if entries else None
            else:
                title   = info.get("title","Desconocido"); channel = info.get("uploader","—")
                m,s     = divmod(info.get("duration",0) or 0, 60); dur_str = f"{m}:{s:02d}"
                thumb_url = info.get("thumbnail")
                blocked = info.get("availability") in ("needs_auth","subscriber_only","premium_only")
                if blocked or bool(info.get("copyright_text")):
                    cr_text,cr_color = "⚠️  Posible COPYRIGHT detectado", self.C["WARNING"]
                elif info.get("age_limit",0)>0:
                    cr_text,cr_color = "🔞  Contenido restringido", self.C["WARNING"]
                elif info.get("license",""):
                    cr_text,cr_color = f"📄  Licencia: {info['license']}", self.C["SUCCESS"]
                else:
                    cr_text,cr_color = "✅  Sin restricciones detectadas", self.C["SUCCESS"]

            self.after(0, lambda: (
                self.lbl_title.configure(text=title),
                self.lbl_channel.configure(text=f"Canal/Autor: {channel}"),
                self.lbl_duration.configure(text=f"Duración: {dur_str}"),
                self.lbl_copyright.configure(text=cr_text, fg=cr_color),
                self._set_status(self.T("status_info_ok"), self.C["SUCCESS"])
            ))
            self._log(f"INFO: {title}")
            if thumb_url and HAS_PIL:
                threading.Thread(target=self._load_thumbnail, args=(thumb_url,), daemon=True).start()
        except Exception as e:
            self.after(0, lambda: self._set_status(f"Error: {e}", self.C["ERROR"]))
            self._log(f"ERROR fetch: {e}")

    def _load_thumbnail(self, url):
        try:
            with urlopen(url, timeout=6) as r: data = r.read()
            img   = Image.open(io.BytesIO(data)).resize((112,63), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._thumb_img = photo
            self.after(0, lambda: self.lbl_thumb.configure(image=photo, text=""))
        except Exception:
            self.after(0, lambda: self.lbl_thumb.configure(image="", text="🖼", font=("Segoe UI",22)))

    # ════════════════════════════════════════════════════════════════════════
    # DESCARGA
    # ════════════════════════════════════════════════════════════════════════
    def _build_ydl_opts(self, fmt, quality, template, hook):
        codec = FORMATS[fmt]["codec"]
        pp    = [{"key":"FFmpegExtractAudio","preferredcodec":codec}]
        if FORMATS[fmt]["lossy"]: pp[0]["preferredquality"] = quality
        pp.append({"key":"FFmpegMetadata","add_metadata":True})
        if fmt == "MP3": pp.append({"key":"EmbedThumbnail"})
        opts = {
            "format":"bestaudio/best",
            "outtmpl":os.path.join(self.output_dir, template+".%(ext)s"),
            "progress_hooks":[hook], "quiet":True, "no_warnings":True,
            "writethumbnail":(fmt=="MP3"), "postprocessors":pp,
            "concurrent_fragment_downloads":self.cfg.get("concurrent",1),
        }
        if self.cfg.get("proxy","").strip():   opts["proxy"]       = self.cfg["proxy"].strip()
        if self.cfg.get("throttle","").strip(): opts["ratelimit"]   = self.cfg["throttle"].strip()
        c = self.cfg.get("cookies","none")
        if c and c not in ("none", self.T("cookies_none")): opts["cookiesfrombrowser"] = (c,)
        return opts

    def _start_queue(self):
        if self.is_downloading: return
        if self.url_text.get("1.0","end").strip() and not self.queue: self._add_to_queue()
        if not self.queue:
            messagebox.showwarning(self.T("warn_empty_q_title"), self.T("warn_empty_queue")); return
        self.is_downloading = True; self._completed = 0; self._cancel_evt.clear()
        self.btn_download.configure(state="disabled", text=self.T("downloading"))
        self.btn_cancel.configure(state="normal")
        self.cfg.update({"format":self.format_var.get(),"quality":self.quality_var.get(),
                         "template":self.template_var.get()}); save_config(self.cfg)
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _cancel_download(self):
        self._cancel_evt.set(); self.btn_cancel.configure(state="disabled")
        self._set_status(self.T("status_cancelled"), self.C["WARNING"])

    def _process_queue(self):
        total = len(self.queue); concurrent = max(1, self.cfg.get("concurrent",1))
        if concurrent > 1:
            sem = threading.Semaphore(concurrent); threads = []
            for i,url in enumerate(list(self.queue),1):
                if self._cancel_evt.is_set(): break
                def run(u=url,ix=i):
                    with sem:
                        if not self._cancel_evt.is_set(): self._download_one(u,ix,total)
                t=threading.Thread(target=run,daemon=True); t.start(); threads.append(t)
            for t in threads: t.join()
        else:
            for i,url in enumerate(list(self.queue),1):
                if self._cancel_evt.is_set(): self._log(self.T("cancelled_log")); break
                self.after(0,lambda i=i,t=total: self._set_status(f"[{i}/{t}] Preparando…", self.C["SUBTEXT"]))
                self._log(f"\n▶ [{i}/{total}] {url}")
                self._download_one(url,i,total)
        self.after(0, self._queue_finished)

    def _download_one(self, url, idx, total):
        if self._cancel_evt.is_set(): return
        fmt     = self.format_var.get(); quality = self.quality_var.get()
        template= self.template_var.get().strip() or "%(title)s"
        max_retries = self.cfg.get("retries",3)

        def hook(d):
            if self._cancel_evt.is_set(): raise yt_dlp.utils.DownloadError("cancelled")
            if d["status"] == "downloading":
                try:
                    pct  = float(d.get("_percent_str","0%").strip().replace("%",""))
                    eta  = d.get("_eta_str","—"); speed = d.get("_speed_str","")
                    self.after(0, lambda p=pct: self.progress_var.set(p))
                    self.after(0, lambda p=pct,e=eta,sp=speed:
                        self._set_status(self.T("status_eta",i=idx,t=total,pct=p,speed=sp,eta=e), self.C["TEXT"]))
                except ValueError: pass
            elif d["status"] == "finished":
                self.after(0, lambda: self.progress_var.set(100))
                self.after(0, lambda: self._set_status(
                    f"[{idx}/{total}] {self.T('status_converting')}", self.C["SUBTEXT"]))

        opts = self._build_ydl_opts(fmt, quality, template, hook)

        for attempt in range(max_retries+1):
            if self._cancel_evt.is_set(): return
            if attempt > 0: self._log(self.T("retry_log",n=attempt,max=max_retries))
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                entries = ([e for e in info.get("entries",[]) if e]
                           if info.get("_type")=="playlist" else [info])
                now = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
                for e in entries:
                    m,s = divmod(e.get("duration",0) or 0, 60)
                    fn  = template
                    for var in ["title","uploader","artist"]:
                        fn = fn.replace(f"%({var})s", e.get(var,"") or "")
                    ext = FORMATS[fmt]["codec"].replace("vorbis","ogg")
                    self.history.append({
                        "titulo":e.get("title","—"),"canal":e.get("uploader","—"),
                        "formato":fmt,"duracion":f"{m}:{s:02d}","fecha":now,
                        "carpeta":self.output_dir,
                        "filepath":os.path.join(self.output_dir, fn.strip()+f".{ext}"),
                    })
                    self._completed += 1
                save_history(self.history)
                self.after(0, self._refresh_history); self.after(0, self._refresh_stats)
                self._log(f"✅ {url}")
                return   # éxito — salir del loop de reintentos

            except yt_dlp.utils.DownloadError as e:
                msg = str(e)
                if "cancelled" in msg.lower(): return
                if "ffmpeg" in msg.lower():
                    self._log("⚠️  FFmpeg no encontrado — descargando sin conversión")
                    opts_raw = {k:v for k,v in opts.items() if k not in ("postprocessors","writethumbnail")}
                    try:
                        with yt_dlp.YoutubeDL(opts_raw) as ydl: ydl.download([url])
                        self._log("✅ Audio sin conversión"); self._completed+=1
                    except Exception as e2: self._log(f"ERROR fallback: {e2}")
                    return
                # Error de red/otro → reintento si quedan intentos
                if attempt < max_retries:
                    self._log(f"⚠️  Error (intento {attempt+1}): {msg[:80]}")
                else:
                    self._log(f"❌ Fallido tras {max_retries+1} intentos: {msg[:80]}")
                    self.after(0, lambda m=msg: self._set_status(f"Error: {m[:60]}", self.C["ERROR"]))
            except Exception as e:
                self._log(f"ERROR inesperado: {e}"); return

    def _queue_finished(self):
        n=self._completed; fmt=self.format_var.get()
        self._clear_queue(); self.progress_var.set(0)
        self.is_downloading=False
        self.btn_download.configure(state="normal",text=self.T("btn_download"))
        self.btn_cancel.configure(state="disabled")
        if not self._cancel_evt.is_set():
            self._set_status(self.T("status_done",n=n,fmt=fmt,folder=self.output_dir), self.C["SUCCESS"])
            desktop_notify(self.T("notif_title"), self.T("notif_msg",n=n,fmt=fmt))

    # ════════════════════════════════════════════════════════════════════════
    # HISTORIAL
    # ════════════════════════════════════════════════════════════════════════
    def _refresh_history(self, records=None):
        if records is None: records = self.history
        self.hist_tree.delete(*self.hist_tree.get_children())
        for r in reversed(records):
            self.hist_tree.insert("","end",values=(
                r.get("titulo","—"),r.get("canal","—"),r.get("formato","—"),
                r.get("duracion","—"),r.get("fecha","—"),r.get("carpeta","—")))
        self.lbl_hist_count.configure(text=self.T("hist_entries",n=len(records)))

    def _filter_history(self):
        try:
            if not self.hist_tree.winfo_exists(): return   # widget destruido durante reload
        except Exception:
            return
        q=self.search_var.get().lower(); ph=self.T("hist_search").lower()
        if not q or q==ph: self._refresh_history(); return
        self._refresh_history([r for r in self.history
                               if q in r.get("titulo","").lower() or q in r.get("canal","").lower()])

    def _open_hist_folder(self, _):
        sel = self.hist_tree.focus()
        if not sel: return
        vals = self.hist_tree.item(sel,"values")
        if len(vals)>=6: open_folder(vals[5])

    def _clear_history(self):
        if messagebox.askyesno(self.T("confirm_title"),self.T("confirm_clear")):
            self.history.clear(); save_history(self.history)
            self._refresh_history(); self._refresh_stats()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
               filetypes=[("CSV","*.csv")], initialfile="historial.csv")
        if not path: return
        try:
            with open(path,"w",newline="",encoding="utf-8-sig") as f:
                w=csv.DictWriter(f,fieldnames=["titulo","canal","formato","duracion","fecha","carpeta"])
                w.writeheader()
                w.writerows({k:v for k,v in r.items() if k!="filepath"} for r in self.history)
            self._log(self.T("csv_saved",path=path))
            self._set_status(self.T("csv_saved",path=path), self.C["SUCCESS"])
        except Exception as e: self._log(f"ERROR CSV: {e}")

    def _refresh_stats(self):
        h=self.history
        top_fmt = Counter(r.get("formato","?") for r in h).most_common(1)[0][0] if h else "—"
        top_ch  = Counter(r.get("canal","?")   for r in h).most_common(1)[0][0] if h else "—"
        self.stats_labels["stats_total"].configure(text=str(len(h)))
        self.stats_labels["stats_fmt"].configure(text=top_fmt)
        self.stats_labels["stats_platform"].configure(text=(top_ch[:18] if h else "—"))
        self.stats_labels["stats_mb"].configure(text=f"{estimate_mb(h)} MB")

    # ════════════════════════════════════════════════════════════════════════
    # REPRODUCTOR
    # ════════════════════════════════════════════════════════════════════════
    def _play_selected(self):
        if not HAS_PYGAME: messagebox.showinfo("pygame",self.T("pygame_missing")); return
        sel = self.hist_tree.focus()
        if not sel: return
        vals=self.hist_tree.item(sel,"values"); titulo=vals[0] if vals else ""; carpeta=vals[5] if len(vals)>=6 else self.output_dir
        audio_path=None
        for r in reversed(self.history):
            if r.get("titulo","")==titulo:
                fp=r.get("filepath","")
                if fp and os.path.exists(fp): audio_path=fp; break
        if not audio_path and os.path.isdir(carpeta):
            nc=titulo[:30].lower().replace("/","").replace("\\","").replace(":","")
            for fn in os.listdir(carpeta):
                if nc and nc in fn.lower(): audio_path=os.path.join(carpeta,fn); break
        if not audio_path: messagebox.showinfo("",self.T("no_audio_file")); return
        try:
            pygame.mixer.music.load(audio_path); pygame.mixer.music.play()
            self.lbl_now_playing.configure(text=f"♪ {os.path.basename(audio_path)[:38]}")
            self.btn_stop_player.configure(state="normal")
        except Exception as e: messagebox.showerror("",str(e))

    def _stop_player(self):
        if HAS_PYGAME:
            try: pygame.mixer.music.stop()
            except Exception: pass
        self.lbl_now_playing.configure(text=""); self.btn_stop_player.configure(state="disabled")

    # ════════════════════════════════════════════════════════════════════════
    # AJUSTES
    # ════════════════════════════════════════════════════════════════════════
    def _pick_accent(self):
        color = colorchooser.askcolor(color=self.accent_var.get(), title="Color de acento")
        if color and color[1]:
            self.accent_var.set(color[1])
            self.accent_preview.configure(bg=color[1])

    def _save_settings(self):
        self.cfg.update({
            "proxy":      self.proxy_var.get().strip(),
            "throttle":   self.throttle_var.get().strip(),
            "cookies":    self.cookies_var.get(),
            "concurrent": self.concurrent_var.get(),
            "retries":    self.retries_var.get(),
            "theme":      self.theme_var.get(),
            "accent":     self.accent_var.get(),
        }); save_config(self.cfg)
        self.lbl_settings_status.configure(text=self.T("settings_saved"))
        self.after(3000, lambda: self.lbl_settings_status.configure(text=""))
        # Recarga tema si cambió
        self._reload_theme()

    def _update_ytdlp(self):
        self.btn_update.configure(state="disabled")
        self.lbl_update_status.configure(text=self.T("updating"), fg=self.C["WARNING"])
        threading.Thread(target=self._do_update, daemon=True).start()

    def _do_update(self):
        try:
            r=subprocess.run([sys.executable,"-m","pip","install","-U","yt-dlp"],
                             capture_output=True,text=True,timeout=60)
            if r.returncode==0:
                self.after(0,lambda: self.lbl_update_status.configure(text=self.T("update_ok"),fg=self.C["SUCCESS"]))
                self._log(self.T("update_ok"))
            else:
                err=(r.stderr.strip().splitlines()[-1] if r.stderr else "unknown")
                self.after(0,lambda e=err: self.lbl_update_status.configure(text=self.T("update_fail",err=e),fg=self.C["ERROR"]))
        except Exception as e:
            self.after(0,lambda e=e: self.lbl_update_status.configure(text=self.T("update_fail",err=str(e)),fg=self.C["ERROR"]))
        finally:
            self.after(0,lambda: self.btn_update.configure(state="normal"))


if __name__ == "__main__":
    app = App()
    app.geometry("840x820"); app.minsize(740,720)
    app.mainloop()

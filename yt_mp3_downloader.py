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
    import mutagen
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC, error as MutagenError
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

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

try:
    import pystray
    from pystray import MenuItem as TrayItem
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

try:
    import syncedlyrics
    HAS_LYRICS = True
except ImportError:
    HAS_LYRICS = False


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

FAVORITES_FILE = os.path.join(os.path.expanduser("~"), ".favorites.json")
PROFILES_FILE  = os.path.join(os.path.expanduser("~"), ".profiles.json")

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return []

def save_favorites(favs):
    try:
        with open(FAVORITES_FILE,"w",encoding="utf-8") as f: json.dump(favs,f,ensure_ascii=False,indent=2)
    except Exception: pass

def load_profiles():
    defaults = [
        {"name":"Música HQ","format":"MP3","quality":"320","template":"%(title)s"},
        {"name":"Podcast",  "format":"MP3","quality":"128","template":"%(title)s"},
        {"name":"Lossless", "format":"FLAC","quality":"320","template":"%(title)s"},
    ]
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return defaults

def save_profiles(profiles):
    try:
        with open(PROFILES_FILE,"w",encoding="utf-8") as f: json.dump(profiles,f,ensure_ascii=False,indent=2)
    except Exception: pass

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
        "BG":"#111318","PANEL":"#1c1f26","PANEL2":"#22252e",
        "SIDEBAR":"#16181f","SIDEBAR_ACTIVE":"#2a2d38",
        "ACCENT":"#e94560","ACCENT2":"#1e3a5f",
        "ACCENT_SOFT":"#1e2535",
        "TEXT":"#e8eaf0","SUBTEXT":"#8b909e","MUTED":"#555a68",
        "SUCCESS":"#3dd68c","WARNING":"#f5a623","ERROR":"#f06565",
        "HIST_BG":"#0e1015","BORDER":"#2a2d38","CARD":"#1c1f26",
    },
    "light": {
        "BG":"#f4f6fa","PANEL":"#ffffff","PANEL2":"#eef0f6",
        "SIDEBAR":"#ffffff","SIDEBAR_ACTIVE":"#eef2ff",
        "ACCENT":"#e94560","ACCENT2":"#3b5bdb",
        "ACCENT_SOFT":"#eef2ff",
        "TEXT":"#1a1d27","SUBTEXT":"#5c6070","MUTED":"#9ca3af",
        "SUCCESS":"#16a34a","WARNING":"#d97706","ERROR":"#dc2626",
        "HIST_BG":"#f9fafb","BORDER":"#e2e6f0","CARD":"#ffffff",
    },
}

# ─── Strings i18n ─────────────────────────────────────────────────────────────
STRINGS = {
    "es": {
        "app_title":"Audio Downloader",
        "tab_download":"  Descargar  ","tab_history":"  Historial  ",
        "tab_settings":"  Ajustes  ",
        "url_label":"URL  (una por línea — arrastra desde el navegador o pega aquí)",
        "btn_info":"Ver Info","btn_add":"Añadir a cola","btn_clear_url":"Limpiar",
        "folder_lbl":"Carpeta:","btn_change":"Cambiar","btn_open_folder":"Abrir carpeta",
        "fmt_lbl":"Formato:","quality_lbl":"Calidad:","template_lbl":"Nombre archivo:",
        "queue_lbl":"Cola de descarga","btn_remove":"Eliminar",
        "btn_clear_q":"Vaciar cola","in_queue":"{n} en cola",
        "btn_cancel":"Cancelar","btn_download":"DESCARGAR COLA",
        "downloading":"Descargando…","log_lbl":"Log",
        "status_paste":"Pega URLs o arrástralas desde el navegador",
        "status_fetching":"Obteniendo información…","status_info_ok":"Info cargada.",
        "status_added":"{n} URL(s) añadidas.","status_converting":"Convirtiendo…",
        "status_done":"✅ {n} archivo(s) {fmt} en: {folder}",
        "status_cancelled":"⏹ Cancelada.","status_eta":"[{i}/{t}] {pct:.1f}%  {speed}  ETA {eta}",
        "warn_empty_queue":"Añade al menos una URL.","warn_empty_q_title":"Cola vacía",
        "notif_title":"Audio Downloader — ¡Listo!","notif_msg":"{n} archivo(s) {fmt} descargados.",
        "hist_search":"Buscar…","btn_clear_hist":"Borrar historial",
        "btn_export_csv":"Exportar CSV","hist_entries":"{n} entrada(s)",
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
        "btn_save_settings":"Guardar ajustes","settings_saved":"✅ Guardado.",
        "btn_update_ytdlp":"Actualizar yt-dlp","updating":"Actualizando…",
        "update_ok":"✅ yt-dlp actualizado.","update_fail":"❌ Error: {err}",
        "no_audio_file":"No se encontró el archivo. ¿Ya fue descargado?",
        "pygame_missing":"Instala pygame:\npip install pygame",
        "ctx_move_up":"Mover arriba","ctx_move_down":"Mover abajo",
        "ctx_open_browser":"Abrir en navegador","ctx_remove":"Eliminar",
        "about_title":"Acerca de","about_text":"Audio Downloader \n\nHecho por Maken\nLicencia MIT · Eres libre de usarlo, modificarlo y redistribuirlo como quieras.\n\nMotor: yt-dlp  |  UI: Python/Tkinter",
        "btn_about":"Acerca de",
        "tab_convert":"  Convertir  ",
        "tab_video":"  Vídeo  ",
        "tab_lyrics":"  Letras  ",
        "convert_src":"Archivo origen:","convert_open":"Abrir","convert_fmt":"Formato destino:",
        "convert_btn":"Convertir","convert_done":"✅ Convertido: {path}","convert_err":"❌ Error: {err}",
        "convert_no_file":"Selecciona un archivo primero.","convert_no_ffmpeg":"FFmpeg no encontrado.",
        "video_url_lbl":"URL de YouTube (vídeo):","video_quality":"Calidad:","video_btn":"Descargar Vídeo",
        "video_done":"✅ Vídeo guardado en: {folder}","video_subs":"Subtítulos (si disponibles)",
        "lyrics_query":"Artista — Canción:","lyrics_btn":"Buscar letra","lyrics_searching":"Buscando…",
        "lyrics_save":"Guardar .lrc","lyrics_saved":"✅ .lrc guardado: {path}",
        "lyrics_not_found":"No se encontraron letras sincronizadas.",
        "preview_btn":"▶ Preview 30s","preview_stop":"⏹ Parar preview","preview_loading":"Cargando preview…",
        "auto_organize":"Auto-organizar por artista/álbum",
        "tab_search":"  Buscar  ",
        "search_placeholder":"Buscar canción, artista o álbum…",
        "btn_search":"Buscar","search_results":"Resultados",
        "btn_add_result":"Añadir a cola","no_results":"Sin resultados.",
        "searching":"Buscando…",
        "tab_charts":"  Gráficas  ",
        "chart_monthly":"Descargas por mes","chart_formats":"Formatos",
        "no_data_chart":"Sin datos aún. Descarga algo primero.",
        "schedule_lbl":"⏰ Programar inicio de cola:",
        "schedule_hint":"Formato HH:MM  (vacío = ahora)","schedule_set":"⏰ Programado para {t}",
        "schedule_cancel":"Cancelar programación","schedule_cancelled":"Programación cancelada.",
        "tab_metadata":"  Metadatos  ",
        "meta_pick":"Selecciona un MP3 del historial o…",
        "meta_open":"Abrir MP3","meta_title":"Título","meta_artist":"Artista",
        "meta_album":"Álbum","meta_year":"Año","meta_genre":"Género",
        "meta_save":"Guardar metadatos","meta_saved":"✅ Metadatos guardados.",
        "meta_error":"❌ Error: {err}","meta_no_mutagen":"Instala mutagen:\npip install mutagen",
        "meta_no_file":"Selecciona un archivo MP3 primero.",
    },
    "en": {
        "app_title":"Audio Downloader",
        "tab_download":"  Download  ","tab_history":"  History  ",
        "tab_settings":"  Settings  ",
        "url_label":"URL  (one per line — drag from browser or paste here)",
        "btn_info":"Get Info","btn_add":"Add to queue","btn_clear_url":"Clear",
        "folder_lbl":"Folder:","btn_change":"Change","btn_open_folder":"Open folder",
        "fmt_lbl":"Format:","quality_lbl":"Quality:","template_lbl":"Filename template:",
        "queue_lbl":"Download queue","btn_remove":"Remove",
        "btn_clear_q":"Clear queue","in_queue":"{n} in queue",
        "btn_cancel":"Cancel","btn_download":"DOWNLOAD QUEUE",
        "downloading":"Downloading…","log_lbl":"Log",
        "status_paste":"Paste URLs or drag them from your browser",
        "status_fetching":"Fetching info…","status_info_ok":"Info loaded.",
        "status_added":"{n} URL(s) added.","status_converting":"Converting…",
        "status_done":"✅ {n} {fmt} file(s) in: {folder}",
        "status_cancelled":"⏹ Cancelled.","status_eta":"[{i}/{t}] {pct:.1f}%  {speed}  ETA {eta}",
        "warn_empty_queue":"Add at least one URL.","warn_empty_q_title":"Empty queue",
        "notif_title":"Audio Downloader — Done!","notif_msg":"{n} {fmt} file(s) downloaded.",
        "hist_search":"Search…","btn_clear_hist":"Clear history",
        "btn_export_csv":"Export CSV","hist_entries":"{n} entries",
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
        "btn_save_settings":"Save settings","settings_saved":"✅ Saved.",
        "btn_update_ytdlp":"Update yt-dlp","updating":"Updating…",
        "update_ok":"✅ yt-dlp updated.","update_fail":"❌ Error: {err}",
        "no_audio_file":"File not found. Has it been downloaded?",
        "pygame_missing":"Install pygame:\npip install pygame",
        "ctx_move_up":"Move up","ctx_move_down":"Move down",
        "ctx_open_browser":"Open in browser","ctx_remove":"Remove",
        "about_title":"About","about_text":"Audio Downloader \n\nMade by Maken\nMIT License · You are free to use, modify, and redistribute it as you wish.\n\nEngine: yt-dlp  |  UI: Python/Tkinter",
        "btn_about":"About",
        "tab_convert":"  Convert  ",
        "tab_video":"  Video  ",
        "tab_lyrics":"  Lyrics  ",
        "convert_src":"Source file:","convert_open":"Open","convert_fmt":"Target format:",
        "convert_btn":"Convert","convert_done":"✅ Converted: {path}","convert_err":"❌ Error: {err}",
        "convert_no_file":"Select a file first.","convert_no_ffmpeg":"FFmpeg not found.",
        "video_url_lbl":"YouTube URL (video):","video_quality":"Quality:","video_btn":"Download Video",
        "video_done":"✅ Video saved to: {folder}","video_subs":"Subtitles (if available)",
        "lyrics_query":"Artist — Song:","lyrics_btn":"Search lyrics","lyrics_searching":"Searching…",
        "lyrics_save":"Save .lrc","lyrics_saved":"✅ .lrc saved: {path}",
        "lyrics_not_found":"No synced lyrics found.",
        "preview_btn":"▶ Preview 30s","preview_stop":"⏹ Stop preview","preview_loading":"Loading preview…",
        "auto_organize":"Auto-organize by artist/album",
        "tab_search":"  Search  ",
        "search_placeholder":"Search song, artist or album…",
        "btn_search":"Search","search_results":"Results",
        "btn_add_result":"Add to queue","no_results":"No results.",
        "searching":"Searching…",
        "tab_charts":"  Charts  ",
        "chart_monthly":"Downloads per month","chart_formats":"Formats",
        "no_data_chart":"No data yet. Download something first.",
        "schedule_lbl":"⏰ Schedule queue start:",
        "schedule_hint":"Format HH:MM  (empty = now)","schedule_set":"⏰ Scheduled for {t}",
        "schedule_cancel":"Cancel schedule","schedule_cancelled":"Schedule cancelled.",
        "tab_metadata":"  Metadata  ",
        "meta_pick":"Select an MP3 from history or…",
        "meta_open":"Open MP3","meta_title":"Title","meta_artist":"Artist",
        "meta_album":"Album","meta_year":"Year","meta_genre":"Genre",
        "meta_save":"Save metadata","meta_saved":"✅ Metadata saved.",
        "meta_error":"❌ Error: {err}","meta_no_mutagen":"Install mutagen:\npip install mutagen",
        "meta_no_file":"Select an MP3 file first.",
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
        self.favorites      = load_favorites()
        self.profiles       = load_profiles()
        self._tray_icon     = None
        self._custom_cover  = None
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
        s.configure("TProgressbar", troughcolor=C["BORDER"], background=C["ACCENT"], thickness=6)
        s.configure("Hist.Treeview", background=C["HIST_BG"], foreground=C["TEXT"],
                    rowheight=28, fieldbackground=C["HIST_BG"], borderwidth=0, font=("Segoe UI",9))
        s.configure("Hist.Treeview.Heading", background=C["PANEL"], foreground=C["SUBTEXT"],
                    font=("Segoe UI",9,"bold"), relief="flat")
        s.map("Hist.Treeview", background=[("selected",C["ACCENT_SOFT"])],
                               foreground=[("selected",C["TEXT"])])

    def _reload_theme(self):
        self.C = self._build_theme()
        self._apply_styles()
        try:
            for name, _, cb in self.search_var.trace_info():
                self.search_var.trace_remove(name, cb)
        except Exception:
            pass
        for w in self.winfo_children(): w.destroy()
        self._sidebar_btns = {}
        self._content_frames = {}
        self._build_ui()
        self._refresh_history()
        self._refresh_stats()
        self._refresh_charts()

    # ── i18n ─────────────────────────────────────────────────────────────────
    def T(self, k, **kw):
        s = STRINGS[self.lang].get(k,k)
        return s.format(**kw) if kw else s

    # ════════════════════════════════════════════════════════════════════════
    # BUILD UI — Sidebar layout
    # ════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        C = self.C
        self.title(self.T("app_title"))
        self._active_section = "download"

        # ── Root layout: sidebar + main ──────────────────────────────────────
        root_frame = tk.Frame(self, bg=C["BG"])
        root_frame.pack(fill="both", expand=True)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        sidebar = tk.Frame(root_frame, bg=C["SIDEBAR"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(sidebar, bg=C["SIDEBAR"])
        logo_frame.pack(fill="x", pady=(16,8), padx=12)
        logo_icon = tk.Frame(logo_frame, bg=C["ACCENT"], width=34, height=34)
        logo_icon.pack(side="left"); logo_icon.pack_propagate(False)
        tk.Label(logo_icon, text="♪", font=("Segoe UI",16,"bold"),
                 bg=C["ACCENT"], fg="white").place(relx=0.5, rely=0.5, anchor="center")
        logo_txt = tk.Frame(logo_frame, bg=C["SIDEBAR"])
        logo_txt.pack(side="left", padx=(8,0))
        tk.Label(logo_txt, text="Downloader", font=("Segoe UI",13,"bold"),
                 bg=C["SIDEBAR"], fg=C["TEXT"]).pack(anchor="w")
        tk.Label(logo_txt, text="Audio Downloader", font=("Segoe UI",8),
                 bg=C["SIDEBAR"], fg=C["MUTED"]).pack(anchor="w")

        # Separador
        tk.Frame(sidebar, bg=C["BORDER"], height=1).pack(fill="x", padx=12, pady=(0,8))

        # ── Secciones del sidebar ──────────────────────────────────────────
        self._sidebar_btns = {}
        self._content_frames = {}

        SIDEBAR_ITEMS = [
            ("download",  "⬇", self.T("tab_download").strip()),
            ("search",    "🔍", self.T("tab_search").strip()),
            ("history",   "📋", self.T("tab_history").strip()),
            ("favorites", "⭐", "Favoritos"),
            ("convert",   "🔄", self.T("tab_convert").strip()),
            ("video",     "🎬", self.T("tab_video").strip()),
            ("charts",    "📊", self.T("tab_charts").strip()),
            ("lyrics",    "🎵", self.T("tab_lyrics").strip()),
            ("metadata",  "🏷", self.T("tab_metadata").strip()),
        ]

        nav_frame = tk.Frame(sidebar, bg=C["SIDEBAR"])
        nav_frame.pack(fill="both", expand=True, padx=8)

        for key, icon, label in SIDEBAR_ITEMS:
            self._make_sidebar_btn(nav_frame, key, icon, label)

        # Separador + Ajustes al final
        tk.Frame(sidebar, bg=C["BORDER"], height=1).pack(fill="x", padx=12, pady=4)
        settings_frame = tk.Frame(sidebar, bg=C["SIDEBAR"])
        settings_frame.pack(fill="x", padx=8, pady=(0,4))
        self._make_sidebar_btn(settings_frame, "settings", "⚙", self.T("tab_settings").strip())

        # Idioma + versión
        bottom = tk.Frame(sidebar, bg=C["SIDEBAR"])
        bottom.pack(fill="x", padx=12, pady=(4,12))
        tk.Frame(bottom, bg=C["BORDER"], height=1).pack(fill="x", pady=(0,8))
        lang_row = tk.Frame(bottom, bg=C["SIDEBAR"]); lang_row.pack(fill="x")
        tk.Label(lang_row, text=self.T("lang_lbl"), font=("Segoe UI",9),
                 bg=C["SIDEBAR"], fg=C["MUTED"]).pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang.upper())
        lang_cb = ttk.Combobox(lang_row, textvariable=self.lang_var, values=["ES","EN"],
                               state="readonly", width=4, font=("Segoe UI",9))
        lang_cb.pack(side="left", padx=(4,0))
        lang_cb.bind("<<ComboboxSelected>>", self._change_lang)
        tk.Label(bottom, text="v3.0 · by Maken", font=("Segoe UI",8),
                 bg=C["SIDEBAR"], fg=C["MUTED"]).pack(anchor="w", pady=(6,0))

        # ── MAIN PANEL ───────────────────────────────────────────────────────
        main_frame = tk.Frame(root_frame, bg=C["BG"])
        main_frame.pack(side="left", fill="both", expand=True)

        # Topbar
        self.topbar = tk.Frame(main_frame, bg=C["PANEL"], height=52)
        self.topbar.pack(fill="x"); self.topbar.pack_propagate(False)
        tk.Frame(self.topbar, bg=C["BORDER"], height=1).pack(side="bottom", fill="x")

        self.lbl_topbar_title = tk.Label(
            self.topbar, text="", font=("Segoe UI",14,"bold"),
            bg=C["PANEL"], fg=C["TEXT"])
        self.lbl_topbar_title.pack(side="left", padx=20)

        self.lbl_topbar_sub = tk.Label(
            self.topbar, text="", font=("Segoe UI",9),
            bg=C["PANEL"], fg=C["MUTED"])
        self.lbl_topbar_sub.pack(side="left", padx=(0,0))

        # Botones topbar derecha
        topbar_right = tk.Frame(self.topbar, bg=C["PANEL"])
        topbar_right.pack(side="right", padx=16)
        self._btn_open_folder = self._make_topbar_btn(
            topbar_right, "📂 " + self.T("btn_open_folder"),
            lambda: open_folder(self.output_dir))
        self._btn_open_folder.pack(side="right", padx=(4,0))
        self._btn_about = self._make_topbar_btn(
            topbar_right, self.T("btn_about"), self._show_about)
        self._btn_about.pack(side="right", padx=(4,0))

        # Content area (stack de frames)
        content_area = tk.Frame(main_frame, bg=C["BG"])
        content_area.pack(fill="both", expand=True)

        # Crear todos los frames de contenido
        sections = [
            ("download",  self._build_tab_download),
            ("search",    self._build_tab_search),
            ("history",   self._build_tab_history),
            ("favorites", self._build_tab_favorites),
            ("convert",   self._build_tab_convert),
            ("video",     self._build_tab_video),
            ("charts",    self._build_tab_charts),
            ("lyrics",    self._build_tab_lyrics),
            ("metadata",  self._build_tab_metadata),
            ("settings",  self._build_tab_settings),
        ]
        for key, builder in sections:
            frame = tk.Frame(content_area, bg=C["BG"])
            frame.place(relwidth=1, relheight=1)
            builder(frame)
            self._content_frames[key] = frame

        # Mostrar sección inicial
        self._switch_section("download")

    def _make_sidebar_btn(self, parent, key, icon, label):
        C = self.C
        is_active = (key == self._active_section)
        bg  = C["SIDEBAR_ACTIVE"] if is_active else C["SIDEBAR"]
        fg  = C["TEXT"]           if is_active else C["SUBTEXT"]
        acc = C["ACCENT"]         if is_active else C["SIDEBAR"]

        btn_frame = tk.Frame(parent, bg=bg, cursor="hand2")
        btn_frame.pack(fill="x", pady=1)

        # Barra lateral izquierda (indicador activo)
        indicator = tk.Frame(btn_frame, bg=acc, width=3)
        indicator.pack(side="left", fill="y")

        inner = tk.Frame(btn_frame, bg=bg)
        inner.pack(side="left", fill="x", expand=True, padx=(10,8), pady=7)

        tk.Label(inner, text=f"{icon}  {label}", font=("Segoe UI",10),
                 bg=bg, fg=fg, anchor="w").pack(side="left")

        def on_click(_=None): self._switch_section(key)
        def on_enter(_=None):
            if key != self._active_section:
                btn_frame.configure(bg=C["PANEL2"])
                inner.configure(bg=C["PANEL2"])
                for w in inner.winfo_children(): w.configure(bg=C["PANEL2"])
        def on_leave(_=None):
            if key != self._active_section:
                btn_frame.configure(bg=C["SIDEBAR"])
                inner.configure(bg=C["SIDEBAR"])
                for w in inner.winfo_children(): w.configure(bg=C["SIDEBAR"])

        for widget in [btn_frame, inner] + list(inner.winfo_children()):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>",    on_enter)
            widget.bind("<Leave>",    on_leave)

        self._sidebar_btns[key] = (btn_frame, inner, indicator)

    def _make_topbar_btn(self, parent, text, command):
        C = self.C
        btn = tk.Button(parent, text=text, font=("Segoe UI",9),
                        bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                        activebackground=C["BORDER"], activeforeground=C["TEXT"],
                        padx=10, pady=5, bd=0, command=command)
        return btn

    def _switch_section(self, key):
        C = self.C
        TOPBAR = {
            "download":  ("⬇  " + self.T("tab_download").strip(),  "YouTube · SoundCloud · Vimeo · Bandcamp · +1000"),
            "search":    ("🔍  " + self.T("tab_search").strip(),    "Busca canciones sin salir de la app"),
            "history":   ("📋  " + self.T("tab_history").strip(),   "Tus descargas anteriores"),
            "favorites": ("⭐  Favoritos",                           "URLs y playlists guardadas"),
            "convert":   ("🔄  " + self.T("tab_convert").strip(),   "Convierte archivos de audio locales"),
            "video":     ("🎬  " + self.T("tab_video").strip(),     "Descarga vídeos en MP4"),
            "charts":    ("📊  " + self.T("tab_charts").strip(),    "Estadísticas de tus descargas"),
            "lyrics":    ("🎵  " + self.T("tab_lyrics").strip(),    "Letras sincronizadas (.lrc)"),
            "metadata":  ("🏷   " + self.T("tab_metadata").strip(), "Edita etiquetas ID3 de tus MP3"),
            "settings":  ("⚙   " + self.T("tab_settings").strip(), "Configuración de la aplicación"),
        }
        # Desactivar anterior
        prev = self._active_section
        if prev in self._sidebar_btns:
            bf, inner, ind = self._sidebar_btns[prev]
            bf.configure(bg=C["SIDEBAR"])
            inner.configure(bg=C["SIDEBAR"])
            ind.configure(bg=C["SIDEBAR"])
            for w in inner.winfo_children(): w.configure(bg=C["SIDEBAR"], fg=C["SUBTEXT"])
        # Activar nuevo
        self._active_section = key
        if key in self._sidebar_btns:
            bf, inner, ind = self._sidebar_btns[key]
            bf.configure(bg=C["SIDEBAR_ACTIVE"])
            inner.configure(bg=C["SIDEBAR_ACTIVE"])
            ind.configure(bg=C["ACCENT"])
            for w in inner.winfo_children(): w.configure(bg=C["SIDEBAR_ACTIVE"], fg=C["TEXT"])
        # Actualizar topbar
        title, sub = TOPBAR.get(key, (key, ""))
        self.lbl_topbar_title.configure(text=title)
        self.lbl_topbar_sub.configure(text=f"  {sub}")
        # Mostrar frame correcto
        for k, frame in self._content_frames.items():
            frame.lift() if k == key else frame.lower()

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
        tk.Button(self.thumb_frame, text="🖼 Portada", font=("Segoe UI",7),
                  bg=C["PANEL2"], fg=C["SUBTEXT"], relief="flat", cursor="hand2",
                  command=self._pick_custom_cover).pack(fill="x", pady=(2,0))
        self.lbl_cover_name = tk.Label(self.thumb_frame, text="", font=("Segoe UI",6),
                                        bg=C["PANEL"], fg=C["SUCCESS"], wraplength=108)
        self.lbl_cover_name.pack()

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

        # Perfiles de descarga
        cr_prof = tk.Frame(p, bg=C["BG"]); cr_prof.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5,0))
        tk.Label(cr_prof, text="Perfil:", font=("Segoe UI",9), bg=C["BG"], fg=C["SUBTEXT"]).pack(side="left", padx=(0,4))
        self.profile_var = tk.StringVar(value=self.profiles[0]["name"] if self.profiles else "")
        self.profile_cb  = ttk.Combobox(cr_prof, textvariable=self.profile_var,
                                         values=[p["name"] for p in self.profiles],
                                         state="readonly", width=13, font=("Segoe UI",9))
        self.profile_cb.pack(side="left", padx=(0,4))
        self.profile_cb.bind("<<ComboboxSelected>>", self._apply_profile)
        tk.Button(cr_prof, text="💾 Guardar perfil actual", font=("Segoe UI",8),
                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=8, pady=2, command=self._save_current_profile).pack(side="left")

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

        # Auto-organizar
        self.auto_organize_var = tk.BooleanVar(value=self.cfg.get("auto_organize", False))
        tk.Checkbutton(p, text=self.T("auto_organize"), variable=self.auto_organize_var,
                       font=("Segoe UI",9), bg=C["BG"], fg=C["SUBTEXT"],
                       selectcolor=C["ACCENT2"], activebackground=C["BG"],
                       activeforeground=C["TEXT"],
                       command=lambda: self.cfg.update({"auto_organize": self.auto_organize_var.get()}) or save_config(self.cfg)
                       ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(4,0))

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

        # Programar inicio
        sched_f = tk.Frame(p, bg=C["BG"]); sched_f.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6,0))
        self.lbl_sched = tk.Label(sched_f, text=self.T("schedule_lbl"), font=("Segoe UI",9),
                                   bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_sched.pack(side="left")
        self.schedule_var = tk.StringVar()
        tk.Entry(sched_f, textvariable=self.schedule_var, font=("Consolas",9),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=4, width=7).pack(side="left", padx=(6,0), ipady=3)
        tk.Label(sched_f, text=self.T("schedule_hint"), font=("Segoe UI",7),
                 bg=C["BG"], fg=C["SUBTEXT"]).pack(side="left", padx=6)
        self.lbl_sched_info = tk.Label(sched_f, text="", font=("Segoe UI",8),
                                        bg=C["BG"], fg=C["WARNING"])
        self.lbl_sched_info.pack(side="left", padx=4)

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
        tk.Button(sr, text="M3U", font=("Segoe UI",9),
                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=8, pady=3, command=lambda: self._export_m3u(auto=False)).pack(side="right", padx=(5,0))
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
    # PORTADA PERSONALIZADA
    # ════════════════════════════════════════════════════════════════════════
    def _pick_custom_cover(self):
        path = filedialog.askopenfilename(
            title="Elegir imagen de portada",
            filetypes=[("Imágenes","*.jpg *.jpeg *.png *.webp"),("All","*.*")])
        if path:
            self._custom_cover = path
            self.lbl_cover_name.configure(text=f"✔ {os.path.basename(path)[:18]}")
            if HAS_PIL:
                try:
                    img = Image.open(path).resize((112,63), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._thumb_img = photo
                    self.lbl_thumb.configure(image=photo, text="")
                except Exception: pass
        else:
            self._custom_cover = None
            self.lbl_cover_name.configure(text="")
            self.lbl_thumb.configure(image="", text="🖼", font=("Segoe UI",22))

    def _embed_custom_cover(self, filepath):
        if not HAS_MUTAGEN or not self._custom_cover or not os.path.exists(filepath): return
        try:
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, APIC
            with open(self._custom_cover,"rb") as f: img_data = f.read()
            mime = "image/jpeg" if self._custom_cover.lower().endswith((".jpg",".jpeg")) else "image/png"
            audio = MP3(filepath, ID3=ID3)
            try: audio.add_tags()
            except Exception: pass
            audio.tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=img_data))
            audio.save()
            self._log(f"🖼 Portada personalizada: {os.path.basename(filepath)}")
        except Exception as e:
            self._log(f"⚠️  Error portada: {e}")

    # ════════════════════════════════════════════════════════════════════════
    # PERFILES DE DESCARGA
    # ════════════════════════════════════════════════════════════════════════
    def _apply_profile(self, _=None):
        name = self.profile_var.get()
        for p in self.profiles:
            if p["name"] == name:
                self.format_var.set(p.get("format","MP3"))
                self.quality_var.set(p.get("quality","320"))
                self.template_var.set(p.get("template","%(title)s"))
                self._on_format_change(); break

    def _save_current_profile(self):
        name = self.profile_var.get().strip()
        if not name: return
        new_p = {"name":name,"format":self.format_var.get(),
                 "quality":self.quality_var.get(),"template":self.template_var.get()}
        for i,p in enumerate(self.profiles):
            if p["name"] == name:
                self.profiles[i] = new_p; save_profiles(self.profiles)
                self._log(f"💾 Perfil '{name}' actualizado"); return
        self.profiles.append(new_p)
        save_profiles(self.profiles)
        self.profile_cb.configure(values=[p["name"] for p in self.profiles])
        self._log(f"💾 Perfil '{name}' guardado")

    # ════════════════════════════════════════════════════════════════════════
    # EXPORTAR M3U
    # ════════════════════════════════════════════════════════════════════════
    def _export_m3u(self, auto=False):
        if not self.history: return
        path = (os.path.join(self.output_dir,"playlist.m3u") if auto else
                filedialog.asksaveasfilename(defaultextension=".m3u",
                    filetypes=[("Playlist M3U","*.m3u")], initialfile="playlist.m3u"))
        if not path: return
        try:
            with open(path,"w",encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for r in self.history:
                    fp = r.get("filepath","")
                    try:
                        parts = r.get("duracion","0:00").split(":")
                        secs  = int(parts[0])*60 + int(parts[1])
                    except Exception: secs = -1
                    f.write(f"#EXTINF:{secs},{r.get('titulo','—')} - {r.get('canal','—')}\n")
                    if fp and os.path.exists(fp): f.write(fp + "\n")
            if not auto: self._set_status(f"✅ M3U: {path}", self.C["SUCCESS"])
            self._log(f"📋 M3U: {path}")
        except Exception as e: self._log(f"ERROR M3U: {e}")

    # ════════════════════════════════════════════════════════════════════════
    # TAB FAVORITOS
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_favorites(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=18, pady=14)
        p.pack(fill="both", expand=True)
        p.columnconfigure(0, weight=1); p.rowconfigure(1, weight=1)

        top = tk.Frame(p, bg=C["BG"]); top.grid(row=0, column=0, sticky="ew", pady=(0,8))
        top.columnconfigure(0, weight=1)
        self.fav_entry_var = tk.StringVar()
        fe = tk.Entry(top, textvariable=self.fav_entry_var, font=("Segoe UI",10),
                      bg=C["PANEL"], fg=C["SUBTEXT"], insertbackground=C["TEXT"],
                      relief="flat", bd=6)
        fe.insert(0, "Pega una URL o nombre para guardar como favorito…")
        fe.bind("<FocusIn>", lambda e: (fe.delete(0,"end"), fe.configure(fg=C["TEXT"]))
                              if "Pega" in fe.get() else None)
        fe.grid(row=0, column=0, sticky="ew", ipady=4, padx=(0,8))
        tk.Button(top, text="Guardar", font=("Segoe UI",9,"bold"),
                  bg=C["ACCENT"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=10, pady=4, command=self._fav_add).grid(row=0, column=1)

        fav_outer = tk.Frame(p, bg=C["PANEL"]); fav_outer.grid(row=1, column=0, sticky="nsew")
        fav_outer.rowconfigure(0, weight=1); fav_outer.columnconfigure(0, weight=1)
        self.fav_list = tk.Listbox(fav_outer, font=("Segoe UI",10),
                                    bg=C["PANEL"], fg=C["TEXT"], relief="flat",
                                    selectbackground=C["ACCENT2"], activestyle="none", bd=6)
        fav_sb = tk.Scrollbar(fav_outer, command=self.fav_list.yview)
        self.fav_list.configure(yscrollcommand=fav_sb.set)
        self.fav_list.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        fav_sb.grid(row=0, column=1, sticky="ns")
        self.fav_list.bind("<Double-1>", self._fav_send_to_queue)
        self._fav_refresh()

        bf = tk.Frame(p, bg=C["BG"]); bf.grid(row=2, column=0, sticky="ew", pady=(6,0))
        tk.Button(bf, text="Añadir a cola", font=("Segoe UI",9,"bold"),
                  bg=C["ACCENT2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=12, pady=5, command=self._fav_send_to_queue).pack(side="left")
        tk.Button(bf, text="Eliminar", font=("Segoe UI",9),
                  bg=C["PANEL"], fg=C["SUBTEXT"], relief="flat", cursor="hand2",
                  padx=10, pady=5, command=self._fav_remove).pack(side="left", padx=(6,0))
        tk.Label(bf, text="Doble click → añadir a cola directamente",
                 font=("Segoe UI",8), bg=C["BG"], fg=C["SUBTEXT"]).pack(side="right")

    def _fav_refresh(self):
        try:
            self.fav_list.delete(0,"end")
            for fav in self.favorites:
                self.fav_list.insert("end", (fav.get("name") or fav.get("url",""))[:80])
        except Exception: pass

    def _fav_add(self):
        val = self.fav_entry_var.get().strip()
        if not val or "Pega" in val: return
        entry = {"name": val[:60], "url": val}
        if not any(f.get("url")==val for f in self.favorites):
            self.favorites.append(entry)
            save_favorites(self.favorites)
            self._fav_refresh()
            self.fav_entry_var.set("")

    def _fav_remove(self):
        sel = self.fav_list.curselection()
        if not sel: return
        self.favorites.pop(sel[0])
        save_favorites(self.favorites)
        self._fav_refresh()

    def _fav_send_to_queue(self, _=None):
        sel = self.fav_list.curselection()
        if not sel: return
        fav = self.favorites[sel[0]]
        url = fav.get("url","")
        if url and url not in self.queue:
            self.queue.append(url)
            self.queue_list.insert("end", fav.get("name","")[:74])
            self._update_queue_count()
            self._set_status(self.T("status_added",n=1), self.C["SUCCESS"])
            self.nb.select(0)


    # ════════════════════════════════════════════════════════════════════════
    # PREVIEW 30s
    # ════════════════════════════════════════════════════════════════════════
    def _preview_selected(self):
        if not HAS_PYGAME:
            messagebox.showinfo("pygame", self.T("pygame_missing")); return
        sel = self.search_tree.focus()
        if not sel: return
        idx = list(self.search_tree.get_children()).index(sel)
        if idx >= len(self._search_results_urls): return
        url = self._search_results_urls[idx]
        self.lbl_preview_status.configure(text=self.T("preview_loading"), fg=self.C["SUBTEXT"])
        self.btn_preview.configure(state="disabled")
        threading.Thread(target=self._preview_worker, args=(url,), daemon=True).start()

    def _preview_worker(self, url):
        import tempfile
        try:
            tmpdir  = tempfile.gettempdir()
            tmpbase = os.path.join(tmpdir, "preview")
            for fn in os.listdir(tmpdir):
                if fn.startswith("preview"):
                    try: os.remove(os.path.join(tmpdir,fn))
                    except Exception: pass
            opts = {
                "format":"bestaudio/best","outtmpl": tmpbase+".%(ext)s",
                "quiet":True,"no_warnings":True,
                "postprocessors":[{"key":"FFmpegExtractAudio",
                                   "preferredcodec":"mp3","preferredquality":"128"}],
                "postprocessor_args":["-t","35"],
            }
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            found = next((os.path.join(tmpdir,f) for f in os.listdir(tmpdir)
                         if f.startswith("preview") and f.endswith(".mp3")), None)
            if not found:
                self.after(0, lambda: self.lbl_preview_status.configure(
                    text="No se pudo cargar", fg=self.C["ERROR"])); return
            self._preview_tmpfile = found
            pygame.mixer.music.load(found)
            pygame.mixer.music.play()
            self.after(0, lambda: (
                self.lbl_preview_status.configure(text="▶ Reproduciendo preview…", fg=self.C["SUCCESS"]),
                self.btn_preview_stop.configure(state="normal"),
                self.btn_preview.configure(state="normal"),
            ))
        except Exception as e:
            self.after(0, lambda err=str(e)[:50]: (
                self.lbl_preview_status.configure(text=f"Error: {err}", fg=self.C["ERROR"]),
                self.btn_preview.configure(state="normal"),
            ))

    def _preview_stop(self):
        if HAS_PYGAME:
            try: pygame.mixer.music.stop()
            except Exception: pass
        self.lbl_preview_status.configure(text="")
        self.btn_preview_stop.configure(state="disabled")
        if self._preview_tmpfile and os.path.exists(self._preview_tmpfile):
            try: os.remove(self._preview_tmpfile)
            except Exception: pass
            self._preview_tmpfile = None

    # ════════════════════════════════════════════════════════════════════════
    # TAB CONVERTIDOR LOCAL
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_convert(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=28, pady=20)
        p.pack(fill="both", expand=True); p.columnconfigure(1, weight=1)

        tk.Label(p, text=self.T("convert_src"), font=("Segoe UI",10),
                 bg=C["BG"], fg=C["TEXT"]).grid(row=0, column=0, sticky="w", pady=8, padx=(0,16))
        src_f = tk.Frame(p, bg=C["BG"]); src_f.grid(row=0, column=1, sticky="ew", pady=8)
        src_f.columnconfigure(0, weight=1)
        self.convert_src_var = tk.StringVar()
        tk.Entry(src_f, textvariable=self.convert_src_var, font=("Segoe UI",9),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=6).grid(row=0, column=0, sticky="ew", ipady=4)
        tk.Button(src_f, text=self.T("convert_open"), font=("Segoe UI",9),
                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=8, pady=4, command=self._convert_pick_file).grid(row=0, column=1, padx=(8,0))

        tk.Label(p, text=self.T("convert_fmt"), font=("Segoe UI",10),
                 bg=C["BG"], fg=C["TEXT"]).grid(row=1, column=0, sticky="w", pady=8, padx=(0,16))
        fmt_f = tk.Frame(p, bg=C["BG"]); fmt_f.grid(row=1, column=1, sticky="w", pady=8)
        self.convert_fmt_var = tk.StringVar(value="MP3")
        for fmt in ["MP3","AAC","FLAC","WAV","OGG"]:
            tk.Radiobutton(fmt_f, text=fmt, variable=self.convert_fmt_var, value=fmt,
                           font=("Segoe UI",10), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=6)

        tk.Label(p, text=self.T("quality_lbl"), font=("Segoe UI",10),
                 bg=C["BG"], fg=C["TEXT"]).grid(row=2, column=0, sticky="w", pady=8, padx=(0,16))
        qual_f = tk.Frame(p, bg=C["BG"]); qual_f.grid(row=2, column=1, sticky="w", pady=8)
        self.convert_qual_var = tk.StringVar(value="320")
        for q in ["128","192","256","320"]:
            tk.Radiobutton(qual_f, text=f"{q}k", variable=self.convert_qual_var, value=q,
                           font=("Segoe UI",10), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=6)

        tk.Frame(p, bg=C["PANEL"], height=1).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12,14))
        btn_f = tk.Frame(p, bg=C["BG"]); btn_f.grid(row=4, column=0, columnspan=2, sticky="w")
        tk.Button(btn_f, text=self.T("convert_btn"), font=("Segoe UI",12,"bold"),
                  bg=C["ACCENT"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=20, pady=10, activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                  command=self._convert_file).pack(side="left")
        self.lbl_convert_status = tk.Label(btn_f, text="", font=("Segoe UI",9),
                                            bg=C["BG"], fg=C["SUCCESS"])
        self.lbl_convert_status.pack(side="left", padx=14)
        self.convert_progress = ttk.Progressbar(p, maximum=100, mode="indeterminate")
        self.convert_progress.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12,0))
        tk.Label(p, text="El archivo convertido se guarda en la misma carpeta que el original.",
                 font=("Segoe UI",8), bg=C["BG"], fg=C["SUBTEXT"]).grid(
                 row=6, column=0, columnspan=2, sticky="w", pady=(8,0))

    def _convert_pick_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Audio","*.mp3 *.aac *.flac *.wav *.ogg *.m4a *.opus *.webm"),("All","*.*")],
            initialdir=self.output_dir)
        if path: self.convert_src_var.set(path)

    def _convert_file(self):
        src = self.convert_src_var.get().strip()
        if not src:
            self.lbl_convert_status.configure(text=self.T("convert_no_file"), fg=self.C["WARNING"]); return
        if not os.path.exists(src):
            self.lbl_convert_status.configure(text="Archivo no encontrado.", fg=self.C["ERROR"]); return
        self.lbl_convert_status.configure(text="Convirtiendo...", fg=self.C["SUBTEXT"])
        self.convert_progress.start(10)
        threading.Thread(target=self._convert_worker,
                         args=(src, self.convert_fmt_var.get(), self.convert_qual_var.get()),
                         daemon=True).start()

    def _convert_worker(self, src, fmt, quality):
        import subprocess
        codec = FORMATS[fmt]["codec"]
        ext   = codec.replace("vorbis","ogg")
        dest  = os.path.splitext(src)[0] + f"_converted.{ext}"
        try:
            args = ["ffmpeg","-y","-i",src]
            if FORMATS[fmt]["lossy"]: args += ["-b:a",f"{quality}k"]
            args.append(dest)
            r = subprocess.run(args, capture_output=True, timeout=300)
            if r.returncode == 0:
                self.after(0, lambda: (
                    self.lbl_convert_status.configure(
                        text=self.T("convert_done",path=os.path.basename(dest)), fg=self.C["SUCCESS"]),
                    self.convert_progress.stop(),
                    self.convert_progress.configure(value=100, mode="determinate"),
                ))
                self._log(f"🔄 {os.path.basename(src)} → {os.path.basename(dest)}")
            else:
                err = (r.stderr.decode("utf-8","ignore").splitlines()[-1][:60]
                       if r.stderr else "error desconocido")
                self.after(0, lambda e=err: (
                    self.lbl_convert_status.configure(text=self.T("convert_err",err=e), fg=self.C["ERROR"]),
                    self.convert_progress.stop(),
                ))
        except FileNotFoundError:
            self.after(0, lambda: (
                self.lbl_convert_status.configure(text=self.T("convert_no_ffmpeg"), fg=self.C["ERROR"]),
                self.convert_progress.stop(),
            ))
        except Exception as e:
            self.after(0, lambda err=str(e)[:60]: (
                self.lbl_convert_status.configure(text=self.T("convert_err",err=err), fg=self.C["ERROR"]),
                self.convert_progress.stop(),
            ))

    # ════════════════════════════════════════════════════════════════════════
    # TAB VÍDEO
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_video(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=28, pady=20)
        p.pack(fill="both", expand=True); p.columnconfigure(1, weight=1)

        tk.Label(p, text=self.T("video_url_lbl"), font=("Segoe UI",10),
                 bg=C["BG"], fg=C["TEXT"]).grid(row=0, column=0, sticky="w", pady=8, padx=(0,16))
        self.video_url_var = tk.StringVar()
        tk.Entry(p, textvariable=self.video_url_var, font=("Segoe UI",10),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=8).grid(row=0, column=1, sticky="ew", pady=8, ipady=5)

        tk.Label(p, text=self.T("video_quality"), font=("Segoe UI",10),
                 bg=C["BG"], fg=C["TEXT"]).grid(row=1, column=0, sticky="w", pady=8, padx=(0,16))
        qual_f = tk.Frame(p, bg=C["BG"]); qual_f.grid(row=1, column=1, sticky="w", pady=8)
        self.video_qual_var = tk.StringVar(value="1080")
        for q in ["720","1080","1440","2160"]:
            tk.Radiobutton(qual_f, text=f"{q}p", variable=self.video_qual_var, value=q,
                           font=("Segoe UI",10), bg=C["BG"], fg=C["TEXT"],
                           selectcolor=C["ACCENT2"], activebackground=C["BG"],
                           activeforeground=C["TEXT"]).pack(side="left", padx=8)

        self.video_subs_var = tk.BooleanVar(value=False)
        tk.Checkbutton(p, text=self.T("video_subs"), variable=self.video_subs_var,
                       font=("Segoe UI",9), bg=C["BG"], fg=C["TEXT"],
                       selectcolor=C["ACCENT2"], activebackground=C["BG"],
                       activeforeground=C["TEXT"]).grid(row=2, column=1, sticky="w", pady=4)

        tk.Frame(p, bg=C["PANEL"], height=1).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10,14))
        btn_f = tk.Frame(p, bg=C["BG"]); btn_f.grid(row=4, column=0, columnspan=2, sticky="w")
        self.btn_video_dl = tk.Button(btn_f, text=self.T("video_btn"),
                                       font=("Segoe UI",12,"bold"), bg=C["ACCENT"], fg=C["TEXT"],
                                       relief="flat", cursor="hand2", padx=20, pady=10,
                                       activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                                       command=self._start_video_download)
        self.btn_video_dl.pack(side="left")
        self.lbl_video_status = tk.Label(btn_f, text="", font=("Segoe UI",9),
                                          bg=C["BG"], fg=C["SUCCESS"])
        self.lbl_video_status.pack(side="left", padx=14)
        self.video_progress_var = tk.DoubleVar()
        ttk.Progressbar(p, variable=self.video_progress_var, maximum=100).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(12,0))
        tk.Label(p, text="Los vídeos se guardan en la carpeta de descarga configurada.",
                 font=("Segoe UI",8), bg=C["BG"], fg=C["SUBTEXT"]).grid(
                 row=6, column=0, columnspan=2, sticky="w", pady=(8,0))

    def _start_video_download(self):
        url = self.video_url_var.get().strip()
        if not url: return
        self.btn_video_dl.configure(state="disabled")
        self.lbl_video_status.configure(text="Preparando...", fg=self.C["SUBTEXT"])
        threading.Thread(target=self._video_worker, args=(url,), daemon=True).start()

    def _video_worker(self, url):
        qual = self.video_qual_var.get()
        subs = self.video_subs_var.get()
        def hook(d):
            if d["status"]=="downloading":
                try:
                    pct = float(d.get("_percent_str","0%").strip().replace("%",""))
                    self.after(0, lambda p=pct: self.video_progress_var.set(p))
                    self.after(0, lambda p=pct: self.lbl_video_status.configure(
                        text=f"{p:.1f}%  {d.get('_speed_str','')}  ETA {d.get('_eta_str','—')}",
                        fg=self.C["TEXT"]))
                except ValueError: pass
        opts = {
            "format": f"bestvideo[height<={qual}]+bestaudio/best[height<={qual}]",
            "outtmpl": os.path.join(self.output_dir,"%(title)s.%(ext)s"),
            "quiet":True,"no_warnings":True,"progress_hooks":[hook],
            "merge_output_format":"mp4",
        }
        if subs:
            opts.update({"writesubtitles":True,"writeautomaticsub":True,"subtitleslangs":["es","en"]})
        try:
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            self.after(0, lambda: (
                self.lbl_video_status.configure(
                    text=self.T("video_done",folder=self.output_dir), fg=self.C["SUCCESS"]),
                self.video_progress_var.set(100),
                self.btn_video_dl.configure(state="normal"),
            ))
            desktop_notify("Downloader", f"Video en {self.output_dir}")
        except Exception as e:
            self.after(0, lambda err=str(e)[:80]: (
                self.lbl_video_status.configure(text=f"Error: {err}", fg=self.C["ERROR"]),
                self.btn_video_dl.configure(state="normal"),
            ))

    # ════════════════════════════════════════════════════════════════════════
    # TAB LETRAS
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_lyrics(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=18, pady=14)
        p.pack(fill="both", expand=True)
        p.columnconfigure(0, weight=1); p.rowconfigure(2, weight=1)

        top = tk.Frame(p, bg=C["BG"]); top.grid(row=0, column=0, sticky="ew", pady=(0,4))
        top.columnconfigure(0, weight=1)
        self.lyrics_query_var = tk.StringVar()
        tk.Entry(top, textvariable=self.lyrics_query_var, font=("Segoe UI",11),
                  bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                  relief="flat", bd=8).grid(row=0, column=0, sticky="ew", ipady=5)
        self.btn_lyrics_search = tk.Button(top, text=self.T("lyrics_btn"),
                                            font=("Segoe UI",10,"bold"), bg=C["ACCENT"], fg=C["TEXT"],
                                            relief="flat", cursor="hand2", padx=12, pady=5,
                                            activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                                            command=self._search_lyrics)
        self.btn_lyrics_search.grid(row=0, column=1, padx=(8,0))
        tk.Label(p, text=self.T("lyrics_query"), font=("Segoe UI",8),
                 bg=C["BG"], fg=C["SUBTEXT"]).grid(row=1, column=0, sticky="w", pady=(0,6))
        self.lbl_lyrics_status = tk.Label(p, text="", font=("Segoe UI",8),
                                           bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_lyrics_status.grid(row=1, column=0, sticky="e")

        lyr_outer = tk.Frame(p, bg=C["PANEL"])
        lyr_outer.grid(row=2, column=0, sticky="nsew")
        lyr_outer.rowconfigure(0, weight=1); lyr_outer.columnconfigure(0, weight=1)
        self.lyrics_text = tk.Text(lyr_outer, font=("Segoe UI",10), bg=C["PANEL"], fg=C["TEXT"],
                                    insertbackground=C["TEXT"], relief="flat", wrap="word",
                                    state="disabled", bd=8)
        lyr_sb = tk.Scrollbar(lyr_outer, command=self.lyrics_text.yview)
        self.lyrics_text.configure(yscrollcommand=lyr_sb.set)
        self.lyrics_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        lyr_sb.grid(row=0, column=1, sticky="ns")

        save_f = tk.Frame(p, bg=C["BG"]); save_f.grid(row=3, column=0, sticky="ew", pady=(6,0))
        self.btn_save_lrc = tk.Button(save_f, text=self.T("lyrics_save"),
                                       font=("Segoe UI",9,"bold"), bg=C["ACCENT2"], fg=C["TEXT"],
                                       relief="flat", cursor="hand2", padx=12, pady=5,
                                       state="disabled", command=self._save_lrc)
        self.btn_save_lrc.pack(side="left")
        self.lbl_lrc_status = tk.Label(save_f, text="", font=("Segoe UI",8),
                                        bg=C["BG"], fg=C["SUCCESS"])
        self.lbl_lrc_status.pack(side="left", padx=8)
        self._current_lrc = None

    def _search_lyrics(self):
        query = self.lyrics_query_var.get().strip()
        if not query: return
        if not HAS_LYRICS:
            messagebox.showinfo("syncedlyrics","Instala syncedlyrics: pip install syncedlyrics"); return
        self.lbl_lyrics_status.configure(text=self.T("lyrics_searching"), fg=self.C["SUBTEXT"])
        self.btn_lyrics_search.configure(state="disabled")
        threading.Thread(target=self._lyrics_worker, args=(query,), daemon=True).start()

    def _lyrics_worker(self, query):
        try:
            lrc = syncedlyrics.search(query)
            if lrc:
                self._current_lrc = lrc
                self.after(0, lambda: (
                    self.lyrics_text.configure(state="normal"),
                    self.lyrics_text.delete("1.0","end"),
                    self.lyrics_text.insert("end", lrc),
                    self.lyrics_text.configure(state="disabled"),
                    self.lbl_lyrics_status.configure(text="Letras encontradas.", fg=self.C["SUCCESS"]),
                    self.btn_save_lrc.configure(state="normal"),
                ))
            else:
                self._current_lrc = None
                self.after(0, lambda: (
                    self.lyrics_text.configure(state="normal"),
                    self.lyrics_text.delete("1.0","end"),
                    self.lyrics_text.configure(state="disabled"),
                    self.lbl_lyrics_status.configure(text=self.T("lyrics_not_found"), fg=self.C["WARNING"]),
                    self.btn_save_lrc.configure(state="disabled"),
                ))
        except Exception as e:
            self.after(0, lambda err=str(e)[:50]: self.lbl_lyrics_status.configure(
                text=f"Error: {err}", fg=self.C["ERROR"]))
        finally:
            self.after(0, lambda: self.btn_lyrics_search.configure(state="normal"))

    def _save_lrc(self):
        if not self._current_lrc: return
        query = self.lyrics_query_var.get().strip().replace(" ","_").replace("/","")[:40]
        path  = filedialog.asksaveasfilename(defaultextension=".lrc",
                    filetypes=[("LRC","*.lrc"),("Text","*.txt")],
                    initialfile=f"{query}.lrc")
        if not path: return
        try:
            with open(path,"w",encoding="utf-8") as f: f.write(self._current_lrc)
            self.lbl_lrc_status.configure(
                text=self.T("lyrics_saved",path=os.path.basename(path)), fg=self.C["SUCCESS"])
        except Exception as e:
            self.lbl_lrc_status.configure(text=f"Error: {e}", fg=self.C["ERROR"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB BÚSQUEDA
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_search(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=18, pady=14)
        p.pack(fill="both", expand=True)
        p.columnconfigure(0, weight=1); p.rowconfigure(2, weight=1)

        sf = tk.Frame(p, bg=C["BG"]); sf.grid(row=0, column=0, sticky="ew", pady=(0,8))
        sf.columnconfigure(0, weight=1)
        self.search_query_var = tk.StringVar()
        self._search_ph = "Buscar canción, artista o álbum…"
        se = tk.Entry(sf, textvariable=self.search_query_var, font=("Segoe UI",11),
                      bg=C["PANEL"], fg=C["SUBTEXT"], insertbackground=C["TEXT"],
                      relief="flat", bd=8)
        se.insert(0, self._search_ph)
        se.bind("<FocusIn>",  lambda e: (se.delete(0,"end"), se.configure(fg=C["TEXT"]))
                              if se.get()==self._search_ph else None)
        se.bind("<Return>", lambda e: self._do_search())
        se.grid(row=0, column=0, sticky="ew", ipady=5)
        self.btn_do_search = tk.Button(sf, text="Buscar",
                                        font=("Segoe UI",10,"bold"), bg=C["ACCENT"], fg=C["TEXT"],
                                        relief="flat", cursor="hand2", padx=14, pady=5,
                                        activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                                        command=self._do_search)
        self.btn_do_search.grid(row=0, column=1, padx=(8,0))

        self.lbl_search_status = tk.Label(p, text="", font=("Segoe UI",9), bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_search_status.grid(row=1, column=0, sticky="w", pady=(0,4))

        res_outer = tk.Frame(p, bg=C["PANEL"]); res_outer.grid(row=2, column=0, sticky="nsew")
        res_outer.rowconfigure(0, weight=1); res_outer.columnconfigure(0, weight=1)
        self.search_tree = ttk.Treeview(res_outer,
                                         columns=("titulo","canal","duracion"),
                                         show="headings", style="Hist.Treeview")
        for cid,w,lbl in [("titulo",420,"Título"),("canal",160,"Canal"),("duracion",70,"Dur.")]:
            self.search_tree.heading(cid, text=lbl)
            self.search_tree.column(cid, width=w, anchor="w", stretch=(cid=="titulo"))
        s_vsb = tk.Scrollbar(res_outer, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=s_vsb.set)
        self.search_tree.grid(row=0, column=0, sticky="nsew")
        s_vsb.grid(row=0, column=1, sticky="ns")
        self._search_results_urls = []

        bf = tk.Frame(p, bg=C["BG"]); bf.grid(row=3, column=0, sticky="ew", pady=(6,0))
        tk.Button(bf, text="＋ Añadir a cola", font=("Segoe UI",10,"bold"),
                  bg=C["ACCENT2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=14, pady=6, activebackground=C["ACCENT"], activeforeground=C["TEXT"],
                  command=self._add_search_result_to_queue).pack(side="left")
        self.btn_preview = tk.Button(bf, text=self.T("preview_btn"), font=("Segoe UI",9),
                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=10, pady=6, command=self._preview_selected)
        self.btn_preview.pack(side="left", padx=(6,0))
        self.btn_preview_stop = tk.Button(bf, text=self.T("preview_stop"), font=("Segoe UI",9),
                  bg=C["PANEL2"], fg=C["WARNING"], relief="flat", cursor="hand2",
                  padx=10, pady=6, state="disabled", command=self._preview_stop)
        self.btn_preview_stop.pack(side="left", padx=(4,0))
        self.lbl_preview_status = tk.Label(bf, text="", font=("Segoe UI",8),
                                            bg=C["BG"], fg=C["SUBTEXT"])
        self.lbl_preview_status.pack(side="left", padx=8)
        tk.Label(bf, text="Doble click o selecciona y pulsa ＋", font=("Segoe UI",8),
                 bg=C["BG"], fg=C["SUBTEXT"]).pack(side="right")
        self.search_tree.bind("<Double-1>", lambda e: self._add_search_result_to_queue())
        self._preview_tmpfile = None

    def _do_search(self):
        q = self.search_query_var.get().strip()
        if not q or q == self._search_ph: return
        self.lbl_search_status.configure(text="Buscando…", fg=self.C["SUBTEXT"])
        self.btn_do_search.configure(state="disabled")
        threading.Thread(target=self._search_worker, args=(q,), daemon=True).start()

    def _search_worker(self, query):
        try:
            opts = {"quiet":True,"no_warnings":True,"extract_flat":True,
                    "skip_download":True,"playlistend":12}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch12:{query}", download=False)
            entries = info.get("entries",[]) or []
            results = []
            for e in entries:
                if not e: continue
                dur = e.get("duration") or 0
                m,s = divmod(int(dur),60)
                results.append({
                    "titulo":   e.get("title","—"),
                    "canal":    e.get("uploader") or e.get("channel","—"),
                    "duracion": f"{m}:{s:02d}",
                    "url":      e.get("url") or e.get("webpage_url",""),
                })
            self.after(0, lambda r=results: self._show_search_results(r))
        except Exception as ex:
            self.after(0, lambda: self.lbl_search_status.configure(
                text=f"Error: {ex}", fg=self.C["ERROR"]))
        finally:
            self.after(0, lambda: self.btn_do_search.configure(state="normal"))

    def _show_search_results(self, results):
        self.search_tree.delete(*self.search_tree.get_children())
        self._search_results_urls = []
        if not results:
            self.lbl_search_status.configure(text="Sin resultados.", fg=self.C["WARNING"]); return
        for r in results:
            self.search_tree.insert("","end", values=(r["titulo"],r["canal"],r["duracion"]))
            self._search_results_urls.append(r["url"])
        self.lbl_search_status.configure(
            text=f"{len(results)} resultados", fg=self.C["SUCCESS"])

    def _add_search_result_to_queue(self):
        sel = self.search_tree.focus()
        if not sel: return
        idx = list(self.search_tree.get_children()).index(sel)
        if idx >= len(self._search_results_urls): return
        url = self._search_results_urls[idx]
        if url and url not in self.queue:
            self.queue.append(url)
            title = self.search_tree.item(sel,"values")[0]
            self.queue_list.insert("end", (title[:74]+"…") if len(title)>74 else title)
            self._update_queue_count()
            self._set_status(self.T("status_added",n=1), self.C["SUCCESS"])
            self.nb.select(0)   # volver a tab Descargar

    # ════════════════════════════════════════════════════════════════════════
    # TAB GRÁFICAS
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_charts(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=18, pady=14)
        p.pack(fill="both", expand=True)
        p.columnconfigure(0, weight=1); p.rowconfigure(0, weight=1)
        self.charts_frame = p

    def _refresh_charts(self):
        """Regenera gráficas. Silencia si matplotlib no está instalado."""
        if not HAS_MPL: return
        try:
            if not self.charts_frame.winfo_exists(): return
        except Exception: return
        C = self.C
        for w in self.charts_frame.winfo_children(): w.destroy()
        h = self.history
        if not h:
            tk.Label(self.charts_frame, text="Sin datos aún. Descarga algo primero.",
                     font=("Segoe UI",11), bg=C["BG"], fg=C["SUBTEXT"]).pack(expand=True)
            return

        fig = Figure(figsize=(8,4), dpi=90, facecolor=C["BG"])
        fig.subplots_adjust(wspace=0.35, left=0.08, right=0.97, top=0.88, bottom=0.18)

        # Barras: descargas por mes
        ax1 = fig.add_subplot(1,2,1)
        month_counter = Counter()
        for r in h:
            try: month_counter[r.get("fecha","")[:5]] += 1
            except Exception: pass
        months = sorted(month_counter.keys())[-8:]
        vals   = [month_counter[m] for m in months]
        bars   = ax1.bar(months, vals, color=C["ACCENT"], edgecolor="none")
        ax1.set_facecolor(C["PANEL2"]); ax1.tick_params(colors=C["TEXT"], labelsize=7)
        for sp in ax1.spines.values(): sp.set_visible(False)
        ax1.set_title("Descargas por mes", color=C["TEXT"], fontsize=9, pad=8)
        for bar,v in zip(bars,vals):
            ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                     str(v), ha="center", va="bottom", fontsize=7, color=C["TEXT"])

        # Pie: formatos
        ax2 = fig.add_subplot(1,2,2)
        fmt_c  = Counter(r.get("formato","?") for r in h)
        COLORS = ["#e94560","#0f3460","#4ade80","#facc15","#a78bfa"]
        ax2.pie(list(fmt_c.values()), labels=list(fmt_c.keys()), autopct="%1.0f%%",
                colors=COLORS[:len(fmt_c)],
                textprops={"color":C["TEXT"],"fontsize":8},
                wedgeprops={"edgecolor":C["BG"],"linewidth":2})
        ax2.set_facecolor(C["BG"])
        ax2.set_title("Formatos", color=C["TEXT"], fontsize=9, pad=8)

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB METADATOS
    # ════════════════════════════════════════════════════════════════════════
    def _build_tab_metadata(self, parent):
        C = self.C
        p = tk.Frame(parent, bg=C["BG"], padx=28, pady=18)
        p.pack(fill="both", expand=True); p.columnconfigure(1, weight=1)

        # Selector archivo
        ff = tk.Frame(p, bg=C["BG"]); ff.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,12))
        self.meta_path_var = tk.StringVar(value="")
        tk.Label(ff, textvariable=self.meta_path_var, font=("Segoe UI",8),
                 bg=C["BG"], fg=C["ACCENT"], wraplength=500, justify="left").pack(side="left", fill="x", expand=True)
        tk.Button(ff, text="📂 Abrir MP3", font=("Segoe UI",9),
                  bg=C["PANEL2"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=10, pady=4, command=self._meta_open_file).pack(side="right")

        tk.Frame(p, bg=C["PANEL"], height=1).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,14))

        # Campos
        self._meta_vars = {}
        for i,(lbl_txt,tag) in enumerate([("Título","title"),("Artista","artist"),
                                           ("Álbum","album"),("Año","date"),("Género","genre")]):
            tk.Label(p, text=lbl_txt, font=("Segoe UI",10),
                     bg=C["BG"], fg=C["TEXT"]).grid(row=i+2, column=0, sticky="w", pady=6, padx=(0,16))
            var = tk.StringVar()
            tk.Entry(p, textvariable=var, font=("Segoe UI",10),
                     bg=C["PANEL"], fg=C["TEXT"], insertbackground=C["TEXT"],
                     relief="flat", bd=6).grid(row=i+2, column=1, sticky="ew", pady=6)
            self._meta_vars[tag] = var

        tk.Frame(p, bg=C["PANEL"], height=1).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(12,10))
        sf2 = tk.Frame(p, bg=C["BG"]); sf2.grid(row=9, column=0, columnspan=2, sticky="w")
        tk.Button(sf2, text="💾 Guardar metadatos", font=("Segoe UI",11,"bold"),
                  bg=C["ACCENT"], fg=C["TEXT"], relief="flat", cursor="hand2",
                  padx=16, pady=8, activebackground=C["ACCENT2"], activeforeground=C["TEXT"],
                  command=self._meta_save).pack(side="left")
        self.lbl_meta_status = tk.Label(sf2, text="", font=("Segoe UI",9),
                                         bg=C["BG"], fg=C["SUCCESS"])
        self.lbl_meta_status.pack(side="left", padx=12)
        tk.Label(p, text="Tip: doble click en Historial carga el archivo aquí automáticamente",
                 font=("Segoe UI",7), bg=C["BG"], fg=C["SUBTEXT"]).grid(
                 row=10, column=0, columnspan=2, sticky="w", pady=(8,0))

    def _meta_open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("MP3","*.mp3"),("Audio","*.mp3 *.aac *.flac *.ogg"),("All","*.*")],
            initialdir=self.output_dir)
        if path: self._meta_load(path)

    def _meta_load(self, path):
        self.meta_path_var.set(path)
        if not HAS_MUTAGEN: return
        try:
            audio = EasyID3(path)
            for tag,var in self._meta_vars.items():
                var.set((audio.get(tag) or [""])[0])
        except Exception:
            for var in self._meta_vars.values(): var.set("")

    def _meta_save(self):
        path = self.meta_path_var.get()
        if not path:
            self.lbl_meta_status.configure(text="Selecciona un archivo MP3 primero.", fg=self.C["WARNING"]); return
        if not HAS_MUTAGEN:
            messagebox.showinfo("mutagen","Instala mutagen:\npip install mutagen"); return
        try:
            try:   audio = EasyID3(path)
            except MutagenError: audio = mutagen.File(path, easy=True); audio.add_tags()
            for tag,var in self._meta_vars.items():
                v = var.get().strip()
                if v: audio[tag] = v
                elif tag in audio: del audio[tag]
            audio.save()
            self.lbl_meta_status.configure(text="✅ Metadatos guardados.", fg=self.C["SUCCESS"])
            self.after(3000, lambda: self.lbl_meta_status.configure(text=""))
        except Exception as e:
            self.lbl_meta_status.configure(text=f"❌ Error: {str(e)[:60]}", fg=self.C["ERROR"])

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
        # Comprobar programación de tiempo
        sched = self.schedule_var.get().strip()
        if sched:
            try:
                h,m = map(int, sched.split(":"))
                now = datetime.datetime.now()
                target = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if target <= now: target += datetime.timedelta(days=1)   # mañana si ya pasó
                delay_s = (target - now).total_seconds()
                self.lbl_sched_info.configure(text=self.T("schedule_set",t=sched))
                self._set_status(self.T("schedule_set",t=sched), self.C["WARNING"])
                # Lanzar en background con delay
                def _delayed():
                    import time; time.sleep(delay_s)
                    if not self._cancel_evt.is_set():
                        self.after(0, self._launch_queue)
                threading.Thread(target=_delayed, daemon=True).start()
                # Botón cancelar sirve también para cancelar la programación
                self.btn_cancel.configure(state="normal",
                    command=lambda: (self._cancel_evt.set(),
                                     self.lbl_sched_info.configure(text=""),
                                     self._set_status(self.T("schedule_cancelled"), self.C["SUBTEXT"]),
                                     self.btn_cancel.configure(state="disabled",
                                         command=self._cancel_download)))
                return
            except ValueError:
                pass   # formato incorrecto → ignorar y descargar ahora
        self._launch_queue()

    def _launch_queue(self):
        """Arranca la cola inmediatamente (sin programación)."""
        self.lbl_sched_info.configure(text="")
        self.schedule_var.set("")
        self.btn_cancel.configure(command=self._cancel_download)
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

        # Portada personalizada — sobreescribe EmbedThumbnail si el usuario eligió una
        if self._custom_cover and os.path.exists(self._custom_cover) and fmt == "MP3":
            opts["writethumbnail"] = False
            opts["postprocessors"] = [pp for pp in opts.get("postprocessors",[])
                                      if pp.get("key") != "EmbedThumbnail"]

        # Detección de duplicados (pre-check sin descargar)
        def _already_exists(title, folder, ext):
            safe = "".join(c for c in title if c not in r'\/:*?"<>|')[:60].strip().lower()
            return any(safe in fn.lower() and fn.lower().endswith(f".{ext}")
                       for fn in (os.listdir(folder) if os.path.isdir(folder) else []))

        ext_chk = FORMATS[fmt]["codec"].replace("vorbis","ogg")
        try:
            with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True,"skip_download":True}) as ydl:
                pre = ydl.extract_info(url, download=False)
            pre_entries = ([e for e in pre.get("entries",[]) if e]
                           if pre and pre.get("_type")=="playlist" else [pre] if pre else [])
            dupes = [e.get("title","?") for e in pre_entries
                     if _already_exists(e.get("title",""), self.output_dir, ext_chk)]
            if dupes:
                self._log(f"⚠️  Ya existen {len(dupes)} archivo(s): {', '.join(dupes[:2])}{'…' if len(dupes)>2 else ''}")
                if len(dupes) == len(pre_entries):
                    self._log("✅ Todos ya descargados — saltando"); return
        except Exception: pass   # si falla el pre-check, continuar igual

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
                self.after(0, self._refresh_charts)
                # Portada personalizada tras conversión
                if self._custom_cover:
                    for e in entries:
                        fn = template
                        for var in ["title","uploader","artist"]:
                            fn = fn.replace(f"%({var})s", e.get(var,"") or "")
                        fpath = os.path.join(self.output_dir, fn.strip()+".mp3")
                        if os.path.exists(fpath):
                            self.after(100, lambda fp=fpath: self._embed_custom_cover(fp))
                # Auto-organizar por artista/álbum
                if self.auto_organize_var.get():
                    for e in entries:
                        artist = e.get("artist") or e.get("uploader","Desconocido")
                        album  = e.get("album")  or e.get("playlist_title","")
                        fn_base = template
                        for var in ["title","uploader","artist"]:
                            fn_base = fn_base.replace(f"%({var})s", e.get(var,"") or "")
                        ext = FORMATS[fmt]["codec"].replace("vorbis","ogg")
                        src = os.path.join(self.output_dir, fn_base.strip()+f".{ext}")
                        if os.path.exists(src):
                            dest_dir = os.path.join(self.output_dir,
                                "".join(c for c in artist if c not in r'\/:*?"<>|')[:40],
                                "".join(c for c in album  if c not in r'\/:*?"<>|')[:40] if album else "")
                            os.makedirs(dest_dir, exist_ok=True)
                            dest = os.path.join(dest_dir, os.path.basename(src))
                            if not os.path.exists(dest):
                                import shutil; shutil.move(src, dest)
                                self._log(f"📂 Organizado: {artist}/{album or ''}")
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
            self._export_m3u(auto=True)

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

    def _open_hist_folder(self, event):
        sel = self.hist_tree.focus()
        if not sel: return
        vals = self.hist_tree.item(sel,"values")
        if len(vals)>=6: open_folder(vals[5])
        # Cargar filepath en tab metadatos si existe
        titulo = vals[0] if vals else ""
        for r in reversed(self.history):
            if r.get("titulo","") == titulo:
                fp = r.get("filepath","")
                if fp and os.path.exists(fp):
                    self._meta_load(fp)
                break

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
        self._refresh_charts()

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
        self.after(100, self._reload_theme)

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
    import time

    # ── App principal (oculta mientras carga) ─────────────────────────────
    app = App()
    app.withdraw()   # ocultar hasta que el splash termine

    # ── Splash como Toplevel sobre la app ─────────────────────────────────
    splash = tk.Toplevel(app)
    splash.overrideredirect(True)
    splash.attributes("-topmost", True)
    splash.configure(bg="#111318")

    W, H = 420, 240
    sw = splash.winfo_screenwidth(); sh = splash.winfo_screenheight()
    splash.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    # Canvas del splash
    sc = tk.Canvas(splash, width=W, height=H, bg="#111318", highlightthickness=0)
    sc.pack(fill="both", expand=True)
    sc.create_rectangle(1, 1, W-1, H-1, outline="#2a2d38", fill="#1c1f26", width=1)
    sc.create_oval(178, 28, 242, 92, fill="#e94560", outline="")
    sc.create_text(210, 60, text="♪", font=("Segoe UI", 26, "bold"), fill="white")
    sc.create_text(210, 108, text="Audio Downloader",
                   font=("Segoe UI", 15, "bold"), fill="#e8eaf0")
    sc.create_text(210, 128, text="by Maken", font=("Segoe UI", 9), fill="#555a68")
    sc.create_rectangle(40, 170, 380, 178, fill="#2a2d38", outline="")
    bar = sc.create_rectangle(40, 170, 40, 178, fill="#e94560", outline="")
    status_lbl = sc.create_text(210, 196, text="Iniciando…",
                                 font=("Segoe UI", 9), fill="#8b909e")
    sc.create_text(210, 220, text="v3.0", font=("Segoe UI", 8), fill="#3a3d4a")
    splash.update()

    def _set_progress(pct, msg=""):
        x2 = 40 + int(340 * min(pct, 1.0))
        sc.coords(bar, 40, 170, x2, 178)
        if msg: sc.itemconfigure(status_lbl, text=msg)
        splash.update()

    # Animación de carga — pasos con tiempos reales
    STEPS = [
        (0.20, "Cargando configuración…"),
        (0.45, "Iniciando yt-dlp…"),
        (0.70, "Preparando interfaz…"),
        (0.90, "Casi listo…"),
    ]
    for pct, msg in STEPS:
        _set_progress(pct, msg)
        time.sleep(0.12)

    _set_progress(1.0, "¡Listo!")
    time.sleep(0.15)

    # Cerrar splash y mostrar app
    splash.destroy()
    app.geometry("960x720"); app.minsize(820,620)
    app.deiconify()

    # ── System tray al cerrar ─────────────────────────────────────────────
    def _on_close():
        if HAS_TRAY:
            app.withdraw()
            if app._tray_icon is None:
                try:
                    from PIL import Image as _PI, ImageDraw as _PID
                    ico = _PI.new("RGBA",(64,64),(0,0,0,0))
                    d   = _PID.Draw(ico)
                    hx  = app.C.get("ACCENT","#e94560").lstrip("#")
                    rgb = tuple(int(hx[i:i+2],16) for i in (0,2,4))
                    d.ellipse([4,4,60,60], fill=rgb+(255,))
                except Exception:
                    from PIL import Image as _PI
                    ico = _PI.new("RGBA",(64,64),(233,69,96,255))
                def _show(icon,item): app.after(0, app.deiconify)
                def _quit(icon,item): icon.stop(); app.after(0, app.destroy)
                menu = pystray.Menu(TrayItem("Abrir",_show,default=True), TrayItem("Salir",_quit))
                app._tray_icon = pystray.Icon("AudioDownloader", ico, "Audio Downloader", menu)
                threading.Thread(target=app._tray_icon.run, daemon=True).start()
        else:
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", _on_close)
    app.mainloop()

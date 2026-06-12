# 🎵 Audio Downloader

Descargador de audio para YouTube, SoundCloud, Vimeo, Bandcamp y +1000 plataformas más. Hecho por **Maken**.

---

## ✨ Características

- ⬇️ Descarga audio en **MP3, AAC, FLAC, WAV u OGG**
- 🎨 Portada incrustada automáticamente en el MP3
- 📋 Cola de descarga con múltiples URLs o playlists enteras
- 🌐 Compatible con YouTube, SoundCloud, Vimeo, Bandcamp, Twitter/X, Twitch y más
- 📂 Historial de descargas con búsqueda y exportar CSV
- ▶️ Reproductor de preescucha integrado
- 🔔 Notificaciones de escritorio al terminar
- ⚙️ Ajustes: proxy, velocidad máxima, cookies de navegador, reintentos automáticos
- 🎨 Tema oscuro / claro con color de acento personalizable
- 🌍 Interfaz en Español e Inglés

---

## 🚀 Uso (ejecutable .exe)

1. Descarga `AudioDownloader.exe` desde [Releases](../../releases)
2. Doble click — no necesitas instalar nada

> Compatible con **Windows 10 / 11**

---

## 🛠️ Ejecutar desde el código fuente

**Requisitos:**
```bash
pip install yt-dlp plyer pygame Pillow requests tkinterdnd2
```

FFmpeg (para conversión a MP3/AAC/etc.):
→ https://www.gyan.dev/ffmpeg/builds/ — descarga `ffmpeg-release-essentials.zip` y añade la carpeta `bin\` al PATH

**Ejecutar:**
```bash
python yt_mp3_downloader.py
```

---

## 📦 Compilar el .exe tú mismo

1. Coloca `ffmpeg.exe` y `ffprobe.exe` en una carpeta `ffmpeg\` junto al código
2. Ejecuta `build_exe.bat`
3. El exe aparece en `dist\AudioDownloader.exe`

Instrucciones detalladas en `INSTRUCCIONES_BUILD.txt`

---

## 📁 Archivos del repositorio

| Archivo | Descripción |
|---|---|
| `yt_mp3_downloader.py` | Código fuente principal |
| `build_exe.bat` | Script para compilar el .exe |
| `INSTRUCCIONES_BUILD.txt` | Guía detallada para compilar |

---

## ⚖️ Licencia

MIT — Eres libre de usarlo, modificarlo y redistribuirlo.  
Hecho por **Maken**.

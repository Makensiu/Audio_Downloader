# 🎵 Audio Downloader

Descargador de audio para YouTube, SoundCloud, Vimeo, Bandcamp y +1000 plataformas más.  
Hecho por **Maken** · Uso personal entre amigos · No redistribuir sin permiso.

---

## ✨ Características

**Descarga**
- ⬇️ Formatos: MP3, AAC, FLAC, WAV, OGG
- 🎨 Portada incrustada automática (thumbnail) o imagen personalizada
- 📋 Cola multi-URL con soporte de playlists completas
- 🔍 Buscador integrado — sin salir de la app
- ⭐ Favoritos — guarda URLs/canales para añadir a la cola en 1 click
- 🔄 Detección de duplicados — no descarga lo que ya tienes
- ⏰ Programación de descargas por hora (HH:MM)
- ↩️ Reintentos automáticos en error de red
- 📂 Perfiles de descarga (Música HQ / Podcast / Lossless / personalizados)

**Gestión**
- 📋 Historial con búsqueda, exportar CSV y exportar M3U
- 🏷️ Editor de metadatos ID3 (título, artista, álbum, año, género)
- 📊 Gráficas: descargas por mes + pie chart de formatos
- ▶️ Reproductor de preescucha integrado

**Extra**
- 🌙 Minimiza a bandeja del sistema (system tray)
- 🎨 Tema oscuro / claro + color de acento personalizable
- 🌍 Interfaz en Español e Inglés
- 🔔 Notificaciones de escritorio al terminar
- 🔄 Actualización de yt-dlp desde la propia app
- ⚙️ Proxy, velocidad máxima, cookies de navegador

---

## 🚀 Uso (ejecutable .exe)

1. Descarga `AudioDownloader.exe` desde [Releases](../../releases)
2. Doble click — no necesitas instalar nada

> Compatible con **Windows 10 / 11**

---

## 🛠️ Ejecutar desde código fuente

```bash
pip install yt-dlp plyer pygame Pillow requests tkinterdnd2 mutagen matplotlib pystray
python yt_mp3_downloader.py
```

FFmpeg (necesario para conversión):  
→ https://www.gyan.dev/ffmpeg/builds/ — `ffmpeg-release-essentials.zip` → añade `bin\` al PATH

---

## 📦 Compilar el .exe

1. Crea carpeta `ffmpeg\` junto al código con `ffmpeg.exe` y `ffprobe.exe`
2. Ejecuta `build_exe.bat`
3. Resultado en `dist\AudioDownloader.exe`

Guía detallada en `INSTRUCCIONES_BUILD.txt`

---

## 📁 Archivos

| Archivo | Descripción |
|---|---|
| `yt_mp3_downloader.py` | Código fuente principal |
| `build_exe.bat` | Script para compilar el .exe |
| `INSTRUCCIONES_BUILD.txt` | Guía de compilación |

---

## ⚖️ Licencia

MIT — Hecho por **Maken**.

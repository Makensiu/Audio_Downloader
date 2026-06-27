# 🎵 Audio Downloader

Descargador de audio y vídeo para YouTube, SoundCloud, Vimeo, Bandcamp y +1000 plataformas más.  
Hecho por **Maken** · Uso personal entre amigos · No redistribuir sin permiso.

---

## ✨ Características

**Descarga de audio**
- ⬇️ Formatos: MP3, AAC, FLAC, WAV, OGG
- 🎨 Portada incrustada automática o imagen personalizada
- 📋 Cola multi-URL con soporte de playlists completas
- 🔄 Detección de duplicados — no descarga lo que ya tienes
- ⏰ Programación de descargas por hora (HH:MM)
- ↩️ Reintentos automáticos en error de red
- 📂 Perfiles de descarga (Música HQ / Podcast / Lossless / personalizados)
- 📂 Auto-organizar por artista/álbum tras descargar

**Descarga de vídeo**
- 🎬 MP4 en 720p / 1080p / 1440p / 4K
- 📝 Subtítulos opcionales en ES/EN

**Búsqueda y reproducción**
- 🔍 Buscador integrado — sin salir de la app
- ▶️ Preview de 30s antes de descargar
- ⭐ Favoritos — guarda URLs/canales para añadir a la cola en 1 click
- ▶️ Reproductor de preescucha en historial

**Gestión**
- 📋 Historial con búsqueda, exportar CSV y exportar M3U
- 🏷️ Editor de metadatos ID3 (título, artista, álbum, año, género)
- 🔄 Convertidor local entre formatos (sin descargar nada)
- 🎵 Letras sincronizadas (.lrc) con guardado de archivo
- 📊 Gráficas: descargas por mes + pie chart de formatos

**Interfaz**
- 🖥️ Sidebar lateral estilo Material Design (oscuro/claro)
- ✨ Splash screen de carga
- 🌙 Minimiza a bandeja del sistema (system tray)
- 🎨 Tema oscuro / claro + color de acento personalizable
- 🌍 Interfaz en Español e Inglés
- 🔔 Notificaciones de escritorio al terminar

**Extra**
- ⚙️ Proxy, velocidad máxima, cookies de navegador, descargas paralelas
- 🔄 Actualización de yt-dlp desde la propia app

---

## 🚀 Uso (ejecutable .exe)

1. Descarga `AudioDownloader.exe` desde [Releases](../../releases)
2. Doble click — no necesitas instalar nada

> Compatible con **Windows 10 / 11**

---

## 🛠️ Ejecutar desde código fuente

```bash
pip install yt-dlp plyer pygame Pillow requests tkinterdnd2 mutagen matplotlib pystray syncedlyrics
python yt_mp3_downloader.py
```

FFmpeg (necesario para conversión):  
→ https://www.gyan.dev/ffmpeg/builds/ — `ffmpeg-release-essentials.zip` → añade `bin\` al PATH

---

## 📦 Compilar el .exe tú mismo

1. Crea carpeta `ffmpeg\` junto al código con `ffmpeg.exe` y `ffprobe.exe`
2. Ejecuta `build_exe.bat`
3. Resultado en `dist\AudioDownloader.exe`

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

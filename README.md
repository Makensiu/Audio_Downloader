# 🎵 Maken Audio Downloader

Descargador de audio y vídeo para YouTube, SoundCloud, Vimeo, Bandcamp y +1000 plataformas más.  
Hecho por **Maken** · Uso personal entre amigos · No redistribuir sin permiso.

---

## ✨ Características

**Interfaz**
- 🏠 Dashboard con estadísticas, últimas descargas y favoritos
- 🖥️ Sidebar lateral estilo Material Design (oscuro/claro)
- ✨ Splash screen de carga
- 🗜️ Modo compacto (mini ventana con progreso mientras descarga en segundo plano)
- 💡 Tooltips y atajos de teclado (Esc cancela, Ctrl+V pega URL)
- 🌙 Minimiza a bandeja del sistema (configurable)

**Descarga de audio**
- ⬇️ Formatos: MP3, AAC, FLAC, WAV, OGG
- 🎨 Portada incrustada automática o imagen personalizada
- 📋 Cola multi-URL con soporte de playlists completas
- 📋 Detección de URL en el portapapeles
- 🔄 Detección de duplicados — no descarga lo que ya tienes
- ⏰ Programación de descargas por hora (HH:MM)
- ↩️ Reintentos automáticos en error de red
- 📶 Verificación de conexión antes de descargar
- 📂 Perfiles de descarga y auto-organizar por artista/álbum
- ⚡ Fragmentos concurrentes por archivo + cache de metadatos (descargas más rápidas)

**Descarga de vídeo**
- 🎬 MP4 en 720p / 1080p / 1440p / 4K con subtítulos opcionales

**Búsqueda y reproducción**
- 🔍 Buscador integrado con preview de 30s
- ⭐ Favoritos con acceso rápido desde el Dashboard
- ▶️ Reproductor de preescucha en historial

**Gestión**
- 📋 Historial con búsqueda, selección múltiple, exportar CSV y M3U
- 🏷️ Editor de metadatos ID3, individual y en lote (batch)
- 🔄 Convertidor local entre formatos
- 🎵 Letras sincronizadas (.lrc)
- 📊 Gráficas de descargas por mes y formatos

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
2. Asegúrate de que `maken_icon.ico` esté en la misma carpeta
3. Ejecuta `build_exe.bat`
4. Resultado en `dist\AudioDownloader.exe`

---

## 📁 Archivos

| Archivo | Descripción |
|---|---|
| `yt_mp3_downloader.py` | Código fuente principal |
| `build_exe.bat` | Script para compilar el .exe |
| `maken_icon.ico` | Icono de la aplicación |
| `INSTRUCCIONES_BUILD.txt` | Guía de compilación |

---

## ⚖️ Licencia

MIT — Hecho por **Maken**.

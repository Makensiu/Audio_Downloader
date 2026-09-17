@echo off
:: ─────────────────────────────────────────────────────────────────
::  Maken Audio Downloader — Build script v9
:: ─────────────────────────────────────────────────────────────────

echo [1/4] Instalando dependencias...
pip install pyinstaller yt-dlp plyer pygame Pillow requests tkinterdnd2 mutagen matplotlib pystray syncedlyrics

echo.
echo [2/4] Comprobando ffmpeg.exe y ffprobe.exe...
if not exist "ffmpeg\ffmpeg.exe" (
    echo ERROR: No se encontro ffmpeg\ffmpeg.exe
    echo.
    echo  1. Descarga FFmpeg: https://www.gyan.dev/ffmpeg/builds/
    echo     Archivo: ffmpeg-release-essentials.zip
    echo  2. Extrae y copia ffmpeg.exe + ffprobe.exe a la carpeta "ffmpeg\"
    echo  3. Vuelve a ejecutar este script
    pause
    exit /b 1
)
if not exist "ffmpeg\ffprobe.exe" (
    echo ERROR: No se encontro ffmpeg\ffprobe.exe
    pause
    exit /b 1
)
echo  OK

set ICON_ARG=
if exist "maken_icon.ico" (
    set ICON_ARG=--icon "maken_icon.ico"
    echo  Icono encontrado: maken_icon.ico
) else (
    echo  Aviso: no se encontro maken_icon.ico, se usara el icono por defecto
)

echo.
echo [3/4] Compilando .exe...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "AudioDownloader" ^
  %ICON_ARG% ^
  --add-binary "ffmpeg\ffmpeg.exe;ffmpeg" ^
  --add-binary "ffmpeg\ffprobe.exe;ffmpeg" ^
  --add-data "maken_icon.ico;." ^
  --hidden-import "plyer.platforms.win.notification" ^
  --hidden-import "tkinterdnd2" ^
  --hidden-import "pygame" ^
  --hidden-import "PIL" ^
  --hidden-import "mutagen" ^
  --hidden-import "pystray" ^
  --hidden-import "matplotlib" ^
  --hidden-import "syncedlyrics" ^
  --collect-all "yt_dlp" ^
  --collect-all "tkinterdnd2" ^
  --collect-all "matplotlib" ^
  --collect-all "pystray" ^
  --collect-all "syncedlyrics" ^
  yt_mp3_downloader.py

echo.
echo [4/4] Listo!
if exist "dist\AudioDownloader.exe" (
    echo  EXE generado en: dist\AudioDownloader.exe
    echo  Comparte ese unico archivo con tus amigos.
) else (
    echo  ERROR: Revisa los mensajes de arriba.
)
pause

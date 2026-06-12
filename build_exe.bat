@echo off
:: ─────────────────────────────────────────────────────────────────
::  Audio Downloader — Build script
::  Genera AudioDownloader.exe con FFmpeg empaquetado dentro
::  Ejecutar desde la carpeta donde están los archivos
:: ─────────────────────────────────────────────────────────────────

echo [1/4] Instalando dependencias de Python...
pip install pyinstaller yt-dlp plyer pygame Pillow requests tkinterdnd2

echo.
echo [2/4] Comprobando ffmpeg.exe y ffprobe.exe...
if not exist "ffmpeg\ffmpeg.exe" (
    echo ERROR: No se encontro ffmpeg\ffmpeg.exe
    echo.
    echo  1. Descarga FFmpeg desde: https://www.gyan.dev/ffmpeg/builds/
    echo     Archivo: ffmpeg-release-essentials.zip
    echo  2. Descomprime el zip
    echo  3. Dentro encontraras una carpeta "bin" con ffmpeg.exe y ffprobe.exe
    echo  4. Crea una carpeta llamada "ffmpeg" junto a este .bat
    echo  5. Copia ffmpeg.exe y ffprobe.exe dentro de esa carpeta "ffmpeg"
    echo  6. Vuelve a ejecutar este script
    pause
    exit /b 1
)
if not exist "ffmpeg\ffprobe.exe" (
    echo ERROR: No se encontro ffmpeg\ffprobe.exe
    echo Copia ffprobe.exe tambien en la carpeta ffmpeg\
    pause
    exit /b 1
)
echo  ffmpeg.exe y ffprobe.exe encontrados OK

echo.
echo [3/4] Compilando .exe con PyInstaller...
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "AudioDownloader" ^
  --add-binary "ffmpeg\ffmpeg.exe;ffmpeg" ^
  --add-binary "ffmpeg\ffprobe.exe;ffmpeg" ^
  --hidden-import "plyer.platforms.win.notification" ^
  --hidden-import "tkinterdnd2" ^
  --hidden-import "pygame" ^
  --hidden-import "PIL" ^
  --collect-all "yt_dlp" ^
  --collect-all "tkinterdnd2" ^
  yt_mp3_downloader.py

echo.
echo [4/4] Listo!
if exist "dist\AudioDownloader.exe" (
    echo  EXE generado en: dist\AudioDownloader.exe
    echo  Puedes compartir ese unico archivo con tus amigos.
    echo  No necesitan Python, FFmpeg ni nada instalado.
) else (
    echo  ERROR: No se genero el exe. Revisa los mensajes de arriba.
)

pause

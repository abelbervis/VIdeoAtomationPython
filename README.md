# 🚀 NASA Shorts Generator (`nasa_shorts`)

Generador minimalista de videos verticales automáticos (formato YouTube Shorts, Instagram Reels y TikTok) sobre ciencia, astronomía y física utilizando material audiovisual oficial de la **NASA**.

---

## 🌟 Características

- **Sin interfaz gráfica ni servidores**: Aplicación CLI minimalista y robusta para la terminal.
- **Formato Vertical Óptimo**: Resolución 1080x1920 (9:16), 30 FPS, H.264 / AAC, renderizado rápido con FFmpeg.
- **Contenido Oficial de la NASA**: Consulta en tiempo real la API oficial de la NASA (*NASA Image and Video Library*). Prioriza videos en movimiento y complementa con fotografías de alta resolución.
- **Guiones Científicos Estructurados**: Generación mediante LLM (Gemini / OpenAI / motor científico local) con gancho inicial (hook), división por escenas y palabras clave en inglés para máxima precisión en la búsqueda astronómica.
- **Narración y Subtítulos Dinámicos**: Módulo TTS con timestamps reales y subtítulos automáticos (`.srt` y `.ass`) con estilo viral y resaltado activo palabra por palabra (`dynamic highlight`).
- **Transiciones Cinemáticas Suaves**: Transiciones fluidas entre escenas con FFmpeg `xfade` (`fade`, `dissolve`, `slideleft`, `wipeleft`, `random`) y variedad en movimientos de cámara Ken Burns (zoom-in, zoom-out, paneos y tilts) para imágenes fijas.
- **Efectos de Sonido Automáticos (SFX)**: Generador de efectos de audio procedurales sincronizados: impacto cinematográfico (*boom*) en la escena gancho y barridos (*whoosh*) en cada cambio de escena.
- **Música de Fondo Opcional**: Mezcla automática de 3 pistas (voz, música, SFX) con *audio ducking* si existe un archivo en `assets/music/background.mp3`.
- **Registro de Licencias y Fuentes**: Exporta `output/source_metadata.json` con todos los identificadores de NASA, autores y enlaces originales.
- **Bajo Consumo de Hardware**: Optimizado para ejecutarse en computadoras estándar (Intel i5, 8GB RAM, sin GPU dedicada).

---

## 📁 Estructura del Proyecto

```text
nasa_shorts/
│
├── main.py                     # Punto de entrada CLI
├── config.py                   # Configuraciones centralizadas y variables de entorno
├── requirements.txt            # Dependencias Python
├── .env.example                # Plantilla de variables de entorno y API keys
│
├── providers/
│   └── nasa.py                 # Cliente oficial NASA Image & Video API
│
├── ai/
│   └── script_generator.py     # Generador de guiones estructurados (Gemini/OpenAI)
│
├── audio/
│   ├── tts.py                  # Motor TTS (Edge-TTS, OpenAI, Google)
│   └── music.py                # Mezcla y ajuste de música de fondo
│
├── subtitles/
│   └── generator.py            # Generación de subtítulos .srt y .ass verticales
│
├── video/
│   └── render.py               # Renderizado con FFmpeg y efectos Ken Burns
│
├── utils/
│   └── files.py                # Utilidades de descarga, metadatos y sistema de archivos
│
├── assets/
│   ├── music/                  # Carpeta para background.mp3 opcional
│   └── .gitkeep
│
├── output/                     # Carpeta raíz de salidas
│   └── <nombre_del_video>/     # Cada video se guarda en su propia carpeta organizada
│       ├── <nombre>.mp4        # Video vertical final renderizado (1080x1920)
│       ├── script.json         # Guión generado por la IA (título, hook, escenas, keywords)
│       ├── subtitles.srt       # Subtítulos universales sincronizados
│       ├── subtitles.ass       # Subtítulos verticales formateados para móviles
│       ├── narration.mp3       # Pista de audio de la voz en off completa
│       └── metadata.json       # Registro de resolución, duración y fuentes/licencias
│
└── README.md
```

---

## 🐳 Ejecución Rápida con Docker (Sin instalar Python ni FFmpeg localmente)

Si tienes **Docker** instalado, no necesitas instalar Python, ni librerías, ni FFmpeg en tu sistema operativo:

### 1. Construir la imagen (solo una vez):
```bash
docker build -t nasa_shorts .
```

### 2. Ejecutar y generar tu video:
```bash
# En Linux / macOS:
docker run --rm -v "$(pwd)/output:/app/output" --env-file .env nasa_shorts --topic "agujeros negros"

# En Windows (PowerShell):
docker run --rm -v "${PWD}/output:/app/output" --env-file .env nasa_shorts --topic "agujeros negros"

# En Windows (CMD):
docker run --rm -v "%cd%/output:/app/output" --env-file .env nasa_shorts --topic "agujeros negros"
```

El video se guardará automáticamente en la carpeta local `output/` de tu máquina.

---

## ⚙️ Requisitos Previos (Sin Docker)

1. **Python 3.10+**
2. **FFmpeg** instalado en tu sistema:
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install -y ffmpeg`
   - **macOS** (Homebrew): `brew install ffmpeg`
   - **Windows** (Chocolatey o Scoop): `choco install ffmpeg` o descarga desde [ffmpeg.org](https://ffmpeg.org/download.html).

---

## 📥 Instalación

1. Clona o copia el repositorio:
   ```bash
   cd nasa_shorts
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. (Opcional) Configura tus API keys en `.env`:
   ```bash
   cp .env.example .env
   ```
   *Nota: La API oficial de la NASA de imágenes y videos es pública y no requiere clave obligatoria. Si agregas `GEMINI_API_KEY` u `OPENAI_API_KEY`, el generador creará guiones dinámicos personalizados con IA.*

---

## 💻 Uso en Terminal (CLI)

### 1. Generación Básica
```bash
python main.py --topic "agujeros negros"
```

### 2. Con Pregunta Específica
```bash
python main.py --topic "¿Qué pasaría si la Tierra dejara de girar?"
```

### 3. Ajustando la Duración
```bash
python main.py --topic "Marte" --duration 30
python main.py --topic "James Webb" --duration 45
```

### 4. Usar la API de Pexels (Stock Videos en 9:16 Vertical & Fotos HD)
Puedes generar videos usando la biblioteca oficial de **Pexels** (ideal para temas de naturaleza, océanos, tecnología, ciudades, física, etc.):

1. Obtén tu clave gratuita en [pexels.com/api](https://www.pexels.com/api/) (se genera al instante en 30 segundos).
2. Agrégala en tu archivo `.env`:
   ```env
   PEXELS_API_KEY="tu_clave_de_pexels_aqui"
   ```
3. Ejecuta indicando `--provider pexels`:
   ```bash
   # Océanos con Pexels
   python main.py --topic "los secretos del océano profundo" --provider pexels

   # Inteligencia artificial o tecnología con Pexels
   python main.py --topic "la revolución de la inteligencia artificial" --provider pexels

   # O pasando la clave directamente por parámetro CLI:
   python main.py --topic "volcanes" --provider pexels --pexels-key "tu_clave"
   ```

### 5. Modo Inteligente Automático (`--provider auto`)
Por defecto (`auto`), el sistema enruta inteligentemente:
- Si el tema es astronómico/espacio ("Marte", "agujeros negros", "Tierra"), consulta primero la **NASA**.
- Si el tema es general o no se encuentra en la NASA, busca videos verticales en **Pexels**.

### 6. Transiciones, Subtítulos Dinámicos y Efectos de Sonido
Por defecto, las transiciones suaves (`fade`), los subtítulos resaltados dinámicamente y los efectos de sonido (*whoosh* y *boom*) están **activados automáticamente**. Puedes personalizar su comportamiento:

```bash
# Elegir tipo de transición (fade, dissolve, wipeleft, slideleft, random, etc.):
python main.py --topic "agujeros negros" --transition dissolve

# Transiciones aleatorias variadas en cada corte:
python main.py --topic "nebulosas" --transition random

# Generar con cortes directos tradicionales sin transiciones:
python main.py --topic "satélites" --no-transitions

# Desactivar subtítulos dinámicos palabra por palabra (mostrar líneas estáticas):
python main.py --topic "marte" --no-dynamic-subtitles

# Desactivar efectos de sonido automáticos:
python main.py --topic "el sol" --no-sfx
```

### 7. Con Música de Fondo
Coloca un archivo en `assets/music/background.mp3` o pásalo como argumento:
```bash
python main.py --topic "El Sistema Solar" --music "ruta/a/mi_musica.mp3"
```

### 8. Ayuda de Comandos
```bash
python main.py --help
```

---

## 📜 Salidas Generadas

Cada ejecución crea una **sola carpeta con el nombre del video** dentro de `output/<nombre_del_video>/` con todos sus archivos agrupados:

- `output/<nombre_del_video>/<nombre_del_video>.mp4`: Video vertical final 1080x1920 optimizado para Shorts/Reels/TikTok.
- `output/<nombre_del_video>/script.json`: Guión completo estructurado por la IA (título, gancho, escenas con narración y keywords).
- `output/<nombre_del_video>/subtitles.srt`: Subtítulos universales sincronizados listos para subir a YouTube/TikTok.
- `output/<nombre_del_video>/subtitles.ass`: Subtítulos con estilos y fuentes adaptadas a móviles.
- `output/<nombre_del_video>/narration.mp3`: Audio completo de la locución/narración.
- `output/<nombre_del_video>/metadata.json`: Registro de resolución, FPS, duración y atribución/licencias de las imágenes y videos (NASA / Pexels).

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
# Con docker-compose (el método más simple):
docker compose run --rm nasa-shorts --discover
docker compose run --rm nasa-shorts --top-choice 2

# O con docker run:
# En Linux / macOS:
docker run --rm -v "$(pwd)/output:/app/output" --env-file .env nasa_shorts --discover
docker run --rm -v "$(pwd)/output:/app/output" --env-file .env nasa_shorts --top-choice 2

# En Windows (PowerShell):
docker run --rm -v "${PWD}/output:/app/output" --env-file .env nasa_shorts --discover
docker run --rm -v "${PWD}/output:/app/output" --env-file .env nasa_shorts --top-choice 2

# En Windows (CMD):
docker run --rm -v "%cd%/output:/app/output" --env-file .env nasa_shorts --discover
docker run --rm -v "%cd%/output:/app/output" --env-file .env nasa_shorts --top-choice 2
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

### 4. Modo Descubrimiento y Tendencias Virales de la NASA (`--discover` y `--trending`)
Puedes consultar en tiempo real las novedades astronómicas de la NASA evaluadas con IA, o crear videos sobre ellas de forma 100% autónoma:

```bash
# 1. Explorar la lista clasificada por viralidad (sin renderizar video):
python main.py --discover

# 2. Generar el video de la opción elegida (garantizando exactamente el tema de la lista):
python main.py --top-choice 1   # Genera la opción #1
python main.py --top-choice 2   # Genera la opción #2

# 3. Si deseas forzar una nueva consulta en vivo a la NASA ignorando la caché previa:
python main.py --discover --refresh
# o directamente:
python main.py --top-choice 1 --refresh
```

> **Sincronización de Sesión**: La lista generada con `--discover` se guarda en `output/.trending_cache.json`. Al ejecutar `--top-choice <N>`, el sistema reutiliza la lista exacta de tu consulta previa para que la opción elegida coincida al 100% (incluso entre ejecuciones de contenedores en Docker).

### 5. Modo Descubridor de Ideas de Contenido (`--discover-ideas` o `--ideas`)
Si no tienes un tema en mente o pasas mucho tiempo pensando qué video producir, este modo actúa como un **estratega de contenido viral interactivo**. Te sugiere ideas estructuradas con ganchos (*hooks*) de 3 segundos, enfoques visuales y justificación de retención:

```bash
# 1. Abrir el descubridor interactivo de ideas:
python main.py --discover-ideas

# 2. Filtrar por categorías o nichos específicos:
python main.py --discover-ideas --ideas-category misterios
python main.py --discover-ideas --ideas-category agujeros_negros
python main.py --discover-ideas --ideas-category planetas_extremos
python main.py --discover-ideas --ideas-category james_webb
python main.py --discover-ideas --ideas-category paradojas
python main.py --discover-ideas --ideas-category que_pasaria_si

# 3. Solo ver la lista en terminal sin entrar al modo interactivo:
python main.py --discover-ideas --list-ideas

# 4. Generar directamente una opción específica:
python main.py --discover-ideas --top-choice 1
```

En el menú interactivo puedes pulsar el número de la idea `[1-5]` para producir el video al instante, pulsar `[R]` para regenerar 5 ideas frescas diferentes, o `[C]` para cambiar de categoría temática.

### 5. Navegación Histórica en el Archivo de la NASA (`--date`, `--days-back`, `--archive`)
¿Te interesa hablar de eventos o descubrimientos astronómicos del pasado aunque no sean recientes? Puedes viajar en el tiempo a cualquier fecha desde **junio de 1995 hasta hoy**:

```bash
# 1. Explorar una fecha específica en el pasado (por ejemplo, el eclipse de abril de 2024 o el sobrevuelo de Plutón en 2015):
python main.py --discover --date 2024-04-08
python main.py --discover --date 2015-07-14

# 2. Navegar N días hacia atrás en el pasado:
python main.py --discover --days-back 30   # Descubrimientos de hace 1 mes
python main.py --discover --days-back 180  # Descubrimientos de hace 6 meses
python main.py --discover --days-back 365  # Descubrimientos de hace 1 año

# 3. Explorar gemas aleatorias legendarias a lo largo de 30 años de archivo de la NASA:
python main.py --discover --archive

# 4. Generar el video directamente a partir del descubrimiento histórico elegido:
python main.py --top-choice 2

# En Docker (con docker compose):
docker compose run --rm nasa-shorts --discover --date 2024-04-08
docker compose run --rm nasa-shorts --top-choice 2
```

### 6. Atribución con Fecha en Pantalla
Cada imagen o video de la NASA incluye automáticamente una elegante insignia semi-transparente en la esquina superior izquierda con la fuente y la **fecha exacta de captura o publicación** (por ejemplo: `NASA APOD · 8 Abr 2024` o `NASA Image & Video Library · 14 Jul 2015`).
- La insignia aparece con un suave desvanecimiento (`fade-in`), permanece en pantalla durante **2.8 segundos** para brindar el crédito y contexto temporal, y luego se desvanece suavemente para no saturar la pantalla ni distraer al espectador de la narrativa.
- Si prefieres desactivar la fecha en la insignia, puedes usar el argumento `--no-badge-date`.

### 5. Usar la API de Pexels (Stock Videos en 9:16 Vertical & Fotos HD)
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

### 5. Proveedor Pixabay para Animaciones y Simulaciones 3D (`--provider pixabay`)
Pixabay destaca por sus animaciones 3D/CGI de física cuántica, bucles cósmicos, órbitas y nebulosas en movimiento:

1. Obtén tu clave gratuita en [pixabay.com/api/docs](https://pixabay.com/api/docs/) (hasta 5.000 peticiones/hora).
2. Agrégala en tu `.env`:
   ```env
   PIXABAY_API_KEY="tu_clave_de_pixabay_aqui"
   ```
3. Ejecuta indicando `--provider pixabay`:
   ```bash
   python main.py --topic "colisión de galaxias" --provider pixabay
   python main.py --topic "simulación de agujero negro" --provider pixabay --pixabay-key "tu_clave"
   ```

### 6. Proveedor Pollinations con Modelo FLUX (`--provider pollinations`) y Rescate Automático con IA
¿Narras un concepto cósmico imposible o exótico (lluvia de hierro en un exoplaneta, el interior de un horizonte de sucesos, un océano de metano en Titán) que las bibliotecas de stock comunes no tienen?
El sistema integra **Pollinations.ai** potenciado por el modelo **FLUX.1**:

- **Completamente Gratuito y sin registro obligatorio:** No requiere API key obligatoria para uso público. Si deseas elevar los límites de concurrencia puedes obtener una clave gratuita en [enter.pollinations.ai](https://enter.pollinations.ai/).
- **Generación Visual Dedicada:** Puedes crear todo el video usando imágenes fotorrealistas de alta definición (9:16 vertical) generadas por IA:
  ```bash
  python main.py --topic "lluvia de magma en exoplanetas" --provider pollinations
  ```
- **Fallback Inteligente con IA (Rescate en modo Auto):** En la cascada inteligente (`--provider auto`), si NASA, Pexels o Pixabay no encuentran un recurso que coincida con la narración de una escena, el sistema **no coloca fondos vacíos**: genera automáticamente una toma cinematográfica personalizada con FLUX que ilustra exactamente lo que se está narrando.
  - Para desactivar el rescate de IA y usar fondo neutro sintético: `--no-ai-fallback`.

### 7. Cascada Inteligente de 4 Niveles (`--provider auto`)
Por defecto (`auto`), el sistema ejecuta un enrutamiento en cascada de alta resiliencia:
- **Temas Espaciales:**
  1. **NASA:** Tomas reales y documentales oficiales (`keywords`).
  2. **Pexels:** Videos cinematográficos de archivo y timelapses de cielo nocturno (`keywords`).
  3. **Pixabay:** Animaciones 3D, CGI y simulaciones espaciales (`keywords`).
  4. **Pollinations (FLUX):** Generación fotorrealista personalizada para conceptos científicos que no existen en stock.
- **Temas Generales / Terrestres:**
  1. **Pexels** → 2. **Pixabay** → 3. **NASA** → 4. **Pollinations (FLUX)**.

### 8. Generación Directa y Agente Revisor Opcional (`--review`)
Por defecto, la generación de guión se ejecuta en **un solo pase directo y conciso** sin agentes intermedios innecesarios, maximizando la velocidad y facilidad de edición:
- **Búsqueda visual unificada:** El guión incluye una lista concisa de `keywords` en inglés por escena que alimenta a todos los proveedores sin duplicar campos.
- **Cadencia y ritmo optimizado:** El modelo genera narraciones concisas de 12 a 16 palabras por escena calculadas para el habla natural.
- **Revisor opcional:** Si deseas activar una segunda pasada de auditoría con un crítico LLM:
```bash
python main.py --topic "materia oscura" --review
```
```

### 8. Transiciones, Subtítulos Dinámicos y Efectos de Sonido
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

# Subtítulos Karaoke con animación Pop-In y ajuste de palabras por pantalla:
# Por defecto viene activo el efecto 'pop' con 3 palabras por pantalla (ritmo viral para Shorts/Reels):
python main.py --topic "agujeros negros" --color yellow --subtitle-animation pop --subtitle-words 3

# Desactivar animación de rebote y usar corte instantáneo:
python main.py --topic "nebulosas" --subtitle-animation none

# Desactivar efectos de sonido automáticos:
python main.py --topic "el sol" --no-sfx

# Mezcla de Audio Dinámica (Auto-Ducking Sidechain):
# Viene activo por defecto: la música se atenúa cuando la voz habla y sube suavemente en pausas.
# Si prefieres una mezcla de volumen de música plano sin compresión sidechain:
python main.py --topic "marte" --no-auto-ducking

# Titular / Gancho Flotante de Alto Impacto (Hook Title Overlay):
# Viene activo por defecto: en los primeros 2.5s aparece un titular contundente en el tercio superior
# con entrada elástica de impacto sincronizada con el SFX boom.
# Puedes personalizar el texto o desactivarlo:
python main.py --topic "el sol" --hook-title "¿Y SI EL SOL SE APAGA HOY?"
python main.py --topic "agujeros negros" --no-hook-title

# Opciones de Badges de Atribución y Etiquetas Visuales:
# Por defecto se muestra qué objeto se observa (ej. Cometa Pons-Brooks) y la fuente con fecha.
# Puedes ocultar la etiqueta del objeto visual o la fecha si prefieres un diseño más minimalista:
python main.py --topic "cometas" --no-badge-label
python main.py --topic "galaxias" --no-badge-date
```

### 7. Filtro Inteligente Anti-Logos y Relevancia Visual Cósmica
El motor de búsqueda de medios integra un filtro de calidad estricto:
- **Exclusión Institucional**: Descarta automáticamente imágenes con logos institucionales (meatball, worm), conferencias de prensa, salas de reuniones, directores en podios o fotos corporativas.
- **Anclaje Temático**: Todas las escenas intermedias mantienen continuidad visual ancladas al objeto astronómico real del descubrimiento en lugar de fotos genéricas o disconexas.
- **Etiqueta Visual Cinematográfica**: Cada escena muestra durante los primeros 2.8 segundos dos elegantes insignias semitransparentes apiladas y perfectamente espaciadas: la superior indica qué se está observando en pantalla (ej. `Cometa Pons-Brooks`, `Corona Solar Total`, `Galaxia M51`) y la inferior muestra su fuente y fecha oficial (`NASA APOD · 8 Abr 2024`), sin interferir entre sí.

### 8. Con Música de Fondo
Coloca un archivo en `assets/music/background.mp3` o pásalo como argumento:
```bash
python main.py --topic "El Sistema Solar" --music "ruta/a/mi_musica.mp3"
```

### 9. Ayuda de Comandos
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

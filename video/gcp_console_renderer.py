"""
Google Cloud Console Hyper-Realistic UI Simulator & Scene Renderer.
Replaces abstract, text-heavy slides with visual, hands-on demonstrations of the actual GCP Console:
- Google Cloud Top Header & Navigation Bar
- Real interactive forms (Create Bucket, Location selection, Storage Class picker)
- Real-world visual metaphors (Desk Drawer, Closet, Storage Unit, Underground Vault)
- Drag & Drop file uploads with progress indicators
- Zoomed-in focused CLI terminals
- Extreme visual rule: Max 1 core idea and 3 keywords at a time!
"""

import html
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


def escape_xml(text: str) -> str:
    """Escapes special characters for SVG/XML."""
    return html.escape(str(text))


class GCPConsoleRenderer:
    """Renders pixel-perfect Google Cloud Console UI simulation scenes."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def render_console_scene_svg(
        self,
        scene_type: str,
        title: str,
        highlight_keyword: str = "",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Renders an engaging, practical GCP Console scene."""
        w, h = self.width, self.height
        data = extra_data or {}
        
        # Build layout body based on scene_type
        if scene_type == "hook_bill_alert":
            body_svg = self._build_hook_bill_alert(w, h, data)
        elif scene_type == "create_bucket_ui":
            body_svg = self._build_create_bucket_ui(w, h, data)
        elif scene_type == "storage_analogies":
            body_svg = self._build_storage_analogies(w, h, data)
        elif scene_type == "drag_and_drop_upload":
            body_svg = self._build_drag_and_drop_upload(w, h, data)
        elif scene_type == "cli_zoom":
            body_svg = self._build_cli_zoom(w, h, data)
        elif scene_type == "golden_rules_summary":
            body_svg = self._build_golden_rules_summary(w, h, data)
        else:
            body_svg = self._build_storage_analogies(w, h, data)

        keyword_pill = ""
        if highlight_keyword:
            keyword_pill = f"""
            <rect x="{w - 380}" y="24" width="320" height="42" rx="21" fill="#1E3A8A" stroke="#38BDF8" stroke-width="2"/>
            <text x="{w - 220}" y="51" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">
              ⚡ {escape_xml(highlight_keyword.upper())}
            </text>"""

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="bgConsole" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F19"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>

    <!-- Top GCP Rainbow Stripe -->
    <linearGradient id="gcpRainbow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4285F4"/>
      <stop offset="35%" stop-color="#34A853"/>
      <stop offset="70%" stop-color="#FBBC05"/>
      <stop offset="100%" stop-color="#EA4335"/>
    </linearGradient>

    <filter id="boxShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000000" flood-opacity="0.6"/>
    </filter>

    <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="#38BDF8" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Canvas Background -->
  <rect width="{w}" height="{h}" fill="url(#bgConsole)"/>
  <rect x="0" y="0" width="{w}" height="4" fill="url(#gcpRainbow)"/>

  <!-- OFFICIAL GOOGLE CLOUD CONSOLE TOP HEADER -->
  <g id="gcp_header">
    <rect x="0" y="4" width="{w}" height="64" fill="#182234" stroke="#1E293B" stroke-width="1"/>
    
    <!-- Menu Hamburger & Logo -->
    <g transform="translate(24, 22)">
      <line x1="0" y1="4" x2="20" y2="4" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="0" y1="12" x2="20" y2="12" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="0" y1="20" x2="20" y2="20" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
      
      <!-- Google Cloud Logo & Title -->
      <circle cx="50" cy="12" r="10" fill="#4285F4"/>
      <text x="70" y="20" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
        Google Cloud
      </text>
      <text x="210" y="20" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="18">
        |  Consola de Administración
      </text>
    </g>

    <!-- Project Picker -->
    <g transform="translate(520, 16)">
      <rect x="0" y="0" width="280" height="38" rx="8" fill="#0F172A" stroke="#334155" stroke-width="1.2"/>
      <text x="16" y="24" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="14" font-weight="bold">
        📁 prod-empresa-2025
      </text>
      <polygon points="255,16 265,16 260,24" fill="#94A3B8"/>
    </g>

    <!-- Search Bar -->
    <g transform="translate(830, 16)">
      <rect x="0" y="0" width="460" height="38" rx="8" fill="#0F172A" stroke="#334155" stroke-width="1.2"/>
      <text x="18" y="24" fill="#64748B" font-family="'Liberation Sans', sans-serif" font-size="14">
        🔍 Buscar en Cloud Storage, buckets, permisos...
      </text>
    </g>

    <!-- Right Icons & Status -->
    <g transform="translate({w - 240}, 18)">
      <rect x="0" y="0" width="36" height="34" rx="6" fill="#1E293B"/>
      <text x="10" y="23" fill="#38BDF8" font-family="monospace" font-size="16" font-weight="bold">&gt;_</text>
      
      <circle cx="65" cy="17" r="14" fill="#047857"/>
      <text x="65" y="22" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold" text-anchor="middle">MEX</text>
      
      <circle cx="110" cy="17" r="16" fill="#1D4ED8"/>
      <text x="110" y="22" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="14" font-weight="bold" text-anchor="middle">PRO</text>
    </g>
  </g>

  <!-- BREADCRUMB / PRODUCT BAR -->
  <g transform="translate(40, 88)">
    <text x="0" y="24" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold">
      Cloud Storage
    </text>
    <text x="110" y="24" fill="#64748B" font-family="'Liberation Sans', sans-serif" font-size="16">&gt;</text>
    <text x="130" y="24" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold">
      {escape_xml(title)}
    </text>
    {keyword_pill}
  </g>

  <!-- MAIN INTERACTIVE DISPLAY CANVAS -->
  <g transform="translate(40, 140)">
    {body_svg}
  </g>

  <!-- SLEEK MINIMALIST PRESENTER STATUS (Bottom) -->
  <g transform="translate(40, {h - 60})">
    <rect x="0" y="0" width="{w - 80}" height="42" rx="10" fill="#0A0E17" stroke="#1E293B" stroke-width="1.2"/>
    <circle cx="24" cy="21" r="10" fill="#0284C7"/>
    <text x="24" y="25" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">🎙️</text>
    <text x="44" y="26" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="14" font-weight="bold">
      TUTORIAL GOOGLE CLOUD
    </text>
    <text x="260" y="26" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="13">
      • Explicación didáctica paso a paso
    </text>
    
    <text x="{w - 180}" y="26" fill="#10B981" font-family="'Liberation Sans', sans-serif" font-size="13" font-weight="bold" text-anchor="end">
      ● CONSOLA EN VIVO
    </text>
  </g>
</svg>"""
        return svg

    def _build_hook_bill_alert(self, w: int, h: int, data: Dict[str, Any]) -> str:
        """Visual scene showing cloud billing shock vs Google Cloud Storage solution."""
        return f"""
        <!-- Left: The Real-World Pain (Unexpected Bill) -->
        <g transform="translate(40, 40)" filter="url(#boxShadow)">
          <rect x="0" y="0" width="840" height="740" rx="20" fill="#181114" stroke="#EF4444" stroke-width="2.5"/>
          
          <rect x="40" y="40" width="260" height="40" rx="10" fill="#EF4444" fill-opacity="0.2"/>
          <text x="56" y="66" fill="#FCA5A5" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold">
            ⚠️ EL PROBLEMA REAL
          </text>

          <text x="40" y="140" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="36" font-weight="bold">
            ¿Factura Gigantesca por Almacenamiento?
          </text>
          <text x="40" y="190" fill="#FDA4AF" font-family="'Liberation Sans', sans-serif" font-size="20">
            Dejar terabytes en discos duros virtuales activos cuesta hasta 10 veces más.
          </text>

          <!-- Simulated Bill Invoice Card -->
          <g transform="translate(40, 240)">
            <rect x="0" y="0" width="760" height="420" rx="14" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
            
            <text x="40" y="50" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">Concepto</text>
            <text x="600" y="50" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16" text-anchor="end">Total</text>
            <line x1="40" y1="70" x2="720" y2="70" stroke="#334155" stroke-width="1"/>

            <text x="40" y="120" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold">Discos SSD fijados 24/7 (sin usar)</text>
            <text x="600" y="120" fill="#EF4444" font-family="'Liberation Sans', sans-serif" font-size="24" font-weight="bold" text-anchor="end">$420.00 USD</text>

            <text x="40" y="180" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold">Servidores encendidos solo para alojar archivos</text>
            <text x="600" y="180" fill="#EF4444" font-family="'Liberation Sans', sans-serif" font-size="24" font-weight="bold" text-anchor="end">$680.00 USD</text>

            <rect x="40" y="230" width="680" height="80" rx="10" fill="#450A0A" stroke="#EF4444" stroke-width="2"/>
            <text x="60" y="278" fill="#FCA5A5" font-family="'Liberation Sans', sans-serif" font-size="26" font-weight="bold">
              TOTAL DESPERDICIADO: $1,100.00 USD / mes
            </text>

            <text x="40" y="360" fill="#F87171" font-family="'Liberation Sans', sans-serif" font-size="18">
              ❌ Error común: Pagar por servidores cuando solo necesitas guardar archivos.
            </text>
          </g>
        </g>

        <!-- Right: The Solution (Google Cloud Buckets) -->
        <g transform="translate(940, 40)" filter="url(#boxShadow)">
          <rect x="0" y="0" width="880" height="740" rx="20" fill="#0C1A2E" stroke="#10B981" stroke-width="2.5"/>
          
          <rect x="40" y="40" width="280" height="40" rx="10" fill="#10B981" fill-opacity="0.2"/>
          <text x="56" y="66" fill="#6EE7B7" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold">
            ✓ LA SOLUCIÓN DEFINITIVA
          </text>

          <text x="40" y="140" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="36" font-weight="bold">
            Google Cloud Storage (Buckets)
          </text>
          <text x="40" y="190" fill="#A7F3D0" font-family="'Liberation Sans', sans-serif" font-size="20">
            Pagas solo centavos por lo que guardas. Cero servidores. Cero desperdicio.
          </text>

          <!-- 3 Benefits Cards -->
          <g transform="translate(40, 240)">
            <g transform="translate(0, 0)">
              <rect x="0" y="0" width="800" height="110" rx="12" fill="#0A2540" stroke="#38BDF8" stroke-width="1.8"/>
              <text x="30" y="48" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold">
                1. ESCALABILIDAD INFINITA
              </text>
              <text x="30" y="85" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="18">
                Sube 1 foto o 10 millones de backups sin configurar discos ni particiones.
              </text>
            </g>

            <g transform="translate(0, 130)">
              <rect x="0" y="0" width="800" height="110" rx="12" fill="#064E3B" stroke="#10B981" stroke-width="1.8"/>
              <text x="30" y="48" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold">
                2. AHORRO DE HASTA 90%
              </text>
              <text x="30" y="85" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="18">
                Desde $0.02 USD por gigabyte en activo, hasta $0.0012 USD en archivo.
              </text>
            </g>

            <g transform="translate(0, 260)">
              <rect x="0" y="0" width="800" height="110" rx="12" fill="#1E293B" stroke="#F59E0B" stroke-width="1.8"/>
              <text x="30" y="48" fill="#FBBF24" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold">
                3. SEGURIDAD BANCARIA AUTOMÁTICA
              </text>
              <text x="30" y="85" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="18">
                Cifrado automático en reposo con llaves gestionadas por Google.
              </text>
            </g>
          </g>
        </g>
        """

    def _build_create_bucket_ui(self, w: int, h: int, data: Dict[str, Any]) -> str:
        """Visual recreation of the actual 'Crear un bucket' form in Google Cloud Console."""
        return f"""
        <g id="create_bucket_form" filter="url(#boxShadow)">
          <rect x="40" y="20" width="{w - 80}" height="760" rx="16" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>

          <!-- Step 1: Bucket Name (Global Unique) -->
          <g transform="translate(90, 60)">
            <circle cx="20" cy="20" r="16" fill="#1D4ED8"/>
            <text x="20" y="26" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">1</text>
            <text x="50" y="26" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="24" font-weight="bold">
              Asigna un nombre a tu bucket
            </text>
            <text x="50" y="55" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
              El nombre debe ser único a nivel mundial entre todos los usuarios de Google Cloud.
            </text>

            <!-- Name Input Field with Success Check -->
            <rect x="50" y="75" width="800" height="56" rx="8" fill="#0B1324" stroke="#10B981" stroke-width="2"/>
            <text x="70" y="110" fill="#FFFFFF" font-family="monospace" font-size="20" font-weight="bold">
              mi-empresa-backups-2025
            </text>
            <rect x="870" y="75" width="220" height="56" rx="8" fill="#064E3B"/>
            <text x="980" y="110" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">
              ✓ Nombre disponible
            </text>
          </g>

          <!-- Step 2: Location (Region vs Multi-region) -->
          <g transform="translate(90, 250)">
            <circle cx="20" cy="20" r="16" fill="#1D4ED8"/>
            <text x="20" y="26" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">2</text>
            <text x="50" y="26" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="24" font-weight="bold">
              Elige dónde almacenar tus datos
            </text>

            <!-- Region selector cards -->
            <g transform="translate(50, 60)">
              <!-- Region Choice (Recommended for low cost) -->
              <rect x="0" y="0" width="500" height="150" rx="12" fill="#1E293B" stroke="#38BDF8" stroke-width="2.5" filter="url(#neonGlow)"/>
              <circle cx="36" cy="36" r="12" fill="#0284C7"/>
              <circle cx="36" cy="36" r="6" fill="#FFFFFF"/>
              <text x="65" y="42" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
                Región Única (us-central1, Iowa)
              </text>
              <rect x="360" y="20" width="120" height="30" rx="6" fill="#065F46"/>
              <text x="420" y="40" fill="#6EE7B7" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold" text-anchor="middle">
                MENOR COSTO
              </text>
              <text x="65" y="80" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
                Mayor velocidad y menor latencia para aplicaciones en una sola zona.
              </text>
              <text x="65" y="115" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="18" font-weight="bold">
                Precio estimado: $0.020 USD por GB / mes
              </text>
            </g>

            <g transform="translate(580, 60)">
              <!-- Multi-region Choice -->
              <rect x="0" y="0" width="500" height="150" rx="12" fill="#0B1324" stroke="#334155" stroke-width="1.5"/>
              <circle cx="36" cy="36" r="12" fill="#1E293B" stroke="#64748B" stroke-width="2"/>
              <text x="65" y="42" fill="#CBD5E1" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
                Multirregión (EE. UU. o Europa)
              </text>
              <text x="65" y="80" fill="#64748B" font-family="'Liberation Sans', sans-serif" font-size="16">
                Alta disponibilidad geo-redundante para empresas multinacionales.
              </text>
              <text x="65" y="115" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="18">
                Precio estimado: $0.026 USD por GB / mes
              </text>
            </g>
          </g>

          <!-- Step 3: Interactive Call to Action Button -->
          <g transform="translate(140, 560)">
            <rect x="0" y="0" width="400" height="70" rx="12" fill="#1D4ED8" stroke="#60A5FA" stroke-width="2" filter="url(#neonGlow)"/>
            <text x="200" y="44" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="24" font-weight="bold" text-anchor="middle">
              + CREAR BUCKET
            </text>

            <!-- Virtual Hand / Cursor Pointer -->
            <g transform="translate(360, 45)">
              <polygon points="0,0 8,24 15,18 26,35 32,32 21,15 28,12" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>
            </g>

            <text x="440" y="44" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
              ✓ Creación instantánea en menos de 2 segundos
            </text>
          </g>
        </g>
        """

    def _build_storage_analogies(self, w: int, h: int, data: Dict[str, Any]) -> str:
        """Visual real-world metaphors for Cloud Storage classes (Desk Drawer, Closet, Storage Unit, Vault)."""
        card_w = 410
        card_h = 720
        gap = 25

        analogies = [
            {
                "title": "STANDARD",
                "metaphor": "EL CAJÓN DE TU ESCRITORIO",
                "icon": "📦",
                "frequency": "Todos los días",
                "use_case": "Imágenes web, APIs activas, streaming y archivos de uso constante.",
                "cost": "$0.020 / GB",
                "border": "#38BDF8",
                "badge_bg": "#0284C7",
                "tip": "Sin coste por lectura"
            },
            {
                "title": "NEARLINE",
                "metaphor": "EL ARMARIO DE TU CASA",
                "icon": "🗄️",
                "frequency": "1 vez al mes",
                "use_case": "Backups mensuales, reportes contables que consultas ocasionalmente.",
                "cost": "$0.010 / GB",
                "border": "#34D399",
                "badge_bg": "#059669",
                "tip": "Ahorras un 50%"
            },
            {
                "title": "COLDLINE",
                "metaphor": "LA BODEGA / TRASTERO",
                "icon": "🏚️",
                "frequency": "1 vez al año",
                "use_case": "Archivos históricos de proyectos pasados que casi nunca necesitas tocar.",
                "cost": "$0.004 / GB",
                "border": "#FBBF24",
                "badge_bg": "#D97706",
                "tip": "Ahorras un 75%"
            },
            {
                "title": "ARCHIVE",
                "metaphor": "CAJA FUERTE BAJO TIERRA",
                "icon": "🔒",
                "frequency": "Solo auditorías legales",
                "use_case": "Copias de respaldo obligatorias por ley guardadas por 5 o 10 años.",
                "cost": "$0.0012 / GB",
                "border": "#A78BFA",
                "badge_bg": "#7C3AED",
                "tip": "Costo casi cero (90% ahorro)"
            }
        ]

        cards_svg = ""
        for i, item in enumerate(analogies):
            x = 40 + i * (card_w + gap)
            cards_svg += f"""
            <g transform="translate({x}, 40)" filter="url(#boxShadow)">
              <rect x="0" y="0" width="{card_w}" height="{card_h}" rx="18" fill="#0F172A" stroke="{item['border']}" stroke-width="2.5"/>

              <!-- Class Badge -->
              <rect x="25" y="25" width="{card_w - 50}" height="42" rx="10" fill="{item['badge_bg']}"/>
              <text x="{card_w / 2}" y="52" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold" text-anchor="middle">
                {item['title']}
              </text>

              <!-- Real World Metaphor Big Headline -->
              <text x="{card_w / 2}" y="130" font-size="60" text-anchor="middle">{item['icon']}</text>
              <text x="{card_w / 2}" y="190" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold" text-anchor="middle">
                {item['metaphor']}
              </text>

              <!-- Access Frequency Pill -->
              <rect x="35" y="225" width="{card_w - 70}" height="46" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1"/>
              <text x="{card_w / 2}" y="255" fill="{item['border']}" font-family="'Liberation Sans', sans-serif" font-size="17" font-weight="bold" text-anchor="middle">
                📅 Acceso: {item['frequency']}
              </text>

              <!-- Practical Description -->
              <rect x="25" y="295" width="{card_w - 50}" height="180" rx="12" fill="#0A0E17"/>
              <text x="40" y="335" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="14" font-weight="bold">CASO DE USO IDEAL:</text>
              <foreignObject x="40" y="350" width="{card_w - 80}" height="110">
                <p xmlns="http://www.w3.org/1999/xhtml" style="color: #E2E8F0; font-family: 'Liberation Sans', sans-serif; font-size: 16px; line-height: 1.4; margin: 0;">
                  {item['use_case']}
                </p>
              </foreignObject>

              <!-- Pricing Highlight Tag -->
              <g transform="translate(25, 500)">
                <rect x="0" y="0" width="{card_w - 50}" height="100" rx="12" fill="#141E33" stroke="{item['border']}" stroke-width="1.5"/>
                <text x="20" y="40" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="14">Coste mensual aprox:</text>
                <text x="20" y="78" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="28" font-weight="bold">{item['cost']}</text>
              </g>

              <!-- Tip at bottom -->
              <rect x="25" y="625" width="{card_w - 50}" height="60" rx="10" fill="{item['badge_bg']}" fill-opacity="0.2"/>
              <text x="{card_w / 2}" y="662" fill="{item['border']}" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">
                💡 {item['tip']}
              </text>
            </g>"""

        return cards_svg

    def _build_drag_and_drop_upload(self, w: int, h: int, data: Dict[str, Any]) -> str:
        """Visual demonstration of dragging & uploading files to GCP Console with instant encryption."""
        return f"""
        <g id="upload_demo" filter="url(#boxShadow)">
          <rect x="40" y="20" width="{w - 80}" height="760" rx="16" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>

          <!-- Header of the Bucket Contents -->
          <g transform="translate(80, 60)">
            <text x="0" y="30" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="28" font-weight="bold">
              gs://mi-empresa-backups-2025/
            </text>
            
            <!-- Action buttons -->
            <rect x="0" y="60" width="220" height="46" rx="8" fill="#1D4ED8"/>
            <text x="110" y="90" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">
              ↑ SUBIR ARCHIVOS
            </text>

            <rect x="240" y="60" width="220" height="46" rx="8" fill="#1E293B" stroke="#475569" stroke-width="1"/>
            <text x="350" y="90" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="middle">
              + CREAR CARPETA
            </text>
          </g>

          <!-- Interactive Drag and Drop Zone -->
          <g transform="translate(80, 200)">
            <rect x="0" y="0" width="{w - 160}" height="320" rx="16" fill="#0A0E1A" stroke="#38BDF8" stroke-width="3" stroke-dasharray="12,12"/>
            
            <text x="{(w - 160) / 2}" y="90" font-size="64" text-anchor="middle">📂</text>
            <text x="{(w - 160) / 2}" y="150" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="26" font-weight="bold" text-anchor="middle">
              Arrastra tus archivos directamente aquí
            </text>
            <text x="{(w - 160) / 2}" y="190" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="18" text-anchor="middle">
              O usa la línea de comandos gcloud storage para sincronizar carpetas completas
            </text>
          </g>

          <!-- Active Uploading File Simulator Card -->
          <g transform="translate(80, 560)">
            <rect x="0" y="0" width="{w - 160}" height="180" rx="14" fill="#1E293B" stroke="#10B981" stroke-width="2" filter="url(#neonGlow)"/>
            
            <!-- File Icon & Details -->
            <rect x="30" y="30" width="60" height="60" rx="8" fill="#065F46"/>
            <text x="60" y="68" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="28" text-anchor="middle">📄</text>

            <text x="110" y="55" fill="#FFFFFF" font-family="monospace" font-size="22" font-weight="bold">
              backup_fotos_empresa.tar.gz (4.8 GB)
            </text>
            <text x="110" y="85" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold">
              ✓ Subida completada a 85 MB/s • Cifrado automático AES-256 activado
            </text>

            <!-- Progress Bar -->
            <rect x="110" y="110" width="{w - 320}" height="18" rx="9" fill="#0B1324"/>
            <rect x="110" y="110" width="{w - 320}" height="18" rx="9" fill="#10B981"/>
            <text x="{w - 190}" y="125" fill="#10B981" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold" text-anchor="end">
              100% OK
            </text>
          </g>
        </g>
        """

    def _build_cli_zoom(self, w: int, h: int, data: Dict[str, Any]) -> str:
        """Focused zoom into the exact gcloud storage CLI command."""
        return f"""
        <g id="cli_focused_zoom" filter="url(#boxShadow)">
          <rect x="80" y="40" width="{w - 160}" height="700" rx="20" fill="#050811" stroke="#38BDF8" stroke-width="3" filter="url(#neonGlow)"/>

          <!-- Top Terminal Bar -->
          <rect x="80" y="40" width="{w - 160}" height="54" rx="20" fill="#0D1424"/>
          <circle cx="120" cy="67" r="9" fill="#EF4444"/>
          <circle cx="148" cy="67" r="9" fill="#F59E0B"/>
          <circle cx="176" cy="67" r="9" fill="#10B981"/>
          
          <text x="{w / 2}" y="74" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="18" font-weight="bold" text-anchor="middle">
            Google Cloud Shell — gcloud storage CLI
          </text>

          <!-- High-Contrast Zoomed Command -->
          <g transform="translate(140, 160)">
            <text x="0" y="40" fill="#64748B" font-family="monospace" font-size="20">
              # Creación de bucket profesional en 1 sola línea:
            </text>

            <rect x="0" y="70" width="{w - 280}" height="130" rx="12" fill="#0C1A30" stroke="#0284C7" stroke-width="2"/>
            <text x="40" y="130" fill="#38BDF8" font-family="monospace" font-size="28" font-weight="bold">
              $ gcloud storage buckets create gs://mi-empresa-backups-2025 \
            </text>
            <text x="75" y="175" fill="#38BDF8" font-family="monospace" font-size="28" font-weight="bold">
                --location=us-central1 --default-storage-class=COLDLINE
            </text>
          </g>

          <!-- System Output with Success Badge -->
          <g transform="translate(140, 420)">
            <rect x="0" y="0" width="{w - 280}" height="180" rx="12" fill="#042F2E" stroke="#10B981" stroke-width="2"/>
            
            <text x="40" y="50" fill="#34D399" font-family="monospace" font-size="22" font-weight="bold">
              Creating gs://mi-empresa-backups-2025/...
            </text>
            <text x="40" y="95" fill="#6EE7B7" font-family="monospace" font-size="22">
              ✓ HTTP 200 OK: Bucket creado exitosamente en us-central1
            </text>
            <text x="40" y="140" fill="#A7F3D0" font-family="monospace" font-size="22">
              ✓ Clase de almacenamiento: COLDLINE (Ahorro del 75% activado por defecto)
            </text>
          </g>

          <text x="{w / 2}" y="680" fill="#FBBF24" font-family="'Liberation Sans', sans-serif" font-size="22" font-weight="bold" text-anchor="middle">
            💡 PRO-TIP: También puedes usar el comando 'gcloud storage cp' para subir carpetas completas.
          </text>
        </g>
        """

    def _build_golden_rules_summary(self, w: int, h: int, data: Dict[str, Any]) -> str:
        """Clear executive summary: 3 golden rules to save 80% on cloud storage."""
        return f"""
        <g id="summary_golden_rules" filter="url(#boxShadow)">
          <rect x="100" y="40" width="{w - 200}" height="700" rx="20" fill="#0B132B" stroke="#10B981" stroke-width="3"/>

          <text x="{w / 2}" y="120" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="40" font-weight="bold" text-anchor="middle">
            LAS 3 REGLAS DE ORO DE GOOGLE CLOUD STORAGE
          </text>
          <text x="{w / 2}" y="165" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="22" text-anchor="middle">
            Aplica esto hoy para reducir tu factura de almacenamiento hasta un 80%
          </text>

          <!-- 3 High Impact Rule Cards -->
          <g transform="translate(160, 220)">
            <!-- Rule 1 -->
            <g transform="translate(0, 0)">
              <rect x="0" y="0" width="{w - 320}" height="120" rx="14" fill="#1E293B" stroke="#38BDF8" stroke-width="2"/>
              <circle cx="50" cy="60" r="28" fill="#0284C7"/>
              <text x="50" y="70" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="28" font-weight="bold" text-anchor="middle">1</text>
              <text x="110" y="50" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="26" font-weight="bold">
                Usa STANDARD solo para archivos de acceso diario
              </text>
              <text x="110" y="90" fill="#CBD5E1" font-family="'Liberation Sans', sans-serif" font-size="18">
                Páginas web, avatares de usuarios, apps activas y multimedia de consumo continuo.
              </text>
            </g>

            <!-- Rule 2 -->
            <g transform="translate(0, 150)">
              <rect x="0" y="0" width="{w - 320}" height="120" rx="14" fill="#064E3B" stroke="#10B981" stroke-width="2"/>
              <circle cx="50" cy="60" r="28" fill="#059669"/>
              <text x="50" y="70" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="28" font-weight="bold" text-anchor="middle">2</text>
              <text x="110" y="50" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="26" font-weight="bold">
                Mueve tus backups a COLDLINE o ARCHIVE automáticamente
              </text>
              <text x="110" y="90" fill="#E2E8F0" font-family="'Liberation Sans', sans-serif" font-size="18">
                Configura una regla de Lifecycle (Ciclo de vida) para que a los 30 días pasen a bajo costo.
              </text>
            </g>

            <!-- Rule 3 -->
            <g transform="translate(0, 300)">
              <rect x="0" y="0" width="{w - 320}" height="120" rx="14" fill="#451A03" stroke="#F59E0B" stroke-width="2"/>
              <circle cx="50" cy="60" r="28" fill="#D97706"/>
              <text x="50" y="70" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="28" font-weight="bold" text-anchor="middle">3</text>
              <text x="110" y="50" fill="#FBBF24" font-family="'Liberation Sans', sans-serif" font-size="26" font-weight="bold">
                Elige región única (ej. us-central1) si no requieres multi-continente
              </text>
              <text x="110" y="90" fill="#FEF3C7" font-family="'Liberation Sans', sans-serif" font-size="18">
                Ahorras de inmediato un 25% extra en la tarifa base de almacenamiento.
              </text>
            </g>
          </g>

          <text x="{w / 2}" y="700" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="24" font-weight="bold" text-anchor="middle">
            ¡Felicidades! Ya dominas la arquitectura de Google Cloud Storage como un profesional.
          </text>
        </g>
        """

    def rasterize_svg_to_png(self, svg_content: str, output_png_path: Path) -> bool:
        """Converts SVG content to pixel-perfect PNG using FFmpeg librsvg."""
        output_png_path = Path(output_png_path)
        output_png_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_svg = output_png_path.parent / f"_tmp_{output_png_path.stem}.svg"

        tmp_svg.write_text(svg_content, encoding="utf-8")

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(tmp_svg),
                "-vf", f"scale={self.width}:{self.height}",
                str(output_png_path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode != 0:
                err_msg = res.stderr.decode("utf-8", errors="ignore")
                print(f"  ⚠️ Error rasterizando SVG a PNG ({output_png_path.name}):\n{err_msg[-400:]}")
        except Exception as e:
            print(f"  ❌ Error ejecutando FFmpeg para rasterizar SVG: {e}")
        finally:
            if tmp_svg.exists():
                tmp_svg.unlink()

        # Fallback guarantee
        if not output_png_path.exists() or output_png_path.stat().st_size == 0:
            cmd_fb = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c=0x0B0F19:s={self.width}x{self.height}:d=1",
                "-vframes", "1",
                str(output_png_path)
            ]
            subprocess.run(cmd_fb, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return output_png_path.exists()

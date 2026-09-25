import { NASAMediaItem } from '../types';

export const FALLBACK_NASA_MEDIA: NASAMediaItem[] = [
  {
    id: 'nasa-1',
    nasa_id: 'GSFC_20190925_m13437_BlackHole',
    title: 'Simulación de Agujero Negro Supermasivo',
    description: 'Visualización computarizada que muestra cómo la gravedad extrema de un agujero negro deforma la luz y distorsiona el disco de acreción.',
    date_created: '2024-09-25',
    center: 'GSFC',
    keywords: ['black hole', 'accretion disk', 'relativity', 'gravitational lensing'],
    thumbUrl: 'https://images-assets.nasa.gov/image/GSFC_20190925_m13437_BlackHole/GSFC_20190925_m13437_BlackHole~orig.jpg',
    fullUrl: 'https://images-assets.nasa.gov/image/GSFC_20190925_m13437_BlackHole/GSFC_20190925_m13437_BlackHole~orig.jpg',
    media_type: 'image',
  },
  {
    id: 'nasa-2',
    nasa_id: 'PIA25686',
    title: 'Cúmulo de Pandora visto por James Webb',
    description: 'La vista infrarroja profunda de James Webb revela tres cúmulos masivos de galaxias fusionándose en un megacúmulo con lentes gravitacionales gigantescas.',
    date_created: '2024-02-15',
    center: 'JPL',
    keywords: ['james webb', 'deep field', 'pandora cluster', 'infrared'],
    thumbUrl: 'https://images-assets.nasa.gov/image/PIA25686/PIA25686~orig.jpg',
    fullUrl: 'https://images-assets.nasa.gov/image/PIA25686/PIA25686~orig.jpg',
    media_type: 'image',
  },
  {
    id: 'nasa-3',
    nasa_id: 'PIA13123',
    title: 'Erupción Solar y Bucles Coronales Dinámicos',
    description: 'El Observatorio de Dinámica Solar (SDO) captura plasma estelar a millones de grados elevándose a lo largo de líneas de campo magnético.',
    date_created: '2024-08-08',
    center: 'GSFC',
    keywords: ['sun', 'solar flare', 'coronal loop', 'sdo'],
    thumbUrl: 'https://images-assets.nasa.gov/image/PIA13123/PIA13123~orig.jpg',
    fullUrl: 'https://images-assets.nasa.gov/image/PIA13123/PIA13123~orig.jpg',
    media_type: 'image',
  },
  {
    id: 'nasa-4',
    nasa_id: 'PIA19048',
    title: 'Ondas Gravitacionales de Colisión de Agujeros Negros',
    description: 'Representación visual del espacio-tiempo curvado cuando dos agujeros negros en órbita colisionan y liberan más energía que todas las estrellas observables juntas.',
    date_created: '2025-01-20',
    center: 'JPL/Caltech',
    keywords: ['gravitational waves', 'ligo', 'merger', 'singularity'],
    thumbUrl: 'https://images-assets.nasa.gov/image/PIA19048/PIA19048~orig.jpg',
    fullUrl: 'https://images-assets.nasa.gov/image/PIA19048/PIA19048~orig.jpg',
    media_type: 'image',
  },
  {
    id: 'nasa-5',
    nasa_id: 'PIA23865',
    title: 'Nebulosa del Anillo del Sur vista por JWST',
    description: 'Espectacular imagen en infrarrojo cercano y medio revelando la estrella agonizante expulsando capas de gas y polvo cósmico.',
    date_created: '2024-07-12',
    center: 'STScI',
    keywords: ['nebula', 'jwst', 'southern ring', 'stellar death'],
    thumbUrl: 'https://images-assets.nasa.gov/image/PIA23865/PIA23865~orig.jpg',
    fullUrl: 'https://images-assets.nasa.gov/image/PIA23865/PIA23865~orig.jpg',
    media_type: 'image',
  },
  {
    id: 'nasa-6',
    nasa_id: 'PIA19656',
    title: 'Encélado y sus Géiseres de Vapor Suboceánico',
    description: 'La sonda Cassini vuela a través de los penachos criovolcánicos de Encélado, confirmando un océano global de agua líquida bajo su corteza helada.',
    date_created: '2025-05-18',
    center: 'JPL',
    keywords: ['enceladus', 'cassini', 'ocean world', 'geysers', 'saturn'],
    thumbUrl: 'https://images-assets.nasa.gov/image/PIA19656/PIA19656~orig.jpg',
    fullUrl: 'https://images-assets.nasa.gov/image/PIA19656/PIA19656~orig.jpg',
    media_type: 'image',
  },
];

export async function searchNASAMedia(query: string): Promise<NASAMediaItem[]> {
  try {
    const cleanQuery = encodeURIComponent(query.trim() || 'cosmos');
    const url = `https://images-api.nasa.gov/search?q=${cleanQuery}&media_type=image`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`NASA API error: ${res.status}`);

    const data = await res.json();
    const items = data.collection?.items || [];

    const results: NASAMediaItem[] = items.slice(0, 12).map((item: any) => {
      const d = item.data?.[0] || {};
      const links = item.links || [];
      const thumb = links.find((l: any) => l.rel === 'preview')?.href || '';
      return {
        id: item.href || d.nasa_id || Math.random().toString(),
        nasa_id: d.nasa_id || 'NASA-ITEM',
        title: d.title || 'NASA Media Asset',
        description: d.description || '',
        date_created: d.date_created ? d.date_created.slice(0, 10) : '2025',
        center: d.center || 'NASA',
        keywords: d.keywords || [],
        thumbUrl: thumb,
        fullUrl: thumb,
        media_type: d.media_type || 'image',
      };
    });

    if (results.length === 0) {
      return FALLBACK_NASA_MEDIA;
    }
    return results;
  } catch (err) {
    console.warn('Using NASA offline fallback assets:', err);
    return FALLBACK_NASA_MEDIA.filter(
      (m) =>
        m.title.toLowerCase().includes(query.toLowerCase()) ||
        m.keywords?.some((k) => k.toLowerCase().includes(query.toLowerCase())) ||
        query.trim() === ''
    );
  }
}

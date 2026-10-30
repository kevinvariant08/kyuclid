// Display names for subtopic slugs. Task 03 publishes data/taxonomy.json; until then names come from the slug.
// The file doesn't exist yet and fetching it would log a 404, so the fetch is off. Set this to true when it lands.
const PUBLISHED = false;

const entries = new Map();   // slug -> { id, name, topic, definition }

export async function loadTaxonomy() {
  if (!PUBLISHED) return;
  try {
    const res = await fetch(new URL("../../data/taxonomy.json", import.meta.url));
    if (!res.ok) return;
    const t = await res.json();
    for (const x of [...(t.techniques || []), ...(t.configurations || [])]) if (x && x.id) entries.set(x.id, x);
  } catch {}   // names fall back to the slug
}

const humanise = (slug) => { const s = slug.replace(/-/g, " "); return s[0].toUpperCase() + s.slice(1); };
export const subtopicName = (slug) => (entries.get(slug) && entries.get(slug).name) || humanise(slug);

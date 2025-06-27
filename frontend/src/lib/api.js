// src/lib/api.js
const BASE = 'http://localhost:8000'  // например: http://localhost:8000

/** GET /topics */
export async function fetchTopics() {
  const res = await fetch(`${BASE}/topics`, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Ошибка загрузки тем: ${res.status}`);
  return await res.json(); // [{ id, topic: { name, info }, created_at }, …]
}

export async function createTopic({ name, info }) {
  const res = await fetch(`${BASE}/topics`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ name, info })
  });
  if (!res.ok) throw new Error(`Create topic failed: ${res.status}`);
  return await res.json();
}

export async function updateTopic(id, { name, info }) {
  const params = new URLSearchParams({ topic_id: id });
  const res = await fetch(`${BASE}/topics?${params}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ name, info })
  });
  if (!res.ok) throw new Error(`Update topic failed: ${res.status}`);
  return await res.json();
}

export async function deleteTopic(id) {
  const res = await fetch(`${BASE}/topics/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Delete topic failed: ${res.status}`);
}

/** GET /terms/first_letter/?first_letter=X&topic_id=Y&limit=Z */
export async function fetchTermsByLetter({ first_letter, topic_id, limit = 5 }) {
  const params = new URLSearchParams({ first_letter, topic_id, limit });
  const res = await fetch(`${BASE}/terms/first_letter/?${params}`, {
    headers: { Accept: 'application/json' }
  });
  if (!res.ok) throw new Error(`Ошибка загрузки терминов: ${res.status}`);
  const data = await res.json();
  return data.map(item => ({
    id: item.id,
    term: item.term.processed_text?.cleaned_text || item.term.raw_text
  }));
}

/** GET /terms/term_id/?term_id=… */
export async function fetchTermById(term_id) {
  const res = await fetch(`${BASE}/terms/term_id/?term_id=${term_id}`, {
    headers: { Accept: 'application/json' }
  });
  if (!res.ok) throw new Error(`Ошибка загрузки терма: ${res.status}`);
  return await res.json(); // { id, term: { raw_text, processed_text, … }, created_at }
}

/** GET /descriptions/{term_id} */
export async function fetchDescriptionByTermId(term_id) {
  const res = await fetch(`${BASE}/descriptions/${term_id}`, {
    headers: { Accept: 'application/json' }
  });
  if (!res.ok) throw new Error(`Ошибка загрузки описания: ${res.status}`);
  return await res.json(); // { id, description: { raw_text, processed_text, … }, created_at }
}

/** GET /graphs/{description_id} */
export async function fetchGraphByDescriptionId(description_id) {
  const res = await fetch(`${BASE}/graphs/${description_id}`, {
    headers: { Accept: 'application/json' }
  });
  if (!res.ok) throw new Error(`Ошибка загрузки графа: ${res.status}`);
  return await res.json(); // { id, graph: { description_id, triplet_count, graph, … }, created_at }
}

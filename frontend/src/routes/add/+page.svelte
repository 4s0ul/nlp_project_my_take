<!-- src/routes/add/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import { goto } from '$app/navigation';

  // хардкодим URL API или берём из env
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

  // список тем и выбранная
  let topics = [];
  let selectedTopicId = '';

  // поля формы
  let rawText = '';
  let description = '';

  // статусы
  let loading = false;
  let error = '';

  // подгружаем темы
  onMount(async () => {
    try {
      const r = await fetch(`${API_BASE}/topics`, {
        headers: { Accept: 'application/json' }
      });
      if (!r.ok) throw new Error(`topics ${r.status}`);
      topics = await r.json();
      if (topics.length) selectedTopicId = topics[0].id;
    } catch (e) {
      error = `Не удалось загрузить темы: ${e.message}`;
    }
  });

  /** 
   * POST /terms 
   * @returns {Promise<{id:string}>} 
   */
  async function createTerm({ topic_id, raw_text }) {
    const res = await fetch(`${API_BASE}/terms`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ topic_id, raw_text })
    });
    // прежде чем кидать, попробуем разобрать JSON или текст
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      console.error('Non-JSON ответ от /terms:', text);
      throw new Error(`Сервер вернул не-JSON при создании терма: ${res.status}`);
    }
    if (!res.ok) {
      console.error('Ошибка  при /terms:', data);
      // если в data.detail есть список ошибок — склеим
      const msgs = Array.isArray(data.detail)
        ? data.detail.map(d => d.msg || JSON.stringify(d)).join('; ')
        : JSON.stringify(data);
      throw new Error(`Ошибка ${res.status}: ${msgs}`);
    }
    return data;
  }

  /** 
   * POST /descriptions 
   */
  async function createDescription({ term_id, raw_text }) {
    const res = await fetch(`${API_BASE}/descriptions`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ term_id, raw_text })
    });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      console.error('Non-JSON ответ от /descriptions:', text);
      throw new Error(`Сервер вернул не-JSON при создании описания: ${res.status}`);
    }
    if (!res.ok) {
      console.error('Ошибка  при /descriptions:', data);
      const msgs = Array.isArray(data.detail)
        ? data.detail.map(d => d.msg || JSON.stringify(d)).join('; ')
        : JSON.stringify(data);
      throw new Error(`Ошибка ${res.status}: ${msgs}`);
    }
    return data;
  }

  // обрабатываем клик «Сохранить»
  async function handleSave() {
    error = '';
    if (!rawText.trim()) {
      error = 'Слово не может быть пустым';
      return;
    }
    loading = true;
    try {
      // создаём термин
      const termResp = await createTerm({
        topic_id: selectedTopicId,
        raw_text: rawText.trim()
      });

      // если есть описание — создаём и его
      if (description.trim()) {
        await createDescription({
          term_id: termResp.id,
          raw_text: description.trim()
        });
      }

      // и переходим в карточку
      goto(`${base}/word/${termResp.id}`, { replaceState: true });
    } catch (e) {
      // покажем пользователю текст ошибки
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<main>
  <h1>Добавить слово</h1>

  {#if error}
    <div class="error">Ошибка: {error}</div>
  {/if}

  <div class="field">
    <label for="topic">Тема</label>
    <select id="topic" bind:value={selectedTopicId} disabled={loading || !topics.length}>
      {#each topics as t}
        <option value={t.id}>{t.topic.name}</option>
      {/each}
    </select>
  </div>

  <div class="field">
    <label for="raw">Слово</label>
    <input
      id="raw"
      type="text"
      bind:value={rawText}
      placeholder="Введите новое слово"
      disabled={loading}
      autofocus
    />
  </div>

  <div class="field">
    <label for="desc">Описание (опционально)</label>
    <textarea
      id="desc"
      bind:value={description}
      placeholder="Введите описание"
      rows="4"
      disabled={loading}
    ></textarea>
  </div>

  <button on:click={handleSave} disabled={loading}>
    {#if loading}Сохраняем…{:else}Сохранить{/if}
  </button>
</main>

<style>
  main {
    max-width: 600px;
    margin: 2rem auto;
    padding: 0 1rem;
    font-family: sans-serif;
  }
  h1 {
    margin-bottom: 1.5rem;
  }
  .field {
    margin-bottom: 1rem;
  }
  label {
    display: block;
    margin-bottom: 0.3rem;
    font-weight: bold;
  }
  input, select, textarea, button {
    width: 100%;
    box-sizing: border-box;
    font-size: 1rem;
  }
  select, input, textarea {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }
  button {
    padding: 0.6rem;
    background-color: #0077cc;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .error {
    background: #fee;
    color: #900;
    padding: 0.5rem;
    border: 1px solid #f99;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style>

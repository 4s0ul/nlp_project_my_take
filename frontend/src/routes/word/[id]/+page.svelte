<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { base } from '$app/paths';
  import { goto } from '$app/navigation';
  import PipelineViz from '$lib/components/PipelineViz.svelte';

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

  let id;
  $: id = $page.params.id;

  // данные
  let termData = null;
  let descData = null;
  let triplets = [];
  let graphData = null;

  let editField = null;
  let editValue = '';

  async function saveField() {
    if (!editField) return;

    // определяем URL и метод
    let url, method = 'PUT';
    const v = encodeURIComponent(editValue);

    switch (editField) {
      case 'raw':
        url    = `${API_BASE}/terms/raw_text/${v}?term_id=${id}`;
        method = 'PUT';
        break;
      case 'cleaned':
        url    = `${API_BASE}/terms/cleaned_text/${v}?term_id=${id}`;
        method = 'PATCH';
        break;
      case 'stemmed':
        url    = `${API_BASE}/terms/stemmed_text/${v}?term_id=${id}`;
        method = 'PATCH';
        break;
      case 'descRaw':
        url    = `${API_BASE}/descriptions/raw_text/${v}?description_id=${descData.id}`;
        method = 'PUT';
        break;
      case 'descCleaned':
        url    = `${API_BASE}/descriptions/new_descriptions_cleaned_text/${v}?description_id=${descData.id}`;
        method = 'PATCH';
        break;
      case 'descStemmed':
        url    = `${API_BASE}/descriptions/new_descriptions_stemmed_text/${v}?description_id=${descData.id}`;
        method = 'PATCH';
        break;
    }

    const res = await fetch(url, { method });
    if (!res.ok) {
      alert(`Ошибка ${res.status}`);
    } else {
      // обновляем локальные данные
      if (editField === 'raw')         termData.term.raw_text                  = editValue;
      if (editField === 'cleaned')     termData.term.processed_text.cleaned_text = editValue;
      if (editField === 'stemmed')     termData.term.processed_text.stemmed_text = editValue;
      if (editField === 'descRaw')     descData.description.raw_text             = editValue;
      if (editField === 'descCleaned') descData.description.processed_text.cleaned_text  = editValue;
      if (editField === 'descStemmed') descData.description.processed_text.stemmed_text  = editValue;
    }

    editField = null;
  }

  // состояния
  let loading = false;
  let error = '';

  // универсальная fetch-функция
  async function fetchJSON(url, opts = {}) {
    const res = await fetch(url, opts);
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(`Неверный JSON от ${url}: ${text}`);
    }
    if (!res.ok) {
      const msgs = Array.isArray(data.detail)
        ? data.detail.map(d => d.msg || JSON.stringify(d)).join('; ')
        : JSON.stringify(data);
      throw new Error(`${url} → ${res.status}: ${msgs}`);
    }
    return data;
  }

  async function loadAll() {
    loading = true;
    error = '';
    try {
      // 1) термин
      termData = await fetchJSON(
        `${API_BASE}/terms/term_id/?term_id=${id}`,
        { headers: { Accept: 'application/json' } }
      );

      // 2) описание
      descData = await fetchJSON(
        `${API_BASE}/descriptions/${id}`,
        { headers: { Accept: 'application/json' } }
      );

      const descId = descData.id;

      // 3) триплеты и граф параллельно
      const [tr, gr] = await Promise.all([
        fetchJSON(`${API_BASE}/triplets/${descId}`, { headers: { Accept: 'application/json' } }),
        fetchJSON(`${API_BASE}/graphs/${descId}`,   { headers: { Accept: 'application/json' } })
      ]);

      triplets = tr;
      graphData = gr;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(loadAll);

  function goEdit() {
    goto(`${base}/add?id=${id}`);
  }

  async function handleDelete() {
    if (!confirm(`Удалить слово «${termData?.term.raw_text}»?`)) return;
    try {
      const res = await fetch(`${API_BASE}/terms/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`DELETE error ${res.status}: ${txt}`);
      }
      goto(`${base}/`);
    } catch (e) {
      error = e.message;
    }
  }

  let newTriplet = {
    subject: '',
    subject_type: '',
    predicate: '',
    predicate_type: '',
    object: '',
    object_type: '',
    language: termData?.term.language ?? 'russian'
  };
  let adding = false;
  let addError = '';

  // Удаление
  async function deleteTriplet(tripletId) {
    if (!confirm('Удалить этот триплет?')) return;
    try {
      const res = await fetch(`${API_BASE}/triplets/${tripletId}`, {
        method: 'DELETE'
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Ошибка удаления: ${res.status} ${txt}`);
      }
      // выкидываем из массива
      triplets = triplets.filter(t => t.id !== tripletId);
    } catch (e) {
      alert(e.message);
    }
  }

  // Добавление
  async function addTriplet() {
    addError = '';
    adding = true;
    try {
      const body = {
        description_id: descData.id,
        data: {
          position: triplets.length + 1,
          subject: newTriplet.subject,
          subject_type: newTriplet.subject_type || null,
          predicate: newTriplet.predicate,
          predicate_type: newTriplet.predicate_type || null,
          object: newTriplet.object,
          object_type: newTriplet.object_type || null,
          language: newTriplet.language
        }
      };
      const created = await fetchJSON(
        `${API_BASE}/triplets`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
          },
          body: JSON.stringify(body)
        }
      );
      // сразу пушим в локальный список
      triplets = [...triplets, created];
      // сброс формы
      newTriplet = {
        subject: '',
        subject_type: '',
        predicate: '',
        predicate_type: '',
        object: '',
        object_type: '',
        language: termData.term.language
      };
    } catch (e) {
      addError = e.message;
    } finally {
      adding = false;
    }
  }
</script>

<main>
  {#if loading}
    <p>Загрузка…</p>

  {:else if error}
    <p class="error">Ошибка: {error}</p>

  {:else if !termData}
    <p class="error">Слово не найдено.</p>

  {:else}
    <!-- 1. Термин -->
<section>
  <h2>Термин</h2>
  <table class="pipeline">
    <thead>
      <tr>
        <th>Сырой текст</th>
        <th>Очистка</th>
        <th>Стемминг</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        {#each ['raw','cleaned','stemmed'] as field}
          <td>
            {#if editField === field}
              <input
                bind:value={editValue}
                on:keypress={e => e.key==='Enter' && saveField()}
              />
              <button on:click={saveField}>💾</button>
            {:else}
              <span>
                {field==='raw'
                  ? termData.term.raw_text
                  : field==='cleaned'
                    ? termData.term.processed_text.cleaned_text
                    : termData.term.processed_text.stemmed_text}
              </span>
              <button class="icon"
                      on:click={() => {
                        editField = field;
                        editValue = field==='raw'
                          ? termData.term.raw_text
                          : field==='cleaned'
                            ? termData.term.processed_text.cleaned_text
                            : termData.term.processed_text.stemmed_text;
                      }}>✏️</button>
            {/if}
          </td>
        {/each}
      </tr>
    </tbody>
  </table>
</section>

    <!-- 2. Описание -->
{#if descData}
<section>
  <h3>Описание</h3>
  <table class="pipeline">
    <thead>
      <tr>
        <th>Сырой текст</th>
        <th>Очистка</th>
        <th>Стемминг</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        {#each ['descRaw','descCleaned','descStemmed'] as field}
          <td>
            {#if editField === field}
              <textarea
              rows="5"
              bind:value={editValue}
              on:keypress={e => e.key==='Enter' && saveField()}
            />
              <button on:click={saveField}>💾</button>

            {:else}
              <span>
                {field==='descRaw'
                  ? descData.description.raw_text
                  : field==='descCleaned'
                    ? descData.description.processed_text.cleaned_text
                    : descData.description.processed_text.stemmed_text}
              </span>
              <button class="icon"
                      on:click={() => {
                        editField = field;
                        editValue = field==='descRaw'
                          ? descData.description.raw_text
                          : field==='descCleaned'
                            ? descData.description.processed_text.cleaned_text
                            : descData.description.processed_text.stemmed_text;
                      }}>✏️</button>
            {/if}
          </td>
        {/each}
      </tr>
    </tbody>
  </table>
</section>
{/if}

    <!-- 3. Триплеты -->
<section>
  <h3>Триплеты</h3>

  {#if triplets.length === 0}
    <p>Нет триплетов.</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Subject</th>
          <th>Subject Type</th>
          <th>Predicate</th>
          <th>Predicate Type</th>
          <th>Object</th>
          <th>Object Type</th>
          <th>—</th>
        </tr>
      </thead>
      <tbody>
        {#each triplets as t, i}
          <tr>
            <td>{i + 1}</td>
            <td>{t.triplet.data.subject}</td>
            <td>{t.triplet.data.subject_type ?? '—'}</td>
            <td>{t.triplet.data.predicate}</td>
            <td>{t.triplet.data.predicate_type ?? '—'}</td>
            <td>{t.triplet.data.object}</td>
            <td>{t.triplet.data.object_type ?? '—'}</td>
            <td>
              <button class="del-btn" on:click={() => deleteTriplet(t.id)}>
                ✕
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}

  <!-- Форма добавления -->
  <form
    on:submit|preventDefault={addTriplet}
    class="triplet-form"
  >
    <fieldset disabled={adding}>
      <legend>Добавить триплет</legend>

      <input
        placeholder="Subject"
        bind:value={newTriplet.subject}
        required
      />
      <input
        placeholder="Subject Type (опционально)"
        bind:value={newTriplet.subject_type}
      />

      <input
        placeholder="Predicate"
        bind:value={newTriplet.predicate}
        required
      />
      <input
        placeholder="Predicate Type (опционально)"
        bind:value={newTriplet.predicate_type}
      />

      <input
        placeholder="Object"
        bind:value={newTriplet.object}
        required
      />
      <input
        placeholder="Object Type (опционально)"
        bind:value={newTriplet.object_type}
      />

      <button type="submit">
        {#if adding}Добавляем…{:else}Добавить{/if}
      </button>

      {#if addError}
        <p class="error">Ошибка: {addError}</p>
      {/if}
    </fieldset>
  </form>
</section>

    <!-- 4. Граф -->
    <section>
      <h3>Граф</h3>
      {#if graphData}
        <pre>{JSON.stringify(graphData.graph.graph, null, 2)}</pre>
      {:else}
        <p>Граф недоступен.</p>
      {/if}
    </section>

    <!-- Кнопки -->
    <div class="actions">
      <button class="delete" on:click={handleDelete}>Удалить</button>
    </div>
  {/if}
</main>

<style>
  main {
    max-width: 800px;
    margin: 2rem auto;
    padding: 0 1rem;
    font-family: sans-serif;
  }
  h2, h3 {
    margin-top: 1.5rem;
  }
  p {
    line-height: 1.4;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 0.3rem 0.5rem;
  }
  pre {
    background: #f5f5f5;
    padding: 1rem;
    overflow-x: auto;
  }
  .actions {
    margin-top: 2rem;
    display: flex;
    gap: 1rem;
  }
  .actions button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  .actions .delete {
    background: #cc0000;
    color: #fff;
  }
  .error {
    color: #cc0000;
  }
  table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.3rem 0.6rem;
  text-align: left;
}
.del-btn {
  background: #cc0000;
  color: #fff;
  border: none;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
  border-radius: 3px;
}
.del-btn:hover {
  background: #a30000;
}

.triplet-form {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  align-items: start;
}
.triplet-form input {
  padding: 0.4rem;
  border: 1px solid #999;
  border-radius: 4px;
}
.triplet-form button {
  grid-column: 1 / -1;
  padding: 0.5rem 1rem;
  background: #0077cc;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.triplet-form button:disabled {
  opacity: 0.6;
  cursor: default;
}
.triplet-form .error {
  grid-column: 1 / -1;
  color: #cc0000;
  font-size: 0.9rem;
}
.pipeline td textarea {
  min-height: 15rem;
  min-width: 22rem;
  padding: 0.5rem;
  font-size: 1rem;
  box-sizing: border-box;
}

</style>

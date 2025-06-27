<!-- src/routes/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import Tabs from '$lib/components/Tabs.svelte';
  import SearchBar from '$lib/components/SearchBar.svelte';
  import {
    fetchTopics,
    fetchTermsByLetter,
    createTopic,
    updateTopic,
    deleteTopic
  } from '$lib/api.js';

  // Русский алфавит
  const alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'.split('');

  // Состояние
  let topics = [];
  let selectedTopic = null;
  let letterGroups = {};    // { 'А': [{id,term},...], ... }
  let loading = false;
  let error = '';
  let search = '';
  let debounceTimer;

  // Форма CRUD для тем
  let showTopicForm = false;
  let formMode = 'create'; // 'create' или 'edit'
  let formName = '';
  let formInfo = '';
  let editingTopicId = null;
  let formError = '';

  // Загрузка списка тем
  onMount(loadTopics);
  async function loadTopics() {
    loading = true;
    error = '';
    try {
      topics = await fetchTopics();
      if (topics.length) {
        selectedTopic = topics[0];
        await loadLetterGroups();
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  // Загрузка терминов по буквам для текущей темы
  async function loadLetterGroups() {
    if (!selectedTopic) return;
    const id = selectedTopic.id;
    const groups = {};
    await Promise.all(
      alphabet.map(async (ltr) => {
        try {
          groups[ltr] = await fetchTermsByLetter({
            first_letter: ltr,
            topic_id: id,
            limit: 5
          });
        } catch {
          groups[ltr] = [];
        }
      })
    );
    letterGroups = groups;
  }

  // Переключение вкладки
  function selectTab(name) {
    const t = topics.find(t => t.topic.name === name);
    if (t) {
      selectedTopic = t;
      search = '';
      loadLetterGroups();
    }
  }

  // Дебаунс для поиска
  function onSearchInput(val) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      search = val.trim();
    }, 500);
  }

  // Фильтрация групп по поиску
  $: filteredGroups = search
    ? Object.fromEntries(
        Object.entries(letterGroups)
          .map(([ltr, arr]) => [ltr, arr.filter(w => w.term.toLowerCase().includes(search.toLowerCase()))])
          .filter(([, arr]) => arr.length)
      )
    : letterGroups;

  // Открытие формы создания темы
  function openCreateTopic() {
    formMode = 'create';
    formName = '';
    formInfo = '';
    editingTopicId = null;
    formError = '';
    showTopicForm = true;
  }

  // Открытие формы редактирования темы
  function openEditTopic(t) {
    formMode = 'edit';
    editingTopicId = t.id;
    formName = t.topic.name;
    formInfo = t.topic.info || '';
    formError = '';
    showTopicForm = true;
  }

  // Удаление темы
  async function handleDeleteTopic(t) {
    if (!confirm(`Удалить тему «${t.topic.name}»?`)) return;
    try {
      await deleteTopic(t.id);
      await loadTopics();
    } catch (e) {
      alert(e.message);
    }
  }

  // Создать/обновить тему
  async function handleCreateOrUpdateTopic() {
    formError = '';
    try {
      if (formMode === 'create') {
        await createTopic({ name: formName, info: formInfo });
      } else {
        await updateTopic(editingTopicId, { name: formName, info: formInfo });
      }
      await loadTopics();
      showTopicForm = false;
    } catch (e) {
      formError = e.message;
    }
  }
</script>

{#if loading}
  <p>Загрузка…</p>
{:else if error}
  <p class="error">Ошибка: {error}</p>
{:else}
  <!-- Кнопка добавить тему + кнопки редактирования/удаления для активной -->
  <div class="top-controls">
    <button class="add-topic" on:click={openCreateTopic}>+ Добавить тему</button>
    {#if selectedTopic}
      <div class="tab-actions">
        <button class="icon" title="Редактировать тему" on:click={() => openEditTopic(selectedTopic)}>✏️</button>
        <button class="icon delete" title="Удалить тему" on:click={() => handleDeleteTopic(selectedTopic)}>🗑️</button>
      </div>
    {/if}
  </div>

  <!-- Вкладки тем -->
  <Tabs
    tabs={topics.map(t => t.topic.name)}
    selected={selectedTopic?.topic.name}
    onSelect={selectTab}
  />

  <!-- Поиск и кнопка добавить слово -->
  <div class="controls">
    <SearchBar
      bind:value={search}
      placeholder="Поиск…"
      onInput={onSearchInput}
    />
    <a class="add-button" href={base + '/add'}>Добавить слово</a>
  </div>

  <!-- Списки терминов по буквам -->
  {#each Object.entries(filteredGroups) as [ltr, list]}
    <section>
      <h2>{ltr}</h2>
      {#if list.length === 0}
        <p class="empty">нет терминов</p>
      {:else}
        <ul>
          {#each list as w}
            <li><a href={base + '/word/' + w.id}>{w.term}</a></li>
          {/each}
        </ul>
      {/if}
    </section>
  {/each}

  <!-- Модалка для формы темы -->
  {#if showTopicForm}
    <div class="overlay" on:click={() => showTopicForm = false}>
      <form class="topic-form"
            on:submit|preventDefault={handleCreateOrUpdateTopic}
            on:click|stopPropagation>
        <h3>{formMode === 'create' ? 'Новая тема' : 'Редактировать тему'}</h3>
        {#if formError}
          <p class="error">{formError}</p>
        {/if}
        <label>
          Название
          <input bind:value={formName} required />
        </label>
        <label>
          Описание
          <textarea bind:value={formInfo} rows="3" />
        </label>
        <div class="buttons">
          <button type="submit">
            {formMode === 'create' ? 'Создать' : 'Сохранить'}
          </button>
          <button type="button" on:click={() => showTopicForm = false}>
            Отмена
          </button>
        </div>
      </form>
    </div>
  {/if}
{/if}

<style>
  /* Общие стили */
  .controls {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
  }
  .add-button {
    padding: 0.5rem 1rem;
    background: #0077cc;
    color: #fff;
    text-decoration: none;
    border-radius: 4px;
  }
  section {
    margin-bottom: 1.5rem;
  }
  h2 {
    margin-bottom: 0.5rem;
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li + li {
    margin-top: 0.25rem;
  }
  .error {
    color: #cc0000;
  }
  .empty {
    font-style: italic;
    color: #888;
  }

  /* Top controls (CRUD тем) */
  .top-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  .add-topic {
    padding: 0.4rem 0.8rem;
    background: #28a745;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  .tab-actions {
    margin-left: auto;
  }
  .tab-actions .icon {
    background: none;
    border: none;
    cursor: pointer;
    margin: 0 0.2rem;
  }
  .tab-actions .delete {
    color: #cc0000;
  }

  /* Модалка формы темы */
  .overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .topic-form {
    background: #fff;
    padding: 1.5rem;
    border-radius: 6px;
    width: 320px;
    box-sizing: border-box;
  }
  .topic-form h3 {
    margin-top: 0;
  }
  .topic-form label {
    display: block;
    margin-bottom: 0.8rem;
  }
  .topic-form input,
  .topic-form textarea {
    width: 100%;
    padding: 0.4rem;
    box-sizing: border-box;
  }
  .topic-form .buttons {
    text-align: right;
    margin-top: 1rem;
  }
  .topic-form button {
    margin-left: 0.5rem;
    padding: 0.4rem 0.8rem;
  }
</style>

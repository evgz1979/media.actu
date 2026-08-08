"use client";

import { ChangeEvent, useMemo, useRef, useState } from "react";

type MediaItem = {
  id: string;
  name: string;
  path: string;
  type: "photo" | "video";
  size: number;
  modified: number;
  url: string;
};

type ScanFolder = { name: string; count: number };

const mediaExtensions = /\.(jpe?g|png|webp|gif|heic|avif|mp4|mov|m4v|webm|avi|mkv)$/i;
const videoExtensions = /\.(mp4|mov|m4v|webm|avi|mkv)$/i;

function formatBytes(bytes: number) {
  if (!bytes) return "0 Б";
  const units = ["Б", "КБ", "МБ", "ГБ"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index > 1 ? 1 : 0)} ${units[index]}`;
}

function formatDate(timestamp: number) {
  return new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "short", year: "numeric" }).format(timestamp);
}

export default function Home() {
  const [items, setItems] = useState<MediaItem[]>([]);
  const [folders, setFolders] = useState<ScanFolder[]>([]);
  const [filter, setFilter] = useState<"all" | "photo" | "video">("all");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<"new" | "old" | "name" | "size">("new");
  const [scanning, setScanning] = useState(false);
  const [view, setView] = useState<"grid" | "list">("grid");
  const [selected, setSelected] = useState<string[]>([]);
  const fallbackInput = useRef<HTMLInputElement>(null);

  const visibleItems = useMemo(() => {
    const filtered = items.filter((item) => {
      const matchesType = filter === "all" || item.type === filter;
      const matchesQuery = `${item.name} ${item.path}`.toLocaleLowerCase("ru").includes(query.toLocaleLowerCase("ru"));
      return matchesType && matchesQuery;
    });
    return filtered.sort((a, b) => {
      if (sort === "old") return a.modified - b.modified;
      if (sort === "name") return a.name.localeCompare(b.name, "ru");
      if (sort === "size") return b.size - a.size;
      return b.modified - a.modified;
    });
  }, [items, filter, query, sort]);

  const totalSize = items.reduce((sum, item) => sum + item.size, 0);
  const photoCount = items.filter((item) => item.type === "photo").length;
  const videoCount = items.length - photoCount;

  async function addFiles(files: File[], folderName: string) {
    const found = files.filter((file) => mediaExtensions.test(file.name));
    const next = found.map((file) => ({
      id: `${folderName}/${file.name}/${file.lastModified}/${file.size}`,
      name: file.name,
      path: (file as File & { webkitRelativePath?: string }).webkitRelativePath || `${folderName}/${file.name}`,
      type: videoExtensions.test(file.name) ? ("video" as const) : ("photo" as const),
      size: file.size,
      modified: file.lastModified,
      url: URL.createObjectURL(file),
    }));
    setItems((current) => {
      const ids = new Set(current.map((item) => item.id));
      return [...current, ...next.filter((item) => !ids.has(item.id))];
    });
    setFolders((current) => {
      const rest = current.filter((folder) => folder.name !== folderName);
      return [...rest, { name: folderName, count: found.length }];
    });
  }

  async function scanDirectory() {
    const picker = (window as unknown as { showDirectoryPicker?: () => Promise<any> }).showDirectoryPicker;
    if (!picker) {
      fallbackInput.current?.click();
      return;
    }
    try {
      setScanning(true);
      const root = await picker();
      const files: File[] = [];
      async function walk(directory: any) {
        for await (const entry of directory.values()) {
          if (entry.kind === "file") files.push(await entry.getFile());
          if (entry.kind === "directory") await walk(entry);
        }
      }
      await walk(root);
      await addFiles(files, root.name);
    } catch (error) {
      if ((error as Error).name !== "AbortError") fallbackInput.current?.click();
    } finally {
      setScanning(false);
    }
  }

  async function handleFallback(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;
    setScanning(true);
    const relative = (files[0] as File & { webkitRelativePath?: string }).webkitRelativePath;
    await addFiles(files, relative?.split("/")[0] || "Выбранная папка");
    event.target.value = "";
    setScanning(false);
  }

  function removeFolder(folderName: string) {
    setFolders((current) => current.filter((folder) => folder.name !== folderName));
    setItems((current) => current.filter((item) => !item.path.startsWith(`${folderName}/`)));
    setSelected([]);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">M</span><span>Медиатека</span></div>
        <nav className="nav-list" aria-label="Основная навигация">
          <button className="nav-item active"><span>▦</span>Все медиа<span className="nav-count">{items.length}</span></button>
          <button className="nav-item" onClick={() => setFilter("photo")}><span>▧</span>Фотографии<span className="nav-count">{photoCount}</span></button>
          <button className="nav-item" onClick={() => setFilter("video")}><span>▷</span>Видео<span className="nav-count">{videoCount}</span></button>
          <button className="nav-item"><span>♡</span>Избранное</button>
          <button className="nav-item"><span>◌</span>Недавние</button>
        </nav>

        <div className="folder-heading"><span>ПАПКИ ДЛЯ СКАНА</span><button onClick={scanDirectory} aria-label="Добавить папку">＋</button></div>
        <div className="folder-list">
          {folders.length === 0 && <p className="folder-empty">Выберите папки — медиа появятся здесь автоматически.</p>}
          {folders.map((folder) => (
            <div className="folder-item" key={folder.name}>
              <span className="folder-icon">⌑</span><div><strong>{folder.name}</strong><small>{folder.count} файлов</small></div>
              <button onClick={() => removeFolder(folder.name)} aria-label={`Убрать папку ${folder.name}`}>×</button>
            </div>
          ))}
        </div>
        <button className="add-folder secondary" onClick={scanDirectory}>＋ Добавить папку</button>
        <div className="storage"><div><span>В каталоге</span><strong>{formatBytes(totalSize)}</strong></div><div className="storage-track"><i style={{ width: `${Math.min(100, totalSize / 5e8)}%` }} /></div><small>Файлы не загружаются в облако</small></div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div className="search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Поиск по названию или папке" aria-label="Поиск"/><kbd>⌘ K</kbd></div>
          <button className="scan-button" onClick={scanDirectory} disabled={scanning}><span>{scanning ? "◌" : "＋"}</span>{scanning ? "Сканирую…" : "Выбрать папку"}</button>
          <input ref={fallbackInput} onChange={handleFallback} type="file" accept="image/*,video/*" multiple className="hidden-input" {...({ webkitdirectory: "" } as object)} />
          <button className="more-button" aria-label="Настройки">•••</button>
        </header>

        <div className="content-inner">
          <div className="title-row"><div><p className="eyebrow">ЛОКАЛЬНАЯ БИБЛИОТЕКА</p><h1>Все медиа</h1><p>{items.length ? `${items.length} файлов · ${formatBytes(totalSize)}` : "Соберите фото и видео в одном понятном месте"}</p></div></div>

          {items.length === 0 ? (
            <section className="empty-state">
              <div className="empty-art"><div className="photo-card back"><span>▶</span></div><div className="photo-card front"><span>☼</span><i /></div><div className="scan-line" /></div>
              <div className="empty-copy"><span className="local-pill">● Только на этом устройстве</span><h2>Выберите папки с фото и видео</h2><p>Медиатека просканирует выбранные папки, включая вложенные, и соберёт всё в удобный каталог. Исходные файлы останутся на своих местах.</p><button className="scan-button large" onClick={scanDirectory}><span>⌑</span>Выбрать папку для скана</button><small>Можно добавить несколько папок по очереди</small></div>
              <div className="feature-strip"><div><span>◎</span><strong>Быстрый обзор</strong><small>Все медиа в одной ленте</small></div><div><span>⌁</span><strong>Без дубликатов</strong><small>Повторные файлы не добавятся</small></div><div><span>◈</span><strong>Приватно</strong><small>Обработка прямо в браузере</small></div></div>
            </section>
          ) : (
            <>
              <div className="toolbar">
                <div className="filters" role="group" aria-label="Тип файлов"><button className={filter === "all" ? "active" : ""} onClick={() => setFilter("all")}>Все <b>{items.length}</b></button><button className={filter === "photo" ? "active" : ""} onClick={() => setFilter("photo")}>Фото <b>{photoCount}</b></button><button className={filter === "video" ? "active" : ""} onClick={() => setFilter("video")}>Видео <b>{videoCount}</b></button></div>
                <div className="toolbar-actions"><select value={sort} onChange={(event) => setSort(event.target.value as typeof sort)} aria-label="Сортировка"><option value="new">Сначала новые</option><option value="old">Сначала старые</option><option value="name">По названию</option><option value="size">По размеру</option></select><div className="view-switch"><button className={view === "grid" ? "active" : ""} onClick={() => setView("grid")}>▦</button><button className={view === "list" ? "active" : ""} onClick={() => setView("list")}>☷</button></div></div>
              </div>
              {selected.length > 0 && <div className="selection-bar"><strong>Выбрано: {selected.length}</strong><button onClick={() => setSelected([])}>Снять выделение</button></div>}
              <div className={`media-${view}`}>
                {visibleItems.map((item) => (
                  <article className={`media-card ${selected.includes(item.id) ? "selected" : ""}`} key={item.id} onClick={() => setSelected((current) => current.includes(item.id) ? current.filter((id) => id !== item.id) : [...current, item.id])}>
                    <div className="media-preview">{item.type === "photo" ? <img src={item.url} alt="" /> : <><video src={item.url} muted preload="metadata"/><span className="play">▶</span></>}<button className="select-dot" aria-label="Выбрать файл">{selected.includes(item.id) ? "✓" : ""}</button><span className="type-badge">{item.type === "photo" ? "ФОТО" : "ВИДЕО"}</span></div>
                    <div className="media-info"><strong title={item.name}>{item.name}</strong><span>{formatDate(item.modified)} · {formatBytes(item.size)}</span><small title={item.path}>{item.path}</small></div>
                  </article>
                ))}
              </div>
              {visibleItems.length === 0 && <div className="no-results"><strong>Ничего не найдено</strong><span>Попробуйте другой запрос или фильтр</span></div>}
            </>
          )}
        </div>
      </section>
    </main>
  );
}

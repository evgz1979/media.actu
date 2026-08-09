const elements = {
  choose: document.querySelector("#choose-source"),
  scan: document.querySelector("#scan"),
  sources: document.querySelector("#sources"),
  status: document.querySelector("#status"),
  summary: document.querySelector("#summary"),
  results: document.querySelector("#results"),
  body: document.querySelector("#results tbody"),
};

let sources = [];

function formatBytes(bytes) {
  if (!bytes) return "0 Б";
  const units = ["Б", "КБ", "МБ", "ГБ", "ТБ"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / (1024 ** index)).toFixed(index > 1 ? 1 : 0)} ${units[index]}`;
}

function setStatus(message, error = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("error", error);
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Неизвестная ошибка");
  return data;
}

function renderSources() {
  elements.sources.replaceChildren();
  elements.scan.disabled = sources.length === 0;

  if (!sources.length) {
    const empty = document.createElement("div");
    empty.className = "source-empty";
    empty.textContent = "Источники пока не добавлены.";
    elements.sources.append(empty);
    setStatus("Источники не выбраны.");
    return;
  }

  for (const path of sources) {
    const row = document.createElement("div");
    row.className = "source-row";

    const label = document.createElement("span");
    label.className = "source-path";
    label.textContent = path;
    label.title = path;

    const remove = document.createElement("button");
    remove.className = "remove";
    remove.type = "button";
    remove.textContent = "Убрать";
    remove.addEventListener("click", () => removeSource(path));

    row.append(label, remove);
    elements.sources.append(row);
  }
  setStatus(`Выбрано источников: ${sources.length}.`);
}

async function loadSources() {
  const data = await request("/api/sources");
  sources = data.sources;
  renderSources();
}

async function chooseSources() {
  elements.choose.disabled = true;
  setStatus("Ожидание выбора папки…");
  try {
    const data = await request("/api/sources/choose", { method: "POST", body: "{}" });
    sources = data.sources;
    renderSources();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    elements.choose.disabled = false;
  }
}

async function removeSource(path) {
  try {
    const data = await request("/api/sources", {
      method: "DELETE",
      body: JSON.stringify({ path }),
    });
    sources = data.sources;
    elements.summary.hidden = true;
    elements.results.hidden = true;
    renderSources();
  } catch (error) {
    setStatus(error.message, true);
  }
}

function renderReport(report) {
  const { summary, files } = report;
  document.querySelector("#total-count").textContent = summary.total;
  document.querySelector("#photo-count").textContent = summary.photos;
  document.querySelector("#video-count").textContent = summary.videos;
  document.querySelector("#total-size").textContent = formatBytes(summary.bytes);
  document.querySelector("#error-count").textContent = summary.errors;
  elements.summary.hidden = false;

  elements.body.replaceChildren();
  for (const file of files) {
    const row = document.createElement("tr");
    const values = [
      file.kind === "photo" ? "ФОТО" : "ВИДЕО",
      file.relative_path,
      file.source,
      formatBytes(file.size),
      new Date(file.modified_at).toLocaleString("ru-RU"),
    ];
    values.forEach((value, index) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      if (index === 1 || index === 2) cell.className = "path";
      if (index === 3) cell.className = "number";
      row.append(cell);
    });
    elements.body.append(row);
  }
  elements.results.hidden = files.length === 0;
  setStatus(
    summary.total
      ? `Сканирование завершено. Найдено файлов: ${summary.total}.`
      : "Сканирование завершено. Медиафайлы не найдены.",
    summary.errors > 0,
  );
}

async function scan() {
  elements.scan.disabled = true;
  elements.choose.disabled = true;
  setStatus("Сканирование вложенных папок…");
  try {
    renderReport(await request("/api/scan", { method: "POST", body: "{}" }));
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    elements.scan.disabled = sources.length === 0;
    elements.choose.disabled = false;
  }
}

elements.choose.addEventListener("click", chooseSources);
elements.scan.addEventListener("click", scan);
loadSources().catch((error) => setStatus(error.message, true));

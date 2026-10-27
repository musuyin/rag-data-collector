"use strict";
const $ = id => document.getElementById(id);
let token = "", current = null, sources = [], offset = 0, total = 0, busy = false;
let selectionVersion = 0;
const pageSize = 20;
function message(text, error = false) { $("message").textContent = text; $("message").className = error ? "error" : ""; }
async function api(path, method = "GET", body) {
  const response = await fetch(path, {method, headers: body === undefined ? {} : {
    "Content-Type": "application/json", "X-Write-Token": token}, body: body === undefined ? undefined : JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data));
  return data;
}
function element(tag, text, className) {
  const node = document.createElement(tag); if (text !== undefined) node.textContent = text;
  if (className) node.className = className; return node;
}
async function refresh() {
  const params = new URLSearchParams({limit: pageSize, offset, q: $("q").value,
    record_type: $("record-type").value, license_status: $("license-filter").value,
    include_deleted: $("include-deleted").checked});
  const [list, stats] = await Promise.all([api(`/api/records?${params}`), api("/api/stats")]);
  total = list.total;
  for (const key of ["total", "active", "withdrawn"]) $(key).textContent = stats[key];
  $("records").replaceChildren();
  for (const item of list.items) {
    const record = item.record, row = element("tr"); row.dataset.id = record.record_id;
    if (current?.record.record_id === record.record_id) row.className = "selected";
    const title = element("td"), link = element("button", item.display.title, "record-link");
    link.type = "button"; link.addEventListener("click", () => run(() => select(record.record_id)));
    title.append(link, element("small", record.record_id));
    const type = element("td"); type.append(element("span", record.record_type, "tag"),
      element("small", item.system.deleted ? "已撤回" : record.record_status));
    const license = element("td"); license.append(element("span", record.license_status,
      record.license_status === "open" ? "tag" : "tag warning"));
    row.append(title, type, license); $("records").append(row);
  }
  $("empty").hidden = total !== 0;
  $("empty").textContent = stats.total === 0 ?
    "还没有记录。先运行 uv run python scripts/import_lancedb.py，或新建一条记录。" : "没有符合筛选条件的记录。";
  $("page-label").textContent = `共 ${total} 条 · ${total ? offset + 1 : 0}–${Math.min(offset + pageSize, total)}`;
  $("prev").disabled = offset === 0; $("next").disabled = offset + pageSize >= total;
}
async function select(id) {
  const version = ++selectionVersion;
  const [item, history] = await Promise.all([api(`/api/records/${encodeURIComponent(id)}`),
    api(`/api/records/${encodeURIComponent(id)}/history`)]);
  if (version !== selectionVersion) return;
  current = item; $("editor-form").hidden = false; $("editor-title").textContent = "编辑记录";
  $("editor").value = JSON.stringify(item.record, null, 2); $("editor").disabled = item.system.deleted;
  $("revision").textContent = `版本 ${item.system.revision}`;
  $("editor-help").textContent = item.system.deleted ? "记录已撤回，可恢复后继续编辑。" : "修改后保存。record_id 固定；人工修改会被保留在操作日志中。";
  $("save").hidden = item.system.deleted; $("withdraw").hidden = item.system.deleted; $("restore").hidden = !item.system.deleted;
  $("provenance").hidden = false; $("origin").textContent = JSON.stringify({origin: item.origin, ...item.system}, null, 2);
  $("history-panel").hidden = false; $("history").replaceChildren();
  for (const event of history.items) {
    const detail = element("details", undefined, "history-item");
    detail.append(element("summary", `v${event.system.revision} · ${event.action} · ${new Date(event.at).toLocaleString()}`),
      element("pre", JSON.stringify(event.record, null, 2))); $("history").append(detail);
  }
  for (const row of $("records").children) row.classList.toggle("selected", row.dataset.id === id);
}
function newRecord() {
  selectionVersion++; current = null; $("editor-form").hidden = false; $("editor-title").textContent = "新建记录";
  $("revision").textContent = ""; $("editor-help").textContent = "填写记录内容，并选择已经登记的来源。";
  $("editor").disabled = false; $("editor").value = JSON.stringify({record_id: "DOC-请替换为英文或数字ID", record_type: "document",
    title: "", text: "", source_id: "", license_status: "unknown", record_status: "draft"}, null, 2);
  $("save").hidden = false; $("withdraw").hidden = true; $("restore").hidden = true;
  $("provenance").hidden = true; $("history-panel").hidden = true; $("editor").focus();
}
async function run(action) {
  if (busy) return;
  busy = true;
  const buttons = [$("save"), $("withdraw"), $("restore"), $("new-record")];
  buttons.forEach(button => button.disabled = true);
  try { await action(); } catch (error) { message(error.message, true); }
  finally { busy = false; buttons.forEach(button => button.disabled = false); }
}
$("filters").addEventListener("submit", event => {event.preventDefault(); run(async () => {offset = 0; await refresh();});});
$("prev").addEventListener("click", () => run(async () => {offset = Math.max(0, offset - pageSize); await refresh();}));
$("next").addEventListener("click", () => run(async () => {offset += pageSize; await refresh();}));
$("new-record").addEventListener("click", () => run(async () => newRecord()));
$("editor-form").addEventListener("submit", event => {event.preventDefault(); run(async () => {
  const record = JSON.parse($("editor").value);
  const result = current ? await api(`/api/records/${encodeURIComponent(current.record.record_id)}`, "PUT", {
    record, revision: current.system.revision}) : await api("/api/records", "POST", record);
  await select(result.record.record_id); await refresh(); message("已保存。");
});});
$("withdraw").addEventListener("click", () => run(async () => {
  if (!current || !confirm(`撤回 ${current.record.record_id}？原始文件会保留，记录可恢复。`)) return;
  const id = current.record.record_id;
  await api(`/api/records/${encodeURIComponent(id)}`, "DELETE", {revision: current.system.revision});
  offset = 0; await select(id); await refresh(); message("记录已撤回。");
}));
$("restore").addEventListener("click", () => run(async () => {
  const id = current.record.record_id;
  await api(`/api/records/${encodeURIComponent(id)}/restore`, "POST", {revision: current.system.revision});
  await select(id); await refresh(); message("记录已恢复。");
}));
run(async () => {
  const session = await api("/api/session"); token = session.write_token; sources = await api("/api/sources");
  for (const source of sources) $("sources").append(element("li", `${source.source_id} · ${source.organization}`));
  await refresh();
});

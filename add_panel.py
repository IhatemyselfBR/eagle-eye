from pathlib import Path
import uuid

html = Path("index.html")
js = Path("script.js")
backend = Path("backend/main.py")

page = html.read_text()
script = js.read_text()
api = backend.read_text()

if 'id="indexFiles"' not in page:
    panel = """
<section id="image-index-panel" style="margin:24px auto;padding:20px;max-width:760px;border:1px solid #51406b;border-radius:16px;background:#171321;color:white">
<h2>Adicionar imagens ao índice</h2>
<p>Selecione imagens para usar nas buscas. Máximo de 10 MB por arquivo.</p>
<input id="indexFiles" type="file" accept="image/*" multiple>
<button id="indexButton" type="button">Adicionar imagens</button>
<p id="indexStatus" role="status"></p>
</section>
"""
    page = page.replace("</body>", panel + "\n</body>", 1)
    html.write_text(page)

if "indexButton" not in script:
    script += """
const indexInput = document.querySelector('#indexFiles');
const indexButton = document.querySelector('#indexButton');
const indexStatus = document.querySelector('#indexStatus');

if (indexInput && indexButton && indexStatus) {
  indexButton.addEventListener('click', async () => {
    const files = [...indexInput.files];
    if (!files.length) {
      indexStatus.textContent = 'Selecione imagens primeiro.';
      return;
    }
    if (files.some(f => f.size > 10 * 1024 * 1024)) {
      indexStatus.textContent = 'Cada imagem deve ter no máximo 10 MB.';
      return;
    }
    const form = new FormData();
    files.forEach(f => form.append('files', f));
    indexButton.disabled = true;
    indexStatus.textContent = 'Enviando imagens...';
    try {
      const res = await fetch(`${API_BASE}/api/index`, {
        method: 'POST', body: form
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Falha no envio');
      indexStatus.textContent =
        `${data.saved} imagem(ns) adicionada(s). Total: ${data.indexed_images}.`;
      indexInput.value = '';
    } catch (e) {
      indexStatus.textContent = 'Erro: ' + e.message;
    } finally {
      indexButton.disabled = false;
    }
  });
}
"""
    js.write_text(script)

if '@app.post("/api/index")' not in api:
    route = '''

@app.post("/api/index")
async def add_images(files: list[UploadFile] = File(...)):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    errors = []
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED:
            errors.append(f"{upload.filename}: formato não permitido")
            continue
        raw = await upload.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            errors.append(f"{upload.filename}: máximo de 10 MB")
            continue
        try:
            load_image(raw)
        except Exception:
            errors.append(f"{upload.filename}: imagem inválida")
            continue
        (INDEX_DIR / f"{uuid.uuid4().hex}{suffix}").write_bytes(raw)
        saved += 1

    total = sum(
        1 for p in INDEX_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED
    )
    return {"ok": True, "saved": saved,
            "indexed_images": total, "errors": errors}
'''
    mount = api.find("app.mount(")
    if mount < 0:
        raise SystemExit("Não encontrei app.mount() no backend.")
    api = api[:mount] + route + "\n" + api[mount:]
    backend.write_text(api)

print("Painel presente:", 'id="indexFiles"' in html.read_text())
print("Rota presente:", '@app.post("/api/index")' in backend.read_text())

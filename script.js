const API_BASE=(window.EAGLE_API_BASE||'').replace(/\/$/,'');
const file=document.querySelector('#file'),drop=document.querySelector('#drop'),preview=document.querySelector('#preview'),img=document.querySelector('#previewImg'),nameEl=document.querySelector('#fileName'),remove=document.querySelector('#remove'),search=document.querySelector('#search'),status=document.querySelector('#status'),results=document.querySelector('#results'),grid=document.querySelector('#resultGrid');
let selected=null;
function setFile(f){if(!f||!f.type.startsWith('image/'))return;if(f.size>10*1024*1024){alert('A imagem precisa ter no máximo 10 MB.');return}selected=f;nameEl.textContent=f.name;img.src=URL.createObjectURL(f);drop.classList.add('hidden');preview.classList.remove('hidden');search.disabled=false}
file.addEventListener('change',e=>setFile(e.target.files[0]));['dragenter','dragover'].forEach(x=>drop.addEventListener(x,e=>{e.preventDefault();drop.classList.add('drag')}));['dragleave','drop'].forEach(x=>drop.addEventListener(x,e=>{e.preventDefault();drop.classList.remove('drag')}));drop.addEventListener('drop',e=>setFile(e.dataTransfer.files[0]));
remove.onclick=()=>{selected=null;file.value='';preview.classList.add('hidden');drop.classList.remove('hidden');search.disabled=true;results.classList.add('hidden');status.classList.add('hidden')};
search.onclick=async()=>{if(!selected)return;search.disabled=true;status.classList.remove('hidden');results.classList.add('hidden');status.textContent='Comparando com o índice local…';try{const body=new FormData();body.append('file',selected);const response=await fetch(`${API_BASE}/api/search`,{method:'POST',body});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Falha na busca.');status.textContent=`Análise concluída · ${data.indexed_images} imagem(ns) no índice`;document.querySelector('#score').textContent='ÍNDICE LOCAL';if(!data.results.length){grid.innerHTML='<p class="empty">Nenhuma imagem indexada ainda. Adicione imagens à pasta <code>image_index</code> e tente novamente.</p>'}else{grid.innerHTML=data.results.map(r=>`<article class="result"><img class="result-image" src="${API_BASE}${r.url}" alt="Imagem encontrada: ${escapeHtml(r.filename)}" loading="lazy"><div><span class="match">${r.similarity}%</span><b>${escapeHtml(r.filename)}</b><small>Similaridade visual aproximada</small></div></article>`).join('')}const notice=document.querySelector('.notice');notice.textContent=data.notice+' A busca compara apenas as imagens disponíveis no índice local; não procura automaticamente na internet.';results.classList.remove('hidden');results.scrollIntoView({behavior:'smooth',block:'start'})}catch(e){status.textContent='Não foi possível conectar ao backend. Confira se api-config.js contém a URL pública do backend e se a API está ativa. Detalhe: '+e.message}finally{search.disabled=false}};
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

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

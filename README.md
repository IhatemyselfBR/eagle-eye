# Eagle Eye — publicação fácil (GitHub Pages + Render)

Este projeto compara uma imagem enviada com imagens colocadas em `image_index/`, usando um hash médio simples e Pillow. Não reconhece identidade facial e não pesquisa a internet automaticamente.

## 1) Publicar o frontend no GitHub Pages
1. Crie um repositório público no GitHub chamado `eagle-eye` (ou outro nome).
2. Envie **todos os arquivos desta pasta**, incluindo `.github/workflows/pages.yml`.
3. Em Settings → Pages, selecione **GitHub Actions** como fonte. O workflow publica o site quando você envia arquivos para a branch `main`.
4. A URL ficará parecida com `https://SEU-USUARIO.github.io/eagle-eye/`.

## 2) Publicar a API no Render
1. No Render, crie um **New Web Service** conectado ao mesmo repositório.
2. O arquivo `render.yaml` define o build e o comando de inicialização; use a raiz do repositório como Root Directory.
3. Após a publicação, copie a URL do serviço, por exemplo `https://eagle-eye-api.onrender.com`.
4. Edite `api-config.js`, trocando `https://SUA-API.onrender.com` pela URL real da API. Envie a alteração ao GitHub.
5. Verifique `https://SUA-API.onrender.com/api/health`.

## 3) Índice de imagens
Adicione imagens que você tem autorização para usar à pasta `image_index/` e envie-as ao repositório. Não coloque fotos privadas ou sensíveis. Em serviços gratuitos, arquivos locais podem ser perdidos quando o serviço reinicia/reimplanta; este exemplo é para demonstração.

## Limitações importantes
- A comparação usa hash médio (Pillow), não embeddings de reconhecimento facial. É mais útil para imagens iguais ou visualmente semelhantes.
- Os percentuais são uma pontuação visual aproximada, não a probabilidade de duas imagens conterem a mesma pessoa.
- Não pesquisa perfis ou fotos pela internet. Isso exigiria uma fonte de busca/indexação separada.
- O plano gratuito do Render pode suspender o serviço após inatividade. A primeira chamada depois disso pode demorar.

## Testar localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Abra `http://127.0.0.1:8000`.

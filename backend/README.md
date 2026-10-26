# Eagle Eye — backend local

Este backend faz **busca por semelhança visual** entre a imagem enviada e imagens dentro de `image_index/`. Não faz reconhecimento de identidade facial e não pesquisa a internet automaticamente.

## Instalar no Termux

Instale Python e dependências:

```bash
pkg update
pkg install python
cd ~/eagle-eye
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Coloque imagens que você tem autorização para usar em `image_index/`. Depois inicie: 

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Abra `http://127.0.0.1:8000` no navegador. Documentação da API: `http://127.0.0.1:8000/docs`.

## Publicação

GitHub Pages hospeda apenas o frontend estático. Para usar a API fora do celular, o backend precisa ficar hospedado em um serviço compatível e o frontend precisa apontar para a URL pública da API. Não publique fotos privadas dentro do repositório.

## Limitações

O método atual usa hash perceptual (pHash), útil para imagens iguais, redimensionadas ou visualmente parecidas, mas não é um modelo semântico nem um sistema biométrico. A porcentagem é uma métrica aproximada de semelhança visual, não uma probabilidade de que duas imagens mostrem a mesma pessoa.

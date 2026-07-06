# 📅 Agenda Inteligente

Sistema de agendamento inteligente com dashboard web, containerizado via Docker Compose. Permite marcação de horários a partir de uma tela e sincronização automática com Google Sheets.

## 🧱 Stack

- **Backend:** Django (API REST)
- **Frontend:** Next.js (dashboard)
- **Automação:** n8n (orquestração dos agendamentos)
- **Integração:** Google Sheets API (opcional)
- **Infra:** Docker Compose

## 🎯 Como funciona

O dashboard em Next.js permite criar e visualizar agendamentos, que são processados pela API Django. O n8n orquestra a automação: quando configurado, sincroniza os dados automaticamente com uma planilha no Google Sheets, permitindo acompanhamento externo sem acesso direto ao banco.

> ⚠️ Projeto local/protótipo, atualmente pausado.

---

## 🚀 Setup local com Docker

Setup local para testar `n8n`, backend Django e dashboard Next.js do Agenda Inteligente.

### Subir

```bash
docker compose up -d
```

Abra os serviços:

- Dashboard: `http://localhost:3000`
- API Django: `http://localhost:8000/api/health/`
- n8n: `http://localhost:5678`

### Parar

```bash
docker compose down
```

### Logs

```bash
docker compose logs -f backend frontend n8n
```

## 📝 Observações

- Os dados ficam persistidos em `./n8n_data`.
- O n8n vai usar SQLite nesse setup local.
- A chave `N8N_ENCRYPTION_KEY` do arquivo `.env` serve só para testes locais. Em produção, use uma chave forte.
- O dashboard usa Google Sheets quando `GSHEETS_SPREADSHEET_ID` e `GSHEETS_CREDENTIALS_PATH` estiverem configurados.
- Sem Google Sheets configurado, o dashboard usa os agendamentos cadastrados no banco SQLite do backend.
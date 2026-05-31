# Agenda Inteligente local com Docker

Setup local para testar `n8n`, backend Django e dashboard Next.js do Agenda Inteligente.

## Subir

```bash
docker compose up -d
```

Abra os servicos:

- Dashboard: `http://localhost:3000`
- API Django: `http://localhost:8000/api/health/`
- n8n: `http://localhost:5678`

## Parar

```bash
docker compose down
```

## Logs

```bash
docker compose logs -f backend frontend n8n
```

## Observações

- Os dados ficam persistidos em `./n8n_data`.
- O n8n vai usar SQLite nesse setup local.
- A chave `N8N_ENCRYPTION_KEY` do arquivo `.env` serve só para testes locais. Em produção, use uma chave forte.
- O dashboard usa Google Sheets quando `GSHEETS_SPREADSHEET_ID` e `GSHEETS_CREDENTIALS_PATH` estiverem configurados.
- Sem Google Sheets configurado, o dashboard usa os agendamentos cadastrados no banco SQLite do backend.

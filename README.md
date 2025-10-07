# Telegram Creative Bot (Gemini + Subbase)

Projeto exemplo de um bot do Telegram para gerar textos, imagens e vídeos usando APIs de IA (por exemplo Gemini PRO), com controle de uso diário por usuário e integração com Subbase (supabase-py).

Estrutura principal:

```
app/
  ├── bot.py
  ├── commands/
  ├── services/
  ├── models/
  └── utils/
server.py
requirements.txt
.env.example
```

Instruções rápidas

1. Copie `.env.example` para `.env` e preencha as chaves.
2. Instale dependências: see `requirements.txt`.
3. Execute `python server.py` para iniciar o Flask keep-alive e o bot (o bot roda em background).

Notas

- Os métodos de integração com Gemini e geração de vídeo estão preparados como stubs/implementações iniciais — substitua pelos endpoints/parametrizações reais da sua conta.
- O serviço de banco de dados usa o cliente do Supabase (Subbase) e espera as tabelas `users`, `logs`, `planos` já criadas.

Replit (passo a passo)

1. No Replit, clique em Import from GitHub e cole: https://github.com/JuliaSMS/bot_telegram.git
2. Vá em Secrets (Environment variables) e adicione as chaves abaixo (obrigatórias para produção):

  - TELEGRAM_TOKEN
  - GEMINI_API_KEY
  - SUPABASE_URL
  - SUPABASE_KEY (ou SUPABASE_SERVICE_KEY)
  - DATABASE_URL (opcional se você usar Supabase Storage directly)

3. Em Shell (ou na UI), confirme o comando de run: o arquivo `.replit` já executa `pip install -r requirements.txt && python server.py`.

4. Configure Always On / Uptime pinger (Replit paid feature) ou adicione UptimeRobot para pingar `https://<your-repl>.repl.co/` a cada 5 minutos.

5. Teste no Telegram: envie `/start`, `/gerar_texto olá`, `/gerar_imagem cena fofa`.

Notas de produção

- Para deploy estável prefira Webhooks (atualize `BOT_MODE=webhook` e `WEBHOOK_URL` no `.env`) e use um servidor com HTTPS.
- Proteja suas chaves (não comite `.env`). Use os secrets da plataforma.


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

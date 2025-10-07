-- SQL example to create required tables in Supabase (Postgres)

create table if not exists users (
  id serial primary key,
  telegram_id bigint unique not null,
  nome text,
  plano text,
  limite_diario int,
  geracoes_hoje int default 0,
  ultima_geracao text
);

create table if not exists logs (
  id serial primary key,
  telegram_id bigint,
  tipo text,
  prompt text,
  resultado text,
  data timestamptz default now()
);

create table if not exists planos (
  id serial primary key,
  nome text,
  limite int,
  preco numeric
);

-- Insert default planos
insert into planos (nome, limite, preco) values ('Free', 5, 0) on conflict do nothing;
insert into planos (nome, limite, preco) values ('Pro', 50, 9.99) on conflict do nothing;

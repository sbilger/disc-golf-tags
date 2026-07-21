-- Discinsanity Hub — Supabase schema (run once in the SQL editor)
-- Phase-1 foundation. Same JSON-blob fast-path as the tags app, plus the
-- tables the hub modules will grow into. Tighten RLS before any public launch.

-- ============================================================
-- Fast path: one JSON row per "hub" (news + this-week) and per "league" (tags).
-- Lets the app go multi-device immediately with zero ORM.
-- ============================================================
create table if not exists public.hubs (
  id text primary key,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
create table if not exists public.leagues (
  id text primary key,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.hubs    enable row level security;
alter table public.leagues enable row level security;

-- PROTOTYPE policies: anon key can read/write. Fine for testing a private group.
-- Replace with Supabase Auth + an is_admin() check before launch (below).
drop policy if exists "anon all (proto)" on public.hubs;
create policy "anon all (proto)" on public.hubs    for all using (true) with check (true);
drop policy if exists "anon all (proto)" on public.leagues;
create policy "anon all (proto)" on public.leagues for all using (true) with check (true);

insert into public.hubs (id, state)    values ('discinsanity', '{}'::jsonb) on conflict (id) do nothing;
insert into public.leagues (id, state) values ('discinsanity', '{}'::jsonb) on conflict (id) do nothing;

-- ============================================================
-- LATER (Phase 1+) — normalized tables + real auth.
-- Members sign in with Supabase Auth; Jeff gets an 'admin' role.
-- ============================================================
-- create table members (
--   id uuid primary key references auth.users on delete cascade,
--   name text, pdga text, role text default 'member',   -- 'member' | 'organizer' | 'admin'
--   created_at timestamptz default now());
--
-- create table news (
--   id bigint generated always as identity primary key,
--   type text, title text, body text, link text, image_url text,
--   published_at timestamptz default now(), created_by uuid references members(id));
--
-- create table events (
--   id bigint generated always as identity primary key,
--   kind text,                -- 'tags' | 'doubles' | 'event'
--   date date, time text, course text, layout text, details text, udisc_url text);
--
-- create table doubles_rounds (
--   id bigint generated always as identity primary key,
--   date date, course text, layout text, format text default 'random-draw');
-- create table doubles_teams (
--   id bigint generated always as identity primary key,
--   round_id bigint references doubles_rounds(id),
--   p1 uuid references members(id), p2 uuid references members(id),
--   score int, place int);
--
-- helper for admin-gated policies:
-- create function is_admin() returns boolean language sql stable as
--   $$ select exists(select 1 from members where id = auth.uid() and role='admin') $$;
-- e.g.  create policy "admins write news" on news for all using (is_admin()) with check (is_admin());
--       create policy "anyone reads news" on news for select using (true);
-- ============================================================

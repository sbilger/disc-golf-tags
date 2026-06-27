-- TagShuffle — Supabase schema (run once in Supabase SQL editor)
-- Prototype fast-path: one row per league holds the whole app state as JSON.
-- Multi-device sync with zero ORM. Tighten RLS before any public launch.

create table if not exists public.leagues (
  id         text primary key,
  state      jsonb       not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- Row Level Security
alter table public.leagues enable row level security;

-- PROTOTYPE policy: anon key can read+write every league row.
-- Fine for a private weekly group. For a real launch, replace with auth
-- (e.g., a per-league secret column, or Supabase Auth + owner_id checks).
drop policy if exists "anon full access (prototype)" on public.leagues;
create policy "anon full access (prototype)"
  on public.leagues for all
  using (true) with check (true);

-- Seed the default league row (app will upsert into it).
insert into public.leagues (id, state)
values ('default', '{}'::jsonb)
on conflict (id) do nothing;

-- ============================================================
-- LATER (normalized) — when you outgrow the JSON blob:
--   leagues(id, name, owner_id, settings jsonb)
--   players(id, league_id, name, current_tag, created_at)
--   rounds(id, league_id, date, course, layout, par)
--   round_results(round_id, player_id, score, place, old_tag, new_tag)
--   trades(id, league_id, date, kind, note, changes jsonb)
-- Keep the JSON blob path until multi-league / per-user auth is needed.
-- ============================================================

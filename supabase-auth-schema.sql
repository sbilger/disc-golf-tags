-- Discinsanity — real Supabase Auth schema (run once in the SQL editor, AFTER
-- supabase-hub-schema.sql and supabase-stripe-schema.sql).
--
-- Replaces account.js's local/demo auth with real Supabase Auth (email/password now,
-- Google/Apple/Facebook OAuth once Sean registers each provider — see docs/TODO-SEAN.md).
--
-- One genuine security upgrade over everything before it: the admin code now lives in
-- `app_secrets`, a table with RLS enabled and ZERO policies (same "no policy = deny"
-- pattern as stripe_customers/payments) — it is NEVER shipped to the client, unlike every
-- ORGANIZER_CODE/ADMIN_CODE constant elsewhere in this app, which are plain JS visible to
-- anyone who views source. Granting admin happens through claim_admin(), a
-- SECURITY DEFINER function that checks the code server-side and is the ONLY path that can
-- ever set role='admin' — a regular authenticated user directly PATCHing their own members
-- row cannot self-promote (enforced by the protect_role_column trigger below).

-- ============================================================
-- members: one row per real Supabase Auth user (auth.users), auto-created by a trigger.
-- ============================================================
create table if not exists public.members (
  id          uuid primary key references auth.users(id) on delete cascade,
  name        text not null default '',
  email       text,
  pdga        text,
  rating      text,
  division    text,
  league_name text,
  has_card    boolean not null default false,
  role        text not null default 'member',  -- 'member' | 'admin' | 'organizer'
  created_at  timestamptz not null default now()
);
alter table public.members enable row level security;

-- Read: open, same posture as the rest of the app's game data (names/PDGA/rating need to
-- be visible for leaderboards, "who's this player" lookups, etc).
drop policy if exists "anyone reads members" on public.members;
create policy "anyone reads members" on public.members for select using (true);

-- Update: users can update their OWN row (name/pdga/rating/division/league_name/has_card),
-- but the trigger below silently reverts any attempt to change `role` this way.
drop policy if exists "users update own row" on public.members;
create policy "users update own row" on public.members
  for update using (auth.uid() = id) with check (auth.uid() = id);

-- Guard: only claim_admin() (below) can ever change `role`.
create or replace function public.protect_role_column()
returns trigger language plpgsql as $$
begin
  if new.role is distinct from old.role
     and coalesce(current_setting('app.bypass_role_guard', true), '') <> 'on' then
    new.role := old.role;
  end if;
  return new;
end;
$$;
drop trigger if exists protect_role on public.members;
create trigger protect_role before update on public.members
  for each row execute function public.protect_role_column();

-- Auto-create a members row whenever a new auth.users row appears — works for email/
-- password signup AND every OAuth provider (Google/Apple/Facebook all land here the same
-- way), no client-side insert needed.
create or replace function public.handle_new_member()
returns trigger language plpgsql security definer as $$
begin
  insert into public.members (id, name, email)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)),
    new.email
  )
  on conflict (id) do nothing;
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_member();

-- ============================================================
-- app_secrets: the admin code lives here, NOT in any client-shipped file. RLS enabled,
-- ZERO policies -> anon/authenticated get nothing directly. Only reachable from inside
-- claim_admin() (SECURITY DEFINER, runs as table owner, bypasses RLS).
-- ============================================================
create table if not exists public.app_secrets (
  key   text primary key,
  value text not null
);
alter table public.app_secrets enable row level security;
-- Intentionally no policies.

-- Sean: set the real admin code here (pick your own value, don't reuse anything posted in
-- chat/git history). Re-run this line whenever you want to rotate it — no code deploy needed.
insert into public.app_secrets (key, value) values ('admin_code', 'CHANGE_ME_IN_SQL_EDITOR')
  on conflict (key) do update set value = excluded.value;

create or replace function public.claim_admin(p_code text)
returns boolean language plpgsql security definer as $$
declare
  real_code text;
begin
  select value into real_code from public.app_secrets where key = 'admin_code';
  if real_code is null or p_code <> real_code then
    return false;
  end if;
  perform set_config('app.bypass_role_guard', 'on', true);
  update public.members set role = 'admin' where id = auth.uid();
  perform set_config('app.bypass_role_guard', 'off', true);
  return true;
end;
$$;

-- Let any authenticated (signed-in) user CALL the function — the function itself gates on
-- the code, not on who's allowed to try.
grant execute on function public.claim_admin(text) to authenticated;

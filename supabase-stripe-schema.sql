-- Discinsanity — Stripe payments schema (run once in the SQL editor, AFTER supabase-hub-schema.sql)
-- Card-on-file (SetupIntent) + off-session charge-on-round-save model. See docs/TODO-SEAN.md
-- "Section 3" for the full setup checklist (Stripe account, Edge Function secrets, deploy, webhook).
--
-- SECURITY: unlike the prototype "anon all" policy on hubs/leagues, these two tables get
-- ZERO policies — meaning the anon/publishable key has NO access at all (RLS default-denies
-- with no matching policy). Only Supabase Edge Functions (using the service_role key, which
-- bypasses RLS entirely) can read or write here. Client-side code never queries these tables
-- directly — it only ever calls the Edge Functions, which is the whole point: card numbers,
-- Stripe customer IDs, and payment records don't belong behind the same open-by-default
-- policy as game scores.

create table if not exists public.stripe_customers (
  email                   text primary key,
  name                    text,
  stripe_customer_id      text not null,
  default_payment_method  text,
  card_brand              text,
  card_last4              text,
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);
alter table public.stripe_customers enable row level security;
-- Intentionally NO policy here. service_role (Edge Functions) bypasses RLS; anon key gets nothing.

create table if not exists public.payments (
  id                        bigint generated always as identity primary key,
  email                     text not null,
  event_date                date not null,
  course                    text,
  amount_cents              int not null,
  stripe_payment_intent_id  text,
  status                    text not null default 'pending',
    -- 'pending' | 'succeeded' | 'failed' | 'requires_action' | 'no_card' | 'no_email'
  error_message             text,
  created_at                timestamptz not null default now()
);
alter table public.payments enable row level security;
-- Same as above: no policy, service_role only.

create index if not exists payments_email_idx      on public.payments(email);
create index if not exists payments_event_date_idx on public.payments(event_date);
create index if not exists payments_pi_idx          on public.payments(stripe_payment_intent_id);

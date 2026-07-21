// supabase/functions/charge-players/index.ts
//
// Called from index.html's saveRound() when the organizer finalizes a Tags night — charges
// every present player's saved card off-session for that week's fee. Players with no card on
// file are skipped (status 'no_card'); players with no email on their account are skipped
// (status 'no_email'). The round itself ALWAYS saves regardless of payment outcome — payment
// is a side-effect of finalizing a night, never a gate on the game data.
//
// A 'pending' row is written to `payments` BEFORE the Stripe call, so the webhook always has
// a row to match against (by stripe_payment_intent_id) even if this function's own response
// never makes it back to the client (network drop, tab closed, etc).
//
// Env vars: STRIPE_SECRET_KEY. SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY auto-injected.
// Deploy with verify_jwt = false (see supabase/config.toml) — same reason as save-card.

import { corsHeaders } from "../_shared/cors.ts";

const STRIPE_SECRET_KEY = Deno.env.get("STRIPE_SECRET_KEY")!;
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

async function stripeApi(path: string, body: Record<string, string>) {
  const r = await fetch(`https://api.stripe.com/v1/${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams(body),
  });
  const json = await r.json();
  return { ok: r.ok, json };
}

async function supa(path: string, init: RequestInit = {}) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  if (!r.ok) throw new Error(`Supabase ${path} failed: ${await r.text()}`);
  return r.status === 204 ? null : r.json();
}

type Player = { name: string; email?: string };

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  try {
    const { players, eventDate, course, feeCents } = (await req.json()) as {
      players: Player[];
      eventDate: string;
      course?: string;
      feeCents: number;
    };
    if (!Array.isArray(players) || !eventDate || !feeCents) {
      throw new Error("players[], eventDate, feeCents required");
    }

    const results: Array<{ name: string; email?: string; status: string }> = [];

    for (const p of players) {
      if (!p.email) {
        results.push({ name: p.name, status: "no_email" });
        continue;
      }

      const rows = await supa(
        `stripe_customers?email=eq.${encodeURIComponent(p.email)}&select=stripe_customer_id,default_payment_method`,
      );
      const cust = rows && rows[0];
      if (!cust || !cust.default_payment_method) {
        results.push({ name: p.name, email: p.email, status: "no_card" });
        continue;
      }

      const pending = await supa("payments", {
        method: "POST",
        headers: { Prefer: "return=representation" },
        body: JSON.stringify({
          email: p.email,
          event_date: eventDate,
          course: course || null,
          amount_cents: feeCents,
          status: "pending",
        }),
      });
      const paymentRowId = pending[0].id;

      const { ok, json } = await stripeApi("payment_intents", {
        amount: String(feeCents),
        currency: "usd",
        customer: cust.stripe_customer_id,
        payment_method: cust.default_payment_method,
        off_session: "true",
        confirm: "true",
      });

      const status = ok ? (json.status === "succeeded" ? "succeeded" : "requires_action") : "failed";
      await supa(`payments?id=eq.${paymentRowId}`, {
        method: "PATCH",
        headers: { Prefer: "return=minimal" },
        body: JSON.stringify({
          status,
          stripe_payment_intent_id: json.id || null,
          error_message: ok ? null : json.error?.message || "charge failed",
        }),
      });
      results.push({ name: p.name, email: p.email, status });
    }

    return new Response(JSON.stringify({ results }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: (e as Error).message }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

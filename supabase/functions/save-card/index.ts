// supabase/functions/save-card/index.ts
//
// Creates (or reuses) a Stripe Customer for a player's email, then a SetupIntent so the
// client can save a card via Stripe.js (stripe.confirmCardSetup). Returns the SetupIntent's
// client_secret.
//
// NOTE: this function does NOT store the resulting payment method — that happens in
// stripe-webhook when Stripe fires `setup_intent.succeeded`. The webhook is the source of
// truth (fires server-side regardless of whether the client's confirmCardSetup round trip
// actually completes, e.g. tab closed mid-flow).
//
// Env vars (set via `supabase secrets set`, never in code): STRIPE_SECRET_KEY.
// SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are auto-injected by the Supabase runtime.
//
// Deploy with verify_jwt = false (see supabase/config.toml) — the client has no real Supabase
// Auth session (account.js is still demo/local auth), so there's no user JWT to verify.

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
  if (!r.ok) throw new Error(json.error?.message || `Stripe ${path} failed`);
  return json;
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

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  try {
    const { email, name } = await req.json();
    if (!email) throw new Error("email required");

    const existing = await supa(
      `stripe_customers?email=eq.${encodeURIComponent(email)}&select=stripe_customer_id`,
    );

    let customerId: string;
    if (existing && existing.length) {
      customerId = existing[0].stripe_customer_id;
    } else {
      const customer = await stripeApi("customers", { email, name: name || "" });
      customerId = customer.id;
      await supa("stripe_customers", {
        method: "POST",
        headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
        body: JSON.stringify({ email, name: name || "", stripe_customer_id: customerId }),
      });
    }

    const setupIntent = await stripeApi("setup_intents", {
      customer: customerId,
      "payment_method_types[]": "card",
      usage: "off_session",
    });

    return new Response(JSON.stringify({ client_secret: setupIntent.client_secret }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: (e as Error).message }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

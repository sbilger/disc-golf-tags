// supabase/functions/stripe-webhook/index.ts
//
// Receives Stripe webhook events. This is the SOURCE OF TRUTH for two things the client-side
// flow can't guarantee on its own (tabs close, networks drop mid-request):
//   1. setup_intent.succeeded -> record the saved payment method as the customer's default
//      (brand/last4 for display), independent of whether save-card's client ever got a
//      response back.
//   2. payment_intent.succeeded / payment_intent.payment_failed -> update the matching
//      `payments` row (matched by stripe_payment_intent_id, written as 'pending' by
//      charge-players) to its final status.
//
// Verifies the Stripe-Signature header by hand (HMAC-SHA256 over "timestamp.payload") rather
// than pulling in the full Stripe SDK — Deno edge runtime, keep it light.
//
// SETUP (Sean, once Stripe account exists): after deploying this function, go to
// Stripe Dashboard -> Developers -> Webhooks -> Add endpoint, URL =
// https://ohvhhcpmohztmlossbjv.supabase.co/functions/v1/stripe-webhook, events to send:
// setup_intent.succeeded, payment_intent.succeeded, payment_intent.payment_failed.
// Stripe gives you a signing secret (whsec_...) at that point — set it as the
// STRIPE_WEBHOOK_SECRET function secret (never in code/chat).
//
// Deploy with verify_jwt = false (see supabase/config.toml) — Stripe's webhook calls carry
// Stripe-Signature, not a Supabase JWT.

const STRIPE_SECRET_KEY = Deno.env.get("STRIPE_SECRET_KEY")!;
const STRIPE_WEBHOOK_SECRET = Deno.env.get("STRIPE_WEBHOOK_SECRET")!;
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

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

async function stripeGet(path: string) {
  const r = await fetch(`https://api.stripe.com/v1/${path}`, {
    headers: { Authorization: `Bearer ${STRIPE_SECRET_KEY}` },
  });
  return r.json();
}

async function verifyStripeSignature(payload: string, sigHeader: string, secret: string) {
  const parts = Object.fromEntries(
    sigHeader.split(",").map((p) => p.split("=") as [string, string]),
  );
  const signedPayload = `${parts.t}.${payload}`;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sigBytes = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(signedPayload));
  const hex = Array.from(new Uint8Array(sigBytes))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return hex === parts.v1;
}

Deno.serve(async (req: Request) => {
  const payload = await req.text();
  const sig = req.headers.get("stripe-signature") || "";

  try {
    const ok = await verifyStripeSignature(payload, sig, STRIPE_WEBHOOK_SECRET);
    if (!ok) return new Response("bad signature", { status: 400 });
  } catch {
    return new Response("bad signature", { status: 400 });
  }

  const event = JSON.parse(payload);

  try {
    if (event.type === "setup_intent.succeeded") {
      const si = event.data.object;
      const customerId = si.customer as string;
      const pmId = si.payment_method as string;
      const pm = await stripeGet(`payment_methods/${pmId}`);
      await supa(`stripe_customers?stripe_customer_id=eq.${customerId}`, {
        method: "PATCH",
        headers: { Prefer: "return=minimal" },
        body: JSON.stringify({
          default_payment_method: pmId,
          card_brand: pm.card?.brand || null,
          card_last4: pm.card?.last4 || null,
          updated_at: new Date().toISOString(),
        }),
      });
    }

    if (event.type === "payment_intent.succeeded" || event.type === "payment_intent.payment_failed") {
      const pi = event.data.object;
      await supa(`payments?stripe_payment_intent_id=eq.${pi.id}`, {
        method: "PATCH",
        headers: { Prefer: "return=minimal" },
        body: JSON.stringify({
          status: event.type === "payment_intent.succeeded" ? "succeeded" : "failed",
          error_message: pi.last_payment_error?.message || null,
        }),
      });
    }

    return new Response("ok", { status: 200 });
  } catch (e) {
    console.error(e);
    return new Response("handler error", { status: 500 });
  }
});

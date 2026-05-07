import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { getStripe } from "@/lib/stripe";
import { getSupabase } from "@/lib/supabase";

export async function POST(request: NextRequest) {
  const stripe = getStripe();
  const supabase = getSupabase();
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

  const body = await request.text();
  const signature = request.headers.get("stripe-signature")!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    console.error("Webhook signature verification failed:", err);
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  try {
    switch (event.type) {

      // ──────────────────────────────────────────────────────────────────────
      // Pago completado → crear/activar usuario en suite_usuarios
      // ──────────────────────────────────────────────────────────────────────
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;

        if (session.mode !== "subscription") break;

        const customerEmail  = session.customer_details?.email?.toLowerCase();
        const customerName   = session.customer_details?.name || "";
        const customerId     = session.customer as string;
        const subscriptionId = session.subscription as string;
        const planType       = session.metadata?.planType || "individual";
        const companyName    = session.metadata?.companyName || "";

        if (!customerEmail) {
          console.error("checkout.session.completed: no customer email");
          break;
        }

        if (planType === "empresa" && companyName) {
          // Admin empresa
          const { error } = await supabase.from("suite_usuarios").upsert(
            {
              email:                  customerEmail,
              nombre:                 customerName || customerEmail.split("@")[0],
              rol:                    "administrador",
              plan:                   "empresa",
              empresa:                companyName,
              activo:                 true,
              stripe_customer_id:     customerId,
              stripe_subscription_id: subscriptionId,
            },
            { onConflict: "email" }
          );
          if (error) console.error("suite_usuarios upsert empresa error:", error);
          else console.log("suite_usuarios upsert empresa OK:", customerEmail);

        } else {
          // Individual
          const { error } = await supabase.from("suite_usuarios").upsert(
            {
              email:                  customerEmail,
              nombre:                 customerName || customerEmail.split("@")[0],
              rol:                    "suscrito",
              plan:                   "individual",
              activo:                 true,
              stripe_customer_id:     customerId,
              stripe_subscription_id: subscriptionId,
            },
            { onConflict: "email" }
          );
          if (error) console.error("suite_usuarios upsert individual error:", error);
          else console.log("suite_usuarios upsert individual OK:", customerEmail);
        }
        break;
      }

      // ──────────────────────────────────────────────────────────────────────
      // Suscripción actualizada (renovación, reactivación)
      // ──────────────────────────────────────────────────────────────────────
      case "customer.subscription.updated": {
        const subscription = event.data.object as Stripe.Subscription;
        const isActive = ["active", "trialing"].includes(subscription.status);

        await supabase
          .from("suite_usuarios")
          .update({ activo: isActive })
          .eq("stripe_subscription_id", subscription.id);

        break;
      }

      // ──────────────────────────────────────────────────────────────────────
      // Suscripción cancelada → desactivar acceso
      // ──────────────────────────────────────────────────────────────────────
      case "customer.subscription.deleted": {
        const subscription = event.data.object as Stripe.Subscription;

        const { data: adminRow } = await supabase
          .from("suite_usuarios")
          .select("empresa")
          .eq("stripe_subscription_id", subscription.id)
          .single();

        if (adminRow?.empresa) {
          await supabase
            .from("suite_usuarios")
            .update({ activo: false })
            .eq("empresa", adminRow.empresa);
        } else {
          await supabase
            .from("suite_usuarios")
            .update({ activo: false })
            .eq("stripe_subscription_id", subscription.id);
        }
        break;
      }

      // ──────────────────────────────────────────────────────────────────────
      // Pago fallido → desactivar acceso
      // ──────────────────────────────────────────────────────────────────────
      case "invoice.payment_failed": {
        const invoice = event.data.object as Stripe.Invoice;
        await supabase
          .from("suite_usuarios")
          .update({ activo: false })
          .eq("stripe_customer_id", invoice.customer as string);
        break;
      }
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("Webhook handler error:", error);
    return NextResponse.json({ error: "Webhook handler failed" }, { status: 500 });
  }
}

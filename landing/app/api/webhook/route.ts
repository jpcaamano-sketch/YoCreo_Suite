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
      // Pago completado → activar usuario en suite_usuarios
      // ──────────────────────────────────────────────────────────────────────
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;

        if (session.mode !== "subscription") break;

        const customerEmail = session.customer_details?.email?.toLowerCase();
        const customerName  = session.customer_details?.name || "";
        const customerId    = session.customer as string;
        const subscriptionId = session.subscription as string;
        const planType      = session.metadata?.planType || "individual";
        const companyName   = session.metadata?.companyName || "";

        if (!customerEmail) break;

        // ── 1. Tablas antiguas (no tocar) ──────────────────────────────────
        if (planType === "empresa" && companyName) {
          const { data: orgData, error: orgError } = await supabase
            .from("organizations")
            .insert({
              name: companyName,
              admin_email: customerEmail,
              customer_id: customerId,
              subscription_id: subscriptionId,
              status: "active",
              seat_count: 1,
            })
            .select()
            .single();

          if (!orgError && orgData) {
            await supabase.from("organization_members").insert({
              organization_id: orgData.id,
              email: customerEmail,
              role: "admin",
              status: "active",
            });

            // ── 2. suite_usuarios — admin empresa ─────────────────────────
            await supabase.from("suite_usuarios").upsert(
              {
                email:                  customerEmail,
                nombre:                 customerName || customerEmail.split("@")[0],
                rol:                    "administrador",
                plan:                   "empresa",
                empresa:                companyName,
                activo:                 true,
                stripe_customer_id:     customerId,
                stripe_subscription_id: subscriptionId,
                organization_id:        orgData.id,
              },
              { onConflict: "email" }
            );
          } else {
            console.error("Error creating organization:", orgError);
          }

        } else {
          // Individual
          await supabase.from("subscriptions").upsert({
            email:           customerEmail,
            customer_id:     customerId,
            subscription_id: subscriptionId,
            status:          "active",
            plan_type:       "individual",
          });

          // ── 2. suite_usuarios — suscriptor individual ──────────────────
          await supabase.from("suite_usuarios").upsert(
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
        }
        break;
      }

      // ──────────────────────────────────────────────────────────────────────
      // Suscripción actualizada (renovación, cambio de plan, reactivación)
      // ──────────────────────────────────────────────────────────────────────
      case "customer.subscription.updated": {
        const subscription = event.data.object as Stripe.Subscription;
        const quantity   = subscription.items.data[0]?.quantity ?? null;
        const isActive   = ["active", "trialing"].includes(subscription.status);

        await supabase
          .from("subscriptions")
          .update({ status: subscription.status, updated_at: new Date().toISOString() })
          .eq("subscription_id", subscription.id);

        await supabase
          .from("organizations")
          .update({
            status: subscription.status,
            updated_at: new Date().toISOString(),
            ...(quantity !== null ? { seat_count: quantity } : {}),
          })
          .eq("subscription_id", subscription.id);

        // Sincronizar suite_usuarios
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

        await supabase
          .from("subscriptions")
          .update({ status: "canceled", updated_at: new Date().toISOString() })
          .eq("subscription_id", subscription.id);

        await supabase
          .from("organizations")
          .update({ status: "canceled", updated_at: new Date().toISOString() })
          .eq("subscription_id", subscription.id);

        // Desactivar en suite_usuarios (admin + todos sus miembros empresa si aplica)
        const { data: adminRow } = await supabase
          .from("suite_usuarios")
          .select("empresa")
          .eq("stripe_subscription_id", subscription.id)
          .single();

        if (adminRow?.empresa) {
          // Desactivar toda la empresa
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
      // Pago fallido → marcar como vencido (no desactiva aún)
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
    console.error("Webhook error:", error);
    return NextResponse.json({ error: "Webhook handler failed" }, { status: 500 });
  }
}

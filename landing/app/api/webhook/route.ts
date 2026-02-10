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
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;

        if (session.mode === "subscription") {
          const customerEmail =
            session.customer_details?.email?.toLowerCase();
          const customerId = session.customer as string;
          const subscriptionId = session.subscription as string;
          const planType = session.metadata?.planType || "individual";
          const companyName = session.metadata?.companyName || "";

          if (planType === "empresa" && companyName) {
            const { data: orgData, error: orgError } = await supabase
              .from("organizations")
              .insert({
                name: companyName,
                admin_email: customerEmail,
                customer_id: customerId,
                subscription_id: subscriptionId,
                status: "active",
                max_members: null,
                seat_count: 1,
              })
              .select()
              .single();

            if (orgError) {
              console.error("Error creating organization:", orgError);
            } else {
              await supabase.from("organization_members").insert({
                organization_id: orgData.id,
                email: customerEmail,
                role: "admin",
                status: "active",
              });
            }
          } else {
            const { error } = await supabase.from("subscriptions").upsert({
              email: customerEmail,
              customer_id: customerId,
              subscription_id: subscriptionId,
              status: "active",
              plan_type: "individual",
            });

            if (error) {
              console.error("Error saving subscription:", error);
            }
          }
        }
        break;
      }

      case "customer.subscription.updated": {
        const subscription = event.data.object as Stripe.Subscription;
        const quantity = subscription.items.data[0]?.quantity ?? null;

        await supabase
          .from("subscriptions")
          .update({
            status: subscription.status,
            updated_at: new Date().toISOString(),
          })
          .eq("subscription_id", subscription.id);

        await supabase
          .from("organizations")
          .update({
            status: subscription.status,
            updated_at: new Date().toISOString(),
            ...(quantity !== null ? { seat_count: quantity } : {}),
          })
          .eq("subscription_id", subscription.id);
        break;
      }

      case "customer.subscription.deleted": {
        const subscription = event.data.object as Stripe.Subscription;

        await supabase
          .from("subscriptions")
          .update({
            status: "canceled",
            updated_at: new Date().toISOString(),
          })
          .eq("subscription_id", subscription.id);

        await supabase
          .from("organizations")
          .update({
            status: "canceled",
            updated_at: new Date().toISOString(),
          })
          .eq("subscription_id", subscription.id);
        break;
      }
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("Webhook error:", error);
    return NextResponse.json(
      { error: "Webhook handler failed" },
      { status: 500 }
    );
  }
}

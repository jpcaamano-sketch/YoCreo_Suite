import { NextResponse } from "next/server";
import { getStripe } from "@/lib/stripe";
import { getSupabase } from "@/lib/supabase";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { organization_id, new_quantity, api_key } = body;

    // Validate API key
    if (!api_key || api_key !== process.env.API_SECRET_KEY) {
      return NextResponse.json(
        { error: "No autorizado" },
        { status: 401 }
      );
    }

    if (!organization_id || !new_quantity || new_quantity < 1) {
      return NextResponse.json(
        { error: "Parámetros inválidos" },
        { status: 400 }
      );
    }

    const supabase = getSupabase();
    const stripe = getStripe();

    // Get organization's subscription_id
    const { data: org, error: orgError } = await supabase
      .from("organizations")
      .select("subscription_id")
      .eq("id", organization_id)
      .single();

    if (orgError || !org?.subscription_id) {
      return NextResponse.json(
        { error: "Organización o suscripción no encontrada" },
        { status: 404 }
      );
    }

    // Get the subscription from Stripe to find the item ID
    const subscription = await stripe.subscriptions.retrieve(
      org.subscription_id
    );
    const subscriptionItemId = subscription.items.data[0]?.id;

    if (!subscriptionItemId) {
      return NextResponse.json(
        { error: "No se encontró el item de suscripción en Stripe" },
        { status: 500 }
      );
    }

    // Update Stripe subscription quantity
    await stripe.subscriptions.update(org.subscription_id, {
      items: [
        {
          id: subscriptionItemId,
          quantity: new_quantity,
        },
      ],
    });

    // Update seat_count in database
    await supabase
      .from("organizations")
      .update({ seat_count: new_quantity })
      .eq("id", organization_id);

    return NextResponse.json({ success: true, seat_count: new_quantity });
  } catch (error) {
    console.error("Error updating seats:", error);
    return NextResponse.json(
      { error: "Error al actualizar asientos" },
      { status: 500 }
    );
  }
}

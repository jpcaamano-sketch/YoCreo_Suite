import { NextResponse } from "next/server";
import { getStripe } from "@/lib/stripe";

export async function POST(req: Request) {
  try {
    const stripe = getStripe();
    const body = await req.json();
    const { planType = "individual", companyName } = body;

    const priceId = process.env.STRIPE_PRICE_ID!;

    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      payment_method_types: ["card"],
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"}/exito?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"}`,
      allow_promotion_codes: true,
      metadata: {
        planType,
        companyName: companyName || "",
      },
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error("Error creating checkout session:", error);
    return NextResponse.json(
      { error: "Error al crear la sesion de pago" },
      { status: 500 }
    );
  }
}

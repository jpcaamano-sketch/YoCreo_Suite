import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export async function GET(request: NextRequest) {
  const email = request.nextUrl.searchParams.get("email");

  if (!email) {
    return NextResponse.json({ error: "Email requerido" }, { status: 400 });
  }

  try {
    const { data, error } = await supabase
      .from("subscriptions")
      .select("status, created_at")
      .eq("email", email.toLowerCase())
      .eq("status", "active")
      .single();

    if (error || !data) {
      return NextResponse.json({ hasAccess: false });
    }

    return NextResponse.json({
      hasAccess: true,
      subscribedAt: data.created_at,
    });
  } catch (error) {
    console.error("Error checking subscription:", error);
    return NextResponse.json(
      { error: "Error al verificar suscripción" },
      { status: 500 }
    );
  }
}

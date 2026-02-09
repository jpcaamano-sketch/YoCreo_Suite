"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

const APP_URL =
  process.env.NEXT_PUBLIC_STREAMLIT_URL ||
  "https://yocreo-app-production.up.railway.app";

function ExitoContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      fetch(`/api/verify-session?session_id=${sessionId}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.email) {
            setEmail(data.email);
          }
          setLoading(false);
        })
        .catch(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [sessionId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-6">
      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-12 max-w-lg text-center">
        <div className="text-6xl mb-6">🎉</div>
        <h1 className="text-3xl font-bold text-white mb-4">
          ¡Bienvenido a YoCreo Suite!
        </h1>

        {loading ? (
          <p className="text-gray-300 mb-8">Verificando tu suscripcion...</p>
        ) : (
          <>
            <p className="text-gray-300 mb-4">
              Tu suscripcion ha sido activada exitosamente.
            </p>
            {email && (
              <p className="text-purple-400 mb-8">
                Cuenta: <strong>{email}</strong>
              </p>
            )}
          </>
        )}

        <div className="space-y-4">
          <a
            href={APP_URL}
            className="block w-full py-4 px-8 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl transition-all transform hover:scale-105"
          >
            Acceder a YoCreo Suite
          </a>

          <p className="text-gray-500 text-sm">
            Guarda este enlace para acceder en el futuro
          </p>
        </div>

        <div className="mt-8 pt-8 border-t border-white/10">
          <h3 className="text-white font-semibold mb-4">Proximos pasos:</h3>
          <ul className="text-left text-gray-400 space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-1">1.</span>
              <span>Accede a la aplicacion con el boton de arriba</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-1">2.</span>
              <span>Ingresa con el email de tu suscripcion</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-1">3.</span>
              <span>Explora las 14 practicas de coaching con IA</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default function ExitoPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
          <p className="text-white">Cargando...</p>
        </div>
      }
    >
      <ExitoContent />
    </Suspense>
  );
}

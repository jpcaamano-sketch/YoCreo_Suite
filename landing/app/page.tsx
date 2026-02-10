"use client";

import { useState } from "react";

const APP_URL =
  process.env.NEXT_PUBLIC_STREAMLIT_URL ||
  "https://yocreo-app-production.up.railway.app";

const practicas = [
  { icono: "🛡️", nombre: "Priorizador de Tareas", desc: "Matriz de Eisenhower con IA" },
  { icono: "🎭", nombre: "Presentación Inspiradora", desc: "Storytelling ejecutivo" },
  { icono: "🗣️", nombre: "Pedidos Impecables", desc: "Comunicación ontológica" },
  { icono: "🎯", nombre: "Delegación Situacional", desc: "Liderazgo Hersey & Blanchard" },
  { icono: "🕊️", nombre: "Mensajes Diplomáticos", desc: "Comunicación asertiva" },
  { icono: "✅", nombre: "Seguimiento de Compromisos", desc: "Accountability efectivo" },
  { icono: "👂", nombre: "Escucha Activa", desc: "Simulador de empatía" },
  { icono: "❓", nombre: "Preguntas Desafiantes", desc: "Preguntas poderosas" },
  { icono: "💬", nombre: "Feedback Constructivo", desc: "Retroalimentación efectiva" },
  { icono: "⚖️", nombre: "Evaluación de Desempeño", desc: "Evaluación objetiva" },
  { icono: "🎯", nombre: "Definición de Objetivos", desc: "Objetivos e indicadores claros" },
  { icono: "📅", nombre: "Planificador de Reuniones", desc: "Agendas ejecutivas efectivas" },
  { icono: "🤝", nombre: "Negociador Harvard", desc: "Estrategia ganar-ganar" },
  { icono: "🙏", nombre: "Disculpas Efectivas", desc: "Repara vínculos genuinamente" },
];

const pasos = [
  {
    num: "1",
    titulo: "Elige tu plan",
    desc: "Selecciona Individual o Empresa y suscríbete en menos de 2 minutos.",
  },
  {
    num: "2",
    titulo: "Accede con tu email",
    desc: "Ingresa a la plataforma con el mismo correo de tu suscripción.",
  },
  {
    num: "3",
    titulo: "Potencia tu liderazgo",
    desc: "Usa las 14 prácticas con IA para resolver desafíos reales de tu día a día.",
  },
];

const beneficios = [
  {
    titulo: "Resultados en minutos",
    desc: "Genera cartas, planes, evaluaciones y feedback listo para usar. Sin perder horas redactando.",
  },
  {
    titulo: "Basado en metodologías reales",
    desc: "Eisenhower, Harvard, Hersey & Blanchard, SCI y más. No es IA genérica: es coaching profesional.",
  },
  {
    titulo: "Exporta y comparte",
    desc: "Descarga todo en PDF o copia al portapapeles. Listo para enviar a tu equipo o jefatura.",
  },
  {
    titulo: "Para líderes y equipos",
    desc: "Plan individual para profesionales. Plan empresa con panel de administración y usuarios ilimitados.",
  },
];

const faqs = [
  {
    q: "¿Qué necesito para usar YoCreo?",
    a: "Solo un navegador web y una suscripción activa. No necesitas instalar nada.",
  },
  {
    q: "¿Cómo funciona la IA?",
    a: "Cada práctica usa prompts especializados que combinan metodologías de coaching con Inteligencia Artificial de última generación para darte resultados profesionales y personalizados.",
  },
  {
    q: "¿Puedo cancelar en cualquier momento?",
    a: "Sí. Tu suscripción es mensual y puedes cancelarla cuando quieras. No hay contratos ni permanencia mínima.",
  },
  {
    q: "¿Cómo funciona el plan Empresa?",
    a: "El administrador suscribe a la empresa y agrega miembros desde el panel de administración. Cada miembro cuesta $10.000/mes y se cobra automáticamente. Sin límite de usuarios. Cada miembro accede con su propio email.",
  },
  {
    q: "¿Mis datos están seguros?",
    a: "Sí. Usamos Stripe para pagos (el mismo procesador de Google y Amazon) y Supabase para datos con encriptación. No almacenamos el contenido que generas.",
  },
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<"individual" | "empresa">(
    "individual"
  );
  const [companyName, setCompanyName] = useState("");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const handleSubscribe = async () => {
    if (selectedPlan === "empresa" && !companyName.trim()) {
      alert("Por favor ingresa el nombre de tu empresa");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          planType: selectedPlan,
          companyName:
            selectedPlan === "empresa" ? companyName.trim() : undefined,
        }),
      });
      const { url, error } = await response.json();

      if (error) {
        alert(error);
        setLoading(false);
        return;
      }

      if (url) {
        window.location.href = url;
      }
    } catch {
      alert("Error al procesar. Intenta de nuevo.");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="container mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="YoCreo" className="h-10" />
            <span className="text-xl font-bold text-white">YoCreo IA</span>
          </div>
          <a
            href={APP_URL}
            className="text-sm text-gray-300 hover:text-white transition-colors border border-white/20 px-4 py-2 rounded-lg hover:border-white/40"
          >
            Iniciar sesion
          </a>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-6 pt-12 pb-16 text-center">
        <p className="text-purple-400 font-medium mb-4 tracking-wide uppercase text-sm">
          Coaching + Inteligencia Artificial
        </p>
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
          Lidera con claridad.
          <br />
          <span className="text-purple-400">Comunica con impacto.</span>
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-10">
          14 prácticas de coaching asistidas por IA que transforman cómo
          delegas, priorizas, das feedback y tomas decisiones.
        </p>
        <a
          href="#planes"
          className="inline-block py-4 px-10 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl transition-all transform hover:scale-105 text-lg"
        >
          Ver planes
        </a>
      </section>

      {/* Cómo funciona */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-12">
          Empieza en 3 pasos
        </h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {pasos.map((p) => (
            <div key={p.num} className="text-center">
              <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">
                {p.num}
              </div>
              <h3 className="text-white font-semibold text-lg mb-2">
                {p.titulo}
              </h3>
              <p className="text-gray-400 text-sm">{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Beneficios */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-12">
          Por qué elegir YoCreo
        </h2>
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {beneficios.map((b, i) => (
            <div
              key={i}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10"
            >
              <h3 className="text-white font-semibold text-lg mb-2">
                {b.titulo}
              </h3>
              <p className="text-gray-400 text-sm leading-relaxed">{b.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Planes */}
      <section id="planes" className="container mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-4">
          Planes
        </h2>
        <p className="text-gray-400 text-center mb-8">
          Sin contratos. Cancela cuando quieras.
        </p>

        {/* Selector de plan */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => setSelectedPlan("individual")}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              selectedPlan === "individual"
                ? "bg-purple-600 text-white"
                : "bg-white/10 text-gray-300 hover:bg-white/20"
            }`}
          >
            Individual
          </button>
          <button
            onClick={() => setSelectedPlan("empresa")}
            className={`px-6 py-3 rounded-xl font-semibold transition-all ${
              selectedPlan === "empresa"
                ? "bg-purple-600 text-white"
                : "bg-white/10 text-gray-300 hover:bg-white/20"
            }`}
          >
            Empresa
          </button>
        </div>

        {/* Tarjetas de precio */}
        <div className="flex flex-col md:flex-row justify-center gap-6 max-w-4xl mx-auto">
          {/* Plan Individual */}
          <div
            className={`flex-1 bg-white/10 backdrop-blur-sm rounded-2xl p-8 transition-all cursor-pointer ${
              selectedPlan === "individual"
                ? "ring-2 ring-purple-500 scale-105"
                : "opacity-60 hover:opacity-80"
            }`}
            onClick={() => setSelectedPlan("individual")}
          >
            <h3 className="text-xl font-bold text-white mb-2">
              Plan Individual
            </h3>
            <p className="text-gray-400 text-sm mb-4">Para profesionales</p>
            <div className="flex items-baseline justify-center gap-2 mb-4">
              <span className="text-4xl font-bold text-white">$10.000</span>
              <span className="text-gray-400">/mes</span>
            </div>
            <ul className="text-left text-gray-300 space-y-2 mb-6">
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> 1 usuario
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> 14 practicas
                de coaching
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> IA ilimitada
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> Exportacion
                PDF + copiar
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> Manuales de
                cada practica
              </li>
            </ul>
            {selectedPlan === "individual" && (
              <button
                onClick={handleSubscribe}
                disabled={loading}
                className="w-full py-4 px-8 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white font-semibold rounded-xl transition-all transform hover:scale-105 disabled:scale-100"
              >
                {loading ? "Procesando..." : "Suscribirme Ahora"}
              </button>
            )}
          </div>

          {/* Plan Empresa */}
          <div
            className={`flex-1 bg-white/10 backdrop-blur-sm rounded-2xl p-8 transition-all cursor-pointer ${
              selectedPlan === "empresa"
                ? "ring-2 ring-purple-500 scale-105"
                : "opacity-60 hover:opacity-80"
            }`}
            onClick={() => setSelectedPlan("empresa")}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-xl font-bold text-white">Plan Empresa</h3>
              <span className="bg-purple-500 text-white text-xs px-2 py-1 rounded-full">
                Popular
              </span>
            </div>
            <p className="text-gray-400 text-sm mb-4">Para equipos</p>
            <div className="flex items-baseline justify-center gap-2 mb-4">
              <span className="text-4xl font-bold text-white">$10.000</span>
              <span className="text-gray-400">/mes por usuario</span>
            </div>
            <p className="text-purple-300 text-xs text-center mb-4">
              Empieza con 1 usuario. Agrega más desde el panel.
            </p>
            <ul className="text-left text-gray-300 space-y-2 mb-6">
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> Usuarios
                ilimitados
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> 14 practicas
                de coaching
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> IA ilimitada
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> Exportacion
                PDF + copiar
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">&#10003;</span> Manuales de
                cada practica
              </li>
              <li className="flex items-center gap-2">
                <span className="text-purple-400">&#9733;</span> Panel de
                Administracion
              </li>
              <li className="flex items-center gap-2">
                <span className="text-purple-400">&#9733;</span> Gestion de
                miembros
              </li>
            </ul>
            {selectedPlan === "empresa" && (
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Nombre de tu empresa"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  onClick={handleSubscribe}
                  disabled={loading}
                  className="w-full py-4 px-8 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white font-semibold rounded-xl transition-all transform hover:scale-105 disabled:scale-100"
                >
                  {loading ? "Procesando..." : "Suscribir Empresa"}
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Practicas */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-4">
          14 Practicas Incluidas
        </h2>
        <p className="text-gray-400 text-center mb-8">
          Cada una con manual descargable e inteligencia artificial
          especializada.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
          {practicas.map((h, i) => (
            <div
              key={i}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-4 flex items-start gap-4 hover:bg-white/10 transition-all"
            >
              <span className="text-3xl">{h.icono}</span>
              <div>
                <h4 className="text-white font-semibold">{h.nombre}</h4>
                <p className="text-gray-400 text-sm">{h.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-8">
          Preguntas Frecuentes
        </h2>
        <div className="max-w-2xl mx-auto space-y-3">
          {faqs.map((faq, i) => (
            <div
              key={i}
              className="bg-white/5 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenFaq(openFaq === i ? null : i)}
                className="w-full flex items-center justify-between p-5 text-left"
              >
                <span className="text-white font-medium">{faq.q}</span>
                <span className="text-gray-400 text-xl ml-4">
                  {openFaq === i ? "\u2212" : "+"}
                </span>
              </button>
              {openFaq === i && (
                <div className="px-5 pb-5">
                  <p className="text-gray-400 text-sm leading-relaxed">
                    {faq.a}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10">
        <div className="container mx-auto px-6 py-10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="YoCreo" className="h-8" />
              <span className="text-white font-semibold">YoCreo IA</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-400">
              <a href={APP_URL} className="hover:text-white transition-colors">
                Acceder a la app
              </a>
              <a href="#planes" className="hover:text-white transition-colors">
                Planes
              </a>
              <a
                href="mailto:contacto@yocreo.cl"
                className="hover:text-white transition-colors"
              >
                Contacto
              </a>
            </div>
          </div>
          <p className="text-center text-gray-500 text-xs mt-8">
            &copy; {new Date().getFullYear()} YoCreo IA. Todos los derechos
            reservados.
          </p>
        </div>
      </footer>
    </div>
  );
}

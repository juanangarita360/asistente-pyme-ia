import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

const API_URL = "http://127.0.0.1:5000/preguntar";

const SUGERENCIAS = [
  "¿Cuánto tiempo tengo para devolver una prenda?",
  "¿Cuáles son los 3 productos más vendidos?",
  "¿Hacen envíos gratis?",
];

export default function AsistenteBoutique() {
  const [mensajes, setMensajes] = useState([
    {
      autor: "asistente",
      texto:
        "Bienvenido/a. Soy el asistente de la tienda — pregúntame sobre políticas, envíos, o cifras de ventas y productos.",
    },
  ]);
  const [input, setInput] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const finRef = useRef(null);

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensajes, cargando]);

  async function enviarPregunta(pregunta) {
    const texto = pregunta.trim();
    if (!texto || cargando) return;

    setMensajes((prev) => [...prev, { autor: "usuario", texto }]);
    setInput("");
    setCargando(true);
    setError(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta: texto }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "No se pudo procesar la pregunta.");
      }

      setMensajes((prev) => [
        ...prev,
        { autor: "asistente", texto: data.respuesta },
      ]);
    } catch (err) {
      setError(
        "No se pudo conectar con el asistente. Verifica que el servidor Flask esté corriendo en " +
        API_URL
      );
    } finally {
      setCargando(false);
    }
  }

  function manejarEnvio(e) {
    e.preventDefault();
    enviarPregunta(input);
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#12201B",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "32px 16px",
        fontFamily: "'Inter', sans-serif",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,500&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        ::selection { background: #C79A56; color: #12201B; }
        .placeholder-ivory::placeholder { color: #F3EDE099; }
        
        /* Estilos específicos para formatear el Markdown renderizado */
        .markdown-content p {
          margin: 0 0 8px 0;
        }
        .markdown-content p:last-child {
          margin-bottom: 0;
        }
        .markdown-content strong {
          color: #C79A56; /* Resaltado dorado para palabras clave en negrita */
          font-weight: 600;
        }
        .markdown-content ul, .markdown-content ol {
          margin: 4px 0 8px 0;
          padding-left: 20px;
        }
        .markdown-content li {
          margin-bottom: 4px;
        }
        .markdown-content li:last-child {
          margin-bottom: 0;
        }

        /* Animación para los dots rebotando en el estado de carga */
        .dot {
          width: 4px;
          height: 4px;
          background-color: #C79A56;
          border-radius: 50%;
          display: inline-block;
          animation: bounce 1.4s infinite ease-in-out both;
        }

        @keyframes bounce {
          0%, 80%, 100% { 
            transform: scale(0);
            opacity: 0.3;
          } 
          40% { 
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>

      <div
        style={{
          width: "100%",
          maxWidth: 440,
          background: "#1B2E28",
          borderRadius: 4,
          border: "1px solid #2E453D",
          overflow: "hidden",
          boxShadow: "0 24px 60px rgba(0,0,0,0.35)",
        }}
      >
        <div
          style={{
            height: 14,
            background:
              "repeating-linear-gradient(90deg, transparent, transparent 8px, #12201B 8px, #12201B 8px)",
          }}
        />
        <div
          style={{
            height: 12,
            backgroundImage:
              "radial-gradient(circle at center, #12201B 3.2px, transparent 3.3px)",
            backgroundSize: "18px 12px",
          }}
        />

        <div
          style={{
            padding: "18px 24px 16px",
            borderBottom: "1px dashed #3E5B51",
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{
                fontFamily: "'Fraunces', serif",
                fontStyle: "italic",
                fontSize: 22,
                color: "#F3EDE0",
                letterSpacing: 0.2,
              }}
            >
              Atelier
            </div>
            <div
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 10,
                color: "#C79A56",
                letterSpacing: 1.5,
                textTransform: "uppercase",
                marginTop: 2,
              }}
            >
              Asistente virtual · Ref. 084
            </div>
          </div>
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: cargando ? "#C79A56" : "#7FA88F",
              flexShrink: 0,
            }}
            title={cargando ? "Procesando" : "Listo"}
          />
        </div>

        <div
          style={{
            padding: "20px 20px 8px",
            display: "flex",
            flexDirection: "column",
            gap: 14,
            maxHeight: 420,
            overflowY: "auto",
          }}
        >
          {mensajes.map((m, i) => (
            <div
              key={i}
              style={{
                alignSelf: m.autor === "usuario" ? "flex-end" : "flex-start",
                maxWidth: "85%",
              }}
            >
              <div
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 9,
                  letterSpacing: 1,
                  textTransform: "uppercase",
                  color: m.autor === "usuario" ? "#B5717A" : "#7FA88F",
                  marginBottom: 4,
                  textAlign: m.autor === "usuario" ? "right" : "left",
                }}
              >
                {m.autor === "usuario" ? "Tú" : "Atelier"}
              </div>
              <div
                style={{
                  background: m.autor === "usuario" ? "#3A2530" : "#22362F",
                  border:
                    m.autor === "usuario"
                      ? "1px solid #6B4652"
                      : "1px solid #3E5B51",
                  color: "#F3EDE0",
                  padding: "10px 14px",
                  borderRadius: 3,
                  fontSize: 14,
                  lineHeight: 1.5,
                }}
              >
                <div className="markdown-content">
                  <ReactMarkdown>{m.texto}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}

          {cargando && (
            <div style={{ alignSelf: "flex-start", maxWidth: "85%" }}>
              <div
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 9,
                  letterSpacing: 1,
                  textTransform: "uppercase",
                  color: "#7FA88F",
                  marginBottom: 4,
                }}
              >
                Atelier
              </div>
              <div
                style={{
                  background: "#22362F",
                  border: "1px solid #3E5B51",
                  color: "#F3EDE099",
                  padding: "12px 16px",
                  borderRadius: 3,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <span style={{ fontSize: 13, fontStyle: "italic", marginRight: 4 }}>
                  consultando el registro
                </span>
                <div style={{ display: "flex", gap: 3, alignItems: "center", marginTop: 4 }}>
                  <span className="dot" style={{ animationDelay: "0s" }} />
                  <span className="dot" style={{ animationDelay: "0.2s" }} />
                  <span className="dot" style={{ animationDelay: "0.4s" }} />
                </div>
              </div>
            </div>
          )}

          {error && (
            <div
              style={{
                background: "#3A2020",
                border: "1px solid #6B3535",
                color: "#F0B8B8",
                padding: "10px 14px",
                borderRadius: 3,
                fontSize: 13,
                lineHeight: 1.5,
              }}
            >
              {error}
            </div>
          )}
          <div ref={finRef} />
        </div>

        {mensajes.length === 1 && (
          <div
            style={{
              padding: "4px 20px 4px",
              display: "flex",
              flexWrap: "wrap",
              gap: 6,
            }}
          >
            {SUGERENCIAS.map((s) => (
              <button
                key={s}
                onClick={() => enviarPregunta(s)}
                style={{
                  background: "transparent",
                  border: "1px solid #3E5B51",
                  color: "#C79A56",
                  fontSize: 11,
                  padding: "6px 10px",
                  borderRadius: 3,
                  cursor: "pointer",
                  fontFamily: "'Inter', sans-serif",
                }}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        <form
          onSubmit={manejarEnvio}
          style={{
            display: "flex",
            gap: 8,
            padding: "16px 20px 22px",
            borderTop: "1px dashed #3E5B51",
            marginTop: 8,
          }}
        >
          <input
            className="placeholder-ivory"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta…"
            disabled={cargando}
            style={{
              flex: 1,
              background: "#12201B",
              border: "1px solid #3E5B51",
              borderRadius: 3,
              padding: "10px 12px",
              color: "#F3EDE0",
              fontSize: 14,
              fontFamily: "'Inter', sans-serif",
              outline: "none",
            }}
          />
          <button
            type="submit"
            disabled={cargando || !input.trim()}
            style={{
              background: "#C79A56",
              color: "#12201B",
              border: "none",
              borderRadius: 3,
              padding: "0 18px",
              fontSize: 13,
              fontWeight: 600,
              cursor: cargando ? "default" : "pointer",
              opacity: cargando || !input.trim() ? 0.6 : 1,
              fontFamily: "'Inter', sans-serif",
            }}
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}
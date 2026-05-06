// ============================================================
// dashboard.js — Carga datos del dashboard y renderiza el gráfico
// ============================================================

let chartInstance = null;

async function loadDashboard(tipo = "categoria") {

  const ctx = document.getElementById("myChart");
  if (!ctx) return;

  try {
    const res  = await fetch("/api/dashboard");
    const data = await res.json();

    // MÉTRICAS
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    setVal("dash-total",       data.total);
    setVal("dash-alertas",     data.alertas);
    setVal("dash-valor",       "S/ " + data.valor.toFixed(2));
    setVal("dash-vencimiento", data.vencimiento);

    // DATOS DEL GRÁFICO
    const labels = data[tipo].labels;
    const values = data[tipo].values;

    // DESTRUIR GRÁFICO ANTERIOR
    if (chartInstance) {
      chartInstance.destroy();
    }

    // CREAR NUEVO GRÁFICO
    chartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: tipo === "categoria"
            ? "Productos por categoría"
            : "Stock por producto",

          data: values,
          backgroundColor: "#111827",
          borderRadius: 8,
          borderSkipped: false,
          barPercentage: 0.70,
          categoryPercentage: 0.85,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#111827",
            titleColor: "#ffffff",
            bodyColor: "#9ca3af",
            padding: 10,
            cornerRadius: 6,
            callbacks: {
              label: (ctx) => {
                return tipo === "categoria"
                  ? ` ${ctx.parsed.y} productos`
                  : ` ${ctx.parsed.y} en stock`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            border: { display: false },
            ticks: {
              color: "#9ca3af",
              font: { family: "'Geist', sans-serif", size: 12 }
            }
          },
          y: {
            beginAtZero: true,
            grid: { color: "#f3f4f6" },
            border: { display: false },
            ticks: {
              color: "#9ca3af",
              font: { family: "'Geist', sans-serif", size: 12 },
              stepSize: 1
            }
          }
        }
      }
    });

  } catch (e) {
    console.error("Error al cargar el dashboard:", e);
  }
}


function loadDashboard2() {
  const buttons = document.querySelectorAll('.toggle-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadDashboard(btn.dataset.grafico);
    });
  });
  loadDashboard("categoria");
}

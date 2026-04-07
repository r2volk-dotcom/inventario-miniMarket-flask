document.addEventListener("DOMContentLoaded", function () {
  const modalRoot = document.getElementById("modal-root");
  const btnAddProduct = document.getElementById("btn-add-product");
  const btnAddEntry = document.getElementById("btn-add-entry");
  const btnRefresh = document.getElementById("btn-refresh");
  const searchInput = document.getElementById("search");
  const searchBtn = document.getElementById("search-btn");
  const btnAddOutput = document.getElementById("btn-add-output");
  const btnAddProvider = document.getElementById("btn-add-provider");
  if (btnAddProvider) btnAddProvider.addEventListener("click", openAddProvider);

  btnAddProduct.addEventListener("click", openAddProduct);
  btnAddEntry.addEventListener("click", openAddEntry);
  btnRefresh.addEventListener("click", () => location.reload());
  btnAddOutput.addEventListener("click", openAddOutput);
  searchBtn && searchBtn.addEventListener("click", applySearch);

  function applySearch() {
    const q = searchInput.value.trim().toLowerCase();
    const rows = document.querySelectorAll("#productos-table tbody tr");
    rows.forEach((r) => {
      const text = r.textContent.toLowerCase();
      r.style.display = text.indexOf(q) >= 0 ? "" : "none";
    });
    const visible = [...rows].filter((r) => r.style.display !== "none").length;
    document.getElementById("info-count").textContent = "Registros: " + visible;
  }

  function openAddProduct() {
    const html = `
      <div class="overlay"></div>
      <div class="modal">
        <h3>Registrar Producto (Minimarket)</h3>
        <div class="row"><label>Código *</label><input id="p-codigo"></div>
        <div class="row"><label>Nombre *</label><input id="p-nombre"></div>
        <div class="row"><label>Categoría</label>
            <select id="p-cat">
                <option value="Abarrotes">Abarrotes</option>
                <option value="Bebidas">Bebidas</option>
                <option value="Lácteos">Lácteos</option>
                <option value="Limpieza">Limpieza</option>
                <option value="Golosinas">Golosinas</option>
                <option value="Otros">Otros</option>
            </select>
        </div>
        <div class="row"><label>Precio Compra (S/)</label><input id="p-pcompra" type="number" step="0.10" value="0"></div>
        <div class="row"><label>Precio Venta (S/)</label><input id="p-pventa" type="number" step="0.10" value="0"></div>
        <div class="row"><label>Stock mín.</label><input id="p-stockmin" type="number" value="5"></div>
        <div class="row"><label>Descripción</label><input id="p-desc"></div>
        <div class="actions"><button id="p-save" class="btn primary">Guardar</button><button id="p-cancel" class="btn">Cancelar</button></div>
      </div>`;
    modalRoot.innerHTML = html;
    document
      .getElementById("p-cancel")
      .addEventListener("click", () => (modalRoot.innerHTML = ""));
    document.getElementById("p-save").addEventListener("click", async () => {
      const data = {
        codigo: document.getElementById("p-codigo").value,
        nombre: document.getElementById("p-nombre").value,
        categoria: document.getElementById("p-cat").value,
        precio_compra: document.getElementById("p-pcompra").value,
        precio_venta: document.getElementById("p-pventa").value,
        stock_min: document.getElementById("p-stockmin").value,
        descripcion: document.getElementById("p-desc").value,
      };
      const res = await fetch("/add_product", {
        method: "POST",
        body: new URLSearchParams(data),
      });
      if (res.ok) {
        alert("Producto registrado.");
        location.reload();
      } else {
        const j = await res.json().catch(() => ({ msg: "Error" }));
        alert("Error: " + (j.msg || "Error"));
      }
    });
  }

  function openAddProvider() {
    const html = `
      <div class="overlay"></div>
      <div class="modal">
        <h3>Registrar Proveedor</h3>
        <div class="row"><label>RUC/DNI *</label><input id="pr-ruc"></div>
        <div class="row"><label>Razón Social *</label><input id="pr-nombre"></div>
        <div class="row"><label>Teléfono</label><input id="pr-tel"></div>
        <div class="row"><label>Dirección</label><input id="pr-dir"></div>
        <div class="actions"><button id="pr-save" class="btn primary">Guardar</button><button id="pr-cancel" class="btn">Cancelar</button></div>
      </div>`;
    const modalRoot = document.getElementById("modal-root");
    modalRoot.innerHTML = html;
    document
      .getElementById("pr-cancel")
      .addEventListener("click", () => (modalRoot.innerHTML = ""));
    document.getElementById("pr-save").addEventListener("click", async () => {
      const data = {
        ruc: document.getElementById("pr-ruc").value,
        nombre: document.getElementById("pr-nombre").value,
        telefono: document.getElementById("pr-tel").value,
        direccion: document.getElementById("pr-dir").value,
      };
      const res = await fetch("/add_provider", {
        method: "POST",
        body: new URLSearchParams(data),
      });
      if (res.ok) {
        alert("Proveedor registrado.");
        modalRoot.innerHTML = ""; // Cerramos modal sin recargar para seguir trabajando
      } else {
        const j = await res.json().catch(() => ({ msg: "Error" }));
        alert("Error: " + (j.msg || "Error"));
      }
    });
  }

  function openAddEntry() {
    Promise.all([
      fetch("/api/products").then((r) => r.json()),
      fetch("/api/providers").then((r) => r.json()),
    ]).then(([products, providers]) => {
      const prodOptions = products
        .map(
          (p) => `<option value="${p.id}">${p.codigo} - ${p.nombre}</option>`
        )
        .join("");
      const provOptions = providers
        .map(
          (p) => `<option value="${p.id}">${p.nombre} (RUC: ${p.ruc})</option>`
        )
        .join("");

      const html = `
        <div class="overlay"></div>
        <div class="modal">
          <h3>Registrar Entrada (Compra)</h3>
          <div class="row"><label>Producto *</label><select id="e-product">${prodOptions}</select></div>
          <div class="row"><label>Proveedor *</label><select id="e-provider">${provOptions}</select></div>
          <div class="row"><label>Cantidad *</label><input id="e-cant" type="number" value="1" min="1"></div>
          <div class="row"><label>Vencimiento</label><input id="e-venc" type="date"></div>
          
          <div class="row"><label>Responsable</label><input id="e-user" value="Almacenero"></div>
          <div class="row"><label>Motivo</label><input id="e-mot" value="Reposición de Stock"></div>
          <div class="actions"><button id="e-save" class="btn success">Confirmar Ingreso</button><button id="e-cancel" class="btn">Cancelar</button></div>
        </div>`;

      const modalRoot = document.getElementById("modal-root");
      modalRoot.innerHTML = html;
      document
        .getElementById("e-cancel")
        .addEventListener("click", () => (modalRoot.innerHTML = ""));
      document.getElementById("e-save").addEventListener("click", async () => {
        const data = {
          producto_id: document.getElementById("e-product").value,
          proveedor_id: document.getElementById("e-provider").value,
          cantidad: document.getElementById("e-cant").value,
          vencimiento: document.getElementById("e-venc").value, // Enviamos fecha
          usuario: document.getElementById("e-user").value,
          motivo: document.getElementById("e-mot").value,
        };
        const res = await fetch("/add_entry", {
          method: "POST",
          body: new URLSearchParams(data),
        });
        if (res.ok) {
          alert("Entrada registrada.");
          location.reload();
        } else {
          alert("Error al registrar.");
        }
      });
    });
  }

  function openAddOutput() {
    fetch("/api/products")
      .then((r) => r.json())
      .then((products) => {
        // Filtramos solo productos con stock > 0 para vender
        const options = products
          .map(
            (p) =>
              `<option value="${p.id}">${p.nombre} (Stock: ${p.stock})</option>`
          )
          .join("");

        const html = `
        <div class="overlay"></div>
        <div class="modal">
          <h3>Registrar Salida (Venta)</h3>
          <div class="row"><label>Producto *</label><select id="s-product">${options}</select></div>
          <div class="row"><label>Cantidad *</label><input id="s-cant" type="number" value="1" min="1"></div>
          <div class="row"><label>Vendedor</label><input id="s-user" value="Cajero 1"></div>
          <div class="row"><label>Motivo</label>
            <select id="s-mot">
                <option value="Venta al público">Venta al público</option>
                <option value="Consumo interno">Consumo interno</option>
                <option value="Merma/Vencido">Merma/Vencido</option>
                <option value="Devolución">Devolución a Proveedor</option>
            </select>
          </div>
          <div class="actions"><button id="s-save" class="btn primary">Confirmar Salida</button><button id="s-cancel" class="btn">Cancelar</button></div>
        </div>`;
        modalRoot.innerHTML = html;

        document
          .getElementById("s-cancel")
          .addEventListener("click", () => (modalRoot.innerHTML = ""));
        document
          .getElementById("s-save")
          .addEventListener("click", async () => {
            const data = {
              producto_id: document.getElementById("s-product").value,
              cantidad: document.getElementById("s-cant").value,
              usuario: document.getElementById("s-user").value,
              motivo: document.getElementById("s-mot").value,
            };
            const res = await fetch("/add_output", {
              method: "POST",
              body: new URLSearchParams(data),
            });
            if (res.ok) {
              alert("Salida registrada. Stock actualizado.");
              location.reload();
            } else {
              const j = await res.json().catch(() => ({ msg: "Error" }));
              alert("Error: " + (j.msg || "Error"));
            }
          });
      });
  }

  // --- FUNCIÓN DASHBOARD (NUEVO) ---
  loadDashboard();

  async function loadDashboard() {
    const ctx = document.getElementById("myChart");
    if (!ctx) return;
    try {
      const res = await fetch("/api/dashboard");
      const data = await res.json();

      document.getElementById("dash-total").textContent = data.total;
      document.getElementById("dash-alertas").textContent = data.alertas;
      document.getElementById("dash-valor").textContent = data.valor.toFixed(2);
      // Actualizamos el nuevo dato
      if (document.getElementById("dash-vencimiento")) {
        document.getElementById("dash-vencimiento").textContent =
          data.vencimiento;
      }

      new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.chart_labels,
          datasets: [
            {
              label: "Productos por Categoría",
              data: data.chart_values,
              backgroundColor: "rgba(43, 124, 255, 0.6)",
              borderColor: "rgba(43, 124, 255, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } },
        },
      });
    } catch (e) {
      console.error(e);
    }
  }
});

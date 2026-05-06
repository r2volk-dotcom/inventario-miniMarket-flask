
// Punto de entrada del frontend
// Este archivo espera que el HTML cargue y luego conectar cada botón con su función
document.addEventListener("DOMContentLoaded", function () {
  // DOMContentLoaded se carga cuando el navegador terminó de leer y construir el HTML
  // Si no usáramos esto, getElementById podría devolver null (el elemento aún no existe)

  // Guardamos cada botón en una variable para asignarle eventos despues
  const btnAddProduct  = document.getElementById("btn-add-product");
  const btnAddEntry    = document.getElementById("btn-add-entry");
  const btnAddOutput   = document.getElementById("btn-add-output");
  const btnAddProvider = document.getElementById("btn-add-provider");
  const btnRefresh     = document.getElementById("btn-refresh");
  const searchInput    = document.getElementById("search");
  const searchBtn      = document.getElementById("search-btn");


  // --- ASIGNAR EVENTOS ---
  // Se usa "&&" para ejecutar el evento solo si el elemento existe.
  // Si el elemento es null o undefined, no se ejecuta nada y evita errores.
  //llamamos a la funciones que estan definidas en modales/..
  btnAddProduct  && btnAddProduct.addEventListener("click", openAddProduct);
  btnAddEntry    && btnAddEntry.addEventListener("click", openAddEntry);
  btnAddOutput   && btnAddOutput.addEventListener("click", openAddOutput);
  btnAddProvider && btnAddProvider.addEventListener("click", openAddProvider);
  // () => location.reload() → function que recarga la página completa
  btnRefresh     && btnRefresh.addEventListener("click", () => location.reload());

  // applySearch está definida aquí abajo (es específica de main.js)
  searchBtn      && searchBtn.addEventListener("click", applySearch);


  // Filtra las filas de la tabla de productos según el texto ingresado
  function applySearch() {

    const q = searchInput.value.trim().toLowerCase();
    // .trim() elimina espacios al inicio y al final
    // .toLowerCase() convierte el texto a minúsculas para comparar sin importar mayúsculas

    const rows = document.querySelectorAll("#productos-table tbody tr");
    // Selecciona todas las filas <tr> dentro del <tbody> de la tabla con id "productos-table"

    rows.forEach((r) => {
      // Recorre cada fila

      r.style.display = r.textContent.toLowerCase().indexOf(q) >= 0 ? "" : "none";
      // Convierte el texto a minúsculas y busca q
      // Si lo encuentra → se muestra, Si no → se oculta
    });

    const visible = [...rows].filter((r) => r.style.display !== "none").length;
    // [...rows] convierte a array, .filter(...) revisa cada fila, r.style.display !== "none" deja solo visibles, .length cuenta el total

    const el = document.getElementById("info-count");
    // document.getElementById busca un elemento por su id y lo guarda en "el"

    if (el) {
      el.textContent = visible + " productos encontrados";
    }
    // Si el elemento existe, entra al bloque y cambia su texto por la cantidad encontrada
  }

  //carga el dashboard
  loadDashboard2();
});


//linea 110

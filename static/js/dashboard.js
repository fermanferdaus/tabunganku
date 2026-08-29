/**
 * Dashboard JS — realtime update cards, chart, paginated riwayat tables, ambil uang actions.
 * Native fetch(), no jQuery dependency.
 */

const fmt = (v) => "Rp " + Number(v).toLocaleString("id-ID");

// --- Cards ---
function updateCards() {
  fetch("/api/uang_masuk_harian")
    .then((r) => r.json())
    .then((d) => {
      if (d.success) {
        document.getElementById("total-uang-masuk").textContent = fmt(
          d.data.total_uang_masuk,
        );
      }
    })
    .catch(() => {});

  fetch("/api/uang_masuk_bulanan")
    .then((r) => r.json())
    .then((d) => {
      if (d.success) {
        document.getElementById("total-uang-masuk-bulanan").textContent = fmt(
          d.data.total_uang_masuk_bulanan,
        );
      }
    })
    .catch(() => {});

  fetch("/api/total_tabungan")
    .then((r) => r.json())
    .then((d) => {
      if (d.success) {
        document.getElementById("total-uang-masuk-seluruh").textContent = fmt(
          d.data.total_uang_masuk_seluruh,
        );
      }
    })
    .catch(() => {});
}

// --- Chart ---
let chartInstance = null;

function updateChart() {
  fetch("/api/chart_data")
    .then((r) => r.json())
    .then((d) => {
      if (!d.success) return;
      const ctx = document.getElementById("grafik");
      if (!ctx) return;

      if (chartInstance) {
        chartInstance.data.labels = d.data.labels || [];
        chartInstance.data.datasets[0].data = d.data.data || [];
        chartInstance.update();
        return;
      }

      chartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: d.data.labels || [],
          datasets: [
            {
              label: "Uang Masuk",
              tension: 0.3,
              backgroundColor: "rgba(37, 99, 235, 0.08)",
              borderColor: "#2563eb",
              borderWidth: 2,
              pointRadius: 4,
              pointBackgroundColor: "#2563eb",
              fill: true,
              data: d.data.data || [],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              ticks: {
                callback: (v) => fmt(v),
              },
              grid: { color: "#f3f4f6" },
            },
            x: {
              grid: { display: false },
            },
          },
        },
      });
    })
    .catch(() => {});
}

// --- Pagination State ---
let dataMasuk = [];
let currentPageMasuk = 1;
let pageSizeMasuk = 10;

let dataKeluar = [];
let currentPageKeluar = 1;
let pageSizeKeluar = 10;

// --- Render Helper for Pagination Buttons ---
function buildPaginationButtons(currentPage, totalPages, onPageClickFnName) {
  if (totalPages <= 1) return "";

  let html = "";

  // Prev button
  const prevDisabled = currentPage === 1;
  html += `
        <button onclick="${prevDisabled ? "" : `${onPageClickFnName}(${currentPage - 1})`}"
            class="px-2.5 py-1 text-xs font-medium rounded border ${
              prevDisabled
                ? "text-gray-300 border-gray-200 cursor-not-allowed"
                : "text-gray-700 border-gray-300 hover:bg-gray-50"
            }">
            &larr; Prev
        </button>
    `;

  // Page numbers with ellipsis
  const maxButtons = 5;
  let startPage = Math.max(1, currentPage - 2);
  let endPage = Math.min(totalPages, startPage + maxButtons - 1);

  if (endPage - startPage < maxButtons - 1) {
    startPage = Math.max(1, endPage - maxButtons + 1);
  }

  if (startPage > 1) {
    html += `<button onclick="${onPageClickFnName}(1)" class="px-2.5 py-1 text-xs font-medium rounded border text-gray-700 border-gray-300 hover:bg-gray-50">1</button>`;
    if (startPage > 2) {
      html += `<span class="px-1 text-xs text-gray-400">...</span>`;
    }
  }

  for (let p = startPage; p <= endPage; p++) {
    const isActive = p === currentPage;
    html += `
            <button onclick="${onPageClickFnName}(${p})"
                class="px-2.5 py-1 text-xs font-medium rounded border ${
                  isActive
                    ? "bg-primary-600 text-white border-primary-600 font-semibold"
                    : "text-gray-700 border-gray-300 hover:bg-gray-50"
                }">
                ${p}
            </button>
        `;
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      html += `<span class="px-1 text-xs text-gray-400">...</span>`;
    }
    html += `<button onclick="${onPageClickFnName}(${totalPages})" class="px-2.5 py-1 text-xs font-medium rounded border text-gray-700 border-gray-300 hover:bg-gray-50">${totalPages}</button>`;
  }

  // Next button
  const nextDisabled = currentPage === totalPages;
  html += `
        <button onclick="${nextDisabled ? "" : `${onPageClickFnName}(${currentPage + 1})`}"
            class="px-2.5 py-1 text-xs font-medium rounded border ${
              nextDisabled
                ? "text-gray-300 border-gray-200 cursor-not-allowed"
                : "text-gray-700 border-gray-300 hover:bg-gray-50"
            }">
            Next &rarr;
        </button>
    `;

  return html;
}

// --- Render Table Uang Masuk ---
function renderTableMasuk() {
  const tbody = document.getElementById("data-uang-masuk");
  const info = document.getElementById("info-uang-masuk");
  const pagination = document.getElementById("pagination-uang-masuk");
  if (!tbody) return;

  const total = dataMasuk.length;
  if (total === 0) {
    tbody.innerHTML =
      '<tr><td colspan="4" class="px-5 py-8 text-center text-gray-400">Belum ada data</td></tr>';
    if (info) info.textContent = "Menampilkan 0 sampai 0 dari 0 data";
    if (pagination) pagination.innerHTML = "";
    return;
  }

  const totalPages = Math.ceil(total / pageSizeMasuk);
  if (currentPageMasuk > totalPages) currentPageMasuk = totalPages;
  if (currentPageMasuk < 1) currentPageMasuk = 1;

  const startIndex = (currentPageMasuk - 1) * pageSizeMasuk;
  const endIndex = Math.min(startIndex + pageSizeMasuk, total);
  const pageItems = dataMasuk.slice(startIndex, endIndex);

  tbody.innerHTML = pageItems
    .map(
      (item, i) => `
        <tr class="hover:bg-gray-50">
            <td class="px-5 py-3 text-gray-600">${startIndex + i + 1}</td>
            <td class="px-5 py-3 text-gray-800">${item.tanggal}</td>
            <td class="px-5 py-3 text-gray-600">${item.waktu}</td>
            <td class="px-5 py-3 text-right font-medium text-emerald-600">+ ${fmt(item.uang_masuk)}</td>
        </tr>
    `,
    )
    .join("");

  if (info) {
    info.textContent = `Menampilkan ${startIndex + 1} sampai ${endIndex} dari ${total} data`;
  }

  if (pagination) {
    pagination.innerHTML = buildPaginationButtons(
      currentPageMasuk,
      totalPages,
      "goToPageMasuk",
    );
  }
}

function goToPageMasuk(page) {
  currentPageMasuk = page;
  renderTableMasuk();
}

function changePageSizeMasuk(size) {
  pageSizeMasuk = parseInt(size) || 10;
  currentPageMasuk = 1;
  renderTableMasuk();
}

function updateRiwayatMasuk() {
  fetch("/api/ambil_uang_masuk")
    .then((r) => r.json())
    .then((d) => {
      if (!d.success) return;
      dataMasuk = d.data || [];
      renderTableMasuk();
    })
    .catch(() => {});
}

// --- Render Table Uang Keluar ---
function renderTableKeluar() {
  const tbody = document.getElementById("data-uang-keluar");
  const info = document.getElementById("info-uang-keluar");
  const pagination = document.getElementById("pagination-uang-keluar");
  if (!tbody) return;

  const total = dataKeluar.length;
  if (total === 0) {
    tbody.innerHTML =
      '<tr><td colspan="4" class="px-5 py-8 text-center text-gray-400">Belum ada data</td></tr>';
    if (info) info.textContent = "Menampilkan 0 sampai 0 dari 0 data";
    if (pagination) pagination.innerHTML = "";
    return;
  }

  const totalPages = Math.ceil(total / pageSizeKeluar);
  if (currentPageKeluar > totalPages) currentPageKeluar = totalPages;
  if (currentPageKeluar < 1) currentPageKeluar = 1;

  const startIndex = (currentPageKeluar - 1) * pageSizeKeluar;
  const endIndex = Math.min(startIndex + pageSizeKeluar, total);
  const pageItems = dataKeluar.slice(startIndex, endIndex);

  tbody.innerHTML = pageItems
    .map(
      (item, i) => `
        <tr class="hover:bg-gray-50">
            <td class="px-5 py-3 text-gray-600">${startIndex + i + 1}</td>
            <td class="px-5 py-3 text-gray-800">${item.tanggal}</td>
            <td class="px-5 py-3 text-gray-600">${item.waktu}</td>
            <td class="px-5 py-3 text-right font-medium text-red-500">- ${fmt(item.uang_keluar)}</td>
        </tr>
    `,
    )
    .join("");

  if (info) {
    info.textContent = `Menampilkan ${startIndex + 1} sampai ${endIndex} dari ${total} data`;
  }

  if (pagination) {
    pagination.innerHTML = buildPaginationButtons(
      currentPageKeluar,
      totalPages,
      "goToPageKeluar",
    );
  }
}

function goToPageKeluar(page) {
  currentPageKeluar = page;
  renderTableKeluar();
}

function changePageSizeKeluar(size) {
  pageSizeKeluar = parseInt(size) || 10;
  currentPageKeluar = 1;
  renderTableKeluar();
}

function updateRiwayatKeluar() {
  fetch("/api/ambil_uang_keluar")
    .then((r) => r.json())
    .then((d) => {
      if (!d.success) return;
      dataKeluar = d.data || [];
      renderTableKeluar();
    })
    .catch(() => {});
}

// --- Auto Format Rupiah Input ---
function initRupiahInput() {
  const input = document.getElementById("inputQuantity");
  if (!input) return;

  input.addEventListener("input", function () {
    const raw = this.value.replace(/[^0-9]/g, "");
    if (!raw) {
      this.value = "";
      return;
    }
    this.value = fmt(raw);
  });
}

// --- Ambil Uang Actions ---
function confirmSubmit() {
  const raw = (document.getElementById("inputQuantity").value || "").replace(
    /[^0-9]/g,
    "",
  );
  const qty = parseInt(raw, 10);
  if (!qty || qty <= 0) {
    Swal.fire({
      icon: "warning",
      title: "Jumlah Tidak Valid",
      text: "Masukkan jumlah yang lebih besar dari 0.",
      confirmButtonColor: "#2563eb",
    });
    return;
  }

  Swal.fire({
    icon: "question",
    title: "Konfirmasi",
    text: `Ambil uang sebesar ${fmt(qty)}?`,
    showCancelButton: true,
    confirmButtonColor: "#2563eb",
    cancelButtonColor: "#6b7280",
    confirmButtonText: "Ya, Ambil",
    cancelButtonText: "Batal",
  }).then((result) => {
    if (!result.isConfirmed) return;

    fetch("/api/proses_pengurangan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jumlah: qty }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.success) {
          Swal.fire({
            icon: "success",
            title: "Berhasil",
            text: "Tabungan telah dikurangi.",
            confirmButtonColor: "#2563eb",
            timer: 2000,
            timerProgressBar: true,
          });
          document.getElementById("inputQuantity").value = "";
          updateAll();
        } else {
          Swal.fire({
            icon: "error",
            title: "Gagal",
            text: d.message,
            confirmButtonColor: "#2563eb",
          });
        }
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Gagal menghubungi server.",
          confirmButtonColor: "#2563eb",
        });
      });
  });
}

function confirmWithdraw() {
  Swal.fire({
    icon: "warning",
    title: "Ambil Seluruh Uang?",
    text: "Semua data tabungan akan dihapus. Tindakan ini tidak bisa dibatalkan.",
    showCancelButton: true,
    confirmButtonColor: "#ef4444",
    cancelButtonColor: "#6b7280",
    confirmButtonText: "Ya, Ambil Semua",
    cancelButtonText: "Batal",
  }).then((result) => {
    if (!result.isConfirmed) return;

    fetch("/api/ambil_semua_tabungan", { method: "POST" })
      .then((r) => r.json())
      .then((d) => {
        if (d.success) {
          Swal.fire({
            icon: "success",
            title: "Seluruh Tabungan Diambil",
            text: "Data tabungan telah dihapus.",
            confirmButtonColor: "#2563eb",
            timer: 2000,
            timerProgressBar: true,
          });
          updateAll();
        } else {
          Swal.fire({
            icon: "error",
            title: "Gagal",
            text: d.message,
            confirmButtonColor: "#2563eb",
          });
        }
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Gagal menghubungi server.",
          confirmButtonColor: "#2563eb",
        });
      });
  });
}

// --- Update All ---
function updateAll() {
  updateCards();
  updateChart();
  updateRiwayatMasuk();
  updateRiwayatKeluar();
}

// Init
initRupiahInput();
updateAll();
setInterval(updateAll, 5000);

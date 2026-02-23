(function () {
  const search = document.getElementById("patient-search");
  const tableBody = document.querySelector("#patient-table tbody");
  if (!search || !tableBody) return;

  let timer = null;
  search.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(async function () {
      const q = search.value.trim();
      if (!q) {
        window.location.reload();
        return;
      }
      const res = await fetch("/admin/patients/search?q=" + encodeURIComponent(q));
      const rows = await res.json();
      tableBody.innerHTML = "";
      if (!rows.length) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-muted">No matches found.</td></tr>';
        return;
      }

      rows.forEach(function (p) {
        const tr = document.createElement("tr");
        tr.innerHTML =
          '<td class="mono">' + p.patient_code + "</td>" +
          "<td>" + p.name + "</td>" +
          "<td>" + (p.blood_group || "-") + "</td>" +
          "<td>" + p.phone + "</td>" +
          '<td><a class="btn btn-ghost" href="/admin/patients/' + p.patient_id + '">View</a></td>';
        tableBody.appendChild(tr);
      });
    }, 280);
  });
})();

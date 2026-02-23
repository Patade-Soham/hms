(function () {
  const doctorInput = document.getElementById("doctor_id");
  const dateInput = document.getElementById("appt_date");
  const slotGrid = document.getElementById("slot-grid");
  const slotInput = document.getElementById("appt_time");
  if (!doctorInput || !dateInput || !slotGrid || !slotInput) return;

  async function loadSlots() {
    if (!doctorInput.value || !dateInput.value) return;
    const payload = new URLSearchParams();
    payload.set("doctor_id", doctorInput.value);
    payload.set("appt_date", dateInput.value);
    const res = await fetch("/appointments/book/slots", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: payload.toString(),
    });
    const data = await res.json();
    renderSlots(data.slots || []);
  }

  function renderSlots(slots) {
    slotGrid.innerHTML = "";
    slotInput.value = "";
    if (!slots.length) {
      const empty = document.createElement("div");
      empty.className = "text-muted";
      empty.textContent = "No slots available for selected date.";
      slotGrid.appendChild(empty);
      return;
    }
    slots.forEach(function (slot) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "slot-btn";
      btn.textContent = slot.slice(0, 5);
      btn.addEventListener("click", function () {
        slotGrid.querySelectorAll(".slot-btn").forEach(function (node) {
          node.classList.remove("active");
        });
        btn.classList.add("active");
        slotInput.value = slot;
      });
      slotGrid.appendChild(btn);
    });
  }

  doctorInput.addEventListener("change", loadSlots);
  dateInput.addEventListener("change", loadSlots);
})();

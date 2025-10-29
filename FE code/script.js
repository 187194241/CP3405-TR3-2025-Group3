// script.js - SmartSeat interaction logic

// simple router helper (multi-page files use window.location.href)
function go(page){
  window.location.href = page;
}

/* ---------- seat data (demo) ---------- */
/* seat maps keyed by venue id; single: rows x cols grid; group: tables */
const SEAT_MAPS = {
  "LT1_single": {
    type: "single",
    rows: 8,
    cols: 12,
    taken: ["A3","B5","C6","D2","F10"]
  },
  "CampusHall_group": {
    type: "group",
    tables: [
      { id: "T1", seats: 4, taken: false },
      { id: "T2", seats: 6, taken: true  },
      { id: "T3", seats: 5, taken: false },
      { id: "T4", seats: 4, taken: false }
    ]
  }
};

/* ---------- utils ---------- */
function $(s){ return document.querySelector(s) }
function $all(s){ return Array.from(document.querySelectorAll(s)) }

function idToSeat(r,c){
  // convert row 0-> 'A', etc.
  return String.fromCharCode(65 + r) + (c+1);
}

/* ---------- SINGLE seat render ---------- */
function renderSingle(containerId, mapKey){
  const container = document.getElementById(containerId);
  if(!container) return;
  const map = SEAT_MAPS[mapKey];
  container.innerHTML = "";
  const grid = document.createElement("div");
  grid.className = "seat-grid";
  for(let r=0;r<map.rows;r++){
    for(let c=0;c<map.cols;c++){
      const sid = idToSeat(r,c);
      const seat = document.createElement("div");
      seat.className = "seat small";
      seat.id = "seat-"+sid;
      seat.textContent = sid;
      if(map.taken.includes(sid)) { seat.classList.add("taken"); seat.title = "Occupied" }
      else { seat.classList.add("available"); seat.onclick = ()=> selectSingleSeat(sid, seat); }
      grid.appendChild(seat);
    }
  }
  container.appendChild(grid);
}

/* ---------- GROUP tables render ---------- */
function renderGroup(containerId, mapKey){
  const container = document.getElementById(containerId);
  if(!container) return;
  const map = SEAT_MAPS[mapKey];
  container.innerHTML = "";
  const layout = document.createElement("div"); layout.className = "table-layout";
  map.tables.forEach(t=>{
    const el = document.createElement("div");
    el.className = "table";
    el.id = "table-"+t.id;
    if(t.taken) el.classList.add("taken");
    el.innerHTML = `<div class="title">${t.id}</div><div class="small">${t.seats} seats</div>`;
    el.onclick = ()=> selectTable(t.id, el, t.taken);
    layout.appendChild(el);
  });
  container.appendChild(layout);
}

/* selection handlers */
function selectSingleSeat(seatId, domEl){
  if(!domEl || domEl.classList.contains("taken")) return;
  // clear prev
  $all(".seat.selected").forEach(s=>s.classList.remove("selected"));
  domEl.classList.add("selected");
  // store selection
  localStorage.setItem("selectedSeat", seatId);
  // update side panel if exists
  const info = $("#selected-info");
  if(info) info.innerHTML = `<h3>Selected ${seatId}</h3><p class="small">Single seat. Click Confirm to continue.</p><div class="meta-row"><span>Accessibility</span><strong>No</strong></div>`;
}

function selectTable(tableId, domEl, taken){
  if(taken) { alert("Table is full"); return; }
  $all(".table.selected").forEach(t=>t.classList.remove("selected"));
  domEl.classList.add("selected");
  localStorage.setItem("selectedTable", tableId);
  const info = $("#selected-info");
  if(info) info.innerHTML = `<h3>Selected ${tableId}</h3><p class="small">Group table. Seats: see details. Click Confirm to continue.</p>`;
}

/* confirm handlers to navigate with chosen seat */
function confirmSingle(){
  const s = localStorage.getItem("selectedSeat");
  if(!s){ alert("Please select a seat first"); return; }
  // pass selection to detail page
  localStorage.setItem("lastReserved", JSON.stringify({type:"single", id:s, code:genCode()}));
  go("seatdetail.html");
}
function confirmTable(){
  const t = localStorage.getItem("selectedTable");
  if(!t){ alert("Please select a table first"); return; }
  localStorage.setItem("lastReserved", JSON.stringify({type:"group", id:t, code:genCode()}));
  go("seatdetail.html");
}

function genCode(){
  return Math.random().toString(36).substring(2,8).toUpperCase();
}

/* seat detail page loader */
function loadSeatDetail(){
  const raw = localStorage.getItem("lastReserved");
  if(!raw) return;
  const data = JSON.parse(raw);
  const el = $("#detail-card");
  if(!el) return;
  el.innerHTML = `<h2>${data.type === "single" ? 'Seat ' + data.id : 'Table ' + data.id}</h2>
    <p class="small">Reservation code: <strong>${data.code}</strong></p>
    <p class="small">Please check in within 10 minutes to secure your booking.</p>
    <div style="margin-top:12px"><button class="btn-primary" onclick="finalizeReservation()">Confirm & Generate QR</button>
    <button style="margin-left:10px" onclick="go('seatmap-single.html')">Back</button></div>`;
}

/* finalize reservation (fake) */
function finalizeReservation(){
  // push to history
  const raw = localStorage.getItem("lastReserved");
  if(!raw) return;
  const hist = JSON.parse(localStorage.getItem("reserveHistory") || "[]");
  hist.unshift(JSON.parse(raw));
  localStorage.setItem("reserveHistory", JSON.stringify(hist.slice(0,10)));
  go("confirmation.html");
}

/* confirmation page */
function loadConfirmation(){
  const raw = localStorage.getItem("lastReserved");
  if(!raw) return;
  const data = JSON.parse(raw);
  const el = $("#confirm-card");
  if(!el) return;
  el.innerHTML = `<h2>Success!</h2>
    <p class="small">${ data.type === "single" ? 'Seat ' + data.id : 'Table ' + data.id } reserved.</p>
    <p class="small">Code: <strong>${data.code}</strong></p>
    <div class="img-placeholder" style="height:180px;margin-top:12px">[QR CODE PLACEHOLDER]</div>
    <div style="margin-top:12px"><button onclick="go('home.html')">Return Home</button>
    <button class="green" onclick="go('profile.html')">View My Reservations</button></div>`;
}

/* profile page */
function loadProfile(){
  const raw = localStorage.getItem("reserveHistory");
  const list = raw ? JSON.parse(raw) : [];
  const el = $("#history-list");
  if(!el) return;
  el.innerHTML = "";
  if(list.length===0){ el.innerHTML = "<p class='small'>No reservations yet.</p>"; return; }
  list.forEach(item=>{
    const node = document.createElement("div");
    node.className = "card small";
    node.style.marginBottom = "8px";
    node.innerHTML = `<strong>${item.type === 'single' ? 'Seat ' + item.id : 'Table ' + item.id}</strong><div class="small">Code: ${item.code}</div>`;
    el.appendChild(node);
  });
}

/* init hooks based on page */
document.addEventListener("DOMContentLoaded", function(){
  // attempt to render seatmaps if containers exist
  if(document.getElementById("single-map")) renderSingle("single-map","LT1_single");
  if(document.getElementById("group-map")) renderGroup("group-map","CampusHall_group");
  if(document.getElementById("selected-info")) {
    const cur = localStorage.getItem("selectedSeat") || localStorage.getItem("selectedTable");
    if(!cur) $("#selected-info").innerHTML = "<p class='small'>No selection yet</p>";
  }
  if(document.getElementById("detail-card")) loadSeatDetail();
  if(document.getElementById("confirm-card")) loadConfirmation();
  if(document.getElementById("history-list")) loadProfile();
});

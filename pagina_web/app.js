/* ============================================================================
   UNViMe — Análisis y Diseño de Algoritmos | Examen 2 - Lógica Interactiva
   Consume window.EXAMEN2_DATA (datos_examen.js) — 100% offline sin servidor
   ============================================================================ */

(function () {
  "use strict";

  const DATA = window.EXAMEN2_DATA;
  if (!DATA) {
    alert("Error: no se encontró datos_examen.js junto a index.html.");
    return;
  }

  const fmt = (n) => (typeof n === "number" ? n.toLocaleString("es-AR") : String(n));

  /* ==========================================================================
     NAVEGACIÓN ENTRE SECCIONES
     ========================================================================== */
  function activarSeccion(secId) {
    document.querySelectorAll(".section-view").forEach((s) => {
      s.classList.toggle("active", s.id === secId);
    });
    document.querySelectorAll(".nav-btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.target === secId);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => activarSeccion(btn.dataset.target));
  });

  document.querySelectorAll("[data-jump]").forEach((el) => {
    el.addEventListener("click", () => activarSeccion(el.dataset.jump));
  });

  /* ==========================================================================
     SECCIÓN 1: PUNTO 1 — LEVENSHTEIN INTERACTIVO
     ========================================================================== */
  let p1Modo = "normalizado";
  let p1PalabraIdx = 0;

  function normalizarCharJS(ch, ignorarTildes) {
    const low = ch.toLowerCase();
    if (!ignorarTildes || low === "ñ") return low;
    return low.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function renderPunto1() {
    const lista = DATA.punto1.modos[p1Modo];
    const umbral = DATA.punto1.umbral;
    const ignorar = p1Modo === "normalizado";

    document.getElementById("p1-modo-norm").classList.toggle("active", ignorar);
    document.getElementById("p1-modo-exact").classList.toggle("active", !ignorar);

    // 1. Tabla A (todas las distancias)
    const tbody = document.getElementById("p1-tabla-distancias");
    tbody.innerHTML = "";
    lista.forEach((item, idx) => {
      const pasa = item.distancia <= umbral;
      const eds = item.operaciones.filter((o) => o.tipo !== "SIN_CAMBIO");
      const nSub = eds.filter((o) => o.tipo === "SUSTITUCION").length;
      const nIns = eds.filter((o) => o.tipo === "INSERCION").length;
      const nDel = eds.filter((o) => o.tipo === "ELIMINACION").length;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono">${idx + 1}</td>
        <td class="mono" style="color:#fff;font-weight:700;">${item.destino}</td>
        <td class="mono">${item.destino.length}</td>
        <td class="mono ${pasa ? "text-green" : "text-rose"}">${item.distancia}</td>
        <td><span class="pill ${pasa ? "green" : "rose"}">${pasa ? "SÍ (≤ 3)" : "NO (> 3)"}</span></td>
        <td class="mono" style="font-size:0.82rem;">${nSub} Sust, ${nIns} Ins, ${nDel} Elim</td>
      `;
      tbody.appendChild(tr);
    });

    // 2. Incisos B, C y D
    const seleccionadas = lista
      .map((item, idx) => ({ item, idx }))
      .filter((x) => x.item.distancia <= umbral)
      .sort((a, b) => a.item.distancia - b.item.distancia || a.idx - b.idx)
      .map((x) => x.item);

    const olBC = document.getElementById("p1-lista-bc");
    olBC.innerHTML = seleccionadas
      .map(
        (s) =>
          `<li><span class="text-green">${s.destino}</span> (distancia = <strong>${s.distancia}</strong>)</li>`
      )
      .join("");

    const salidaD = document.getElementById("p1-salida-d");
    salidaD.innerHTML = `
      <div style="color: var(--text-muted);">Palabra ingresada: <span class="text-amber">"${DATA.punto1.objetivo}"</span></div>
      <div style="color:#fff;font-weight:700;margin-top:6px;">¿Quisiste decir?</div>
      ${seleccionadas
        .map(
          (s, i) =>
            `<div style="padding-left:18px;" class="text-green">${i + 1}. ${s.destino} (distancia = ${s.distancia})</div>`
        )
        .join("")}
    `;

    // 3. Botones selector de palabra para E-I
    const btnBar = document.getElementById("p1-word-buttons");
    btnBar.innerHTML = "";
    lista.forEach((item, idx) => {
      const btn = document.createElement("button");
      btn.className = "btn" + (idx === p1PalabraIdx ? " active" : "");
      btn.textContent = `${idx + 1}. ${item.destino} (d=${item.distancia})`;
      btn.addEventListener("click", () => {
        p1PalabraIdx = idx;
        renderPunto1Detalle();
      });
      btnBar.appendChild(btn);
    });

    renderPunto1Detalle();
  }

  function renderPunto1Detalle() {
    const lista = DATA.punto1.modos[p1Modo];
    const item = lista[p1PalabraIdx];
    const ignorar = p1Modo === "normalizado";
    const umbral = DATA.punto1.umbral;

    // Actualizar botón activo
    document.querySelectorAll("#p1-word-buttons .btn").forEach((b, idx) => {
      b.classList.toggle("active", idx === p1PalabraIdx);
    });

    const m = item.origen.length;
    const n = item.destino.length;
    const pasa = item.distancia <= umbral;

    // KPIs de la palabra elegida
    document.getElementById("p1-resumen-palabra").innerHTML = `
      <div class="kpi-box">
        <div class="kpi-label">Transformación</div>
        <div class="kpi-value mono" style="font-size:1.05rem;">"${item.origen}" → "${item.destino}"</div>
        <div class="kpi-sub">Matriz de ${m + 1} filas × ${n + 1} columnas</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Inciso G · Distancia Mínima</div>
        <div class="kpi-value ${pasa ? "text-green" : "text-rose"}">dp[${m}][${n}] = ${item.distancia}</div>
        <div class="kpi-sub">${pasa ? "Seleccionada (cumple ≤ 3)" : "Descartada (supera 3)"}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Celdas en el camino óptimo</div>
        <div class="kpi-value text-cyan">${item.camino.length} celdas</div>
        <div class="kpi-sub">Desde (${m},${n}) hasta (0,0)</div>
      </div>
    `;

    // Conjunto de celdas en el camino óptimo
    const pathSet = new Set(item.camino.map((c) => `${c[0]},${c[1]}`));

    // Construir tabla HTML de la matriz
    let html = `<table class="matrix-table"><thead><tr><th></th><th>""</th>`;
    for (let j = 0; j < n; j++) {
      const ch = item.destino[j] === " " ? "␣" : item.destino[j];
      html += `<th>${ch}</th>`;
    }
    html += `</tr></thead><tbody>`;

    for (let i = 0; i <= m; i++) {
      const rch = i === 0 ? '""' : item.origen[i - 1] === " " ? "␣" : item.origen[i - 1];
      html += `<tr><th>${rch}</th>`;
      for (let j = 0; j <= n; j++) {
        const onPath = pathSet.has(`${i},${j}`);
        const cls = ["lev-cell"];
        if (onPath) cls.push("on-path");
        html += `<td class="${cls.join(" ")}" data-i="${i}" data-j="${j}">${item.matriz[i][j]}${onPath ? "*" : ""}</td>`;
      }
      html += `</tr>`;
    }
    html += `</tbody></table>`;

    const matDiv = document.getElementById("p1-matriz-container");
    matDiv.innerHTML = html;

    // Click en cada celda para explicar el Inciso F
    matDiv.querySelectorAll("td.lev-cell").forEach((td) => {
      td.addEventListener("click", () => {
        matDiv.querySelectorAll("td.selected-cell").forEach((x) => x.classList.remove("selected-cell"));
        td.classList.add("selected-cell");
        mostrarInspectorCelda(item, Number(td.dataset.i), Number(td.dataset.j), ignorar);
      });
    });

    // Seleccionar automáticamente la celda final (m, n) para que el inspector muestre un ejemplo real al instante
    const lastTd = matDiv.querySelector(`td[data-i="${m}"][data-j="${n}"]`);
    if (lastTd) {
      lastTd.classList.add("selected-cell");
      mostrarInspectorCelda(item, m, n, ignorar);
    }

    // Inciso H: camino desde (m, n) hasta (0, 0)
    const caminoStr = item.camino.map((c) => `(${c[0]},${c[1]})[=${c[2]}]`).join(" → ");
    document.getElementById("p1-camino-h").textContent = caminoStr;

    // Inciso I: operaciones en orden
    const opsDiv = document.getElementById("p1-operaciones-i");
    opsDiv.innerHTML = "";
    let pasoNum = 0;
    item.operaciones.forEach((op) => {
      if (op.tipo !== "SIN_CAMBIO") {
        pasoNum++;
        const pillCls =
          op.tipo === "SUSTITUCION" ? "sub" : op.tipo === "INSERCION" ? "ins" : "del";
        const el = document.createElement("div");
        el.className = "step-item";
        el.innerHTML = `
          <div class="step-circle">${pasoNum}</div>
          <div>
            <h4><span class="op-pill ${pillCls}">${op.tipo}</span>${op.descripcion}</h4>
            <p class="mono">Estado resultante de la palabra: <span class="text-cyan">"${op.estado}"</span></p>
          </div>
        `;
        opsDiv.appendChild(el);
      } else if (op.char_origen !== op.char_destino) {
        const el = document.createElement("div");
        el.className = "step-item";
        el.innerHTML = `
          <div class="step-circle" style="opacity:0.6;">0</div>
          <div>
            <h4><span class="op-pill eq">SIN COSTO</span>${op.descripcion}</h4>
            <p class="mono">Estado resultante: <span class="text-cyan">"${op.estado}"</span></p>
          </div>
        `;
        opsDiv.appendChild(el);
      }
    });
    if (pasoNum === 0) {
      opsDiv.innerHTML = `<div class="callout green">No se requirió ninguna operación de edición (las cadenas son equivalentes).</div>`;
    }
  }

  function mostrarInspectorCelda(item, i, j, ignorar) {
    const box = document.getElementById("p1-cell-inspector");
    const dp = item.matriz;
    if (i === 0 && j === 0) {
      box.innerHTML = `<strong class="text-amber">Celda (0, 0) — Caso base inicial:</strong> transformar <code>""</code> en <code>""</code> cuesta <strong>0</strong> operaciones.`;
      return;
    }
    if (i === 0) {
      box.innerHTML = `<strong class="text-amber">Celda (0, ${j}) — Caso base (fila 0):</strong> transformar cadena vacía <code>""</code> en <code>"${item.destino.slice(0, j)}"</code> requiere <strong>${j} inserciones</strong> → <code>dp[0][${j}] = ${j}</code>.`;
      return;
    }
    if (j === 0) {
      box.innerHTML = `<strong class="text-amber">Celda (${i}, 0) — Caso base (columna 0):</strong> transformar <code>"${item.origen.slice(0, i)}"</code> en cadena vacía <code>""</code> requiere <strong>${i} eliminaciones</strong> → <code>dp[${i}][0] = ${i}</code>.`;
      return;
    }

    const cO = item.origen[i - 1];
    const cD = item.destino[j - 1];
    const iguales = normalizarCharJS(cO, ignorar) === normalizarCharJS(cD, ignorar);
    const costoSust = iguales ? 0 : 1;

    const ins = dp[i][j - 1] + 1;
    const elim = dp[i - 1][j] + 1;
    const sust = dp[i - 1][j - 1] + costoSust;
    const val = dp[i][j];

    box.innerHTML = `
      <div style="margin-bottom:8px;">
        <strong class="text-amber">Inciso F — Cálculo exacto de la celda dp[${i}][${j}]</strong>
        comparando prefijo <code class="text-cyan">"${item.origen.slice(0, i)}"</code> vs <code class="text-cyan">"${item.destino.slice(0, j)}"</code>
        (últimas letras: <code>'${cO}'</code> vs <code>'${cD}'</code> → ${iguales ? '<span class="text-green">iguales, costo = 0</span>' : '<span class="text-rose">distintas, costo = 1</span>'}):
      </div>
      <div class="grid-3">
        <div class="kpi-box" style="${ins === val ? "border-color:var(--green);" : ""}">
          <div class="kpi-label">1. Inserción (izquierda + 1)</div>
          <div class="mono">dp[${i}][${j - 1}] + 1 = ${dp[i][j - 1]} + 1 = <strong class="${ins === val ? "text-green" : ""}">${ins}</strong></div>
        </div>
        <div class="kpi-box" style="${elim === val ? "border-color:var(--green);" : ""}">
          <div class="kpi-label">2. Eliminación (arriba + 1)</div>
          <div class="mono">dp[${i - 1}][${j}] + 1 = ${dp[i - 1][j]} + 1 = <strong class="${elim === val ? "text-green" : ""}">${elim}</strong></div>
        </div>
        <div class="kpi-box" style="${sust === val ? "border-color:var(--green);" : ""}">
          <div class="kpi-label">3. Sustitución (diagonal + ${costoSust})</div>
          <div class="mono">dp[${i - 1}][${j - 1}] + ${costoSust} = ${dp[i - 1][j - 1]} + ${costoSust} = <strong class="${sust === val ? "text-green" : ""}">${sust}</strong></div>
        </div>
      </div>
      <div style="margin-top:8px;" class="mono">
        Resultado: <strong>dp[${i}][${j}] = min(${ins}, ${elim}, ${sust}) = <span class="text-green">${val}</span></strong>
      </div>
    `;
  }

  document.getElementById("p1-modo-norm").addEventListener("click", () => {
    p1Modo = "normalizado";
    renderPunto1();
  });
  document.getElementById("p1-modo-exact").addEventListener("click", () => {
    p1Modo = "exacto";
    renderPunto1();
  });

  /* ==========================================================================
     SECCIÓN 2: PUNTO 2 — FLOYD-WARSHALL + GRAFO SVG + SLIDER k
     ========================================================================== */
  const POS_GRAFO = {
    B: { x: 350, y: 55 },
    A: { x: 560, y: 55 },
    D: { x: 180, y: 135 },
    C: { x: 470, y: 140 },
    E: { x: 330, y: 185 },
    I: { x: 590, y: 205 },
    J: { x: 735, y: 175 },
    H: { x: 100, y: 245 },
    K: { x: 235, y: 295 },
    L: { x: 475, y: 345 },
    M: { x: 155, y: 365 },
    O: { x: 285, y: 405 },
    P: { x: 675, y: 355 },
  };

  let fwParActual = ["M", "J"];
  let fwModoMatriz = "ambas";

  function reconstruirCaminoJS(orig, dest) {
    const p2 = DATA.punto2;
    const verts = p2.vertices;
    const i = verts.indexOf(orig);
    const j = verts.indexOf(dest);
    const dist = p2.dist_final[i][j];
    if (dist === null) return null;

    // Pesos directos para desglose
    const pesos = {};
    p2.bidir.forEach(([u, v, w]) => {
      pesos[`${u}->${v}`] = w;
      pesos[`${v}->${u}`] = w;
    });
    p2.unidir.forEach(([u, v, w]) => {
      pesos[`${u}->${v}`] = w;
    });

    const traza = [];
    const caminoInv = [dest];
    let actual = dest;
    let guard = 0;
    while (actual !== orig && guard < 30) {
      const idxAct = verts.indexOf(actual);
      const ant = p2.pred_final[i][idxAct];
      if (!ant) break;
      traza.push([orig, actual, ant]);
      caminoInv.push(ant);
      actual = ant;
      guard++;
    }
    const camino = caminoInv.reverse();
    const arcos = [];
    for (let t = 0; t < camino.length - 1; t++) {
      const u = camino[t];
      const v = camino[t + 1];
      arcos.push([u, v, pesos[`${u}->${v}`]]);
    }
    return { origen: orig, destino: dest, distancia: dist, camino, traza, arcos };
  }

  function renderGrafoSVG(caminoObj) {
    const p2 = DATA.punto2;
    const pathEdges = new Set();
    const pathNodes = new Set(caminoObj ? caminoObj.camino : []);
    if (caminoObj) {
      caminoObj.arcos.forEach(([u, v]) => pathEdges.add(`${u}->${v}`));
    }

    const R = 21;
    function acortar(p1, p2p, padStart, padEnd) {
      const dx = p2p.x - p1.x;
      const dy = p2p.y - p1.y;
      const len = Math.hypot(dx, dy) || 1;
      return {
        x1: p1.x + (dx / len) * padStart,
        y1: p1.y + (dy / len) * padStart,
        x2: p2p.x - (dx / len) * padEnd,
        y2: p2p.y - (dy / len) * padEnd,
        mx: (p1.x + p2p.x) / 2,
        my: (p1.y + p2p.y) / 2,
        nx: -dy / len,
        ny: dx / len,
      };
    }

    let svg = `<svg viewBox="0 0 830 455" width="830" height="455" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arr-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
        </marker>
        <marker id="arr-neg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#c084fc" />
        </marker>
        <marker id="arr-hi" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399" />
        </marker>
      </defs>`;

    // Dibujar aristas bidireccionales
    p2.bidir.forEach(([u, v, w]) => {
      const fwd = pathEdges.has(`${u}->${v}`);
      const bwd = pathEdges.has(`${v}->${u}`);
      const active = fwd || bwd;
      const src = bwd ? v : u;
      const dst = bwd ? u : v;
      const g = acortar(POS_GRAFO[src], POS_GRAFO[dst], R + 3, R + 5);

      const stroke = active ? "#34d399" : "#475569";
      const sw = active ? 3.5 : 1.7;
      const mStart = active ? "" : `marker-start="url(#arr-gray)"`;
      const mEnd = active ? `marker-end="url(#arr-hi)"` : `marker-end="url(#arr-gray)"`;

      svg += `<line x1="${g.x1.toFixed(1)}" y1="${g.y1.toFixed(1)}" x2="${g.x2.toFixed(1)}" y2="${g.y2.toFixed(1)}"
        stroke="${stroke}" stroke-width="${sw}" ${mStart} ${mEnd} />`;

      const lx = g.mx + g.nx * 13;
      const ly = g.my + g.ny * 13;
      svg += `<rect x="${(lx - 11).toFixed(1)}" y="${(ly - 10).toFixed(1)}" width="22" height="18" rx="4" fill="#0b1222" opacity="0.88" />`;
      svg += `<text x="${lx.toFixed(1)}" y="${(ly + 4).toFixed(1)}" text-anchor="middle" font-family="Consolas,monospace" font-size="13" font-weight="700" fill="${active ? "#6ee7b7" : "#cbd5e1"}">${w}</text>`;
    });

    // Dibujar arcos unidireccionales negativos
    p2.unidir.forEach(([u, v, w]) => {
      const active = pathEdges.has(`${u}->${v}`);
      const g = acortar(POS_GRAFO[u], POS_GRAFO[v], R + 2, R + 6);
      const stroke = active ? "#34d399" : "#c084fc";
      const sw = active ? 4 : 2.3;
      const mEnd = active ? `marker-end="url(#arr-hi)"` : `marker-end="url(#arr-neg)"`;

      svg += `<line x1="${g.x1.toFixed(1)}" y1="${g.y1.toFixed(1)}" x2="${g.x2.toFixed(1)}" y2="${g.y2.toFixed(1)}"
        stroke="${stroke}" stroke-width="${sw}" stroke-dasharray="${active ? "none" : "6,3"}" ${mEnd} />`;

      const lx = g.mx + g.nx * 14;
      const ly = g.my + g.ny * 14;
      svg += `<rect x="${(lx - 13).toFixed(1)}" y="${(ly - 10).toFixed(1)}" width="26" height="18" rx="4" fill="#1b1130" stroke="${active ? "#34d399" : "#c084fc"}" stroke-width="1" />`;
      svg += `<text x="${lx.toFixed(1)}" y="${(ly + 4).toFixed(1)}" text-anchor="middle" font-family="Consolas,monospace" font-size="13" font-weight="800" fill="${active ? "#6ee7b7" : "#e9d5ff"}">${w}</text>`;
    });

    // Dibujar vértices
    p2.vertices.forEach((v) => {
      const p = POS_GRAFO[v];
      const inPath = pathNodes.has(v);
      const isEndpoint = caminoObj && (v === caminoObj.origen || v === caminoObj.destino);
      const fill = isEndpoint ? "#059669" : inPath ? "#134e4a" : "#1e293b";
      const stroke = isEndpoint ? "#6ee7b7" : inPath ? "#34d399" : "#64748b";
      svg += `<circle cx="${p.x}" cy="${p.y}" r="${R}" fill="${fill}" stroke="${stroke}" stroke-width="${inPath ? 3 : 2}" />`;
      svg += `<text x="${p.x}" y="${p.y + 5}" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="15" font-weight="800" fill="#ffffff">${v}</text>`;
    });

    // Leyenda dentro del SVG
    svg += `
      <g transform="translate(18, 16)" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">
        <line x1="0" y1="6" x2="26" y2="6" stroke="#64748b" stroke-width="2" />
        <text x="34" y="10">Bidireccional (+)</text>
        <line x1="0" y1="26" x2="26" y2="26" stroke="#c084fc" stroke-width="2.4" stroke-dasharray="5,3" />
        <text x="34" y="30">Unidireccional negativo (-)</text>
        <line x1="0" y1="46" x2="26" y2="46" stroke="#34d399" stroke-width="3.5" />
        <text x="34" y="50" fill="#6ee7b7">Camino mínimo resaltado</text>
      </g>
    </svg>`;

    document.getElementById("p2-grafo-svg").innerHTML = svg;
  }

  function mostrarCaminoFW(orig, dest) {
    fwParActual = [orig, dest];
    document.getElementById("fw-orig").value = orig;
    document.getElementById("fw-dest").value = dest;

    document.querySelectorAll("[data-fw-pair]").forEach((b) => {
      b.classList.toggle("active", b.dataset.fwPair === `${orig},${dest}`);
    });

    const info = reconstruirCaminoJS(orig, dest);
    renderGrafoSVG(info);

    const box = document.getElementById("p2-camino-detalle");
    if (!info) {
      box.innerHTML = `No existe camino dirigido de <strong>${orig}</strong> a <strong>${dest}</strong>.`;
      return;
    }

    const ruta = info.camino.map((n) => `<strong>${n}</strong>`).join(" → ");
    const arcosStr =
      info.arcos.length > 0
        ? info.arcos.map(([u, v, w]) => `${u} --(${w})--> ${v}`).join("  |  ")
        : "(mismo vértice, costo 0)";
    const sumaStr =
      info.arcos.length > 0
        ? info.arcos.map(([, , w]) => (w < 0 ? `(${w})` : `${w}`)).join(" + ") + ` = ${info.distancia}`
        : "0";
    const trazaStr =
      info.traza.length > 0
        ? info.traza.map(([o, d, a]) => `P[${o}][${d}] = ${a}`).join("  →  ")
        : `P[${orig}][${dest}] = ${orig}`;

    box.innerHTML = `
      <div style="font-size:1rem;margin-bottom:6px;">
        <strong>Camino mínimo ${orig} → ${dest}:</strong> ${ruta}
        &nbsp;|&nbsp; <span class="pill green">Distancia mínima = ${info.distancia}</span>
      </div>
      <div class="mono" style="font-size:0.86rem;margin-bottom:4px;"><strong>Arcos recorridos:</strong> ${arcosStr}</div>
      <div class="mono" style="font-size:0.86rem;margin-bottom:4px;"><strong>Suma verificada:</strong> ${sumaStr}</div>
      <div class="mono" style="font-size:0.84rem;opacity:0.92;"><strong>Reconstrucción hacia atrás en P:</strong> ${trazaStr}</div>
    `;
  }

  function renderMatricesFW(snapIdx) {
    const p2 = DATA.punto2;
    const snap = p2.snapshots[snapIdx];
    const verts = p2.vertices;

    document.getElementById("fw-k-titulo").textContent =
      snapIdx === 0
        ? "Paso 0 / 13 — Matriz Inicial D⁰ (solo conexiones directas)"
        : `Paso ${snapIdx} / 13 — ${snap.label}`;
    document.getElementById("fw-k-mejoras").textContent =
      snapIdx === 0 ? "35 arcos iniciales" : `${snap.mejoras} distancia(s) mejorada(s)`;

    if (snapIdx === 0) {
      document.getElementById("fw-k-ejemplos").textContent =
        "Sin vértices intermedios todavía: los pares sin arco directo valen ∞.";
    } else if (snap.ejemplos.length === 0) {
      document.getElementById("fw-k-ejemplos").textContent =
        `Pasar por ${snap.vertice} no mejoró ninguna distancia adicional.`;
    } else {
      const ej = snap.ejemplos
        .map(([u, v, oldV, newV]) => `${u}→${v}: ${oldV === null ? "∞" : oldV} ⇒ ${newV}`)
        .join("   |   ");
      document.getElementById("fw-k-ejemplos").textContent = `Mejoras en esta iteración: ${ej}`;
    }

    const mejoradosSet = new Set(snap.ejemplos.map(([u, v]) => `${u},${v}`));

    // Matriz D
    let hD = `<table class="matrix-table"><thead><tr><th>D</th>${verts.map((v) => `<th>${v}</th>`).join("")}</tr></thead><tbody>`;
    snap.dist.forEach((fila, i) => {
      hD += `<tr><th>${verts[i]}</th>`;
      fila.forEach((val, j) => {
        const cls = [];
        if (i === j) cls.push("diag-zero");
        else if (val === null) cls.push("inf-val");
        else if (val < 0) cls.push("neg-val");
        if (mejoradosSet.has(`${verts[i]},${verts[j]}`)) cls.push("fw-highlight");
        hD += `<td class="${cls.join(" ")}">${val === null ? "∞" : val}</td>`;
      });
      hD += `</tr>`;
    });
    hD += `</tbody></table>`;
    document.getElementById("p2-matriz-d").innerHTML = hD;

    // Matriz P
    let hP = `<table class="matrix-table"><thead><tr><th>P</th>${verts.map((v) => `<th>${v}</th>`).join("")}</tr></thead><tbody>`;
    snap.pred.forEach((fila, i) => {
      hP += `<tr><th>${verts[i]}</th>`;
      fila.forEach((val, j) => {
        const cls = [];
        if (i === j) cls.push("diag-zero");
        else if (val === null) cls.push("inf-val");
        else cls.push("text-green");
        if (mejoradosSet.has(`${verts[i]},${verts[j]}`)) cls.push("fw-highlight");
        hP += `<td class="${cls.join(" ")}">${val === null ? "-" : val}</td>`;
      });
      hP += `</tr>`;
    });
    hP += `</tbody></table>`;
    document.getElementById("p2-matriz-p").innerHTML = hP;
  }

  function initPunto2() {
    const verts = DATA.punto2.vertices;
    const selO = document.getElementById("fw-orig");
    const selD = document.getElementById("fw-dest");
    verts.forEach((v) => {
      selO.add(new Option(v, v));
      selD.add(new Option(v, v));
    });

    document.querySelectorAll("[data-fw-pair]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const [o, d] = btn.dataset.fwPair.split(",");
        mostrarCaminoFW(o, d);
      });
    });

    document.getElementById("fw-custom-btn").addEventListener("click", () => {
      mostrarCaminoFW(selO.value, selD.value);
    });

    const slider = document.getElementById("fw-k-slider");
    slider.max = DATA.punto2.snapshots.length - 1;
    slider.value = DATA.punto2.snapshots.length - 1;
    slider.addEventListener("input", () => renderMatricesFW(Number(slider.value)));

    const updateVis = (modo) => {
      fwModoMatriz = modo;
      document.getElementById("fw-ver-d").classList.toggle("active", modo === "d");
      document.getElementById("fw-ver-p").classList.toggle("active", modo === "p");
      document.getElementById("fw-ver-ambas").classList.toggle("active", modo === "ambas");
      document.getElementById("p2-matriz-d-wrap").style.display = modo === "p" ? "none" : "block";
      document.getElementById("p2-matriz-p-wrap").style.display = modo === "d" ? "none" : "block";
    };
    document.getElementById("fw-ver-d").addEventListener("click", () => updateVis("d"));
    document.getElementById("fw-ver-p").addEventListener("click", () => updateVis("p"));
    document.getElementById("fw-ver-ambas").addEventListener("click", () => updateVis("ambas"));
    updateVis("ambas");

    // Diagonal Inciso F
    const diagTxt = verts
      .map((v, i) => `D[${v}][${v}] = ${DATA.punto2.dist_final[i][i]}`)
      .join("   |   ");
    document.getElementById("p2-diagonal-f").textContent = diagTxt;

    mostrarCaminoFW("M", "J");
    renderMatricesFW(DATA.punto2.snapshots.length - 1);
  }

  /* ==========================================================================
     SECCIÓN 3: PUNTO 3 — MATRIZ 20x20 Y TRIE VS FUERZA BRUTA
     ========================================================================== */
  let p3Filtro = "TODAS";

  function initPunto3() {
    const p3 = DATA.punto3;
    const ahorro = ((1 - p3.trie_comps / p3.fb_comps) * 100).toFixed(1);

    // Barras comparativas
    const maxC = Math.max(p3.trie_comps, p3.fb_comps);
    document.getElementById("p3-comparativa-barras").innerHTML = `
      <div class="bar-row">
        <div class="bar-meta">
          <span class="text-green">Árbol Trie + 8 direcciones (Elegida)</span>
          <span class="mono text-green">${fmt(p3.trie_comps)} comparaciones (${p3.trie_ms} ms)</span>
        </div>
        <div class="bar-track"><div class="bar-fill green" style="width:${((p3.trie_comps / maxC) * 100).toFixed(1)}%"></div></div>
      </div>
      <div class="bar-row">
        <div class="bar-meta">
          <span class="text-amber">Fuerza Bruta 2D (Baseline Unidad 3)</span>
          <span class="mono text-amber">${fmt(p3.fb_comps)} comparaciones (${p3.fb_ms} ms)</span>
        </div>
        <div class="bar-track"><div class="bar-fill amber" style="width:100%"></div></div>
      </div>
      <p style="font-size:0.87rem;color:var(--text-secondary);margin-top:8px;">
        <strong>Ahorro real:</strong> <span class="text-green">${ahorro}% menos comparaciones</span>
        (${p3.trie_podadas} de 400 celdas podadas instantáneamente en la raíz del Trie).
      </p>
    `;

    // Tabla de palabras
    const tbody = document.getElementById("p3-tabla-palabras");
    const colorMap = {
      ARBOL: "text-green",
      HEAPS: "text-amber",
      SORTS: "text-cyan",
      NODOS: "text-purple",
      GRAFO: "text-rose",
    };

    p3.palabras.forEach((pal) => {
      const h = p3.hallazgos[pal][0];
      const [r0, c0] = h.inicio;
      const [r1, c1] = h.fin;
      const celdasStr = h.celdas.map(([r, c]) => `(${r},${c})`).join("→");
      const tr = document.createElement("tr");
      tr.style.cursor = "pointer";
      tr.innerHTML = `
        <td class="mono ${colorMap[pal]}">${pal}</td>
        <td class="mono">(${r0}, ${c0})</td>
        <td class="mono">(${r1}, ${c1})</td>
        <td class="mono">(${r0 + 1},${c0 + 1}) → (${r1 + 1},${c1 + 1})</td>
        <td><strong>${h.direccion}</strong></td>
        <td class="mono" style="font-size:0.8rem;">${celdasStr}</td>
      `;
      tr.addEventListener("click", () => {
        p3Filtro = pal;
        renderSopa();
      });
      tbody.appendChild(tr);
    });

    // Botones de filtro
    const fbar = document.getElementById("p3-filter-buttons");
    const opts = ["TODAS", ...p3.palabras];
    opts.forEach((op) => {
      const btn = document.createElement("button");
      btn.className = "btn" + (op === "TODAS" ? " active" : "");
      btn.dataset.word = op;
      btn.textContent = op === "TODAS" ? "Mostrar todas (5)" : `Enfocar ${op}`;
      btn.addEventListener("click", () => {
        p3Filtro = op;
        renderSopa();
      });
      fbar.appendChild(btn);
    });

    renderSopa();
  }

  function renderSopa() {
    const p3 = DATA.punto3;
    document.querySelectorAll("#p3-filter-buttons .btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.word === p3Filtro);
    });

    const cellWord = {};
    p3.palabras.forEach((pal) => {
      p3.hallazgos[pal].forEach((h) => {
        h.celdas.forEach(([r, c]) => {
          cellWord[`${r},${c}`] = pal;
        });
      });
    });

    let html = `<div class="sopa-grid"><div class="sopa-hdr"></div>`;
    for (let c = 0; c < 20; c++) html += `<div class="sopa-hdr">${c}</div>`;

    for (let r = 0; r < 20; r++) {
      html += `<div class="sopa-hdr">${r}</div>`;
      for (let c = 0; c < 20; c++) {
        const ch = p3.matriz[r][c];
        const owner = cellWord[`${r},${c}`];
        const cls = ["sopa-cell"];
        if (owner) {
          cls.push(`w-${owner}`);
          if (p3Filtro !== "TODAS") {
            if (owner === p3Filtro) cls.push("focused");
            else cls.push("dimmed");
          }
        } else if (p3Filtro !== "TODAS") {
          cls.push("dimmed");
        }
        html += `<div class="${cls.join(" ")}" title="Fila ${r}, Col ${c}${owner ? " · " + owner : ""}">${ch}</div>`;
      }
    }
    html += `</div>`;
    document.getElementById("p3-sopa-container").innerHTML = html;
  }

  /* ==========================================================================
     SECCIÓN 4: PUNTO 4 — 1.000.000 DE DATOS (PARTES A, B Y C)
     ========================================================================== */
  function initPunto4() {
    const p4 = DATA.punto4;

    // Sub-pestañas A / B / C
    document.querySelectorAll("[data-p4-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.p4Tab;
        document.querySelectorAll("[data-p4-tab]").forEach((b) => b.classList.toggle("active", b === btn));
        document.querySelectorAll(".subtab-panel").forEach((p) => p.classList.toggle("active", p.id === target));
      });
    });

    /* --- PARTE A --- */
    const pa = p4.parteA;
    const ratioOps = (pa.dyv.comps / pa.kadane.comps).toFixed(2);
    const ratioT = (pa.dyv.ms / pa.kadane.ms).toFixed(1);

    document.getElementById("p4a-kpis").innerHTML = `
      <div class="kpi-box">
        <div class="kpi-label">Utilidad Máxima</div>
        <div class="kpi-value text-green">+${fmt(pa.valor_max)}</div>
        <div class="kpi-sub">100% igual en Kadane y D&amp;V</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Tramo Óptimo (inclusive)</div>
        <div class="kpi-value text-cyan" style="font-size:1.15rem;">[${fmt(pa.inicio)} .. ${fmt(pa.fin)}]</div>
        <div class="kpi-sub">${fmt(pa.duracion)} días contiguos</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Kadane O(n)</div>
        <div class="kpi-value text-green">${(pa.kadane.ms / 1000).toFixed(2)} s</div>
        <div class="kpi-sub mono">${fmt(pa.kadane.comps)} comps (≈ 2n)</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Divide y Vencerás O(n log n)</div>
        <div class="kpi-value text-amber">${(pa.dyv.ms / 1000).toFixed(2)} s</div>
        <div class="kpi-sub mono">${ratioT}× más lento (${ratioOps}× comps)</div>
      </div>
    `;

    document.getElementById("p4a-tabla").innerHTML = `
      <tr>
        <td class="text-green">Kadane (Prog. Dinámica)</td>
        <td class="mono">Θ(n)</td>
        <td class="mono text-green">${fmt(pa.kadane.comps)}</td>
        <td class="mono text-green">${pa.kadane.ms} ms (${(pa.kadane.ms / 1000).toFixed(2)} s)</td>
        <td class="mono">O(1)</td>
        <td>Lineal exacto (~2 comparaciones por elemento)</td>
      </tr>
      <tr>
        <td class="text-amber">Divide y Vencerás</td>
        <td class="mono">Θ(n log n)</td>
        <td class="mono text-amber">${fmt(pa.dyv.comps)}</td>
        <td class="mono text-amber">${pa.dyv.ms} ms (${(pa.dyv.ms / 1000).toFixed(2)} s)</td>
        <td class="mono">O(log n)</td>
        <td>≈ n·log₂(n) + 2n (~19.93M + 2M) + 2M llamadas recursivas</td>
      </tr>
    `;

    document.getElementById("p4a-barras").innerHTML = `
      <div class="bar-row">
        <div class="bar-meta"><span class="text-green">Kadane — Comparaciones</span><span class="mono text-green">${fmt(pa.kadane.comps)}</span></div>
        <div class="bar-track"><div class="bar-fill green" style="width:${((pa.kadane.comps / pa.dyv.comps) * 100).toFixed(1)}%"></div></div>
      </div>
      <div class="bar-row">
        <div class="bar-meta"><span class="text-amber">Divide y Vencerás — Comparaciones</span><span class="mono text-amber">${fmt(pa.dyv.comps)}</span></div>
        <div class="bar-track"><div class="bar-fill amber" style="width:100%"></div></div>
      </div>
    `;

    renderGraficoParteA(pa, p4.n);

    /* --- PARTE B --- */
    const pb = p4.parteB;
    document.getElementById("p4b-kpis").innerHTML = `
      <div class="kpi-box">
        <div class="kpi-label">Períodos hallados</div>
        <div class="kpi-value text-green">k = ${pb.k}</div>
        <div class="kpi-sub">0 solapamientos verificados</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Utilidad acumulada Top-10</div>
        <div class="kpi-value text-green">+${fmt(pb.suma_total)}</div>
        <div class="kpi-sub">Suma de los 10 tramos disjuntos</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Llamadas parciales Kadane</div>
        <div class="kpi-value text-cyan">${pb.evals}</div>
        <div class="kpi-sub">Exactamente 2k - 1 = 19</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Tiempo total (1M datos)</div>
        <div class="kpi-value text-amber">${(pb.ms / 1000).toFixed(2)} s</div>
        <div class="kpi-sub mono">${fmt(pb.comps)} comps · Mem O(k)</div>
      </div>
    `;

    document.getElementById("p4b-tabla").innerHTML = pb.top10
      .map(
        (it) => `
      <tr>
        <td class="mono ${it.rank === 1 ? "text-green" : "text-cyan"}">#${it.rank}</td>
        <td class="mono text-green">+${fmt(it.utilidad)}</td>
        <td class="mono">${fmt(it.inicio)}</td>
        <td class="mono">${fmt(it.fin)}</td>
        <td class="mono">${fmt(it.longitud)}</td>
        <td class="mono" style="font-size:0.82rem;">[${fmt(it.segmento_origen[0])} .. ${fmt(it.segmento_origen[1])}]</td>
      </tr>
    `
      )
      .join("");

    renderTimelineParteB(pb.top10, p4.n);

    /* --- PARTE C --- */
    const pc = p4.parteC;
    document.getElementById("p4c-tabla").innerHTML = pc.filas
      .map((f) => {
        const cls = f.metodo === "Hoare" ? "text-green" : f.metodo === "Lomuto" ? "text-amber" : "text-cyan";
        return `
        <tr>
          <td class="${cls}">${f.nombre}</td>
          <td class="mono" style="color:#fff;font-weight:700;">${f.valor}</td>
          <td class="mono">${fmt(f.comps)}</td>
          <td class="mono">${fmt(f.swaps)}</td>
          <td class="mono">${f.ms} ms (${(f.ms / 1000).toFixed(2)} s)</td>
          <td class="mono">${f.mem}</td>
        </tr>
      `;
      })
      .join("");

    const fHoare50 = pc.filas[0];
    const fLomuto50 = pc.filas[1];
    const fMerge = pc.filas[6];
    const maxTime = fMerge.ms;

    document.getElementById("p4c-barras").innerHTML = `
      <div class="bar-row">
        <div class="bar-meta"><span class="text-green">QuickSelect Hoare (p50)</span><span class="mono text-green">${fHoare50.ms} ms · ${fmt(fHoare50.comps)} comps · ${fmt(fHoare50.swaps)} swaps</span></div>
        <div class="bar-track"><div class="bar-fill green" style="width:${Math.max(4, (fHoare50.ms / maxTime) * 100).toFixed(1)}%"></div></div>
      </div>
      <div class="bar-row">
        <div class="bar-meta"><span class="text-amber">QuickSelect Lomuto (p50 — afectado por repetidos)</span><span class="mono text-amber">${fLomuto50.ms} ms · ${fmt(fLomuto50.comps)} comps · ${fmt(fLomuto50.swaps)} swaps</span></div>
        <div class="bar-track"><div class="bar-fill amber" style="width:${Math.max(6, (fLomuto50.ms / maxTime) * 100).toFixed(1)}%"></div></div>
      </div>
      <div class="bar-row">
        <div class="bar-meta"><span class="text-cyan">Merge Sort Baseline (ordenamiento completo)</span><span class="mono text-cyan">${fMerge.ms} ms · ${fmt(fMerge.comps)} comps · ${fmt(fMerge.swaps)} escr. aux</span></div>
        <div class="bar-track"><div class="bar-fill cyan" style="width:100%"></div></div>
      </div>
    `;

    document.getElementById("p4c-validacion").innerHTML = pc.validacion
      .map(
        (v) => `
      <tr>
        <td style="color:#fff;font-weight:700;">${v.nombre}</td>
        <td class="mono text-green">${v.valor}</td>
        <td class="mono">${fmt(v.cnt_lt)} (${v.pct_lt}%)</td>
        <td class="mono">${fmt(v.cnt_le)} (${v.pct_le}%)</td>
        <td class="mono text-cyan">${v.bb_comps} comps (log₂ 1M ≈ 20)</td>
        <td><span class="pill green">VALIDADO OK</span></td>
      </tr>
    `
      )
      .join("");

    const sp = (fMerge.ms / fHoare50.ms).toFixed(1);
    document.getElementById("p4c-disc-1").innerHTML =
      `Cuando solo necesitamos un cuantil puntual (como la mediana), ordenar todo el millón con Merge Sort cuesta <strong>Θ(n log n)</strong> (${fmt(fMerge.comps)} comparaciones y memoria auxiliar <strong>Θ(n)</strong>), mientras QuickSelect descarta una partición entera en cada paso (Reducción por tamaño variable, Unidad 4) logrando <strong>Θ(n) promedio</strong> y <strong>O(1) memoria auxiliar</strong>. En nuestra medición real, Hoare fue <strong>${sp}× más rápido</strong> que Merge Sort. Ordenar todo solo conviene si se van a consultar muchísimos cuantiles distintos.`;

    document.getElementById("p4c-disc-2").innerHTML =
      `El archivo real tiene 1.000.000 de enteros en <code>[${p4.min_val}, ${p4.max_val}]</code>: solo <strong>${p4.unicos} valores únicos</strong> (~4.975 repetidos por valor). En <code>p50</code>, <strong>Lomuto</strong> hizo <strong>${fmt(fLomuto50.comps)} comparaciones y ${fmt(fLomuto50.swaps)} swaps</strong> frente a solo <strong>${fmt(fHoare50.comps)} comparaciones y ${fmt(fHoare50.swaps)} swaps</strong> de <strong>Hoare</strong>, porque Lomuto empuja todos los iguales hacia un mismo lado y se vuelve cuadrático O(d²) en el bloque de ~5.000 ceros, mientras Hoare los parte por la mitad (Unidad 5, Diap. 30).`;

    document.getElementById("p4c-disc-3").innerHTML =
      `Ante una <strong>entrada adversa</strong> (por ejemplo un arreglo ya ordenado eligiendo siempre el último elemento como pivote), cada partición reduce solo de <em>n</em> a <em>n−1</em> y el algoritmo degenera a <strong>O(n²)</strong>. Para evitarlo se aplica <strong>pivote aleatorio</strong>, <strong>mediana de tres</strong>, <strong>partición en 3 vías (Dutch National Flag)</strong> para repetidos o el algoritmo determinístico <strong>Mediana de Medianas (Unidad 4, Diap. 41–51)</strong> que garantiza peor caso <strong>O(n)</strong>.`;

    const rep = pc.demo_repetidos;
    const mult = Math.round(rep.lomuto.comps / Math.max(1, rep.hoare.comps));
    document.getElementById("p4c-demo-repetidos").innerHTML = `
      <strong>Evidencia experimental con ${fmt(rep.m)} elementos idénticos <code>[42, 42, ..., 42]</code> (buscando mediana):</strong><br />
      • <strong>Hoare:</strong> <span class="mono">${fmt(rep.hoare.comps)} comparaciones</span> (${rep.hoare.ms} ms) — partición balanceada.<br />
      • <strong>Lomuto:</strong> <span class="mono">${fmt(rep.lomuto.comps)} comparaciones</span> (${rep.lomuto.ms} ms) — <strong>¡${mult}× más comparaciones!</strong> (degradación cuadrática O(m²)).
    `;
  }

  function renderGraficoParteA(pa, n) {
    const curva = pa.curva;
    const W = 820;
    const H = 290;
    const padL = 72;
    const padR = 24;
    const padT = 24;
    const padB = 42;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const ys = curva.map((p) => p.acum);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const spanY = maxY - minY || 1;

    const xOf = (dia) => padL + (dia / (n - 1)) * plotW;
    const yOf = (val) => padT + plotH - ((val - minY) / spanY) * plotH;

    const xIni = xOf(pa.inicio);
    const xFin = xOf(pa.fin);

    const ptsAll = curva.map((p) => `${xOf(p.dia).toFixed(1)},${yOf(p.acum).toFixed(1)}`).join(" ");
    const ptsOpt = curva
      .filter((p) => p.dia >= pa.inicio - n / 100 && p.dia <= pa.fin + n / 100)
      .map((p) => `${xOf(p.dia).toFixed(1)},${yOf(p.acum).toFixed(1)}`)
      .join(" ");

    const yZero = yOf(0);
    const ticksY = [maxY, Math.round((maxY + minY) / 2), minY];

    let svg = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">`;

    // Grilla horizontal
    ticksY.forEach((tv) => {
      const y = yOf(tv);
      svg += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="rgba(148,163,184,0.16)" stroke-dasharray="4,4" />`;
      svg += `<text x="${padL - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-family="Consolas,monospace" font-size="11" fill="#94a3b8">${fmt(tv)}</text>`;
    });

    // Línea Y = 0
    if (yZero >= padT && yZero <= H - padB) {
      svg += `<line x1="${padL}" y1="${yZero.toFixed(1)}" x2="${W - padR}" y2="${yZero.toFixed(1)}" stroke="rgba(148,163,184,0.38)" />`;
    }

    // Banda sombreada del tramo óptimo
    svg += `<rect x="${xIni.toFixed(1)}" y="${padT}" width="${(xFin - xIni).toFixed(1)}" height="${plotH}" fill="rgba(52,211,153,0.18)" stroke="#34d399" stroke-width="1.5" stroke-dasharray="4,3" />`;
    svg += `<text x="${((xIni + xFin) / 2).toFixed(1)}" y="${padT + 16}" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" font-weight="800" fill="#6ee7b7">+${fmt(pa.valor_max)}</text>`;

    // Curva completa + segmento óptimo resaltado
    svg += `<polyline points="${ptsAll}" fill="none" stroke="#22d3ee" stroke-width="2" />`;
    svg += `<polyline points="${ptsOpt}" fill="none" stroke="#34d399" stroke-width="3.6" />`;

    // Eje X y etiquetas
    svg += `<line x1="${padL}" y1="${H - padB}" x2="${W - padR}" y2="${H - padB}" stroke="#475569" />`;
    [0, 250000, 500000, 750000, 1000000].forEach((d) => {
      const x = xOf(Math.min(d, n - 1));
      svg += `<text x="${x.toFixed(1)}" y="${H - padB + 18}" text-anchor="middle" font-family="Consolas,monospace" font-size="11" fill="#94a3b8">${fmt(d)}</text>`;
    });
    svg += `<text x="${W / 2}" y="${H - 5}" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#cbd5e1">Día (índice 0 a 999.999) — Tramo óptimo resaltado en verde: [${fmt(pa.inicio)} .. ${fmt(pa.fin)}]</text>`;

    svg += `</svg>`;
    document.getElementById("p4a-grafico-svg").innerHTML = svg;
  }

  function renderTimelineParteB(top10, n) {
    const W = 820;
    const H = 128;
    const padL = 30;
    const padR = 30;
    const trackW = W - padL - padR;
    const colors = [
      "#34d399", "#22d3ee", "#fbbf24", "#c084fc", "#fb7185",
      "#60a5fa", "#4ade80", "#f472b6", "#facc15", "#38bdf8",
    ];

    let svg = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">`;
    svg += `<text x="${padL}" y="22" font-family="Segoe UI,sans-serif" font-size="12.5" font-weight="700" fill="#cbd5e1">Mapa temporal de los 10 períodos contiguos disjuntos sobre [0 .. 999.999]:</text>`;
    svg += `<rect x="${padL}" y="42" width="${trackW}" height="34" rx="7" fill="#111827" stroke="#334155" />`;

    top10.forEach((it, idx) => {
      const x = padL + (it.inicio / n) * trackW;
      const w = Math.max(5, ((it.fin - it.inicio + 1) / n) * trackW);
      const col = colors[idx % colors.length];
      svg += `<rect x="${x.toFixed(1)}" y="44" width="${w.toFixed(1)}" height="30" rx="4" fill="${col}" opacity="0.86">
        <title>#${it.rank}: utilidad +${fmt(it.utilidad)} [${fmt(it.inicio)}..${fmt(it.fin)}]</title>
      </rect>`;
      if (w >= 16) {
        svg += `<text x="${(x + w / 2).toFixed(1)}" y="63" text-anchor="middle" font-family="Consolas,monospace" font-size="11" font-weight="800" fill="#090e1a">#${it.rank}</text>`;
      }
    });

    [0, 250000, 500000, 750000, 1000000].forEach((d) => {
      const x = padL + (d / n) * trackW;
      svg += `<text x="${x.toFixed(1)}" y="96" text-anchor="middle" font-family="Consolas,monospace" font-size="11" fill="#94a3b8">${fmt(d)}</text>`;
    });
    svg += `<text x="${W / 2}" y="116" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#6ee7b7">Pasa el mouse sobre cada bloque para ver su utilidad e índices exactos · 0 solapamientos</text>`;
    svg += `</svg>`;

    document.getElementById("p4b-timeline-svg").innerHTML = svg;
  }

  /* ==========================================================================
     INICIALIZACIÓN GLOBAL
     ========================================================================== */
  renderPunto1();
  initPunto2();
  initPunto3();
  initPunto4();
})();

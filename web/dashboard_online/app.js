const config = window.SUPABASE_DASHBOARD_CONFIG || {};

const formatNumber = (value) =>
  new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(value ?? 0);

const formatDateTime = (value) => {
  if (!value) return "Sem publicacao";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(parsed);
};

const decisionBadgeClass = (decision) => {
  if (decision === "Atacar Agora") return "attack";
  if (decision === "Aprofundar Analise") return "deep";
  if (decision === "Monitorar") return "monitor";
  return "discard";
};

async function fetchSnapshot() {
  const url =
    `${config.projectUrl}/rest/v1/${config.currentTable}` +
    `?dashboard_slug=eq.${encodeURIComponent(config.dashboardSlug)}` +
    `&select=payload,generated_at,executed_at`;

  const response = await fetch(url, {
    headers: {
      apikey: config.anonKey,
      Authorization: `Bearer ${config.anonKey}`,
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Falha ao ler dashboard online: ${response.status}`);
  }

  const rows = await response.json();
  if (!rows.length) {
    throw new Error("Nenhum snapshot encontrado no banco online.");
  }
  return rows[0];
}

function renderKpis(kpis) {
  const items = [
    ["Registros", kpis.records_total],
    ["No radar", kpis.radar_matches],
    ["Ativos no RS", kpis.rio_grande_do_sul],
    ["Ataque operacional", kpis.attack_now],
    ["Ataque investimento", kpis.investment_attack_now],
  ];

  document.getElementById("kpi-grid").innerHTML = items
    .map(
      ([label, value]) => `
        <article class="kpi-card">
          <span class="status-label">${label}</span>
          <strong>${formatNumber(value)}</strong>
        </article>
      `,
    )
    .join("");
}

function renderMetricList(containerId, items) {
  document.getElementById(containerId).innerHTML = items
    .map(
      (item) => `
        <div class="metric-row">
          <span>${item.label}</span>
          <span>${formatNumber(item.value)}</span>
        </div>
      `,
    )
    .join("");
}

function renderRadarCities(items) {
  document.getElementById("radar-cities").innerHTML = items
    .map((item) => `<span class="tag">${item.city_state} | ${item.priority}</span>`)
    .join("");
}

function renderOpportunities(items) {
  document.getElementById("opportunities-body").innerHTML = items
    .map(
      (item) => `
        <tr>
          <td><strong>${item.investment_score.toFixed(2)}</strong></td>
          <td><span class="badge ${decisionBadgeClass(item.investment_decision)}">${item.investment_decision}</span></td>
          <td><a class="record-link" href="${item.link || "#"}" target="_blank" rel="noreferrer">${item.title || "-"}</a></td>
          <td>${[item.city, item.state].filter(Boolean).join(" / ") || "-"}</td>
          <td>${item.source_name || "-"}</td>
          <td>${item.price_label || "-"}</td>
          <td>${item.discount_label || "-"}</td>
        </tr>
      `,
    )
    .join("");
}

async function loadOnlineDashboard() {
  const row = await fetchSnapshot();
  const payload = row.payload || {};

  document.getElementById("generated-at").textContent = formatDateTime(row.generated_at || payload.generated_at);
  document.getElementById("status-line").textContent =
    `${payload.status?.project_stage || "Sem status"} | ${payload.status?.dashboard_stage || "Sem fase"}`;

  renderKpis(payload.kpis || {});
  renderMetricList("decision-list", payload.decision_breakdown || []);
  renderMetricList("investment-list", payload.investment_breakdown || []);
  renderRadarCities(payload.radar_cities || []);
  renderOpportunities((payload.all_opportunities || []).slice(0, 20));
}

document.getElementById("refresh-button").addEventListener("click", () => {
  loadOnlineDashboard().catch((error) => {
    document.getElementById("status-line").textContent = error.message;
  });
});

loadOnlineDashboard().catch((error) => {
  document.getElementById("status-line").textContent = error.message;
});

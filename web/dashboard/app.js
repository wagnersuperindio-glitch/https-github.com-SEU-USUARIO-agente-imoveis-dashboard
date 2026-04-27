const formatNumber = (value) =>
  new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(value ?? 0);

const formatDateTime = (value) => {
  if (!value) return "Sem execucao registrada";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(parsed);
};

let allOpportunities = [];

const decisionBadgeClass = (decision) => {
  if (decision === "Atacar Agora") return "attack";
  if (decision === "Aprofundar Analise") return "deep";
  if (decision === "Monitorar") return "monitor";
  return "discard";
};

function renderKpis(kpis) {
  const items = [
    ["Conectores previstos", kpis.connectors_total, "Escopo total de captura que o painel acompanha."],
    ["Fontes com sucesso", kpis.success_sources, "Fontes que responderam na ultima execucao validada."],
    ["Fontes com erro", kpis.blocked_sources, "Fontes que exigem revisao tecnica ou protecao especial."],
    ["Registros carregados", kpis.records_total, "Base total enriquecida pelo motor atual."],
    ["No radar prioritario", kpis.radar_matches, "Ativos aderentes as cidades-alvo configuradas."],
    ["Ativos no RS", kpis.rio_grande_do_sul, "Cobertura geral do Rio Grande do Sul."],
    ["Ataque operacional", kpis.attack_now, "Ativos fortes pela triagem de operacao."],
    ["Ataque de investimento", kpis.investment_attack_now, "Melhores ativos para decisao de capital."],
    ["Entrou na semana", kpis.entered_week, "Ativos novos desde a ultima segunda."],
    ["Mudou na semana", kpis.changed_week, "Ativos alterados desde a ultima segunda."],
  ];

  document.getElementById("kpi-grid").innerHTML = items
    .map(
      ([label, value, description]) => `
        <article class="kpi-card">
          <span class="status-label">${label}</span>
          <strong>${formatNumber(value)}</strong>
          <p>${description}</p>
        </article>
      `,
    )
    .join("");
}

function renderMetricList(containerId, items) {
  const container = document.getElementById(containerId);
  container.innerHTML = items
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

function renderBlockedSources(items) {
  const container = document.getElementById("blocked-list");
  if (!items.length) {
    container.innerHTML = '<div class="movement-empty">Nenhuma fonte com erro na ultima execucao.</div>';
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <div class="blocked-item">
          <div>
            <strong>${item.source_name}</strong>
            <small>${item.connector_name}</small>
          </div>
          <small>${item.error}</small>
        </div>
      `,
    )
    .join("");
}

function renderExecutionHistory(items) {
  const container = document.getElementById("execution-history");
  if (!items.length) {
    container.innerHTML = '<div class="movement-empty">Sem execucoes registradas para exibir.</div>';
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <div class="metric-row">
          <div class="history-main">
            <strong>${formatDateTime(item.executed_at)}</strong>
            <small>${formatNumber(item.connectors_success)}/${formatNumber(item.connectors_total)} fontes com sucesso | ${formatNumber(item.records_total)} registros</small>
          </div>
          <span>${item.connectors_error ? `${formatNumber(item.connectors_error)} erro(s)` : "OK"}</span>
        </div>
      `,
    )
    .join("");
}

function renderReportHistory(items) {
  const container = document.getElementById("report-history");
  if (!items.length) {
    container.innerHTML = '<div class="movement-empty">Sem relatorios registrados para exibir.</div>';
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <div class="metric-row">
          <div class="history-main">
            <strong>${item.name}</strong>
            <small>${formatDateTime(item.updated_at)}</small>
          </div>
          <span>Markdown</span>
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

function renderWeeklySummary(summary) {
  const items = [
    ["Entradas", summary.entered_total ?? 0],
    ["Mudancas", summary.changed_total ?? 0],
    ["Saidas", summary.exited_total ?? 0],
  ];

  document.getElementById("weekly-summary").innerHTML = items
    .map(
      ([label, value]) => `
        <article class="summary-card">
          <span class="status-label">${label}</span>
          <strong>${formatNumber(value)}</strong>
        </article>
      `,
    )
    .join("");
}

function renderMovementList(containerId, totalId, items) {
  document.getElementById(totalId).textContent = formatNumber(items.length);
  const container = document.getElementById(containerId);

  if (!items.length) {
    container.innerHTML = '<div class="movement-empty">Sem itens neste bloco ate o momento.</div>';
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="movement-item">
          <div class="movement-item-main">
            <strong>${item.title}</strong>
            <small>${item.asset_type} | ${item.city} / ${item.state} | ${item.source_name}</small>
          </div>
          <div class="movement-item-side">
            ${item.link ? `<a class="record-link" href="${item.link}" target="_blank" rel="noreferrer">${item.price_label}</a>` : `<small>${item.price_label}</small>`}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderOpportunities(items) {
  document.getElementById("opportunities-body").innerHTML = items
    .map(
      (item) => `
        <tr>
          <td><strong>${item.investment_score.toFixed(2)}</strong></td>
          <td><span class="badge ${decisionBadgeClass(item.investment_decision)}">${item.investment_decision}</span></td>
          <td><strong>${item.operational_score.toFixed(2)}</strong></td>
          <td><span class="badge ${decisionBadgeClass(item.decision)}">${item.decision}</span></td>
          <td>
            <div class="opportunity-title">
              <a class="record-link" href="${item.link || "#"}" target="_blank" rel="noreferrer">${item.title || "-"}</a>
            </div>
            <div class="opportunity-meta">${item.asset_type || "-"} | ${item.event_stage || "Sem etapa"} | m² ${item.price_per_m2_label}</div>
          </td>
          <td>${[item.city, item.state].filter(Boolean).join(" / ") || "-"}</td>
          <td>${item.source_name}</td>
          <td>${item.price_label}</td>
          <td>${item.discount_label}</td>
          <td>${item.area_label}</td>
        </tr>
      `,
    )
    .join("");
}

function populateFilterOptions(payload) {
  const mapping = [
    ["source-filter", payload.filters.sources, "Todas as fontes"],
    ["decision-filter", payload.filters.decisions, "Todas as decisoes operacionais"],
    ["investment-filter", payload.filters.investment_decisions, "Todas as decisoes de investimento"],
    ["state-filter", payload.filters.states, "Todos os estados"],
    ["geo-filter", payload.filters.geo_status, "Todos os status geograficos"],
  ];

  mapping.forEach(([id, values, firstLabel]) => {
    const select = document.getElementById(id);
    select.innerHTML =
      `<option value="">${firstLabel}</option>` +
      values.map((value) => `<option value="${value}">${value}</option>`).join("");
  });
}

function applyFilters() {
  const search = document.getElementById("search-input").value.trim().toLowerCase();
  const source = document.getElementById("source-filter").value;
  const decision = document.getElementById("decision-filter").value;
  const investment = document.getElementById("investment-filter").value;
  const state = document.getElementById("state-filter").value;
  const geo = document.getElementById("geo-filter").value;

  const filtered = allOpportunities.filter((item) => {
    const haystack = `${item.title} ${item.asset_type} ${item.city} ${item.state} ${item.source_name}`.toLowerCase();
    if (search && !haystack.includes(search)) return false;
    if (source && item.source_name !== source) return false;
    if (decision && item.decision !== decision) return false;
    if (investment && item.investment_decision !== investment) return false;
    if (state && item.state !== state) return false;
    if (geo && item.geo_status !== geo) return false;
    return true;
  });

  renderOpportunities(filtered.slice(0, 150));
}

function renderAccess(access) {
  document.getElementById("access-mode").textContent = access.access_mode || "Painel interno";
  document.getElementById("local-url").href = access.local_url || "#";
  document.getElementById("network-url").href = access.network_url || "#";
  document.getElementById("access-note").textContent = access.https_enabled
    ? "Painel com HTTPS ativo. Compartilhe apenas com pessoas autorizadas."
    : "Painel sem HTTPS ainda. Recomenda-se uso em rede interna confiavel ou VPN.";
  document.getElementById("security-mode").textContent = access.https_enabled ? "HTTPS ativo" : "HTTP interno";
}

function renderUser(auth) {
  const user = auth?.user;
  document.getElementById("user-display").textContent = user?.display_name || "Nao autenticado";
  document.getElementById("user-role").textContent = user?.role ? `Perfil: ${user.role}` : "Sem perfil carregado";
}

function showLoginGate(message = "Use um usuario autorizado da empresa para liberar o dashboard.") {
  document.getElementById("login-gate").classList.remove("hidden");
  document.getElementById("gate-error").textContent = message;
}

function hideLoginGate() {
  document.getElementById("login-gate").classList.add("hidden");
}

async function login() {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();

  if (!username || !password) {
    showLoginGate("Informe usuario e senha para entrar no painel.");
    return;
  }

  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    showLoginGate(payload.message || "Falha de autenticacao.");
    throw new Error("Falha de autenticacao");
  }

  hideLoginGate();
  document.getElementById("login-password").value = "";
  await loadDashboard();
}

async function logout() {
  await fetch("/api/auth/logout", { method: "POST" });
  renderUser(null);
  showLoginGate("Sessao encerrada. Entre novamente para acessar o painel.");
}

async function loadSession() {
  const response = await fetch("/api/auth/session", { cache: "no-store" });
  if (!response.ok) {
    renderUser(null);
    showLoginGate("Entre com seu usuario corporativo para acessar o painel.");
    throw new Error("Sessao inexistente");
  }
  const payload = await response.json();
  renderUser(payload);
  hideLoginGate();
  return payload;
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard", { cache: "no-store" });
  if (response.status === 401) {
    renderUser(null);
    showLoginGate("Sessao expirada ou inexistente. Entre novamente.");
    throw new Error("Nao autenticado");
  }
  const payload = await response.json();

  hideLoginGate();
  document.getElementById("project-stage").textContent =
    `${payload.status.project_stage} | ${payload.status.dashboard_stage}`;
  document.getElementById("execution-date").textContent =
    formatDateTime(payload.status.latest_execution.executed_at);
  document.getElementById("report-date").textContent =
    payload.status.last_report?.updated_at
      ? `Relatorio mais recente: ${formatDateTime(payload.status.last_report.updated_at)}`
      : "Sem relatorio mais recente";

  renderAccess(payload.access || {});
  renderUser(payload.auth || null);
  renderKpis(payload.kpis);
  renderWeeklySummary(payload.weekly_movement?.summary || {});
  renderMetricList("decision-list", payload.decision_breakdown);
  renderMetricList("investment-list", payload.investment_breakdown);
  renderMetricList("source-list", payload.source_breakdown);
  renderMetricList("radar-list", payload.radar_breakdown);
  renderBlockedSources(payload.blocked_sources || []);
  renderExecutionHistory(payload.execution_history || []);
  renderReportHistory(payload.report_history || []);
  renderRadarCities(payload.radar_cities || []);
  renderMovementList("entered-list", "entered-total", payload.weekly_movement?.entered || []);
  renderMovementList("changed-list", "changed-total", payload.weekly_movement?.changed || []);
  renderMovementList("exited-list", "exited-total", payload.weekly_movement?.exited || []);

  allOpportunities = payload.all_opportunities || [];
  populateFilterOptions(payload);
  applyFilters();
}

document.getElementById("refresh-button").addEventListener("click", () => {
  loadDashboard().catch((error) => {
    if (error.message !== "Nao autenticado") {
      console.error(error);
    }
  });
});

document.getElementById("login-button").addEventListener("click", () => {
  login().catch((error) => {
    if (error.message !== "Falha de autenticacao") {
      console.error(error);
    }
  });
});

document.getElementById("logout-button").addEventListener("click", () => {
  logout().catch(console.error);
});

["login-username", "login-password"].forEach((id) => {
  document.getElementById(id).addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      login().catch((error) => {
        if (error.message !== "Falha de autenticacao") {
          console.error(error);
        }
      });
    }
  });
});

["search-input", "source-filter", "decision-filter", "investment-filter", "state-filter", "geo-filter"].forEach((id) => {
  const element = document.getElementById(id);
  element.addEventListener("input", applyFilters);
  element.addEventListener("change", applyFilters);
});

loadSession()
  .then(() => loadDashboard())
  .catch((error) => {
    if (error.message !== "Sessao inexistente") {
      console.error(error);
    }
  });

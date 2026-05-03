const config = window.SUPABASE_DASHBOARD_CONFIG || {};
const sessionStorageKey = "agente-imoveis-dashboard-session";
let allOpportunities = [];
let currentSession = null;

const authGate = document.getElementById("auth-gate");
const loginPanel = document.getElementById("login-panel");
const signupPanel = document.getElementById("signup-panel");
const passwordPanel = document.getElementById("password-panel");
const authStatus = document.getElementById("auth-status");
const currentUserEl = document.getElementById("current-user");
const sessionStatusEl = document.getElementById("session-status");
const logoutButton = document.getElementById("logout-button");
const refreshButton = document.getElementById("refresh-button");

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

const formatDateOnly = (value) => {
  if (!value) return "Sem data";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
  }).format(parsed);
};

const decisionBadgeClass = (decision) => {
  if (decision === "Atacar Agora") return "attack";
  if (decision === "Aprofundar Analise") return "deep";
  if (decision === "Monitorar") return "monitor";
  return "discard";
};

const typeBadgeClass = (type) => (type === "Leilao" ? "leilao" : "compra");

const auctionTimingBadgeClass = (timing) => {
  if (timing === "Data Futura") return "future";
  if (timing === "Data Passada") return "past";
  return "undated";
};

function setAuthStatus(message, tone = "neutral") {
  authStatus.textContent = message;
  authStatus.dataset.tone = tone;
}

function setSession(session) {
  currentSession = session || null;
  if (session) {
    localStorage.setItem(sessionStorageKey, JSON.stringify(session));
  } else {
    localStorage.removeItem(sessionStorageKey);
  }
  refreshSessionUi();
}

function readStoredSession() {
  try {
    const raw = localStorage.getItem(sessionStorageKey);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function showAuthPanel(target) {
  const panels = {
    login: loginPanel,
    signup: signupPanel,
    password: passwordPanel,
  };

  const tabs = {
    login: document.getElementById("login-tab"),
    signup: document.getElementById("signup-tab"),
    password: document.getElementById("password-tab"),
  };

  Object.entries(panels).forEach(([key, panel]) => {
    panel.classList.toggle("hidden", key !== target);
  });

  Object.entries(tabs).forEach(([key, button]) => {
    button.classList.toggle("auth-tab-active", key === target);
  });
}

function refreshSessionUi() {
  const email = currentSession?.user?.email || "Nao autenticado";
  const lastAuth = currentSession?.authenticated_at
    ? formatDateTime(currentSession.authenticated_at)
    : "Entre com usuario e senha.";

  currentUserEl.textContent = email;
  sessionStatusEl.textContent = currentSession ? `Sessao ativa desde ${lastAuth}` : "Entre para acessar o dashboard.";
  logoutButton.classList.toggle("hidden", !currentSession);
  authGate.classList.toggle("hidden", Boolean(currentSession));
  refreshButton.disabled = !currentSession;
}

async function authRequest(path, method, body, accessToken = "") {
  const response = await fetch(`${config.projectUrl}${path}`, {
    method,
    headers: {
      apikey: config.anonKey,
      Authorization: accessToken ? `Bearer ${accessToken}` : `Bearer ${config.anonKey}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.msg || payload.error_description || payload.error || `Falha ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

async function login() {
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value.trim();
  if (!email || !password) {
    setAuthStatus("Preencha usuario e senha para entrar.", "error");
    return;
  }

  setAuthStatus("Validando acesso...", "neutral");
  const payload = await authRequest("/auth/v1/token?grant_type=password", "POST", {
    email,
    password,
  });

  setSession({
    access_token: payload.access_token,
    refresh_token: payload.refresh_token,
    user: payload.user,
    authenticated_at: new Date().toISOString(),
  });
  setAuthStatus("Acesso liberado com sucesso.", "success");
  await loadOnlineDashboard();
}

async function signUp() {
  const email = document.getElementById("signup-email").value.trim();
  const password = document.getElementById("signup-password").value.trim();
  if (!email || !password) {
    setAuthStatus("Preencha e-mail e senha para cadastrar o usuario.", "error");
    return;
  }

  setAuthStatus("Criando usuario no ambiente online...", "neutral");
  const payload = await authRequest("/auth/v1/signup", "POST", {
    email,
    password,
  });

  if (payload.access_token) {
    setSession({
      access_token: payload.access_token,
      refresh_token: payload.refresh_token,
      user: payload.user,
      authenticated_at: new Date().toISOString(),
    });
    setAuthStatus("Usuario criado e autenticado.", "success");
    await loadOnlineDashboard();
    return;
  }

  setAuthStatus("Usuario criado. Se o Supabase exigir confirmacao, valide o e-mail antes de entrar.", "success");
}

async function changePassword() {
  if (!currentSession?.access_token) {
    setAuthStatus("Entre no painel antes de trocar a senha.", "error");
    showAuthPanel("login");
    return;
  }

  const newPassword = document.getElementById("new-password").value.trim();
  if (!newPassword) {
    setAuthStatus("Informe a nova senha.", "error");
    return;
  }

  setAuthStatus("Atualizando senha do usuario atual...", "neutral");
  await authRequest("/auth/v1/user", "PUT", { password: newPassword }, currentSession.access_token);
  setAuthStatus("Senha atualizada com sucesso.", "success");
}

function logout() {
  setSession(null);
  setAuthStatus("Sessao encerrada.", "neutral");
  showAuthPanel("login");
}

function classifyOpportunity(item) {
  const sourceText = `${item.source_name || ""} ${item.category || ""} ${item.event_stage || ""}`.toLowerCase();
  const isAuction =
    Boolean(item.event_stage) ||
    sourceText.includes("leil") ||
    sourceText.includes("banco_leilao") ||
    sourceText.includes("praca");

  const eventDate = item.event_date ? new Date(item.event_date) : null;
  const hasValidDate = eventDate && !Number.isNaN(eventDate.getTime());
  const now = new Date();

  let auctionTiming = "Nao se aplica";
  if (isAuction && hasValidDate) {
    auctionTiming = eventDate >= now ? "Data Futura" : "Data Passada";
  } else if (isAuction) {
    auctionTiming = "Sem Data";
  }

  return {
    ...item,
    opportunity_type: isAuction ? "Leilao" : "Compra Direta",
    auction_timing: auctionTiming,
    event_date_label: hasValidDate ? formatDateOnly(item.event_date) : "Sem data",
  };
}

async function fetchSnapshot() {
  if (!currentSession?.access_token) {
    throw new Error("Autenticacao obrigatoria para ler o dashboard.");
  }

  const url =
    `${config.projectUrl}/rest/v1/${config.currentTable}` +
    `?dashboard_slug=eq.${encodeURIComponent(config.dashboardSlug)}` +
    `&select=payload,generated_at,executed_at`;

  const response = await fetch(url, {
    headers: {
      apikey: config.anonKey,
      Authorization: `Bearer ${currentSession.access_token}`,
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      logout();
      throw new Error("Sessao expirada ou sem permissao. Entre novamente.");
    }
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
    ["Registros", kpis.records_total, "Base total atualmente publicada no dashboard externo."],
    ["No radar", kpis.radar_matches, "Ativos aderentes as cidades priorizadas."],
    ["Ativos no RS", kpis.rio_grande_do_sul, "Cobertura atual do estado no snapshot."],
    ["Ataque operacional", kpis.attack_now, "Triagem operacional forte para acao imediata."],
    ["Ataque investimento", kpis.investment_attack_now, "Decisoes de capital mais agressivas."],
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
  document.getElementById(containerId).innerHTML = items
    .map(
      (item) => `
        <div class="metric-row">
          <span>${item.label}</span>
          <strong>${formatNumber(item.value)}</strong>
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
          <td><span class="badge ${typeBadgeClass(item.opportunity_type)}">${item.opportunity_type}</span></td>
          <td>
            ${
              item.opportunity_type === "Leilao"
                ? `<span class="badge ${auctionTimingBadgeClass(item.auction_timing)}">${item.event_date_label}</span>`
                : '<span class="badge compra">Compra aberta</span>'
            }
          </td>
          <td><strong>${item.investment_score.toFixed(2)}</strong></td>
          <td><span class="badge ${decisionBadgeClass(item.investment_decision)}">${item.investment_decision}</span></td>
          <td>
            <div class="opportunity-title">
              <a class="record-link" href="${item.link || "#"}" target="_blank" rel="noreferrer">${item.title || "-"}</a>
            </div>
            <div class="opportunity-meta">${item.asset_type || "-"} | ${item.event_stage || "Sem etapa"} | ${item.price_per_m2_label || "-"}</div>
          </td>
          <td>${[item.city, item.state].filter(Boolean).join(" / ") || "-"}</td>
          <td>${item.source_name || "-"}</td>
          <td>${item.price_label || "-"}</td>
          <td>${item.discount_label || "-"}</td>
        </tr>
      `,
    )
    .join("");
}

function populateFilters(items) {
  const types = [...new Set(items.map((item) => item.opportunity_type))].sort();
  const auctionTimings = [...new Set(items.map((item) => item.auction_timing).filter(Boolean))].sort();
  const decisions = [...new Set(items.map((item) => item.decision).filter(Boolean))].sort();
  const investmentDecisions = [...new Set(items.map((item) => item.investment_decision).filter(Boolean))].sort();
  const cities = [...new Set(items.map((item) => item.city).filter(Boolean))].sort();

  const populate = (id, values, firstLabel) => {
    document.getElementById(id).innerHTML =
      `<option value="">${firstLabel}</option>` +
      values.map((value) => `<option value="${value}">${value}</option>`).join("");
  };

  populate("opportunity-type-filter", types, "Todos os tipos");
  populate("auction-timing-filter", auctionTimings, "Todas as situacoes de data");
  populate("decision-filter", decisions, "Todas as decisoes operacionais");
  populate("investment-filter", investmentDecisions, "Todas as decisoes de investimento");
  populate("city-filter", cities, "Todas as cidades");
}

function applyFilters() {
  const search = document.getElementById("search-input").value.trim().toLowerCase();
  const type = document.getElementById("opportunity-type-filter").value;
  const auctionTiming = document.getElementById("auction-timing-filter").value;
  const decision = document.getElementById("decision-filter").value;
  const investmentDecision = document.getElementById("investment-filter").value;
  const city = document.getElementById("city-filter").value;

  const filtered = allOpportunities.filter((item) => {
    const haystack =
      `${item.title || ""} ${item.city || ""} ${item.state || ""} ${item.source_name || ""} ${item.event_stage || ""}`.toLowerCase();
    if (search && !haystack.includes(search)) return false;
    if (type && item.opportunity_type !== type) return false;
    if (auctionTiming && item.auction_timing !== auctionTiming) return false;
    if (decision && item.decision !== decision) return false;
    if (investmentDecision && item.investment_decision !== investmentDecision) return false;
    if (city && item.city !== city) return false;
    return true;
  });

  renderOpportunities(filtered.slice(0, 40));
}

function buildCountList(items, key) {
  const counts = new Map();
  items.forEach((item) => {
    const label = item[key] || "-";
    counts.set(label, (counts.get(label) || 0) + 1);
  });
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([label, value]) => ({ label, value }));
}

async function loadOnlineDashboard() {
  const row = await fetchSnapshot();
  const payload = row.payload || {};
  const enriched = (payload.all_opportunities || []).map(classifyOpportunity);
  const weeklySummary = payload.weekly_movement?.summary || {};

  document.getElementById("generated-at").textContent = formatDateTime(row.generated_at || payload.generated_at);
  document.getElementById("executed-at").textContent = formatDateTime(row.executed_at || payload.status?.latest_execution?.executed_at);
  document.getElementById("status-line").textContent =
    `${payload.status?.project_stage || "Sem status"} | ${payload.status?.dashboard_stage || "Sem fase"}`;
  document.getElementById("update-window").textContent =
    `Atualizacao prevista: segunda e quarta | 10:00. Janela: ${formatNumber(weeklySummary.entered_total || 0)} entradas | ${formatNumber(weeklySummary.changed_total || 0)} mudancas | ${formatNumber(weeklySummary.exited_total || 0)} saidas`;

  renderKpis(payload.kpis || {});
  renderMetricList("decision-list", payload.decision_breakdown || []);
  renderMetricList("investment-list", payload.investment_breakdown || []);
  renderMetricList("opportunity-type-list", buildCountList(enriched, "opportunity_type"));
  renderMetricList("auction-timing-list", buildCountList(enriched.filter((item) => item.opportunity_type === "Leilao"), "auction_timing"));
  renderMetricList("weekly-summary", [
    { label: "Entrou desde a ultima segunda", value: weeklySummary.entered_total || 0 },
    { label: "Mudou desde a ultima segunda", value: weeklySummary.changed_total || 0 },
    { label: "Saiu desde a ultima segunda", value: weeklySummary.exited_total || 0 },
  ]);
  renderRadarCities(payload.radar_cities || []);

  allOpportunities = enriched;
  populateFilters(allOpportunities);
  applyFilters();
}

document.getElementById("login-tab").addEventListener("click", () => showAuthPanel("login"));
document.getElementById("signup-tab").addEventListener("click", () => showAuthPanel("signup"));
document.getElementById("password-tab").addEventListener("click", () => showAuthPanel("password"));
document.getElementById("login-button").addEventListener("click", () => {
  login().catch((error) => setAuthStatus(error.message, "error"));
});
document.getElementById("signup-button").addEventListener("click", () => {
  signUp().catch((error) => setAuthStatus(error.message, "error"));
});
document.getElementById("password-button").addEventListener("click", () => {
  changePassword().catch((error) => setAuthStatus(error.message, "error"));
});
logoutButton.addEventListener("click", logout);

refreshButton.addEventListener("click", () => {
  loadOnlineDashboard().catch((error) => {
    document.getElementById("status-line").textContent = error.message;
  });
});

["search-input", "opportunity-type-filter", "auction-timing-filter", "decision-filter", "investment-filter", "city-filter"].forEach((id) => {
  document.getElementById(id).addEventListener("input", applyFilters);
  document.getElementById(id).addEventListener("change", applyFilters);
});

setSession(readStoredSession());
showAuthPanel(currentSession ? "password" : "login");
setAuthStatus(currentSession ? "Sessao recuperada. Atualize o painel se precisar." : "Aguardando login.", "neutral");

if (currentSession) {
  loadOnlineDashboard().catch((error) => {
    document.getElementById("status-line").textContent = error.message;
  });
}

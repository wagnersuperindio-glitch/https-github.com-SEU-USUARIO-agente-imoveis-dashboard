const config = window.SUPABASE_DASHBOARD_CONFIG || {};
const sessionStorageKey = "agente-imoveis-dashboard-session";
const accessRequestsTable = config.accessRequestsTable || "dashboard_access_requests";

let allOpportunities = [];
let currentSession = null;
let accessRequests = [];

const authGate = document.getElementById("auth-gate");
const loginPanel = document.getElementById("login-panel");
const requestPanel = document.getElementById("request-panel");
const passwordPanel = document.getElementById("password-panel");
const authStatus = document.getElementById("auth-status");
const currentUserEl = document.getElementById("current-user");
const sessionStatusEl = document.getElementById("session-status");
const logoutButton = document.getElementById("logout-button");
const refreshButton = document.getElementById("refresh-button");
const adminPanel = document.getElementById("admin-panel");
const adminStatus = document.getElementById("admin-status");

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

function digitsOnly(value) {
  return (value || "").replace(/\D/g, "");
}

function userRole() {
  return currentSession?.user?.user_metadata?.role || "";
}

function isAdminSession() {
  return ["admin", "diretoria"].includes(userRole());
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
    request: requestPanel,
    password: passwordPanel,
  };

  const tabs = {
    login: document.getElementById("login-tab"),
    request: document.getElementById("request-tab"),
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
  adminPanel.classList.toggle("hidden", !currentSession || !isAdminSession());
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

async function restInsert(table, payload) {
  const response = await fetch(`${config.projectUrl}/rest/v1/${table}`, {
    method: "POST",
    headers: {
      apikey: config.anonKey,
      Authorization: `Bearer ${config.anonKey}`,
      "Content-Type": "application/json",
      Accept: "application/json",
      Prefer: "return=representation",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.message || data.error_description || data.error || `Falha ${response.status}`;
    throw new Error(message);
  }
  return data;
}

async function restSelect(table, query) {
  if (!currentSession?.access_token) {
    throw new Error("Sessao necessaria para consultar dados administrativos.");
  }

  const response = await fetch(`${config.projectUrl}/rest/v1/${table}${query}`, {
    method: "GET",
    headers: {
      apikey: config.anonKey,
      Authorization: `Bearer ${currentSession.access_token}`,
      Accept: "application/json",
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.message || data.error_description || data.error || `Falha ${response.status}`;
    throw new Error(message);
  }
  return data;
}

async function restPatch(table, query, payload) {
  if (!currentSession?.access_token) {
    throw new Error("Sessao necessaria para atualizar dados administrativos.");
  }

  const response = await fetch(`${config.projectUrl}/rest/v1/${table}${query}`, {
    method: "PATCH",
    headers: {
      apikey: config.anonKey,
      Authorization: `Bearer ${currentSession.access_token}`,
      "Content-Type": "application/json",
      Accept: "application/json",
      Prefer: "return=representation",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.message || data.error_description || data.error || `Falha ${response.status}`;
    throw new Error(message);
  }
  return data;
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
  await loadAccessRequests().catch((error) => {
    adminStatus.textContent = error.message;
  });
}

function buildAccessRequestPayload() {
  const fullName = document.getElementById("request-name").value.trim();
  const email = document.getElementById("request-email").value.trim().toLowerCase();
  const cpf = digitsOnly(document.getElementById("request-cpf").value);
  const documentType = document.getElementById("request-document-type").value.trim();
  const documentNumber = document.getElementById("request-document-number").value.trim();
  const phone = document.getElementById("request-phone").value.trim();
  const companyName = document.getElementById("request-company").value.trim();
  const roleRequested = document.getElementById("request-role").value.trim();
  const justification = document.getElementById("request-justification").value.trim();

  if (!fullName || !email || !cpf || !documentType || !documentNumber || !phone || !companyName || !roleRequested) {
    throw new Error("Preencha nome, e-mail, CPF, documento, telefone, empresa e perfil desejado.");
  }

  if (cpf.length !== 11) {
    throw new Error("CPF invalido. Informe os 11 digitos.");
  }

  return {
    full_name: fullName,
    email,
    cpf,
    document_type: documentType,
    document_number: documentNumber,
    phone,
    company_name: companyName,
    role_requested: roleRequested,
    justification,
    status: "pendente",
  };
}

function clearAccessRequestForm() {
  [
    "request-name",
    "request-email",
    "request-cpf",
    "request-document-type",
    "request-document-number",
    "request-phone",
    "request-company",
    "request-role",
    "request-justification",
  ].forEach((id) => {
    const element = document.getElementById(id);
    if (element) {
      element.value = "";
    }
  });
}

async function submitAccessRequest() {
  const payload = buildAccessRequestPayload();
  setAuthStatus("Enviando solicitacao para fila de aprovacao...", "neutral");
  await restInsert(accessRequestsTable, payload);
  setAuthStatus("Solicitacao enviada com sucesso. O acesso so sera liberado apos validacao administrativa.", "success");
  clearAccessRequestForm();
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

async function loadAccessRequests() {
  if (!isAdminSession()) {
    return;
  }

  adminStatus.textContent = "Carregando fila administrativa...";
  accessRequests = await restSelect(
    accessRequestsTable,
    "?select=id,created_at,reviewed_at,reviewed_by,status,full_name,email,cpf,document_type,document_number,phone,company_name,role_requested,justification&order=created_at.desc",
  );
  adminStatus.textContent =
    "Fila carregada. Aprovacao web altera o status da solicitacao; o provisionamento do usuario no Auth continua controlado via script administrativo.";
  applyRequestFilters();
}

function renderAccessRequests(items) {
  document.getElementById("requests-body").innerHTML = items
    .map((item) => {
      const cpfMasked =
        item.cpf && item.cpf.length === 11
          ? `${item.cpf.slice(0, 3)}.${item.cpf.slice(3, 6)}.${item.cpf.slice(6, 9)}-${item.cpf.slice(9)}`
          : item.cpf || "-";
      const canReview = item.status === "pendente";
      const copyCommand = `python .\\scripts\\aprovar_solicitacao_dashboard_online.py --request-id ${item.id} --approve --reviewed-by ${currentSession?.user?.email || "admin"}`;
      return `
        <tr>
          <td><span class="status-pill ${item.status}">${item.status}</span></td>
          <td>
            <strong>${item.full_name || "-"}</strong>
            <div class="request-meta">
              <span>${item.email || "-"}</span>
              <span>${item.phone || "-"}</span>
            </div>
          </td>
          <td>
            <div class="request-meta">
              <span>CPF: ${cpfMasked}</span>
              <span>${item.document_type || "-"}: ${item.document_number || "-"}</span>
            </div>
          </td>
          <td>
            <div class="request-meta">
              <span>${item.company_name || "-"}</span>
              <span>Perfil: ${item.role_requested || "-"}</span>
            </div>
          </td>
          <td>${item.justification || "-"}</td>
          <td>
            <div class="request-meta">
              <span>Solicitado: ${formatDateTime(item.created_at)}</span>
              <span>Revisado: ${formatDateTime(item.reviewed_at)}</span>
              <span>Por: ${item.reviewed_by || "-"}</span>
            </div>
          </td>
          <td>
            <div class="admin-actions">
              ${
                canReview
                  ? `
                <button class="admin-action-button approve" data-request-action="approve" data-request-id="${item.id}">Aprovar</button>
                <button class="admin-action-button reject" data-request-action="reject" data-request-id="${item.id}">Recusar</button>
              `
                  : ""
              }
              <button class="admin-action-button copy" data-request-action="copy" data-request-id="${item.id}" data-command="${encodeURIComponent(copyCommand)}">Copiar comando</button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function applyRequestFilters() {
  const status = document.getElementById("request-status-filter").value;
  const search = document.getElementById("request-search-input").value.trim().toLowerCase();

  const filtered = accessRequests.filter((item) => {
    const haystack = `${item.full_name || ""} ${item.email || ""} ${item.cpf || ""} ${item.company_name || ""}`.toLowerCase();
    if (status && item.status !== status) return false;
    if (search && !haystack.includes(search)) return false;
    return true;
  });

  renderAccessRequests(filtered);
}

async function reviewAccessRequest(requestId, nextStatus) {
  if (!isAdminSession()) {
    throw new Error("Apenas usuarios admin ou diretoria podem revisar solicitacoes.");
  }
  const reviewedBy = currentSession?.user?.email || currentSession?.user?.user_metadata?.display_name || "admin";
  const payload = {
    status: nextStatus,
    reviewed_by: reviewedBy,
    reviewed_at: new Date().toISOString(),
  };
  await restPatch(accessRequestsTable, `?id=eq.${requestId}`, payload);
  await loadAccessRequests();
}

async function copyProvisionCommand(encodedCommand) {
  const command = decodeURIComponent(encodedCommand);
  await navigator.clipboard.writeText(command);
  adminStatus.textContent = "Comando de provisionamento copiado. Use-o na maquina de operacao para criar o usuario final no Auth.";
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
document.getElementById("request-tab").addEventListener("click", () => showAuthPanel("request"));
document.getElementById("password-tab").addEventListener("click", () => showAuthPanel("password"));
document.getElementById("login-button").addEventListener("click", () => {
  login().catch((error) => setAuthStatus(error.message, "error"));
});
document.getElementById("request-button").addEventListener("click", () => {
  submitAccessRequest().catch((error) => setAuthStatus(error.message, "error"));
});
document.getElementById("password-button").addEventListener("click", () => {
  changePassword().catch((error) => setAuthStatus(error.message, "error"));
});
logoutButton.addEventListener("click", logout);
document.getElementById("refresh-requests-button").addEventListener("click", () => {
  loadAccessRequests().catch((error) => {
    adminStatus.textContent = error.message;
  });
});

refreshButton.addEventListener("click", () => {
  loadOnlineDashboard().catch((error) => {
    document.getElementById("status-line").textContent = error.message;
  });
});

["search-input", "opportunity-type-filter", "auction-timing-filter", "decision-filter", "investment-filter", "city-filter"].forEach((id) => {
  document.getElementById(id).addEventListener("input", applyFilters);
  document.getElementById(id).addEventListener("change", applyFilters);
});

["request-status-filter", "request-search-input"].forEach((id) => {
  document.getElementById(id).addEventListener("input", applyRequestFilters);
  document.getElementById(id).addEventListener("change", applyRequestFilters);
});

document.getElementById("requests-body").addEventListener("click", (event) => {
  const button = event.target.closest("[data-request-action]");
  if (!button) return;

  const action = button.dataset.requestAction;
  const requestId = button.dataset.requestId;
  if (action === "approve") {
    reviewAccessRequest(requestId, "aprovado").catch((error) => {
      adminStatus.textContent = error.message;
    });
    return;
  }
  if (action === "reject") {
    reviewAccessRequest(requestId, "recusado").catch((error) => {
      adminStatus.textContent = error.message;
    });
    return;
  }
  if (action === "copy") {
    copyProvisionCommand(button.dataset.command || "").catch((error) => {
      adminStatus.textContent = error.message;
    });
  }
});

setSession(readStoredSession());
showAuthPanel(currentSession ? "password" : "login");
setAuthStatus(
  currentSession
    ? "Sessao recuperada. Atualize o painel se precisar."
    : "Autoinscricao bloqueada. Solicite acesso com CPF, documento e dados obrigatorios.",
  "neutral",
);

if (currentSession) {
  loadOnlineDashboard().catch((error) => {
    document.getElementById("status-line").textContent = error.message;
  });
  loadAccessRequests().catch((error) => {
    adminStatus.textContent = error.message;
  });
}

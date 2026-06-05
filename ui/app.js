const state = {
  user: null,
  product: null,
  order: null,
  paymentMode: "unknown",
};

const services = [
  { name: "gateway", path: "/ready" },
  { name: "users", path: "/api/users/ready" },
  { name: "products", path: "/api/products/ready" },
  { name: "orders", path: "/api/orders/ready" },
  { name: "payments", path: "/api/payments/ready" },
  { name: "notifications", path: "/api/notifications/ready" },
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function newRequestId() {
  return `ui-${crypto.randomUUID()}`;
}

function requestHeaders(extra = {}) {
  return {
    "Content-Type": "application/json",
    "X-Request-ID": $("#requestId").value || newRequestId(),
    ...extra,
  };
}

function setBusy(button, busy) {
  if (!button) return;
  button.disabled = busy;
}

function renderJson(target, value) {
  target.textContent = JSON.stringify(value, null, 2);
}

function badge(label, kind = "neutral") {
  return `<span class="pill ${kind}">${label}</span>`;
}

function setOutputError(target, error) {
  target.textContent = error?.message || String(error);
}

function addActivity(method, path, status) {
  const log = $("#activityLog");
  const item = document.createElement("div");
  item.className = "activity-item";
  item.innerHTML = `
    <strong>${method}</strong>
    <code>${path}</code>
    ${badge(status, status >= 200 && status < 300 ? "ok" : "bad")}
  `;
  log.prepend(item);
  while (log.children.length > 20) {
    log.lastElementChild.remove();
  }
}

async function api(path, options = {}) {
  const method = options.method || "GET";
  const response = await fetch(path, {
    ...options,
    headers: requestHeaders(options.headers || {}),
  });
  addActivity(method, path, response.status);

  let body = null;
  const text = await response.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    const message = typeof body === "string" ? body : JSON.stringify(body);
    throw new Error(`${response.status} ${response.statusText}: ${message}`);
  }

  return { response, body };
}

async function refreshStatus() {
  const grid = $("#serviceGrid");
  grid.innerHTML = services
    .map((service) => `<div class="status-tile"><strong>${service.name}</strong>${badge("checking", "neutral")}</div>`)
    .join("");

  const results = await Promise.all(
    services.map(async (service) => {
      try {
        const { body } = await api(service.path);
        return { ...service, ok: true, detail: body?.status || "ready" };
      } catch (error) {
        return { ...service, ok: false, detail: "down" };
      }
    }),
  );

  grid.innerHTML = results
    .map(
      (result) => `
        <div class="status-tile">
          <strong>${result.name}</strong>
          ${badge(result.detail, result.ok ? "ok" : "bad")}
        </div>
      `,
    )
    .join("");
}

async function setPaymentMode(mode, button) {
  setBusy(button, true);
  try {
    const { body } = await api("/api/payments/test-controls/payment-mode", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
    state.paymentMode = body.mode;
    renderPaymentMode();
  } finally {
    setBusy(button, false);
  }
}

function renderPaymentMode() {
  $("#paymentModeStatus").textContent = state.paymentMode;
  $("#paymentModeStatus").className = `pill ${state.paymentMode === "success" ? "ok" : "warn"}`;
  $$("[data-payment-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.paymentMode === state.paymentMode);
  });
}

function fillDefaults() {
  $("#requestId").value = newRequestId();
  $("#userEmail").value = `qa-${crypto.randomUUID().slice(0, 8)}@example.com`;
}

function selectUser(user) {
  state.user = user;
  $("#selectedUserBadge").textContent = user.id.slice(0, 8);
  $("#selectedUserBadge").className = "pill ok";
  $("#orderUserId").value = user.id;
}

function selectProduct(product) {
  state.product = product;
  $("#selectedProductBadge").textContent = product.id.slice(0, 8);
  $("#selectedProductBadge").className = "pill ok";
  $("#orderProductId").value = product.id;
}

function selectOrder(order) {
  state.order = order;
  $("#selectedOrderBadge").textContent = `${order.status} ${order.id.slice(0, 8)}`;
  $("#selectedOrderBadge").className = `pill ${order.status === "paid" ? "ok" : "warn"}`;
}

async function createUser(event) {
  event.preventDefault();
  const button = event.submitter;
  setBusy(button, true);
  try {
    const { body } = await api("/api/users", {
      method: "POST",
      body: JSON.stringify({
        email: $("#userEmail").value,
        full_name: $("#userFullName").value,
      }),
    });
    selectUser(body);
    renderJson($("#userOutput"), body);
    $("#userEmail").value = `qa-${crypto.randomUUID().slice(0, 8)}@example.com`;
  } catch (error) {
    setOutputError($("#userOutput"), error);
  } finally {
    setBusy(button, false);
  }
}

async function createProduct(event) {
  event.preventDefault();
  const button = event.submitter;
  setBusy(button, true);
  try {
    const { body } = await api("/api/products", {
      method: "POST",
      body: JSON.stringify({
        name: $("#productName").value,
        description: $("#productDescription").value,
        price: Number($("#productPrice").value).toFixed(2),
        currency: "USD",
        stock: Number($("#productStock").value),
      }),
    });
    selectProduct(body);
    renderJson($("#productOutput"), body);
    $("#cacheResult").innerHTML = "";
  } catch (error) {
    setOutputError($("#productOutput"), error);
  } finally {
    setBusy(button, false);
  }
}

async function checkCache() {
  const productId = state.product?.id || $("#orderProductId").value;
  if (!productId) {
    $("#cacheResult").innerHTML = badge("no product", "bad");
    return;
  }

  const button = $("#checkCache");
  setBusy(button, true);
  try {
    const first = await api(`/api/products/${productId}`);
    const second = await api(`/api/products/${productId}`);
    const firstCache = first.response.headers.get("x-cache") || "none";
    const secondCache = second.response.headers.get("x-cache") || "none";
    $("#cacheResult").innerHTML = `${badge(`first ${firstCache}`, firstCache === "MISS" ? "warn" : "ok")} ${badge(`second ${secondCache}`, secondCache === "HIT" ? "ok" : "warn")}`;
    renderJson($("#productOutput"), second.body);
  } catch (error) {
    $("#cacheResult").innerHTML = badge("cache check failed", "bad");
    setOutputError($("#productOutput"), error);
  } finally {
    setBusy(button, false);
  }
}

async function createOrder(event) {
  event.preventDefault();
  const button = event.submitter;
  setBusy(button, true);
  try {
    const { body } = await api("/api/orders", {
      method: "POST",
      body: JSON.stringify({
        user_id: $("#orderUserId").value,
        items: [
          {
            product_id: $("#orderProductId").value,
            quantity: Number($("#orderQuantity").value),
          },
        ],
      }),
    });
    selectOrder(body);
    renderJson($("#orderOutput"), body);
    await waitForOrderNotification(body.id);
  } catch (error) {
    setOutputError($("#orderOutput"), error);
  } finally {
    setBusy(button, false);
  }
}

async function waitForOrderNotification(orderId) {
  const deadline = Date.now() + 12000;
  while (Date.now() < deadline) {
    const notifications = await loadNotifications({ orderId, quiet: true });
    if (notifications.some((item) => item.event_type === "order.paid" || item.event_type === "order.created")) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

async function loadNotifications(options = {}) {
  const orderId = options.orderId;
  const path = orderId ? `/api/notifications?order_id=${encodeURIComponent(orderId)}` : "/api/notifications";
  const { body } = await api(path);
  renderNotifications(body);
  return body;
}

function renderNotifications(items) {
  const tbody = $("#notificationsBody");
  if (!items.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">No notifications</td></tr>';
    return;
  }

  tbody.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${item.event_type}</td>
          <td><code>${item.order_id}</code></td>
          <td><code>${item.user_id}</code></td>
          <td>${badge(item.status, item.status === "created" ? "ok" : "neutral")}</td>
          <td>${new Date(item.created_at).toLocaleString()}</td>
        </tr>
      `,
    )
    .join("");
}

function bindEvents() {
  $("#newRequestId").addEventListener("click", () => {
    $("#requestId").value = newRequestId();
  });

  $("#refreshStatus").addEventListener("click", refreshStatus);
  $("#userForm").addEventListener("submit", createUser);
  $("#productForm").addEventListener("submit", createProduct);
  $("#checkCache").addEventListener("click", checkCache);
  $("#orderForm").addEventListener("submit", createOrder);
  $("#loadNotifications").addEventListener("click", () => loadNotifications());
  $("#filterOrderNotifications").addEventListener("click", () => {
    if (state.order?.id) loadNotifications({ orderId: state.order.id });
  });
  $("#clearActivity").addEventListener("click", () => {
    $("#activityLog").innerHTML = "";
  });

  $$("[data-payment-mode]").forEach((button) => {
    button.addEventListener("click", () => setPaymentMode(button.dataset.paymentMode, button));
  });
}

async function boot() {
  fillDefaults();
  bindEvents();
  renderPaymentMode();
  await refreshStatus();
  await setPaymentMode("success");
  await loadNotifications();
}

boot().catch((error) => {
  addActivity("BOOT", "/", 500);
  console.error(error);
});

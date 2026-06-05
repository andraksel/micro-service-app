const STORE_KEY = "microservices-qa-lab-store";

const demoProducts = [
  {
    name: "Настольная лампа Aurora",
    legacyName: "Aurora Task Lamp",
    description: "Компактная латунная лампа с теплым регулируемым светом для вечерней работы.",
    price: "48.00",
    stock: 16,
    category: "workspace",
    image: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Дорожная сумка Harbor",
    legacyName: "Harbor Canvas Weekender",
    description: "Плотная сумка для коротких поездок, зарядок, блокнотов и ежедневных вещей.",
    price: "72.50",
    stock: 10,
    category: "travel",
    image: "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Портативная колонка EchoStone",
    legacyName: "EchoStone Portable Speaker",
    description: "Минималистичная беспроводная колонка с глубоким звуком для кухни, стола и небольших комнат.",
    price: "96.00",
    stock: 11,
    category: "audio",
    image: "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Набор блокнотов Meridian",
    legacyName: "Meridian Notebook Trio",
    description: "Три блокнота с плотной гладкой бумагой для планов, заметок и быстрых зарисовок.",
    price: "28.90",
    stock: 34,
    category: "workspace",
    image: "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Кофейный набор Ember",
    legacyName: "Ember Pour-Over Set",
    description: "Керамическая воронка, стеклянный сервер и фильтры для неспешного утреннего кофе.",
    price: "68.00",
    stock: 8,
    category: "home",
    image: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Органайзер для техники Orbit",
    legacyName: "Orbit Tech Organizer",
    description: "Тонкий органайзер с отделениями для кабелей, адаптеров, карт и USB-накопителей.",
    price: "39.75",
    stock: 21,
    category: "travel",
    image: "https://images.unsplash.com/photo-1622560480654-d96214fdc887?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Термобутылка Alpine",
    legacyName: "Alpine Insulated Bottle",
    description: "Матовая стальная бутылка, которая сохраняет воду холодной в дороге и во время долгих сессий.",
    price: "31.00",
    stock: 24,
    category: "travel",
    image: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Льняной плед Solace",
    legacyName: "Solace Linen Throw",
    description: "Мягкий тканый плед для кресла, дивана или спокойного домашнего рабочего места.",
    price: "54.00",
    stock: 13,
    category: "home",
    image: "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Алюминиевая подставка Pixel",
    legacyName: "Pixel Aluminum Stand",
    description: "Наклонная подставка для ноутбука, которая поднимает экран и освобождает место на столе.",
    price: "63.00",
    stock: 17,
    category: "workspace",
    image: "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Аромадиффузор Luna",
    legacyName: "Luna Glass Diffuser",
    description: "Стеклянный диффузор с мягким ароматом кедра и цитруса для дома и рабочего места.",
    price: "29.50",
    stock: 19,
    category: "home",
    image: "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Студийные наушники Monitor",
    legacyName: "Studio Monitor Headphones",
    description: "Закрытые наушники для фокусной работы, звонков, монтажа и спокойного прослушивания.",
    price: "119.00",
    stock: 6,
    category: "audio",
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
  },
  {
    name: "Настольный набор Terra",
    legacyName: "Terra Desktop Plant Kit",
    description: "Небольшое кашпо, грунтовая капсула и неприхотливое растение для рабочего стола.",
    price: "22.00",
    stock: 28,
    category: "home",
    image: "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=900&q=80",
  },
];

const fixtureProductLooks = [
  {
    displayName: "Док-станция Slate",
    description: "Компактный USB-C хаб для аккуратного рабочего места и быстрых подключений.",
    category: "workspace",
    image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Кроссовки Canyon Trail",
    description: "Легкие повседневные кроссовки с рельефной подошвой для прогулок и поездок.",
    category: "travel",
    image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Рюкзак Nomad",
    description: "Влагостойкий рюкзак с отделением для ноутбука и карманами для аксессуаров.",
    category: "travel",
    image: "https://images.unsplash.com/photo-1581605405669-fcdf81165afa?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Смарт-часы Aero",
    description: "Минималистичные часы для активности, таймеров и быстрых уведомлений.",
    category: "workspace",
    image: "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Камера Cobalt Instant",
    description: "Компактная камера для быстрых снимков, встреч и командных фото.",
    category: "home",
    image: "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Наушники Wave Buds",
    description: "Компактные беспроводные наушники с чистыми звонками и зарядным кейсом.",
    category: "audio",
    image: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Керамическая кружка Moss",
    description: "Увесистая керамическая кружка с матовой глазурью и удобной ручкой.",
    category: "home",
    image: "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Настольные часы Prism",
    description: "Аналоговые часы с тихим ходом и небольшой ореховой подставкой.",
    category: "workspace",
    image: "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Дорожные органайзеры Summit",
    description: "Три чехла на молнии для одежды, кабелей и мелких вещей в поездке.",
    category: "travel",
    image: "https://images.unsplash.com/photo-1581553680321-4fffae59fccd?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Настольный фонарь Vela",
    description: "Перезаряжаемый фонарь с мягким светом для полок, стола и прикроватной зоны.",
    category: "home",
    image: "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Настольная лампа Aurora",
    description: "Компактная латунная лампа с теплым регулируемым светом для вечерней работы.",
    category: "workspace",
    image: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Дорожная сумка Harbor",
    description: "Плотная сумка для коротких поездок, зарядок, блокнотов и ежедневных вещей.",
    category: "travel",
    image: "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Портативная колонка EchoStone",
    description: "Минималистичная беспроводная колонка с глубоким звуком для кухни, стола и небольших комнат.",
    category: "audio",
    image: "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Набор блокнотов Meridian",
    description: "Три блокнота с плотной гладкой бумагой для планов, заметок и быстрых зарисовок.",
    category: "workspace",
    image: "https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Кофейный набор Ember",
    description: "Керамическая воронка, стеклянный сервер и фильтры для неспешного утреннего кофе.",
    category: "home",
    image: "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Органайзер для техники Orbit",
    description: "Тонкий органайзер с отделениями для кабелей, адаптеров, карт и USB-накопителей.",
    category: "travel",
    image: "https://images.unsplash.com/photo-1622560480654-d96214fdc887?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Термобутылка Alpine",
    description: "Матовая стальная бутылка, которая сохраняет воду холодной в дороге и во время долгих сессий.",
    category: "travel",
    image: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Льняной плед Solace",
    description: "Мягкий тканый плед для кресла, дивана или спокойного домашнего рабочего места.",
    category: "home",
    image: "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Алюминиевая подставка Pixel",
    description: "Наклонная подставка для ноутбука, которая поднимает экран и освобождает место на столе.",
    category: "workspace",
    image: "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Аромадиффузор Luna",
    description: "Стеклянный диффузор с мягким ароматом кедра и цитруса для дома и рабочего места.",
    category: "home",
    image: "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Студийные наушники Monitor",
    description: "Закрытые наушники для фокусной работы, звонков, монтажа и спокойного прослушивания.",
    category: "audio",
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
  },
  {
    displayName: "Настольный набор Terra",
    description: "Небольшое кашпо, грунтовая капсула и неприхотливое растение для рабочего стола.",
    category: "home",
    image: "https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=900&q=80",
  },
];

const fixtureVariants = [
  "Графит",
  "Олива",
  "Марин",
  "Медь",
  "Айвори",
  "Индиго",
  "Кедр",
  "Кварц",
  "Можжевельник",
  "Янтарь",
  "Нордик",
  "Шалфей",
];

const categoryLabels = {
  workspace: "Рабочее место",
  home: "Дом",
  travel: "Путешествия",
  audio: "Аудио",
};

const orderStatusLabels = {
  created: "Создан",
  paid: "Оплачен",
  payment_failed: "Платеж отклонен",
  cancelled: "Отменен",
};

const accountStatusLabels = {
  active: "Активен",
  blocked: "Заблокирован",
  deleted: "Удален",
};

const eventTypeLabels = {
  "order.created": "Заказ создан",
  "order.paid": "Заказ оплачен",
  "order.cancelled": "Заказ отменен",
};

const state = {
  account: null,
  products: [],
  cart: {},
  orders: [],
  notificationsByOrder: {},
  filter: {
    search: "",
    category: "all",
    sort: "newest",
  },
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function money(value) {
  return `$${Number(value).toFixed(2)}`;
}

function requestHeaders(extra = {}) {
  return {
    "Content-Type": "application/json",
    "X-Request-ID": `store-${crypto.randomUUID()}`,
    ...extra,
  };
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: requestHeaders(options.headers || {}),
  });

  const text = await response.text();
  let body = null;
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

function loadLocalState() {
  const raw = localStorage.getItem(STORE_KEY);
  if (!raw) return;
  try {
    const saved = JSON.parse(raw);
    state.account = saved.account || null;
    state.cart = saved.cart || {};
  } catch {
    localStorage.removeItem(STORE_KEY);
  }
}

function saveLocalState() {
  localStorage.setItem(
    STORE_KEY,
    JSON.stringify({
      account: state.account,
      cart: state.cart,
    }),
  );
}

function stableIndex(value, length) {
  const key = String(value || "");
  let hash = 0;
  for (const char of key) {
    hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  }
  return hash % length;
}

function isFixtureProduct(product) {
  return (
    /^QA Product/i.test(product.name) ||
    /^API Test Product$/i.test(product.name) ||
    /pytest fixture/i.test(product.description || "") ||
    /API test/i.test(product.description || "") ||
    /Created from QA dashboard/i.test(product.description || "")
  );
}

function productCode(product) {
  const compact = String(product.id || product.name || "")
    .replace(/[^a-z0-9]/gi, "")
    .slice(-4)
    .toUpperCase();
  return compact || String(stableIndex(product.name, 900) + 100);
}

function productMeta(product, index = 0) {
  const productName = product.name.toLowerCase();
  const matched = demoProducts.find(
    (item) => item.name.toLowerCase() === productName || item.legacyName?.toLowerCase() === productName,
  );
  if (matched) {
    return {
      ...matched,
      displayName: matched.name,
      displayDescription: matched.description,
      isFixture: false,
    };
  }

  if (isFixtureProduct(product)) {
    const look = fixtureProductLooks[index % fixtureProductLooks.length];
    const variant = fixtureVariants[stableIndex(`${product.id || product.name}-variant`, fixtureVariants.length)];
    return {
      ...look,
      displayName: `${variant} ${look.displayName} ${productCode(product)}`,
      displayDescription: look.description,
      isFixture: true,
      sourceName: product.name,
    };
  }

  const fallback = demoProducts[index % demoProducts.length];
  return {
    ...fallback,
    displayName: product.name,
    displayDescription: product.description || fallback.description,
    isFixture: false,
  };
}

function enrichedProducts() {
  return state.products.map((product, index) => ({
    ...product,
    meta: product.meta || productMeta(product, index),
  }));
}

function filteredProducts() {
  const search = state.filter.search.toLowerCase();
  const category = state.filter.category;
  const sorted = enrichedProducts().filter((product) => {
    const matchesSearch =
      !search ||
      product.name.toLowerCase().includes(search) ||
      String(product.description || "").toLowerCase().includes(search) ||
      product.meta.displayName.toLowerCase().includes(search) ||
      product.meta.displayDescription.toLowerCase().includes(search) ||
      product.meta.category.toLowerCase().includes(search) ||
      String(categoryLabels[product.meta.category] || "").toLowerCase().includes(search);
    const matchesCategory = category === "all" || product.meta.category === category;
    return matchesSearch && matchesCategory;
  });

  sorted.sort((a, b) => {
    if (state.filter.sort === "price-asc") return Number(a.price) - Number(b.price);
    if (state.filter.sort === "price-desc") return Number(b.price) - Number(a.price);
    if (state.filter.sort === "stock-desc") return Number(b.stock) - Number(a.stock);
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return sorted;
}

async function refreshHealth() {
  const checks = [
    "/ready",
    "/api/users/ready",
    "/api/products/ready",
    "/api/orders/ready",
    "/api/payments/ready",
    "/api/notifications/ready",
  ];
  const results = await Promise.all(
    checks.map(async (path) => {
      try {
        const { body } = await api(path);
        return body.status === "ready";
      } catch {
        return false;
      }
    }),
  );

  const ok = results.every(Boolean);
  $("#storeHealthLabel").textContent = ok ? "Магазин работает" : "Есть проблемы с сервисами";
  $("#storeHealthDetail").textContent = ok
    ? "Каталог, оформление заказа, платежи и уведомления готовы"
    : "Открой QA Dashboard и проверь readiness сервисов";
  $("#storeHealthLabel").style.color = ok ? "var(--ok)" : "var(--bad)";
}

async function loadProducts() {
  const { body } = await api("/api/products");
  state.products = Array.isArray(body)
    ? body
        .filter((product) => product.status === "active")
        .map((product, index) => ({
          ...product,
          meta: productMeta(product, index),
        }))
    : [];
  renderCatalog();
  renderCart();
}

async function seedCatalog() {
  const existingNames = new Set(state.products.map((product) => product.name.toLowerCase()));
  $("#seedCatalog").disabled = true;
  try {
    for (const product of demoProducts) {
      if (existingNames.has(product.name.toLowerCase()) || existingNames.has(product.legacyName.toLowerCase())) continue;
      await api("/api/products", {
        method: "POST",
        body: JSON.stringify({
          name: product.name,
          description: product.description,
          price: product.price,
          currency: "USD",
          stock: product.stock,
        }),
      });
    }
    await loadProducts();
    showMessage("Демо-каталог готов.", "ok");
  } finally {
    $("#seedCatalog").disabled = false;
  }
}

function renderCatalog() {
  const grid = $("#catalogGrid");
  const products = filteredProducts();
  if (!products.length) {
    grid.innerHTML = `
      <div class="empty-state">
        <span>По текущим фильтрам ничего не найдено. Заполни демо-каталог или очисти поиск.</span>
      </div>
    `;
    return;
  }

  grid.innerHTML = products
    .map(
      (product) => `
        <article class="product-card">
          <div class="product-image" style="background-image: url('${product.meta.image}')"></div>
          <div class="product-body">
            <div class="product-title-row">
              <h3>${escapeHtml(product.meta.displayName)}</h3>
              <span class="price">${money(product.price)}</span>
            </div>
            <p class="product-description">${escapeHtml(product.meta.displayDescription)}</p>
            <div class="product-meta">
              ${badge(categoryLabels[product.meta.category] || product.meta.category, "muted")}
              ${badge(stockLabel(product.stock), product.stock > 5 ? "ok" : "warn")}
            </div>
            <button type="button" data-add-product="${product.id}" ${product.stock <= 0 ? "disabled" : ""}>
              В корзину
            </button>
          </div>
        </article>
      `,
    )
    .join("");

  $$("[data-add-product]").forEach((button) => {
    button.addEventListener("click", () => addToCart(button.dataset.addProduct));
  });
}

function badge(text, kind) {
  return `<span class="badge ${kind}">${escapeHtml(text)}</span>`;
}

function stockLabel(stock) {
  return stock > 0 ? `${stock} в наличии` : "Нет в наличии";
}

function addToCart(productId) {
  const product = state.products.find((item) => item.id === productId);
  if (!product) return;
  const current = state.cart[productId] || 0;
  state.cart[productId] = Math.min(current + 1, product.stock);
  saveLocalState();
  renderCart();
}

function updateCart(productId, delta) {
  const product = state.products.find((item) => item.id === productId);
  if (!product) return;
  const next = (state.cart[productId] || 0) + delta;
  if (next <= 0) {
    delete state.cart[productId];
  } else {
    state.cart[productId] = Math.min(next, product.stock);
  }
  saveLocalState();
  renderCart();
}

function clearCart() {
  state.cart = {};
  saveLocalState();
  renderCart();
}

function cartRows() {
  return Object.entries(state.cart)
    .map(([productId, quantity]) => {
      const product = state.products.find((item) => item.id === productId);
      if (!product) return null;
      return { product, quantity };
    })
    .filter(Boolean);
}

function renderCart() {
  const rows = cartRows();
  const totalItems = rows.reduce((sum, row) => sum + row.quantity, 0);
  const total = rows.reduce((sum, row) => sum + Number(row.product.price) * row.quantity, 0);

  $("#cartSummary").textContent = totalItems ? `${totalItems} шт. в корзине` : "Пока пусто";
  $("#cartTotal").textContent = money(total);

  if (!rows.length) {
    $("#cartItems").innerHTML = '<div class="empty-state">Добавь товары из каталога.</div>';
    $("#checkoutButton").disabled = true;
    return;
  }

  $("#checkoutButton").disabled = false;
  $("#cartItems").innerHTML = rows
    .map(
      ({ product, quantity }) => `
        <div class="cart-item">
          <div class="cart-item-row">
            <strong>${escapeHtml(product.meta.displayName)}</strong>
            <span>${money(Number(product.price) * quantity)}</span>
          </div>
          <div class="cart-item-row">
            <small>${money(product.price)} за шт.</small>
            <div class="quantity-control">
              <button type="button" data-cart-dec="${product.id}" aria-label="Уменьшить количество: ${escapeHtml(product.meta.displayName)}">-</button>
              <span>${quantity}</span>
              <button type="button" data-cart-inc="${product.id}" aria-label="Увеличить количество: ${escapeHtml(product.meta.displayName)}">+</button>
            </div>
          </div>
        </div>
      `,
    )
    .join("");

  $$("[data-cart-dec]").forEach((button) => button.addEventListener("click", () => updateCart(button.dataset.cartDec, -1)));
  $$("[data-cart-inc]").forEach((button) => button.addEventListener("click", () => updateCart(button.dataset.cartInc, 1)));
}

async function createAccount(event) {
  event.preventDefault();
  const button = event.submitter;
  button.disabled = true;
  try {
    const { body } = await api("/api/users", {
      method: "POST",
      body: JSON.stringify({
        email: $("#accountEmail").value,
        full_name: $("#accountName").value,
      }),
    });
    state.account = body;
    saveLocalState();
    renderAccount();
    await loadOrders();
    showMessage("Профиль создан. Теперь можно оформить заказ.", "ok");
  } catch (error) {
    showMessage(`Ошибка создания профиля: ${error.message}`, "bad");
  } finally {
    button.disabled = false;
  }
}

function renderAccount() {
  if (!state.account) {
    $("#accountBadge").textContent = "Гость";
    $("#accountBadge").className = "badge muted";
    $("#accountDetails").innerHTML = "<dt>Статус</dt><dd>Профиль не выбран</dd>";
    return;
  }

  $("#accountBadge").textContent = accountStatusLabels[state.account.status] || state.account.status;
  $("#accountBadge").className = `badge ${state.account.status === "active" ? "ok" : "warn"}`;
  $("#accountDetails").innerHTML = `
    <dt>Имя</dt><dd>${escapeHtml(state.account.full_name)}</dd>
    <dt>Email</dt><dd>${escapeHtml(state.account.email)}</dd>
    <dt>ID пользователя</dt><dd><code>${escapeHtml(state.account.id)}</code></dd>
    <dt>Статус</dt><dd>${escapeHtml(accountStatusLabels[state.account.status] || state.account.status)}</dd>
  `;
}

async function checkout() {
  if (!state.account) {
    showMessage("Перед оформлением заказа создай профиль покупателя.", "bad");
    location.hash = "#account";
    return;
  }

  const rows = cartRows();
  if (!rows.length) {
    showMessage("Корзина пустая.", "bad");
    return;
  }

  $("#checkoutButton").disabled = true;
  try {
    const { body } = await api("/api/orders", {
      method: "POST",
      body: JSON.stringify({
        user_id: state.account.id,
        items: rows.map(({ product, quantity }) => ({
          product_id: product.id,
          quantity,
        })),
      }),
    });
    clearCart();
    showMessage(
      `Заказ ${body.id.slice(0, 8)} создан. Статус: ${orderStatusLabels[body.status] || body.status}.`,
      body.status === "paid" ? "ok" : "bad",
    );
    await waitForNotifications(body.id);
    await loadOrders();
    location.hash = "#orders";
  } catch (error) {
    showMessage(`Ошибка оформления заказа: ${error.message}`, "bad");
  } finally {
    $("#checkoutButton").disabled = false;
  }
}

async function waitForNotifications(orderId) {
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) {
    const notifications = await loadNotifications(orderId);
    if (notifications.length) return;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

async function loadOrders() {
  if (!state.account) {
    state.orders = [];
    renderOrders();
    return;
  }
  const { body } = await api("/api/orders");
  state.orders = Array.isArray(body) ? body.filter((order) => order.user_id === state.account.id) : [];
  for (const order of state.orders.slice(0, 5)) {
    await loadNotifications(order.id);
  }
  renderOrders();
}

async function loadNotifications(orderId) {
  const { body } = await api(`/api/notifications?order_id=${encodeURIComponent(orderId)}`);
  state.notificationsByOrder[orderId] = Array.isArray(body) ? body : [];
  return state.notificationsByOrder[orderId];
}

function renderOrders() {
  const list = $("#ordersList");
  if (!state.account) {
    list.innerHTML = '<div class="empty-state">Создай профиль, чтобы увидеть историю заказов.</div>';
    return;
  }
  if (!state.orders.length) {
    list.innerHTML = '<div class="empty-state">Заказов пока нет. Добавь товары в корзину и оформи покупку.</div>';
    return;
  }

  list.innerHTML = state.orders
    .map((order) => {
      const events = state.notificationsByOrder[order.id] || [];
      return `
        <article class="order-card">
          <div class="order-topline">
            <div>
              <h3>Заказ <code>${escapeHtml(order.id)}</code></h3>
              <p>${new Date(order.created_at).toLocaleString()}</p>
            </div>
            ${badge(orderStatusLabels[order.status] || order.status, order.status === "paid" ? "ok" : order.status === "payment_failed" ? "bad" : "warn")}
          </div>
          <div class="order-items">
            ${order.items
              .map((item) => {
                const catalogProduct = state.products.find((product) => product.id === item.product_id);
                const productLabel = catalogProduct?.meta?.displayName || item.product_id;
                return `
                  <div class="order-line">
                    <span>${escapeHtml(productLabel)} x ${item.quantity}</span>
                    <strong>${money(Number(item.unit_price) * item.quantity)}</strong>
                  </div>
                `;
              })
              .join("")}
          </div>
          <div class="cart-total">
            <span>Итого</span>
            <strong>${money(order.total_amount)}</strong>
          </div>
          <div class="event-list">
            ${
              events.length
                ? events
                    .map(
                      (event) => `
                        <div class="event-line">
                          <span>${escapeHtml(eventTypeLabels[event.event_type] || event.event_type)}</span>
                          <small>${new Date(event.created_at).toLocaleTimeString()}</small>
                        </div>
                      `,
                    )
                    .join("")
                : '<div class="event-line"><span>Уведомление еще не загружено</span></div>'
            }
          </div>
        </article>
      `;
    })
    .join("");
}

function showMessage(text, kind = "ok") {
  const message = $("#checkoutMessage");
  message.hidden = false;
  message.className = `message ${kind}`;
  message.textContent = text;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fillDefaults() {
  $("#accountEmail").value = `store-${crypto.randomUUID().slice(0, 8)}@example.com`;
}

function bindEvents() {
  $("#refreshStore").addEventListener("click", boot);
  $("#seedCatalog").addEventListener("click", seedCatalog);
  $("#clearCart").addEventListener("click", clearCart);
  $("#checkoutButton").addEventListener("click", checkout);
  $("#accountForm").addEventListener("submit", createAccount);
  $("#refreshOrders").addEventListener("click", loadOrders);

  $("#searchInput").addEventListener("input", (event) => {
    state.filter.search = event.target.value;
    renderCatalog();
  });
  $("#categoryFilter").addEventListener("change", (event) => {
    state.filter.category = event.target.value;
    renderCatalog();
  });
  $("#sortSelect").addEventListener("change", (event) => {
    state.filter.sort = event.target.value;
    renderCatalog();
  });
}

async function boot() {
  await refreshHealth();
  await loadProducts();
  renderAccount();
  await loadOrders();
}

loadLocalState();
fillDefaults();
bindEvents();
renderAccount();
renderCart();
boot().catch((error) => showMessage(`Ошибка загрузки магазина: ${error.message}`, "bad"));

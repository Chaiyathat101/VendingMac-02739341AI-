// ── State ──
let allProducts = [];
let cart = {}; // { product_id: { product, quantity } }
let activeCategory = 'all';

// ── Load Products ──
async function loadProducts() {
  const grid = document.getElementById('product-grid');
  try {
    const res = await fetch('/products');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allProducts = await res.json();
    if (!Array.isArray(allProducts)) throw new Error('ข้อมูลไม่ถูกต้อง');
    renderCategoryFilter();
    renderProducts();
  } catch (e) {
    grid.innerHTML = `<p style="color:#e94560;padding:20px">โหลดสินค้าไม่สำเร็จ: ${e.message}<br><button onclick="loadProducts()" style="margin-top:8px;padding:6px 16px;cursor:pointer">ลองใหม่</button></p>`;
  }
}

const CATEGORY_LABELS = {
  'all':         '🗂️ ทั้งหมด',
  'general':     '➕ อื่นๆ',
  // ภาษาไทย (ใน DB จริง)
  'ปากกา':       '🖊️ ปากกา',
  'ดินสอ':       '✏️ ดินสอ',
  'กระดาษ':      '📄 กระดาษ',
  'สมุด':        '📓 สมุด',
  'ยางลบ':       '🩹 ยางลบ',
  'ไม้บรรทัด':   '📏 ไม้บรรทัด',
  'กรรไกร':      '✂️ กรรไกร',
  'เทป':         '🧻 เทป',
  'ที่เย็บกระดาษ': '🗜️ ที่เย็บกระดาษ',
  'มาร์คเกอร์':  '🖍️ มาร์คเกอร์',
  'ไฮไลท์':      '🟡 ไฮไลท์',
  'ลิควิดเปเปอร์': '⬜ ลิควิดเปเปอร์',
  'แฟ้ม':        '🗂️ แฟ้ม',
  'คลิป':        '📌 คลิป',
  'กาว':         '🧴 กาว',
  'อุปกรณ์':     '🔧 อุปกรณ์',
  // อังกฤษ (fallback)
  'pen':         '🖊️ ปากกา',
  'pencil':      '✏️ ดินสอ',
  'paper':       '📄 กระดาษ',
  'notebook':    '📓 สมุด',
  'eraser':      '🩹 ยางลบ',
  'ruler':       '📏 ไม้บรรทัด',
  'scissors':    '✂️ กรรไกร',
  'stapler':     '🗜️ ที่เย็บกระดาษ',
  'marker':      '🖍️ มาร์คเกอร์',
  'highlighter': '🟡 ไฮไลท์',
  'file':        '🗂️ แฟ้ม',
  'clip':        '📌 คลิป',
  'glue':        '🧴 กาว',
  'equipment':   '🔧 อุปกรณ์',
};

function getCategoryLabel(c) {
  return CATEGORY_LABELS[c] || CATEGORY_LABELS[c.toLowerCase()] || ('📦 ' + c);
}

function renderCategoryFilter() {
  const withImage = allProducts.filter(hasRealImage);
  const categories = ['all', ...new Set(withImage.map(p => p.category))];
  const bar = document.getElementById('category-filter');
  bar.innerHTML = categories.map(c => `
    <button class="filter-btn ${c === activeCategory ? 'active' : ''}"
      onclick="setCategory('${c}')">
      ${getCategoryLabel(c)}
    </button>
  `).join('');
}

function setCategory(cat) {
  activeCategory = cat;
  renderCategoryFilter();
  renderProducts();
}

function hasRealImage(p) {
  return p.image_url && p.image_url.startsWith('/static/');
}

function renderProducts() {
  const grid = document.getElementById('product-grid');
  const withImage = allProducts.filter(hasRealImage);
  const filtered = activeCategory === 'all'
    ? withImage
    : withImage.filter(p => p.category === activeCategory);

  if (!filtered.length) { grid.innerHTML = '<p class="loading">ไม่มีสินค้า</p>'; return; }

  grid.innerHTML = filtered.map(p => {
    const status = p.status_text;
    const soldOut = status === 'out_of_stock';
    const surcharge = p.price_surcharge;
    const inCart = cart[p.id] ? cart[p.id].quantity : 0;

    // รูปจริง หรือ emoji fallback
    const isRealImage = p.image_url && p.image_url.startsWith('/static/');
    const imgBlock = isRealImage
      ? `<img class="p-img" src="${p.image_url}" alt="${p.name}" onerror="this.style.display='none';this.nextElementSibling.style.display='block'">`
      : '';
    const emojiBlock = `<div class="p-emoji" ${isRealImage ? 'style="display:none"' : ''}>${p.image_url || '📦'}</div>`;

    return `
      <div class="product-card ${soldOut ? 'out_of_stock' : ''} ${inCart > 0 ? 'selected' : ''}">
        ${imgBlock}${emojiBlock}
        <div class="p-name">${p.name}</div>
        <div class="p-price">${p.price} ฿</div>
        <div class="p-stock">เหลือ ${p.stock} ชิ้น</div>
        <span class="badge ${status}">${p.status_label}</span>
        <div class="card-actions">
          ${inCart > 0 ? `
            <button class="add-btn minus-btn" onclick="event.stopPropagation();removeFromCart(${p.id})">−</button>
            <span class="qty-count">${inCart}</span>
          ` : '<span class="qty-count" style="opacity:0">0</span>'}
          <button class="add-btn plus-btn" onclick="event.stopPropagation();${soldOut ? '' : `addToCart(${p.id})`}"
            ${soldOut || getTotalQty() >= MAX_PER_ORDER ? 'disabled' : ''}>+</button>
        </div>
      </div>
    `;
  }).join('');
}

// ── Cart Drawer ──
function openCart() {
  document.getElementById('cart-drawer').classList.add('open');
  document.getElementById('cart-backdrop').classList.add('open');
}
function closeCart() {
  document.getElementById('cart-drawer').classList.remove('open');
  document.getElementById('cart-backdrop').classList.remove('open');
}

// ── Cart ──
const MAX_PER_ORDER = 3; // จำกัดสูงสุด 3 ชิ้นต่อรอบ

function getTotalQty() {
  return Object.values(cart).reduce((s, { quantity: q }) => s + q, 0);
}

function addToCart(id) {
  const product = allProducts.find(p => p.id === id);
  if (!product) return;
  if (getTotalQty() >= MAX_PER_ORDER) {
    showCartLimitWarning();
    return;
  }
  if (cart[id]) {
    if (cart[id].quantity >= product.stock) return;
    cart[id].quantity++;
  } else {
    cart[id] = { product, quantity: 1 };
  }
  renderCart();
  renderProducts();
}

function showCartLimitWarning() {
  // แสดง toast แจ้งเตือน
  let toast = document.getElementById('cart-limit-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'cart-limit-toast';
    toast.style.cssText = `
      position:fixed;bottom:110px;left:50%;transform:translateX(-50%);
      background:#e94560;color:white;padding:10px 22px;border-radius:24px;
      font-size:0.88rem;font-weight:700;z-index:9999;
      box-shadow:0 4px 16px rgba(233,69,96,0.4);
      font-family:'Sarabun',sans-serif;white-space:nowrap;
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = `⚠️ เลือกได้สูงสุด ${MAX_PER_ORDER} ชิ้นต่อ 1 รอบการซื้อ`;
  toast.style.display = 'block';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.style.display = 'none'; }, 2500);
}

function removeFromCart(id) {
  if (!cart[id]) return;
  cart[id].quantity--;
  if (cart[id].quantity <= 0) delete cart[id];
  renderCart();
  renderProducts();
}

function clearCart() {
  cart = {};
  renderCart();
  renderProducts();
}

function renderCart() {
  const items = Object.values(cart);

  // อัปเดต badge บน FAB -- แสดง X/3
  const totalQtyAll = items.reduce((s, { quantity: q }) => s + q, 0);
  const badge = document.getElementById('cart-badge');
  if (totalQtyAll > 0) {
    badge.textContent = `${totalQtyAll}/${MAX_PER_ORDER}`;
    badge.style.display = 'block';
    badge.style.background = totalQtyAll >= MAX_PER_ORDER ? '#e94560' : '#0f3460';
  } else {
    badge.style.display = 'none';
  }
  const container = document.getElementById('cart-items');

  if (!items.length) {
    container.innerHTML = '<p class="empty-cart">ยังไม่มีสินค้า</p>';
    document.getElementById('cart-total').textContent = '0 บาท';
    document.getElementById('cart-final').textContent = '0 บาท';
    document.getElementById('discount-row').style.display = 'none';
    return;
  }

  container.innerHTML = items.map(({ product: p, quantity: q }) => {
    return `
      <div class="cart-item">
        <div class="cart-item-name">${p.name}</div>
        <div class="cart-item-qty">
          <button class="qty-btn" onclick="removeFromCart(${p.id})">−</button>
          <span>${q}</span>
          <button class="qty-btn" onclick="addToCart(${p.id})">+</button>
        </div>
        <div class="cart-item-price">${(p.price * q).toFixed(0)} ฿</div>
      </div>
    `;
  }).join('');

  const subtotal = items.reduce((s, { product: p, quantity: q }) => s + p.price * q, 0);

  document.getElementById('cart-total').textContent = `${subtotal.toFixed(0)} บาท`;
  document.getElementById('cart-final').textContent = `${subtotal.toFixed(0)} บาท`;
  document.getElementById('discount-row').style.display = 'none';
}

// ── Checkout ──
async function checkout() {
  const items = Object.values(cart);
  if (!items.length) { alert('กรุณาเลือกสินค้าก่อน'); return; }

  const paymentMethod = document.getElementById('payment_method').value;
  const finalTotal = items.reduce((s, { product: p, quantity: q }) => s + p.price * q, 0);

  // QR Code -> แสดงหน้า QR ก่อน ไม่ต้องกรอกเงิน
  if (paymentMethod === 'qr_code') {
    showQRModal(finalTotal);
    return;
  }

  const amountPaid = parseFloat(document.getElementById('amount_paid').value);
  if (!amountPaid || amountPaid <= 0) { alert('กรุณากรอกจำนวนเงิน'); return; }

  if (amountPaid < finalTotal) {
    alert(`เงินไม่พอ ต้องจ่าย ${finalTotal} บาท`);
    return;
  }

  await submitOrder(paymentMethod, finalTotal, amountPaid);
}

function showQRModal(total) {
  const modal = document.getElementById('qr-modal');
  document.getElementById('qr-total-amount').textContent = total.toFixed(0);
  modal.style.display = 'flex';
}

function closeQRModal() {
  document.getElementById('qr-modal').style.display = 'none';
}

async function confirmQRPayment() {
  closeQRModal();
  const items = Object.values(cart);
  const finalTotal = items.reduce((s, { product: p, quantity: q }) => s + p.price * q, 0);
  await submitOrder('qr_code', finalTotal, finalTotal);
}

async function submitOrder(paymentMethod, finalTotal, amountPaid) {
  const items = Object.values(cart);
  let allOk = true;
  let errors = [];
  for (const { product: p, quantity: q } of items) {
    const payload = {
      product_id: p.id,
      quantity: q,
      payment_method: paymentMethod,
      amount_paid: p.price * q,
    };
    const res = await fetch('/sales', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) {
      const err = await res.json();
      errors.push(`${p.name}: ${err.detail}`);
      allOk = false;
    }
  }

  const change = amountPaid - finalTotal;
  showModal(allOk, { total: finalTotal, paid: amountPaid, change, errors });

  if (allOk) {
    clearCart();
    document.getElementById('amount_paid').value = '';
    await loadProducts();
  }
}

function showModal(success, data) {
  document.getElementById('modal-icon').textContent = success ? '✅' : '⚠️';
  document.getElementById('modal-title').textContent = success ? 'ขอบคุณค่ะ!' : 'มีข้อผิดพลาด';
  const body = document.getElementById('modal-body');
  if (success) {
    body.innerHTML = `
      <div class="modal-body-row"><span>ยอดรวม</span><span>${data.total} บาท</span></div>
      <div class="modal-body-row"><span>จ่ายแล้ว</span><span>${data.paid} บาท</span></div>
      <div class="modal-body-row"><b>เงินทอน</b><b style="color:#059669">${data.change.toFixed(0)} บาท</b></div>
      <div style="margin-top:16px;padding:14px;background:#f0fdf4;border-radius:10px;border:1px solid #86efac;text-align:center">
        <div style="font-size:1.8rem;margin-bottom:6px">📦</div>
        <div style="font-weight:700;color:#16a34a;font-size:1rem">กรุณารอรับสินค้าของคุณ</div>
        <div style="color:#15803d;font-size:0.85rem;margin-top:4px">สินค้าจะหล่นจากชั้นในเครื่องอัตโนมัติ</div>
      </div>
    `;
  } else {
    body.innerHTML = `<p style="color:#e94560">${data.errors.join('<br>')}</p>`;
  }
  document.getElementById('result-modal').style.display = 'flex';
}

function closeModal() {
  document.getElementById('result-modal').style.display = 'none';
}

// ── Init ──
loadProducts();


// ── Chatbot Modal ──
function openChatbot() { document.getElementById('chatbot-modal').style.display = 'flex'; }
function closeChatbot() { document.getElementById('chatbot-modal').style.display = 'none'; }

function appendBubble(text, role) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `chat-bubble ${role}`;
  div.innerHTML = role === 'bot'
    ? `<div class="bubble-avatar">🤖</div><div class="bubble-text">${text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}</div>`
    : `<div class="bubble-text">${text}</div><div class="bubble-avatar">👤</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

function appendQuickReplies(replies) {
  if (!replies || !replies.length) return;
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-quick-replies';
  div.innerHTML = replies.map(r => `<button class="quick-reply-btn" onclick="sendQuick('${r}')">${r}</button>`).join('');
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function showTyping() {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-typing'; div.id = 'chat-typing';
  div.innerHTML = `<div class="bubble-avatar">🤖</div><div class="typing-dots"><span></span><span></span><span></span></div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}
function hideTyping() {
  const el = document.getElementById('chat-typing');
  if (el) el.remove();
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  // ลบ quick replies เก่า
  document.querySelectorAll('.chat-quick-replies').forEach(el => el.remove());
  appendBubble(text, 'user');
  showTyping();
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    await new Promise(r => setTimeout(r, 600)); // typing delay
    hideTyping();
    appendBubble(data.text || 'ขออภัย ไม่สามารถตอบได้ครับ', 'bot');
    appendQuickReplies(data.quick_replies);
  } catch (e) {
    hideTyping();
    appendBubble('เกิดข้อผิดพลาด กรุณาลองใหม่ครับ', 'bot');
  }
}

function sendQuick(text) {
  document.getElementById('chat-input').value = text;
  sendChat();
}

// ── Contact Modal ──
function openContact() { document.getElementById('contact-modal').style.display = 'flex'; }
function closeContact() { document.getElementById('contact-modal').style.display = 'none'; }

// ── Developer Modal ──
function openDev() { document.getElementById('dev-modal').style.display = 'flex'; }
function closeDev() { document.getElementById('dev-modal').style.display = 'none'; }

async function uploadDevPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch('/developer/image', { method: 'POST', body: form });
    const data = await res.json();
    if (data.image_url) {
      const img = document.getElementById('dev-photo');
      const placeholder = document.getElementById('dev-photo-placeholder');
      img.src = data.image_url + '?t=' + Date.now(); // cache bust
      img.style.display = 'block';
      placeholder.style.display = 'none';
    }
  } catch (e) {
    alert('อัปโหลดรูปไม่สำเร็จ');
  }
}

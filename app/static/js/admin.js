let isLoggedIn = false;

// ── Login ──
async function doLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch('/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (res.ok) {
    isLoggedIn = true;
    document.getElementById('login-overlay').style.display = 'none';
    document.getElementById('admin-content').style.display = 'block';
    loadAll();
  } else {
    document.getElementById('login-error').style.display = 'block';
  }
}

// ── Load All ──
async function loadAll() {
  await Promise.all([loadStats(), loadProducts(), loadSales()]);
}

async function loadStats() {
  const [productsRes, revenueRes] = await Promise.all([
    fetch('/products'), fetch('/sales/revenue'),
  ]);
  const products = await productsRes.json();
  const { total_revenue } = await revenueRes.json();

  const outOfStock = products.filter(p => p.status_text === 'out_of_stock').length;
  const lowStock = products.filter(p => p.status_text === 'low_stock').length;
  const restock = products.filter(p => p.forecast?.restock_recommended).length;

  document.getElementById('stats-row').innerHTML = `
    <div class="stat-card">
      <div class="s-val">${products.length}</div>
      <div class="s-label">สินค้าทั้งหมด</div>
    </div>
    <div class="stat-card">
      <div class="s-val" style="color:#e94560">${outOfStock}</div>
      <div class="s-label">หมด stock</div>
    </div>
    <div class="stat-card">
      <div class="s-val" style="color:#d97706">${lowStock}</div>
      <div class="s-label">ใกล้หมด</div>
    </div>
    <div class="stat-card">
      <div class="s-val" style="color:#7c3aed">${restock}</div>
      <div class="s-label">แนะนำเติม stock</div>
    </div>
    <div class="stat-card">
      <div class="s-val" style="color:#059669">${total_revenue.toFixed(0)}</div>
      <div class="s-label">รายได้รวม (บาท)</div>
    </div>
  `;
}

async function loadProducts() {
  const res = await fetch('/products');
  const products = await res.json();
  const tbody = document.getElementById('product-tbody');

  tbody.innerHTML = products.map(p => {
    const forecast = p.forecast || {};
    const statusClass = p.status_text === 'ok' ? 'ok' : p.status_text === 'low_stock' ? 'low_stock' : 'out_of_stock';
    const isRealImage = p.image_url && p.image_url.startsWith('/static/');
    const thumb = isRealImage
      ? `<img src="${p.image_url}?t=${Date.now()}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;border:1px solid #eee">`
      : `<span style="font-size:1.8rem">${p.image_url || '📦'}</span>`;

    return `
      <tr>
        <td>
          <label style="cursor:pointer" title="คลิกเพื่ออัปโหลดรูป">
            ${thumb}
            <input type="file" accept="image/*" style="display:none"
              onchange="uploadImage(${p.id}, this)">
          </label>
        </td>
        <td><b>${p.name}</b></td>
        <td>${p.category}</td>
        <td>${p.price} ฿ ${p.price_surcharge ? '<span class="badge surcharge">⬆</span>' : ''}</td>
        <td>${p.stock}</td>
        <td><span class="badge ${statusClass}">${p.status_label}</span></td>
        <td style="font-size:0.75rem;color:#666">${forecast.message || '-'}</td>
        <td>
          <button class="edit-btn" onclick="openEdit(${p.id})">✏️ แก้ไข</button>
          <button class="del-btn" onclick="deleteProduct(${p.id})">ลบ</button>
        </td>
      </tr>
    `;
  }).join('');
}

// ── Edit Modal ──
let _products = [];

async function openEdit(id) {
  // โหลดข้อมูลสดจาก API
  const res = await fetch(`/products/${id}`);
  const p = await res.json();

  document.getElementById('edit-id').value = p.id;
  document.getElementById('edit-name').value = p.name;
  document.getElementById('edit-price').value = p.price;
  document.getElementById('edit-stock').value = p.stock;
  document.getElementById('edit-threshold').value = p.low_stock_threshold;
  document.getElementById('edit-status').value = p.status;

  const catSel = document.getElementById('edit-category');
  // เพิ่ม option ถ้ายังไม่มี
  const exists = [...catSel.options].some(o => o.value === p.category);
  if (!exists) {
    const opt = document.createElement('option');
    opt.value = p.category;
    opt.textContent = p.category;
    catSel.appendChild(opt);
  }
  catSel.value = p.category;

  document.getElementById('edit-modal').style.display = 'flex';
}

function closeEdit() {
  document.getElementById('edit-modal').style.display = 'none';
}

async function saveEdit() {
  const id = document.getElementById('edit-id').value;
  const payload = {
    name:               document.getElementById('edit-name').value.trim(),
    price:              parseFloat(document.getElementById('edit-price').value),
    stock:              parseInt(document.getElementById('edit-stock').value),
    low_stock_threshold:parseInt(document.getElementById('edit-threshold').value) || 5,
    category:           document.getElementById('edit-category').value,
    status:             document.getElementById('edit-status').value,
  };

  if (!payload.name || isNaN(payload.price) || isNaN(payload.stock)) {
    alert('กรุณากรอกข้อมูลให้ครบ');
    return;
  }

  const res = await fetch(`/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (res.ok) {
    closeEdit();
    await loadAll();
  } else {
    const err = await res.json();
    alert('แก้ไขไม่สำเร็จ: ' + JSON.stringify(err.detail));
  }
}

async function uploadImage(productId, input) {
  const file = input.files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`/products/${productId}/image`, { method: 'POST', body: form });
  if (res.ok) {
    await loadProducts();
  } else {
    const err = await res.json();
    alert('อัปโหลดไม่สำเร็จ: ' + err.detail);
  }
}

async function loadSales() {
  const res = await fetch('/sales');
  const sales = await res.json();
  const container = document.getElementById('sales-list');
  if (!sales.length) { container.innerHTML = '<p style="color:#aaa">ยังไม่มีประวัติ</p>'; return; }
  container.innerHTML = sales.map(s => `
    <div class="sale-row">
      <div class="sr-name">${s.product_name} ×${s.quantity}</div>
      <div class="sr-price">${s.total_price} ฿</div>
      <div style="color:#aaa;font-size:0.75rem">${s.sold_at?.slice(0, 16) || ''}</div>
    </div>
  `).join('');
}

// ── Add Product ──
async function addProduct(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById('p_name').value,
    price: parseFloat(document.getElementById('p_price').value),
    stock: parseInt(document.getElementById('p_stock').value),
    low_stock_threshold: parseInt(document.getElementById('p_threshold').value) || 5,
    category: document.getElementById('p_category').value,
  };
  const res = await fetch('/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    document.getElementById('product-form').reset();
    await loadAll();
    alert(`เพิ่ม "${payload.name}" สำเร็จ`);
  } else {
    const err = await res.json();
    alert('Error: ' + JSON.stringify(err.detail));
  }
}

// ── Delete Product ──
async function deleteProduct(id) {
  if (!confirm('ลบสินค้านี้?')) return;
  const res = await fetch(`/products/${id}`, { method: 'DELETE' });
  if (res.ok) await loadAll();
}

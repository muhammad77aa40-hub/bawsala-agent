(function () {
  const C = window.CATALOG;
  const S = C.store;
  const byId = Object.fromEntries(C.products.map(p => [p.id, p]));
  const $ = s => document.querySelector(s);
  const $$ = s => document.querySelectorAll(s);
  const ar = n => n.toLocaleString('ar-IQ');
  const fmt = n => ar(n) + ' د.ع';
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const icon = id => `<svg aria-hidden="true"><use href="#${id}"/></svg>`;
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } }
  };

  /* ---------- product art (inline SVG, tinted per product) ---------- */
  let gid = 0;
  function art(p) {
    const t = p.tint, id = 'g' + (++gid);
    const grad = `<defs><linearGradient id="${id}" x1="0" x2="1"><stop offset="0" stop-color="${t}"/><stop offset=".45" stop-color="${t}" stop-opacity=".82"/><stop offset="1" stop-color="${t}"/></linearGradient></defs>`;
    const label = (x, y, w, h, fs) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" fill="#fbfaf6"/><text x="${x + w / 2}" y="${y + h * .45}" font-size="${fs}" text-anchor="middle" fill="${t}" font-family="IBM Plex Sans Arabic, sans-serif" font-weight="700">الرافدين</text><text x="${x + w / 2}" y="${y + h * .78}" font-size="${fs * .62}" text-anchor="middle" fill="#6e6e69" font-family="IBM Plex Sans Arabic, sans-serif"${p.name.length > 9 ? ` textLength="${w * .86}" lengthAdjust="spacingAndGlyphs"` : ''}>${esc(p.name)}</text>`;
    const shapes = {
      bottle: `<svg viewBox="0 0 100 220">${grad}<rect x="38" y="4" width="24" height="26" rx="4" fill="#2a2a28"/><rect x="41" y="28" width="18" height="18" fill="${t}" opacity=".9"/><path d="M41 46h18c0 10 21 14 21 34v120a14 14 0 0 1-14 14H34a14 14 0 0 1-14-14V80c0-20 21-24 21-34Z" fill="url(#${id})"/><rect x="26" y="88" width="6" height="104" rx="3" fill="#fff" opacity=".25"/>${label(30, 112, 40, 54, 9)}</svg>`,
      dropper: `<svg viewBox="0 0 100 200">${grad}<ellipse cx="50" cy="18" rx="12" ry="15" fill="#2a2a28"/><rect x="36" y="30" width="28" height="22" rx="3" fill="#b9975b"/><rect x="26" y="52" width="48" height="140" rx="12" fill="url(#${id})"/><rect x="31" y="60" width="5" height="120" rx="2.5" fill="#fff" opacity=".25"/>${label(32, 96, 36, 50, 8)}</svg>`,
      jar: `<svg viewBox="0 0 140 140">${grad}<rect x="24" y="14" width="92" height="26" rx="6" fill="#2a2a28"/><rect x="16" y="38" width="108" height="92" rx="20" fill="url(#${id})"/><rect x="24" y="48" width="6" height="70" rx="3" fill="#fff" opacity=".25"/>${label(40, 60, 60, 48, 11)}</svg>`,
      soap: `<svg viewBox="0 0 180 110">${grad}<rect x="10" y="22" width="160" height="76" rx="26" fill="url(#${id})"/><rect x="18" y="16" width="144" height="70" rx="22" fill="${t}"/><text x="90" y="58" font-size="18" text-anchor="middle" fill="#fff" opacity=".55" font-family="IBM Plex Sans Arabic, sans-serif" font-weight="700">الرافدين</text></svg>`,
      pouch: `<svg viewBox="0 0 120 170">${grad}<path d="M18 22h84l6 136a8 8 0 0 1-8 8H20a8 8 0 0 1-8-8Z" fill="#c9a77a"/><rect x="18" y="10" width="84" height="18" rx="3" fill="#b8956a"/><rect x="22" y="14" width="76" height="3" fill="#9b7b52"/><rect x="28" y="60" width="64" height="78" rx="6" fill="url(#${id})"/>${label(34, 72, 52, 52, 10)}</svg>`,
      box: `<svg viewBox="0 0 170 150">${grad}<path d="M20 44 85 20l65 24-65 24Z" fill="${t}" opacity=".75"/><path d="M20 44v76l65 26V68Z" fill="url(#${id})"/><path d="M150 44v76l-65 26V68Z" fill="${t}"/><path d="M150 44v76l-65 26V68Z" fill="#000" opacity=".18"/>${label(30, 74, 46, 42, 9)}<rect x="96" y="80" width="40" height="5" rx="2" fill="#fff" opacity=".4"/><rect x="96" y="92" width="28" height="5" rx="2" fill="#fff" opacity=".3"/></svg>`,
      honey: `<svg viewBox="0 0 130 160">${grad}<rect x="34" y="8" width="62" height="22" rx="5" fill="#2a2a28"/><path d="M28 30h74l12 22v86a14 14 0 0 1-14 14H30a14 14 0 0 1-14-14V52Z" fill="url(#${id})"/><rect x="24" y="58" width="6" height="74" rx="3" fill="#fff" opacity=".3"/>${label(36, 72, 58, 48, 10)}</svg>`
    };
    return shapes[p.shape] || shapes.bottle;
  }
  const tileBg = p => `background: color-mix(in srgb, ${p.tint} 15%, var(--surface-2))`;

  /* ---------- catalog ---------- */
  let activeCat = 'all', activeConcern = null, query = '', sort = '';
  const norm = s => s.replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/گ/g, 'ك').toLowerCase();
  const concernOf = id => C.concerns.find(c => c.ids.includes(id));

  function card(p) {
    return `<article class="card" data-id="${p.id}" tabindex="0" role="button" aria-label="${esc(p.name)}، ${fmt(p.price)}">
      <div class="art" style="${tileBg(p)}">${p.badge ? `<span class="badge">${esc(p.badge)}</span>` : ''}${art(p)}</div>
      <div class="info"><h3>${esc(p.name)}</h3><div class="short">${esc(p.short)}</div>
        <div class="row"><span class="price num">${fmt(p.price)}</span><button class="add" data-add="${p.id}" aria-label="أضف ${esc(p.name)} للسلة">${icon('i-plus')}</button></div>
      </div></article>`;
  }
  function renderGrid() {
    const q = norm(query.trim());
    let list = activeConcern ? activeConcern.ids.map(id => byId[id]) : C.products;
    list = list.filter(p => (activeCat === 'all' || p.cat === activeCat) &&
      (!q || norm([p.name, p.short, p.desc, ...p.tags].join(' ')).includes(q)));
    if (sort) list = [...list].sort((a, b) => sort === 'asc' ? a.price - b.price : b.price - a.price);
    $('#grid').innerHTML = list.map(card).join('') ||
      `<div class="empty"><div>ما لقينا شي يطابق «${esc(query || 'هذا الاختيار')}».</div><button class="btn soft" data-open-chat>اسأل المساعد الذكي</button></div>`;
    const note = $('#filterNote');
    note.hidden = !activeConcern;
    if (activeConcern) note.innerHTML = `<span>منتجات تناسب <b>${esc(activeConcern.name)}</b> · ${ar(list.length)} منتج</span><button data-clear>عرض الكل</button>`;
  }
  $('#chips').innerHTML = C.categories.map(c => `<button class="chip" data-cat="${c.id}" aria-pressed="${c.id === 'all'}">${esc(c.name)}</button>`).join('');
  $('#chips').addEventListener('click', e => {
    const b = e.target.closest('[data-cat]'); if (!b) return;
    activeCat = b.dataset.cat; activeConcern = null;
    $$('.chip').forEach(x => x.setAttribute('aria-pressed', x === b));
    renderGrid();
  });
  $('#q').addEventListener('input', e => { query = e.target.value; renderGrid(); });
  $('#sort').addEventListener('change', e => { sort = e.target.value; renderGrid(); });
  $('#filterNote').addEventListener('click', e => { if (e.target.closest('[data-clear]')) { activeConcern = null; renderGrid(); } });
  $('#openSearch').addEventListener('click', () => { $('#shop').scrollIntoView(); setTimeout(() => $('#q').focus({ preventScroll: true }), 350); });

  $('#concernList').innerHTML = C.concerns.map(c => `<button class="concern" data-concern="${c.id}">
      <span class="ic">${icon('c-' + c.id)}</span><b>${esc(c.name)}</b><span>${ar(c.ids.length)} منتجات</span></button>`).join('');
  $('#concernList').addEventListener('click', e => {
    const b = e.target.closest('[data-concern]'); if (!b) return;
    activeConcern = C.concerns.find(c => c.id === b.dataset.concern); activeCat = 'all'; query = ''; $('#q').value = '';
    $$('.chip').forEach(x => x.setAttribute('aria-pressed', x.dataset.cat === 'all'));
    renderGrid(); $('#shop').scrollIntoView();
  });

  $('#setsGrid').innerHTML = C.products.filter(p => p.cat === 'sets').map(card).join('');
  $('#heroStage').innerHTML = `<span class="tag">الأكثر طلباً: <b>مجموعة الإنبات</b></span>` + ['growth-oil', 'growth-set', 'face-cream'].map(id => art(byId[id])).join('');
  $('#branchList').innerHTML = S.branches.map(b => `<div class="branch"><h3>${esc(b.name)}</h3><div>${esc(b.area)}</div><div class="meta">${esc(b.address)}</div><div class="meta">${esc(b.hours)}</div>
    <a href="https://www.google.com/maps/search/${encodeURIComponent('معصرة الرافدين ' + b.area)}" target="_blank" rel="noopener">افتح بالخريطة ‹</a></div>`).join('');
  renderGrid();

  /* ---------- global clicks ---------- */
  document.addEventListener('click', e => {
    const t = e.target;
    const add = t.closest('[data-add]');
    if (add) { e.stopPropagation(); addToCart(add.dataset.add, 1); flash(add); return; }
    if (t.closest('[data-open-chat]')) { toggleChat(true); return; }
    if (t.closest('[data-cart]')) { openCart(); return; }
    if (t.closest('[data-orders]')) { openOrders(); return; }
    const go = t.closest('[data-go]');
    if (go) { document.getElementById(go.dataset.go).scrollIntoView(); return; }
    const c = t.closest('.card, [data-open]');
    if (c) openProduct(c.dataset.id || c.dataset.open);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && e.target.classList?.contains('card')) openProduct(e.target.dataset.id);
    if (e.key === 'Escape') { closeSheet(); toggleChat(false); }
  });
  function flash(btn) {
    btn.classList.add('done'); const was = btn.innerHTML;
    if (btn.classList.contains('add')) btn.innerHTML = icon('i-check'); else btn.textContent = 'انضاف ✓';
    setTimeout(() => { btn.classList.remove('done'); btn.innerHTML = was; }, 1200);
  }

  // tab bar highlights the section in view
  const tabs = $$('.tabbar [data-go]');
  const io = 'IntersectionObserver' in window && new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) tabs.forEach(b => b.classList.toggle('on', b.dataset.go === (en.target.id === 'shop' ? 'shop' : 'top')));
  }), { rootMargin: '-45% 0px -50% 0px' });
  if (io) ['top', 'shop', 'assistant'].forEach(id => io.observe(document.getElementById(id)));

  /* ---------- sheet ---------- */
  let lastFocus;
  function openSheet(html) {
    lastFocus = document.activeElement;
    $('#toast').classList.remove('on');
    $('#sheetBody').innerHTML = html;
    $('#sheet').hidden = false; $('#scrim').hidden = false;
    document.body.style.overflow = 'hidden';
    requestAnimationFrame(() => { $('#sheet').classList.add('on'); $('#scrim').classList.add('on'); $('#closeSheet').focus({ preventScroll: true }); });
    $('#sheet').scrollTop = 0;
  }
  function closeSheet() {
    if ($('#sheet').hidden) return;
    $('#sheet').classList.remove('on'); $('#scrim').classList.remove('on');
    document.body.style.overflow = '';
    setTimeout(() => { if (!$('#sheet').classList.contains('on')) { $('#sheet').hidden = true; $('#scrim').hidden = true; } }, 340);
    lastFocus?.focus?.({ preventScroll: true });
  }
  $('#closeSheet').addEventListener('click', closeSheet);
  $('#scrim').addEventListener('click', closeSheet);

  function miniCard(p) {
    return `<div class="rec"><div class="mini" data-open="${p.id}" style="${tileBg(p)}">${art(p)}</div><b>${esc(p.name)}</b><span class="price num">${fmt(p.price)}</span><button data-add="${p.id}">أضف للسلة</button></div>`;
  }

  function openProduct(id) {
    const p = byId[id]; if (!p) return;
    toggleChat(false);
    let qty = 1;
    const cn = concernOf(id);
    const related = (cn ? cn.ids : C.products.filter(x => x.cat === p.cat).map(x => x.id)).filter(x => x !== id).slice(0, 4).map(x => byId[x]);
    openSheet(`<div class="pd">
      <div class="pd-art" style="${tileBg(p)}">${p.badge ? `<span class="badge">${esc(p.badge)}</span>` : ''}${art(p)}</div>
      ${cn ? `<div class="eyebrow">يناسب: ${esc(cn.name)}</div>` : ''}
      <h2>${esc(p.name)}</h2>
      <div class="price num" style="font-size:21px;margin-top:2px">${fmt(p.price)}</div>
      <p>${esc(p.desc)}</p>
      <h4>المكونات</h4><div class="ings">${p.ingredients.map(i => `<span>${esc(i)}</span>`).join('')}</div>
      <h4>طريقة الاستخدام</h4><div class="use">${esc(p.usage)}</div>
      <div class="perks"><div><b>طبيعي</b>بدون حافظات</div><div><b>الدفع</b>عند الاستلام</div><div><b>التوصيل</b>٢٤–٤٨ ساعة</div></div>
      ${related.length ? `<h4>يكمّل روتينك</h4><div class="related">${related.map(miniCard).join('')}</div>` : ''}
      <div class="pd-buy">
        <div class="qty"><button data-q="1" aria-label="زيادة">+</button><span class="num" id="pq">١</span><button data-q="-1" aria-label="نقصان">−</button></div>
        <button class="btn block" id="pdAdd">أضف للسلة · <span class="num" id="pdTotal">${fmt(p.price)}</span></button>
      </div></div>`);
    $('#sheetBody').querySelectorAll('[data-q]').forEach(b => b.onclick = () => {
      qty = Math.min(20, Math.max(1, qty + Number(b.dataset.q)));
      $('#pq').textContent = ar(qty); $('#pdTotal').textContent = fmt(p.price * qty);
    });
    $('#pdAdd').onclick = () => { addToCart(id, qty); closeSheet(); };
  }

  /* ---------- cart ---------- */
  let cart = store.get('rafidain.cart', []).filter(l => byId[l.id]);
  const saveCart = () => { store.set('rafidain.cart', cart); renderCount(); };
  function renderCount(bump) {
    const n = cart.reduce((a, l) => a + l.qty, 0);
    $$('.count').forEach(c => { c.hidden = n === 0; c.textContent = ar(n); if (bump) { c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); } });
  }
  function addToCart(id, qty = 1) {
    if (!byId[id]) return;
    const l = cart.find(x => x.id === id);
    if (l) l.qty = Math.min(20, l.qty + qty); else cart.push({ id, qty });
    saveCart(); renderCount(true);
    toast(`انضاف ${byId[id].name}`, 'عرض السلة', openCart);
  }
  function totals(gov) {
    const sub = cart.reduce((a, l) => a + byId[l.id].price * l.qty, 0);
    const d = S.delivery;
    const fee = sub === 0 || sub >= d.freeOver ? 0 : (gov && gov !== 'بغداد' ? d.provinces : d.baghdad);
    return { sub, fee, total: sub + fee };
  }
  function shipBar(sub) {
    const left = S.delivery.freeOver - sub;
    if (left <= 0) return `<div class="ship free">${icon('i-check').replace('<svg', '<svg style="width:16px;height:16px;vertical-align:-3px"')} صار توصيلك مجاني</div>`;
    return `<div class="ship">باقي <b class="num">${fmt(left)}</b> وتحصل توصيل مجاني<div class="bar"><i style="width:${Math.round(sub / S.delivery.freeOver * 100)}%"></i></div></div>`;
  }
  const steps = n => `<div class="steps">${['السلة', 'التوصيل', 'تم'].map((s, i) => `<span class="${i <= n ? 'on' : ''}">${s}</span>`).join('<i></i>')}</div>`;

  function openCart() {
    toggleChat(false);
    if (!cart.length) {
      openSheet(`<div class="done"><h2>السلة فارغة</h2><p class="hint">تصفح المتجر، أو خلّي المساعد يختارلك.</p>
        <div class="ctas"><button class="btn" id="goShop">تسوّق الآن</button><button class="btn soft" data-open-chat>اسأل المساعد</button></div></div>`);
      $('#goShop').onclick = () => { closeSheet(); $('#shop').scrollIntoView(); };
      return;
    }
    const t = totals('بغداد');
    const ids = cart.map(l => l.id);
    const upsell = C.products.filter(p => !ids.includes(p.id) && ids.some(i => concernOf(i)?.ids.includes(p.id))).slice(0, 4);
    openSheet(`<h2>سلتك</h2>${steps(0)}
      <div>${cart.map(l => { const p = byId[l.id]; return `<div class="line">
        <div class="thumb" data-open="${p.id}" style="${tileBg(p)}">${art(p)}</div>
        <div style="min-width:0"><div class="nm">${esc(p.name)}</div><div class="sub num">${fmt(p.price * l.qty)}</div></div>
        <div class="qty"><button data-inc="${p.id}" aria-label="زيادة">+</button><span class="num">${ar(l.qty)}</span><button data-dec="${p.id}" aria-label="${l.qty === 1 ? 'حذف' : 'نقصان'}">${l.qty === 1 ? '×' : '−'}</button></div>
      </div>`; }).join('')}</div>
      ${shipBar(t.sub)}
      <div class="totals num">
        <div><span>المجموع</span><span>${fmt(t.sub)}</span></div>
        <div><span>التوصيل</span><span>${t.fee ? 'من ' + fmt(t.fee) : 'مجاني'}</span></div>
        <div class="grand"><span>الكلي التقريبي</span><span>${fmt(t.total)}</span></div>
      </div>
      <button class="btn block" id="toCheckout">أكمل الطلب</button>
      ${upsell.length ? `<h4 style="margin:22px 0 8px">ناس طلبوا ويّاها هم</h4><div class="related">${upsell.map(miniCard).join('')}</div>` : ''}`);
    $('#sheetBody').querySelectorAll('[data-inc],[data-dec]').forEach(b => b.onclick = () => {
      const id = b.dataset.inc || b.dataset.dec, l = cart.find(x => x.id === id);
      l.qty = Math.min(20, l.qty + (b.dataset.inc ? 1 : -1));
      if (l.qty <= 0) cart = cart.filter(x => x !== l);
      saveCart(); const y = $('#sheet').scrollTop; openCart(); $('#sheet').scrollTop = y;
    });
    $('#toCheckout').onclick = openCheckout;
  }

  function openCheckout() {
    toggleChat(false);
    const prev = store.get('rafidain.customer', {});
    openSheet(`<h2>معلومات التوصيل</h2>${steps(1)}
      <form class="form" id="checkout" novalidate>
        <div class="two">
          <label for="cName">الاسم<input id="cName" required value="${esc(prev.name || '')}" autocomplete="name"></label>
          <label for="cPhone">رقم الهاتف<input id="cPhone" required type="tel" inputmode="tel" dir="ltr" placeholder="07XX XXX XXXX" value="${esc(prev.phone || '')}" autocomplete="tel"></label>
        </div>
        <div class="two">
          <label for="cGov">المحافظة<select id="cGov">${S.governorates.map(g => `<option ${g === (prev.gov || 'بغداد') ? 'selected' : ''}>${g}</option>`).join('')}</select></label>
          <label for="cArea">المنطقة<input id="cArea" required placeholder="مثال: المنصور" value="${esc(prev.area || '')}" autocomplete="address-level3"></label>
        </div>
        <label for="cAddr">أقرب نقطة دالة<input id="cAddr" placeholder="مثال: قرب جامع…" value="${esc(prev.addr || '')}"></label>
        <label for="cNote">ملاحظات<textarea id="cNote" rows="2" placeholder="اختياري"></textarea></label>
        <div class="pay">${icon('i-cash')}الدفع نقداً عند الاستلام</div>
        <div class="totals num" id="coTotals"></div>
        <div class="err" id="coErr" role="alert" hidden></div>
        <button class="btn block" id="placeOrder" type="submit">تأكيد الطلب</button>
        <button class="btn ghost" type="button" id="backCart" style="justify-self:center">رجوع للسلة</button>
      </form>`);
    const upd = () => {
      const t = totals($('#cGov').value);
      $('#coTotals').innerHTML = `<div><span>المنتجات (${ar(cart.reduce((a, l) => a + l.qty, 0))})</span><span>${fmt(t.sub)}</span></div><div><span>التوصيل لـ${esc($('#cGov').value)}</span><span>${t.fee ? fmt(t.fee) : 'مجاني'}</span></div><div class="grand"><span>الكلي</span><span>${fmt(t.total)}</span></div>`;
      $('#placeOrder').textContent = `تأكيد الطلب · ${fmt(t.total)}`;
    };
    $('#cGov').onchange = upd; upd();
    $('#backCart').onclick = openCart;
    $('#checkout').onsubmit = async e => {
      e.preventDefault();
      const c = { name: $('#cName').value.trim(), phone: $('#cPhone').value.replace(/[\s-]/g, '').replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)), gov: $('#cGov').value, area: $('#cArea').value.trim(), addr: $('#cAddr').value.trim(), note: $('#cNote').value.trim() };
      const checks = [['cName', !c.name, 'اكتب الاسم.'], ['cPhone', !/^(\+?964|0)7\d{9}$/.test(c.phone), 'رقم الهاتف لازم يبدي بـ 07 ويكون ١١ رقم.'], ['cArea', !c.area, 'اكتب المنطقة.']];
      checks.forEach(([id, bad]) => $('#' + id).setAttribute('aria-invalid', bad));
      const bad = checks.find(x => x[1]);
      if (bad) { $('#coErr').textContent = bad[2]; $('#coErr').hidden = false; $('#' + bad[0]).focus(); return; }
      store.set('rafidain.customer', c);
      $('#placeOrder').disabled = true; $('#placeOrder').textContent = 'جاري الإرسال…';
      const t = totals(c.gov);
      const order = { customer: c, items: cart.map(l => ({ id: l.id, qty: l.qty })) };
      let id;
      try {
        const r = await fetch('api/orders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(order) });
        if (!r.ok) throw 0; id = (await r.json()).id;
      } catch { id = 'RF-' + String(Date.now()).slice(-6); }  // preview mode: no server
      const orders = store.get('rafidain.orders', []);
      orders.unshift({ id, at: Date.now(), total: t.total, phone: c.phone, items: cart.map(l => `${byId[l.id].name} × ${l.qty}`) });
      store.set('rafidain.orders', orders.slice(0, 20));
      cart = []; saveCart();
      openSheet(`${steps(2)}<div class="done"><div class="tick">${icon('i-check')}</div><h2>وصلنا طلبك، شكراً إلك</h2>
        <p class="hint">رقم الطلب</p><code>${esc(id)}</code>
        <p class="hint" style="max-width:34ch">راح نتصل بيك على <span dir="ltr">${esc(c.phone)}</span> حتى نأكد الطلب. التوصيل خلال ٢٤–٤٨ ساعة.</p>
        <div class="ctas"><button class="btn" id="doneBtn">تمام</button><button class="btn soft" data-orders>تابع طلبك</button></div></div>`);
      $('#doneBtn').onclick = closeSheet;
    };
  }

  /* ---------- my orders ---------- */
  const STAGES = ['new', 'confirmed', 'shipped', 'delivered'];
  const STATUS = { new: 'استلمنا الطلب', confirmed: 'تم التأكيد', shipped: 'ويّه المندوب', delivered: 'تم التوصيل', cancelled: 'ملغي' };
  async function openOrders() {
    toggleChat(false);
    const orders = store.get('rafidain.orders', []);
    if (!orders.length) {
      openSheet(`<div class="done"><h2>ما عندك طلبات بعد</h2><p class="hint">لما تطلب، تكدر تتابع طلبك من هنا.</p><button class="btn" id="goShop">تسوّق الآن</button></div>`);
      $('#goShop').onclick = () => { closeSheet(); $('#shop').scrollIntoView(); };
      return;
    }
    const row = (o, st) => `<div class="order"><div class="top"><b class="num" dir="ltr">${esc(o.id)}</b><span class="pill ${st}">${STATUS[st]}</span></div>
      <div class="hint">${new Date(o.at).toLocaleDateString('ar-IQ', { day: 'numeric', month: 'long' })} · ${fmt(o.total)}</div>
      ${o.items ? `<div class="hint">${o.items.map(esc).join('، ')}</div>` : ''}
      ${st !== 'cancelled' ? `<div class="track">${STAGES.map((s, i) => `<i class="${i <= STAGES.indexOf(st) ? 'on' : ''}"></i>`).join('')}</div>` : ''}</div>`;
    openSheet(`<h2>طلباتي</h2><p class="hint" style="margin:4px 0 14px">للاستفسار اتصل على <span dir="ltr" class="num">${esc(S.phone)}</span></p><div id="orderList">${orders.map(o => row(o, 'new')).join('')}</div>`);
    const live = await Promise.all(orders.map(async o => {
      try { const r = await fetch(`api/orders/${encodeURIComponent(o.id)}?phone=${encodeURIComponent(o.phone || '')}`); if (r.ok) return (await r.json()).status; } catch { /* preview mode */ }
      return 'new';
    }));
    if ($('#orderList')) $('#orderList').innerHTML = orders.map((o, i) => row(o, STATUS[live[i]] ? live[i] : 'new')).join('');
  }

  let toastT;
  function toast(msg, action, fn) {
    const t = $('#toast');
    t.innerHTML = `<span>${esc(msg)}</span>${action ? `<button type="button">${esc(action)}</button>` : ''}`;
    if (action) t.querySelector('button').onclick = () => { t.classList.remove('on'); fn(); };
    t.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('on'), 2600);
  }
  renderCount();

  /* ---------- AI assistant ---------- */
  const history = [];
  const msgs = $('#msgs');
  function toggleChat(on) {
    const chat = $('#chat');
    if (on === chat.classList.contains('on')) return;
    chat.classList.toggle('on', on);
    if (on) { closeSheet(); if (!msgs.children.length) greet(); if (matchMedia('(min-width: 721px)').matches) setTimeout(() => $('#chatInput').focus(), 200); }
  }
  $('#closeChat').addEventListener('click', () => toggleChat(false));

  function bubble(html, who) {
    const d = document.createElement('div'); d.className = 'msg ' + who; d.innerHTML = html; msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight; return d;
  }
  function recs(ids) {
    const list = ids.map(id => byId[id]).filter(Boolean); if (!list.length) return;
    const d = document.createElement('div'); d.className = 'recs'; d.innerHTML = list.map(miniCard).join('');
    msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight;
  }
  function suggestions(list) { $('#sugg').innerHTML = list.map(s => `<button type="button">${esc(s)}</button>`).join(''); }
  $('#sugg').addEventListener('click', e => { const b = e.target.closest('button'); if (b) send(b.textContent); });
  function greet() {
    bubble(esc('هلا بيك بمعصرة الرافدين 🌿\nآني مساعدك الذكي. احجيلي شنو تحتاج: مشكلة بالشعر أو البشرة، أعشاب، أو تريد تطلب مباشرة.'), 'bot');
    suggestions(['شعري يتساقط', 'عندي حبوب بالوجه', 'بشرتي جافة', 'شنو أفضل باكج؟', 'وين فروعكم؟']);
  }

  let lastRecs = [];
  async function send(text) {
    text = text.trim(); if (!text) return;
    bubble(esc(text), 'user'); suggestions([]);
    history.push({ role: 'user', content: text });
    const typing = bubble('<span class="dots" aria-label="يكتب"><i></i><i></i><i></i></span>', 'bot');
    let res;
    try {
      const r = await fetch('api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: history.slice(-16), cart }) });
      if (!r.ok) throw 0; res = await r.json();
    } catch {
      await new Promise(r => setTimeout(r, 500));
      res = localAgent(text);  // preview mode: no server, use the built-in rules
    }
    typing.remove();
    bubble(esc(res.reply), 'bot');
    history.push({ role: 'assistant', content: res.reply });
    if (res.products?.length) { recs(res.products); lastRecs = res.products; }
    (res.actions || []).forEach(a => {
      if (a.type === 'add') addToCart(a.id, a.qty || 1);
      if (a.type === 'checkout') cart.length ? openCheckout() : openCart();
    });
    if (res.suggestions?.length) suggestions(res.suggestions);
  }
  $('#composer').addEventListener('submit', e => { e.preventDefault(); const i = $('#chatInput'); send(i.value); i.value = ''; });

  // Rule-based fallback so the assistant still works without the AI server (preview / offline).
  function localAgent(raw) {
    const t = norm(raw), has = (...w) => w.some(x => t.includes(norm(x)));
    if (has('نعم', 'ضيف', 'اضيف', 'أضف', 'زين', 'تمام', 'اوكي', 'موافق') && lastRecs.length && t.length < 24)
      return { reply: `ضفت ${byId[lastRecs[0]].name} للسلة. تريد تكمل الطلب هسه؟`, actions: [{ type: 'add', id: lastRecs[0] }], suggestions: ['أكمل الطلب', 'أريد شي ثاني'] };
    if (has('اكمل', 'أكمل', 'اطلب', 'الطلب', 'السله', 'سلة'))
      return { reply: 'تمام، فتحتلك صفحة الطلب. الدفع عند الاستلام والتوصيل خلال ٢٤–٤٨ ساعة.', actions: [{ type: 'checkout' }] };
    if (has('تساقط', 'فراغ', 'صلع', 'انبات', 'خفيف', 'يطيح'))
      return { reply: 'للتساقط والفراغات أنصحك بمجموعة الإنبات: زيت الإنبات (١٥ عشبة) ويه الشامبو.\nالزيت ٣ مرات بالأسبوع ويترك ساعتين، والنتيجة تبين ويه الاستمرار من ٦–٨ أسابيع.\nإذا التساقط بعد صبغ أو سشوار، زيت التساقط يفيد هم.', products: ['growth-set', 'growth-oil', 'anti-fall-oil'], suggestions: ['ضيف المجموعة', 'شكد التوصيل؟'] };
    if (has('حبوب', 'دهني', 'رؤوس', 'مسامات', 'حب الشباب'))
      return { reply: 'للبشرة الدهنية والحبوب: صابونة الفحم والعسل صباح ومساء، وماسك الطين مرة بالأسبوع.\nإذا تريد روتين كامل، باكج روتين البشرة أوفر.', products: ['charcoal-soap', 'clay-mask', 'skin-routine'], suggestions: ['ضيف الصابونة', 'بشرتي جافة'] };
    if (has('جاف', 'جفاف', 'نضار', 'بقع', 'تصبغ', 'تجاعيد', 'بشرة', 'بشرتي'))
      return { reply: 'للبشرة الجافة والبقع: كريم الرافدين للبشرة صباح ومساء، وزيت الورد قطرتين قبل النوم.', products: ['face-cream', 'rose-oil', 'skin-routine'], suggestions: ['ضيف الكريم', 'شنو أفضل باكج؟'] };
    if (has('رموش', 'حواجب', 'لحيه', 'لحية'))
      return { reply: 'للرموش والحواجب زيت الخروع بفرشاة قبل النوم. وللحية زيت الإنبات يفيد للفراغات.', products: ['castor-oil', 'growth-oil'] };
    if (has('تقصف', 'هيشان', 'اطراف', 'لمعان'))
      return { reply: 'للتقصف والهيشان: سيروم الأطراف بعد الغسل، وماسك الحناء والأعشاب مرة بالأسبوع.', products: ['hair-serum', 'henna-mask'] };
    if (has('تشقق', 'كعب', 'جسم'))
      return { reply: 'للجسم والتشققات: زبدة الشيا الخام للمناطق الجافة، وزيت اللوز الحلو بعد الشاور.', products: ['shea-butter', 'almond-oil'] };
    if (has('برد', 'كحه', 'كحة', 'زكام', 'شتاء'))
      return { reply: 'للبرد والكحة: زهورات عراقية ويه ملعقة عسل جبلي. صحتين.', products: ['zahourat', 'mountain-honey'] };
    if (has('نوم', 'ارق', 'توتر', 'هدوء'))
      return { reply: 'للنوم والهدوء: كوب بابونج قبل النوم بنص ساعة.', products: ['chamomile'] };
    if (has('عسل')) return { reply: 'عدنا عسل السدر وعسل جبلي من كردستان.', products: ['sidr-honey', 'mountain-honey'] };
    if (has('باكج', 'مجموعه', 'افضل', 'عرض'))
      return { reply: 'أكثر شي ينطلب عدنا مجموعة الإنبات للشعر. وإذا مهتم بالبشرة، روتين البشرة الطبيعي. وخلطة شيخ العطارين هي خلطتنا الأصلية.', products: ['growth-set', 'skin-routine', 'sheikh-blend'] };
    if (has('طلبي', 'تتبع', 'وين وصل'))
      return { reply: 'تكدر تتابع طلباتك من «طلباتي». وإذا تأخر الطلب، اتصل بينا على ' + S.phone + '.' };
    if (has('وين', 'فرع', 'عنوان', 'موقع', 'مكان'))
      return { reply: S.branches.map(b => `${b.name}: ${b.area}، ${b.address}`).join('\n') + `\nللتواصل: ${S.phone}`, suggestions: ['شكد التوصيل؟'] };
    if (has('توصيل', 'شكد', 'سعر', 'محافظ'))
      return { reply: `التوصيل لبغداد ${fmt(S.delivery.baghdad)}، وللمحافظات ${fmt(S.delivery.provinces)}.\nمجاني للطلبات فوق ${fmt(S.delivery.freeOver)}. الدفع عند الاستلام.` };
    if (has('هلا', 'سلام', 'مرحب', 'شلون'))
      return { reply: 'هلا بيك وعليكم السلام. شلون أكدر أساعدك اليوم؟', suggestions: ['شعري يتساقط', 'عندي حبوب بالوجه', 'وين فروعكم؟'] };
    const hits = C.products.filter(p => norm([p.name, ...p.tags].join(' ')).split(/\s+/).some(w => w.length > 2 && t.includes(w))).slice(0, 3);
    if (hits.length) return { reply: 'هاي المنتجات اللي تناسب سؤالك:', products: hits.map(p => p.id) };
    return { reply: `ما فهمت عليك زين. احجيلي عن مشكلة بالشعر أو البشرة، أو اسأل عن منتج، أو اتصل بينا على ${S.phone}.`, suggestions: ['شعري يتساقط', 'بشرتي جافة', 'شنو أفضل باكج؟'] };
  }
})();

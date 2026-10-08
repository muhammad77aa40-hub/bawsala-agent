const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const Anthropic = require('@anthropic-ai/sdk');
const CATALOG = require('./public/catalog.js');

const app = express();
app.use(express.json({ limit: '100kb' }));
app.use(express.static(path.join(__dirname, 'public')));

const MODEL = process.env.AI_MODEL || 'claude-opus-5-5';
const ADMIN_KEY = process.env.ADMIN_KEY;
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
const ORDERS_FILE = path.join(DATA_DIR, 'orders.json');
const anthropic = process.env.ANTHROPIC_API_KEY ? new Anthropic() : null;
const byId = Object.fromEntries(CATALOG.products.map(p => [p.id, p]));

/* ---------------- orders ---------------- */
fs.mkdirSync(DATA_DIR, { recursive: true });
const readOrders = () => { try { return JSON.parse(fs.readFileSync(ORDERS_FILE, 'utf8')); } catch { return []; } };
const writeOrders = list => fs.writeFileSync(ORDERS_FILE, JSON.stringify(list, null, 2));
const STATUS = { new: 'استلمنا الطلب', confirmed: 'تم التأكيد', shipped: 'ويه المندوب', delivered: 'تم التوصيل', cancelled: 'ملغي' };

function priceOrder(items, gov) {
  const lines = (items || []).filter(i => byId[i.id] && Number.isInteger(i.qty) && i.qty > 0 && i.qty <= 50)
    .map(i => ({ id: i.id, name: byId[i.id].name, qty: i.qty, price: byId[i.id].price }));
  const sub = lines.reduce((a, l) => a + l.price * l.qty, 0);
  const d = CATALOG.store.delivery;
  const fee = sub >= d.freeOver ? 0 : (gov === 'بغداد' ? d.baghdad : d.provinces);
  return { lines, sub, fee, total: sub + fee };
}

app.post('/api/orders', async (req, res) => {
  const c = req.body.customer || {};
  const phone = String(c.phone || '').replace(/\s/g, '');
  if (!c.name || !/^(\+?964|0)7\d{9}$/.test(phone) || !c.area || !CATALOG.store.governorates.includes(c.gov))
    return res.status(400).json({ error: 'معلومات التوصيل ناقصة' });
  const p = priceOrder(req.body.items, c.gov);  // prices always come from the catalog, never the browser
  if (!p.lines.length) return res.status(400).json({ error: 'السلة فارغة' });

  const order = {
    id: 'RF-' + crypto.randomInt(100000, 999999), createdAt: new Date().toISOString(), status: 'new',
    customer: { name: String(c.name).slice(0, 80), phone, gov: c.gov, area: String(c.area).slice(0, 120), addr: String(c.addr || '').slice(0, 200), note: String(c.note || '').slice(0, 300) },
    items: p.lines, subtotal: p.sub, delivery: p.fee, total: p.total
  };
  const orders = readOrders(); orders.unshift(order); writeOrders(orders);
  notifyOwner(order).catch(e => console.error('WhatsApp notify failed:', e.message));
  res.json({ id: order.id, total: order.total });
});

// Order status for "طلباتي". The customer's phone number acts as the key, so order ids alone can't be enumerated.
app.get('/api/orders/:id', (req, res) => {
  const o = readOrders().find(x => x.id === req.params.id && x.customer.phone === String(req.query.phone || ''));
  if (!o) return res.sendStatus(404);
  res.json({ id: o.id, status: o.status, total: o.total, createdAt: o.createdAt });
});

// Tells the shop owner on WhatsApp about each new order (optional).
async function notifyOwner(o) {
  const { WHATSAPP_TOKEN, PHONE_NUMBER_ID, OWNER_WHATSAPP } = process.env;
  if (!WHATSAPP_TOKEN || !PHONE_NUMBER_ID || !OWNER_WHATSAPP) return;
  const body = [`طلب جديد ${o.id}`, `${o.customer.name} — ${o.customer.phone}`, `${o.customer.gov} / ${o.customer.area} ${o.customer.addr}`,
    ...o.items.map(i => `• ${i.name} × ${i.qty}`), `الكلي: ${o.total.toLocaleString('en')} د.ع`, o.customer.note && `ملاحظة: ${o.customer.note}`].filter(Boolean).join('\n');
  await fetch(`https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages`, {
    method: 'POST', headers: { Authorization: `Bearer ${WHATSAPP_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ messaging_product: 'whatsapp', to: OWNER_WHATSAPP, type: 'text', text: { body } })
  });
}

/* ---------------- admin (orders list + status) ---------------- */
const admin = (req, res, next) => (ADMIN_KEY && req.get('x-admin-key') === ADMIN_KEY ? next() : res.sendStatus(401));
app.get('/api/admin/orders', admin, (req, res) => res.json(readOrders()));
app.patch('/api/admin/orders/:id', admin, (req, res) => {
  const orders = readOrders(), o = orders.find(x => x.id === req.params.id);
  if (!o) return res.sendStatus(404);
  if (!STATUS[req.body.status]) return res.status(400).json({ error: 'status must be one of ' + Object.keys(STATUS) });
  o.status = req.body.status; writeOrders(orders); res.json(o);
});

/* ---------------- AI assistant ---------------- */
const catalogText = CATALOG.products.map(p =>
  `- ${p.id} | ${p.name} | ${p.price} د.ع | ${p.short} | المكونات: ${p.ingredients.join('، ')} | الاستخدام: ${p.usage} | كلمات: ${p.tags.join('، ')}`).join('\n');
const S = CATALOG.store;

const SYSTEM = `انت "مساعد الرافدين"، المساعد الذكي لمتجر ${S.name} (معصرة ومعشب) في بغداد. شعارنا: ${S.tagline}.
تحجي باللهجة العراقية، بأسلوب ودود ومحترم ومختصر (٢-٤ أسطر بالعادة). لا تستعمل ماركداون ولا نجوم.

شغلك:
- تفهم مشكلة الزبون (شعر، بشرة، جسم، أعشاب، غذائي). إذا الطلب غامض اسأل سؤال واحد بس قبل ما تنصح (مثلاً سبب التساقط، نوع البشرة).
- تقترح من ١ إلى ٣ منتجات من الكتالوج فقط، وتعرضها دائماً بأداة show_products حتى تطلع للزبون كبطاقات.
- إذا الزبون وافق أو طلب منتج، ضيفه بأداة add_to_cart. ولما يريد يكمل، استعمل open_checkout.
- تسأل عن طلب سابق؟ استعمل track_order برقم الطلب.
- لا تخترع منتجات أو أسعار أو خصومات أو نتائج طبية. منتجاتنا طبيعية للعناية وليست علاج. إذا الحالة تبين طبية (تساقط شديد مفاجئ، التهاب، حساسية، حمل، أطفال رضع) انصح بمراجعة طبيب بلطف.
- إذا ما تعرف الجواب، وجّه الزبون يتصل على ${S.phone}.

معلومات المتجر:
${S.branches.map(b => `- ${b.name}: ${b.area}، ${b.address}. ${b.hours}`).join('\n')}
- التوصيل: بغداد ${S.delivery.baghdad} د.ع، المحافظات ${S.delivery.provinces} د.ع، مجاني فوق ${S.delivery.freeOver} د.ع. الدفع عند الاستلام. التوصيل خلال ٢٤–٤٨ ساعة.
- انستغرام: ${S.instagram}

الكتالوج (id | الاسم | السعر | الوصف ...):
${catalogText}`;

const ids = { type: 'array', items: { type: 'string', enum: Object.keys(byId) } };
const TOOLS = [
  { name: 'show_products', description: 'يعرض منتجات للزبون كبطاقات فيها زر "أضف للسلة". استعملها كل ما تقترح منتجات.', strict: true,
    input_schema: { type: 'object', properties: { ids }, required: ['ids'], additionalProperties: false } },
  { name: 'add_to_cart', description: 'يضيف منتج لسلة الزبون. استعملها بس لما الزبون يوافق أو يطلب.', strict: true,
    input_schema: { type: 'object', properties: { id: { type: 'string', enum: Object.keys(byId) }, qty: { type: 'integer' } }, required: ['id', 'qty'], additionalProperties: false } },
  { name: 'open_checkout', description: 'يفتح للزبون صفحة إكمال الطلب (الاسم والعنوان والدفع عند الاستلام).', strict: true,
    input_schema: { type: 'object', properties: {}, additionalProperties: false } },
  { name: 'track_order', description: 'يجيب حالة طلب سابق برقم الطلب مثل RF-123456.', strict: true,
    input_schema: { type: 'object', properties: { order_id: { type: 'string' } }, required: ['order_id'], additionalProperties: false } }
];

function runTool(name, input, out) {
  switch (name) {
    case 'show_products': out.products.push(...input.ids.filter(id => byId[id])); return 'تم عرض المنتجات للزبون.';
    case 'add_to_cart': if (!byId[input.id]) return 'منتج غير موجود';
      out.actions.push({ type: 'add', id: input.id, qty: Math.min(Math.max(input.qty || 1, 1), 20) }); return `انضاف ${byId[input.id].name} للسلة.`;
    case 'open_checkout': out.actions.push({ type: 'checkout' }); return 'انفتحت صفحة الطلب.';
    case 'track_order': {
      const o = readOrders().find(x => x.id.toUpperCase() === String(input.order_id).trim().toUpperCase());
      return o ? `الطلب ${o.id}: ${STATUS[o.status]}. المجموع ${o.total} د.ع. تاريخ الطلب ${o.createdAt.slice(0, 10)}.` : 'ما لقينا طلب بهذا الرقم.';
    }
  }
  return 'أداة غير معروفة';
}

const hits = new Map();  // basic per-IP rate limit: 30 messages / 10 minutes
function limited(ip) {
  const now = Date.now(), list = (hits.get(ip) || []).filter(t => now - t < 600000);
  list.push(now); hits.set(ip, list); return list.length > 30;
}

app.post('/api/chat', async (req, res) => {
  if (!anthropic) return res.status(503).json({ error: 'AI not configured' });  // the page falls back to its built-in rules
  if (limited(req.ip)) return res.json({ reply: `وصلت الحد المسموح من الرسائل. جرّب بعد شوية، أو اتصل بينا على ${S.phone}.` });

  const history = (Array.isArray(req.body.messages) ? req.body.messages : []).slice(-16)
    .filter(m => (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string' && m.content.trim())
    .map(m => ({ role: m.role, content: m.content.slice(0, 2000) }));
  while (history.length && history[0].role !== 'user') history.shift();
  if (!history.length) return res.status(400).json({ error: 'no message' });
  const cart = (req.body.cart || []).filter(l => byId[l.id]).map(l => `${byId[l.id].name} × ${l.qty}`).join('، ');
  if (cart) history[history.length - 1] = { role: 'user', content: `${history[history.length - 1].content}\n\n(سلة الزبون الحالية: ${cart})` };

  const out = { products: [], actions: [] }, texts = [];
  const messages = [...history];
  try {
    for (let turn = 0; turn < 5; turn++) {
      const r = await anthropic.beta.messages.create({
        model: MODEL, max_tokens: 4000, system: SYSTEM, tools: TOOLS, messages,
        output_config: { effort: 'low' },
        cache_control: { type: 'ephemeral' },
        betas: ['server-side-fallback-2026-07-01'], fallbacks: 'default'
      });
      if (r.stop_reason === 'refusal') { texts.push(`ما أكدر أساعد بهالموضوع. لأي سؤال عن منتجاتنا اتصل على ${S.phone}.`); break; }
      texts.push(...r.content.filter(b => b.type === 'text').map(b => b.text.trim()).filter(Boolean));
      if (r.stop_reason !== 'tool_use') break;
      messages.push({ role: 'assistant', content: r.content });
      messages.push({ role: 'user', content: r.content.filter(b => b.type === 'tool_use')
        .map(b => ({ type: 'tool_result', tool_use_id: b.id, content: runTool(b.name, b.input, out) })) });
    }
  } catch (e) {
    console.error('Claude error:', e.status, e.message);
    return res.status(502).json({ error: 'AI unavailable' });
  }
  res.json({ reply: texts.join('\n\n') || 'تفضل، شلون أكدر أساعدك؟', products: [...new Set(out.products)].slice(0, 4), actions: out.actions });
});

app.get('/privacy', (req, res) => res.type('text/plain; charset=utf-8').send(
  `سياسة الخصوصية — ${S.name}\nنجمع فقط الاسم والهاتف والعنوان لتوصيل طلبك. رسائل المساعد الذكي تُعالج لتوليد الرد ولا تُباع لأي جهة. للتواصل: ${S.phone}`));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Al-Rafidain store on :${PORT} (AI ${anthropic ? 'on, ' + MODEL : 'off — set ANTHROPIC_API_KEY'})`));

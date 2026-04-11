const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const FormData = require('form-data');
const Anthropic = require('@anthropic-ai/sdk');
const OpenAI = require('openai');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;
const PHONE_NUMBER_ID = process.env.PHONE_NUMBER_ID || '1085541751306845';
const VERIFY_TOKEN = process.env.VERIFY_TOKEN || 'bawsala_verify_2024';

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const conversationHistory = {};

const SYSTEM_PROMPT = `انت "بوصلة"، وكيل ذكاء اصطناعي لشركة البوصلة للتوصيل السريع في العراق.
تخصصك توصيل الطرود من اربيل لجميع محافظات العراق.
خدماتك: استقبال طلبات التوصيل، تتبع الشحنات، الاسعار، حل الشكاوى.
تكلم بالعربي العراقي البسيط والودود. كون محترف وسريع. ردودك قصيرة وواضحة.`;

async function getClaudeResponse(userId, message) {
    if (!conversationHistory[userId]) conversationHistory[userId] = [];
    conversationHistory[userId].push({ role: 'user', content: message });
    if (conversationHistory[userId].length > 20)
          conversationHistory[userId] = conversationHistory[userId].slice(-20);
    const response = await anthropic.messages.create({
          model: 'claude-opus-4-5',
          max_tokens: 1024,
          system: SYSTEM_PROMPT,
          messages: conversationHistory[userId]
    });
    const reply = response.content[0].text;
    conversationHistory[userId].push({ role: 'assistant', content: reply });
    return reply;
}

async function sendWhatsAppMessage(to, message) {
    await axios.post(`https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages`, {
          messaging_product: 'whatsapp', to, type: 'text', text: { body: message }
    }, { headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}`, 'Content-Type': 'application/json' } });
}

async function downloadMedia(mediaId) {
    const metaRes = await axios.get(`https://graph.facebook.com/v18.0/${mediaId}`,
                                    { headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` } });
    const mediaRes = await axios.get(metaRes.data.url,
                                     { headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` }, responseType: 'arraybuffer' });
    return Buffer.from(mediaRes.data);
}

async function transcribeAudio(audioBuffer) {
    const formData = new FormData();
    formData.append('file', audioBuffer, { filename: 'audio.ogg', contentType: 'audio/ogg' });
    formData.append('model', 'whisper-1');
    const res = await axios.post('https://api.openai.com/v1/audio/transcriptions', formData,
                                 { headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`, ...formData.getHeaders() } });
    return res.data.text;
}

// Webhook verification GET
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
          console.log('Webhook verified!');
          res.status(200).send(challenge);
    } else {
          res.sendStatus(403);
    }
});

// Receive messages POST
app.post('/webhook', async (req, res) => {
    res.sendStatus(200);
    try {
          const message = req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
          if (!message) return;
          const from = message.from;
          const msgType = message.type;
          console.log(`Message from ${from}, type: ${msgType}`);
          if (msgType === 'text') {
                  const reply = await getClaudeResponse(from, message.text.body);
                  await sendWhatsAppMessage(from, reply);
          } else if (msgType === 'audio') {
                  const buf = await downloadMedia(message.audio.id);
                  const text = await transcribeAudio(buf);
                  const reply = await getClaudeResponse(from, `[رسالة صوتية]: ${text}`);
                  await sendWhatsAppMessage(from, reply);
          } else if (msgType === 'image') {
                  const buf = await downloadMedia(message.image.id);
                  const b64 = buf.toString('base64');
                  const caption = message.image?.caption || 'ماذا ترى في هذه الصورة؟';
                  const resp = await anthropic.messages.create({
                            model: 'claude-opus-4-5', max_tokens: 1024,
                            messages: [{ role: 'user', content: [
                              { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: b64 } },
                              { type: 'text', text: caption }
                                      ]}]
                  });
                  await sendWhatsAppMessage(from, resp.content[0].text);
          }
    } catch (err) {
          console.error('Error:', err.message);
    }
});

app.get('/', (req, res) => res.json({
    status: 'البوصلة Agent شغال',
    timestamp: new Date().toISOString()
}));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server on port ${PORT}`));

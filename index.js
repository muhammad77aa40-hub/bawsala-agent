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

const SYSTEM_PROMPT = `Ø§ÙØª "Ø¨ÙØµÙØ©"Ø ÙÙÙÙ Ø°ÙØ§Ø¡ Ø§ØµØ·ÙØ§Ø¹Ù ÙØ´Ø±ÙØ© Ø§ÙØ¨ÙØµÙØ© ÙÙØªÙØµÙÙ Ø§ÙØ³Ø±ÙØ¹ ÙÙ Ø§ÙØ¹Ø±Ø§Ù.
ØªØ®ØµØµÙ ØªÙØµÙÙ Ø§ÙØ·Ø±ÙØ¯ ÙÙ Ø§Ø±Ø¨ÙÙ ÙØ¬ÙÙØ¹ ÙØ­Ø§ÙØ¸Ø§Øª Ø§ÙØ¹Ø±Ø§Ù.
Ø®Ø¯ÙØ§ØªÙ: Ø§Ø³ØªÙØ¨Ø§Ù Ø·ÙØ¨Ø§Øª Ø§ÙØªÙØµÙÙØ ØªØªØ¨Ø¹ Ø§ÙØ´Ø­ÙØ§ØªØ Ø§ÙØ§Ø³Ø¹Ø§Ø±Ø Ø­Ù Ø§ÙØ´ÙØ§ÙÙ.
ØªÙÙÙ Ø¨Ø§ÙØ¹Ø±Ø¨Ù Ø§ÙØ¹Ø±Ø§ÙÙ Ø§ÙØ¨Ø³ÙØ· ÙØ§ÙÙØ¯ÙØ¯. ÙÙÙ ÙØ­ØªØ±Ù ÙØ³Ø±ÙØ¹. Ø±Ø¯ÙØ¯Ù ÙØµÙØ±Ø© ÙÙØ§Ø¶Ø­Ø©.`;

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
                  const reply = await getClaudeResponse(from, `[Ø±Ø³Ø§ÙØ© ØµÙØªÙØ©]: ${text}`);
                  await sendWhatsAppMessage(from, reply);
          } else if (msgType === 'image') {
                  const buf = await downloadMedia(message.image.id);
                  const b64 = buf.toString('base64');
                  const caption = message.image?.caption || 'ÙØ§Ø°Ø§ ØªØ±Ù ÙÙ ÙØ°Ù Ø§ÙØµÙØ±Ø©Ø';
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

app.get('/privacy', (req, res) => res.send('Privacy Policy - Bawsala Messaging Agent. We collect only data necessary to provide our WhatsApp messaging service. Messages are processed to generate AI responses and are not shared with third parties. Contact: bakibaki199111@gmail.com'));

app.get('/', (req, res) => res.json({
    status: 'Ø§ÙØ¨ÙØµÙØ© Agent Ø´ØºØ§Ù',
    timestamp: new Date().toISOString()
}));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server on port ${PORT}`));

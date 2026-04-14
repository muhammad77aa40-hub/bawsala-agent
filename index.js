const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;
const PHONE_NUMBER_ID = process.env.PHONE_NUMBER_ID || '1085541751306845';
const VERIFY_TOKEN = process.env.VERIFY_TOKEN || 'bawsala_verify_2024';

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const conversationHistory = {};

const SYSTEM_PROMPT = `ط§ظ†طھ "ط¨ظˆطµظ„ط©"طŒ ظˆظƒظٹظ„ ط°ظƒط§ط، ط§طµط·ظ†ط§ط¹ظٹ ظ„ط´ط±ظƒط© ط§ظ„ط¨ظˆطµظ„ط© ظ„ظ„طھظˆطµظٹظ„ ط§ظ„ط³ط±ظٹط¹ ظپظٹ ط§ظ„ط¹ط±ط§ظ‚.
طھط®طµطµظƒ طھظˆطµظٹظ„ ط§ظ„ط·ط±ظˆط¯ ظ…ظ† ط§ط±ط¨ظٹظ„ ظ„ط¬ظ…ظٹط¹ ظ…ط­ط§ظپط¸ط§طھ ط§ظ„ط¹ط±ط§ظ‚.
ط®ط¯ظ…ط§طھظƒ: ط§ط³طھظ‚ط¨ط§ظ„ ط·ظ„ط¨ط§طھ ط§ظ„طھظˆطµظٹظ„طŒ طھطھط¨ط¹ ط§ظ„ط´ط­ظ†ط§طھطŒ ط§ظ„ط§ط³ط¹ط§ط±طŒ ط­ظ„ ط§ظ„ط´ظƒط§ظˆظ‰.
طھطھظƒظ„ظ… ط¨ط§ظ„ط¹ط±ط¨ظٹ ط§ظ„ط¹ط±ط§ظ‚ظٹ ط§ظ„ط¨ط³ظٹط· ظˆط§ظ„ظˆط¯ظˆط¯. طھظƒظˆظ† ظ…ط­طھط±ظ… ظˆط³ط±ظٹط¹. ط±ط¯ظˆط¯ظƒ ظ…ط®طھطµط±ط© ظˆظˆط§ط¶ط­ط©.`;

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
            await sendWhatsAppMessage(from, 'ط¹ط°ط±ط§ظ‹طŒ ط­ط§ظ„ظٹط§ظ‹ ظ†ط³طھظ‚ط¨ظ„ ط±ط³ط§ط¦ظ„ ظ†طµظٹط© ظˆطµظˆط± ظپظ‚ط·. ظٹط±ط¬ظ‰ ط¥ط±ط³ط§ظ„ ط±ط³ط§ظ„ط© ظ†طµظٹط©.');
        } else if (msgType === 'image') {
            const buf = await downloadMedia(message.image.id);
            const b64 = buf.toString('base64');
            const caption = message.image?.caption || 'ظ…ط§ط°ط§ طھط±ظ‰ ظپظٹ ظ‡ط°ظ‡ ط§ظ„طµظˆط±ط©طں';
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
    status: 'ط§ظ„ط¨ظˆطµظ„ط© Agent ط´ط؛ط§ظ„',
    timestamp: new Date().toISOString()
}));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server on port ${PORT}`));

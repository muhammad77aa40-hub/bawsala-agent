const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// ========================
// SYSTEM PROMPT - البوصلة
// ========================
const SYSTEM_PROMPT = `أنت "بوصلة"، وكيل ذكاء اصطناعي لشركة البوصلة للتوصيل السريع في العراق.

## معلومات الشركة:
- الاسم: البوصلة للتوصيل السريع (Al-Bawsala Express Delivery)
- التخصص: توصيل الطرود والبريد من أربيل إلى جميع محافظات العراق
- نخدم: الأفراد، الشركات، المحلات التجارية
- نوع الشحنات: بيجات، طرود شخصية، بضائع تجارية

## خدماتك الأساسية:
1. **استقبال طلبات التوصيل الجديدة** - اجمع: اسم المرسل، رقم الهاتف، العنوان في أربيل، المحافظة المقصودة، اسم المستلم، رقم المستلم، نوع الطرد، الوزن التقريبي
2. **تتبع الشحنات** - اطلب رقم الوصل أو رقم الهاتف
3. **الأسعار والاستفسارات** - أخبر الزبون أن التسعير يعتمد على الوزن والوجهة وسيتواصل معه الفريق لتأكيد السعر
4. **حل الشكاوى** - استمع، اعتذر باحترافية، وعد بالمتابعة خلال 24 ساعة
5. **التواصل مع السائقين** - استقبل تحديثات الرحلات والتسليمات

## أسلوب التحدث:
- تكلم بالعربي العراقي البسيط والودود إذا الزبون يحكي عربي
- تكلم بالكردي السوراني إذا الزبون يحكي كردي
- كون محترف، سريع، ومباشر
- لا تطول بالردود، خليها قصيرة وواضحة

## قواعد مهمة:
- إذا الزبون يطلب تتبع شحنة وما عندك بياناتها، قله: "خوش، انتظر شوية وراح نتواصل وياك خلال دقايق"
- إذا ما تعرف الجواب، لا تخترع. قل: "راح أوصل سؤالك للفريق وبرجعلك"
- دايمًا اختم باستفسار: "ضيفك شي ثاني؟" أو "چي شتێکی تر هەیە؟"
- لا تعطي أسعار محددة بدون تأكيد من الفريق`;

// ========================
// حفظ المحادثات في الذاكرة
// ========================
const conversations = {};

function getConversation(phoneNumber) {
  if (!conversations[phoneNumber]) {
    conversations[phoneNumber] = [];
  }
  return conversations[phoneNumber];
}

function addMessage(phoneNumber, role, content) {
  const conv = getConversation(phoneNumber);
  conv.push({ role, content });
  // احتفظ بآخر 20 رسالة بس
  if (conv.length > 20) {
    conversations[phoneNumber] = conv.slice(-20);
  }
}

// ========================
// معالجة الصوت (Whisper)
// ========================
async function transcribeAudio(mediaUrl, accountSid, authToken) {
  try {
    const FormData = require('form-data');
    const https = require('https');
    
    // تحميل الصوت من Twilio
    const audioResponse = await axios.get(mediaUrl, {
      auth: { username: accountSid, password: authToken },
      responseType: 'arraybuffer'
    });

    const formData = new FormData();
    formData.append('file', Buffer.from(audioResponse.data), {
      filename: 'audio.ogg',
      contentType: 'audio/ogg'
    });
    formData.append('model', 'whisper-1');
    formData.append('language', 'ar');

    const whisperResponse = await axios.post(
      'https://api.openai.com/v1/audio/transcriptions',
      formData,
      {
        headers: {
          ...formData.getHeaders(),
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
        }
      }
    );
    
    return whisperResponse.data.text;
  } catch (error) {
    console.error('Whisper error:', error.message);
    return null;
  }
}

// ========================
// الرد بـ Claude
// ========================
async function getClaudeResponse(phoneNumber, userMessage, imageBase64 = null) {
  addMessage(phoneNumber, 'user', userMessage);
  
  const messages = getConversation(phoneNumber).map(msg => {
    if (msg.role === 'user' && imageBase64 && msg === getConversation(phoneNumber).at(-1)) {
      return {
        role: 'user',
        content: [
          { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: imageBase64 } },
          { type: 'text', text: userMessage }
        ]
      };
    }
    return msg;
  });

  const response = await axios.post(
    'https://api.anthropic.com/v1/messages',
    {
      model: 'claude-opus-4-5',
      max_tokens: 1024,
      system: SYSTEM_PROMPT,
      messages: messages
    },
    {
      headers: {
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      }
    }
  );

  const assistantMessage = response.data.content[0].text;
  addMessage(phoneNumber, 'assistant', assistantMessage);
  return assistantMessage;
}

// ========================
// Webhook الرئيسي
// ========================
app.post('/webhook', async (req, res) => {
  const { Body, From, NumMedia, MediaUrl0, MediaContentType0 } = req.body;
  const phoneNumber = From;

  console.log(`📱 رسالة من ${phoneNumber}: ${Body || '[ميديا]'}`);

  try {
    let userMessage = Body || '';
    let imageBase64 = null;

    // معالجة الصوت
    if (NumMedia > 0 && MediaContentType0 && MediaContentType0.startsWith('audio/')) {
      console.log('🎤 رسالة صوتية، جاري التحويل...');
      const transcribed = await transcribeAudio(
        MediaUrl0,
        process.env.TWILIO_ACCOUNT_SID,
        process.env.TWILIO_AUTH_TOKEN
      );
      if (transcribed) {
        userMessage = `[رسالة صوتية]: ${transcribed}`;
        console.log(`🎤 النص: ${transcribed}`);
      } else {
        userMessage = 'أرسل رسالة صوتية لم أتمكن من فهمها';
      }
    }

    // معالجة الصور
    if (NumMedia > 0 && MediaContentType0 && MediaContentType0.startsWith('image/')) {
      console.log('🖼️ صورة مستلمة...');
      const imgResponse = await axios.get(MediaUrl0, {
        auth: {
          username: process.env.TWILIO_ACCOUNT_SID,
          password: process.env.TWILIO_AUTH_TOKEN
        },
        responseType: 'arraybuffer'
      });
      imageBase64 = Buffer.from(imgResponse.data).toString('base64');
      userMessage = userMessage || 'وصلتني هاي الصورة، شنو تريد؟';
    }

    if (!userMessage) {
      userMessage = 'أرسل رسالة';
    }

    const reply = await getClaudeResponse(phoneNumber, userMessage, imageBase64);
    console.log(`🤖 الرد: ${reply}`);

    // إرسال الرد عبر Twilio TwiML
    const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>${reply}</Message>
</Response>`;

    res.set('Content-Type', 'text/xml');
    res.send(twiml);

  } catch (error) {
    console.error('❌ خطأ:', error.message);
    const errorTwiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>عذراً، صار خطأ تقني. حاول مرة ثانية أو تواصل معنا مباشرة.</Message>
</Response>`;
    res.set('Content-Type', 'text/xml');
    res.send(errorTwiml);
  }
});

// Health check
app.get('/', (req, res) => {
  res.json({ status: '✅ البوصلة Agent شغال', time: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 البوصلة Agent شغال على port ${PORT}`);
});



# ✦ NeuraChat AI

### A Modern, Multi-Theme, Streaming AI Chatbot Built with Streamlit

<p align="center">
  <strong>NeuraChat AI</strong> is a premium-feeling, fast, and visually rich AI chatbot application inspired by modern  portfolios and SaaS dashboards.  
  It delivers real-time streaming responses, dynamic themes, and a professional chat experience — all built with Python & Streamlit.
</p>

<p align="center">
  <a href="#">🚀 Live Demo</a> ·
  <a href="#-setup--installation">📖 Documentation</a> ·
  <a href="https://github.com/Codeabhi096/neurachat/issues">🐛 Report Bug</a> ·
  <a href="https://github.com/Codeabhi096/neurachat/issues">💡 Request Feature</a>
</p>

---

## 📸 UI Preview & Themes

NeuraChat AI ships with **six fully dynamic, portfolio-style themes**, each designed for a unique visual identity.

|         Cyber Green        |        Ocean Blue        |         Neon Purple         |
| :------------------------: | :----------------------: | :-------------------------: |
| 🌐 Matrix-inspired dark UI | 🌊 Deep blue modern look | 💜 Electric neon aesthetics |

|         Forest        |     Light Mode     |      Deep Ocean      |
| :-------------------: | :----------------: | :------------------: |
| 🌲 Calm natural tones | ☀️ Clean & minimal | 🌊 Midnight deep sea |

---

## ✨ Key Features

### 💬 Chat Experience

* ⚡ **Real-Time Streaming Responses**
  Messages appear word-by-word (ChatGPT-like) for instant feedback.
* 🔵 **Typing Indicator**
  Animated dots show when the AI is thinking.
* 💬 **Modern Chat Bubbles**
  WhatsApp / ChatGPT-style message layout.
* 🧠 **Conversation Memory**
  Full session-based chat history.
* 📝 **Markdown Rendering**
  Headers, lists, tables, and emphasis supported.
* 💻 **Code Syntax Highlighting**
  Styled code blocks with copy-to-clipboard support.
* 📊 **Mermaid Diagram Support**
  Generate flowcharts, ER diagrams, and sequence diagrams directly from prompts.

---

### 🎨 Theme System

* 6 fully customizable, dynamic themes
* Instant theme switching (no reloads)
* Each theme controls:

  * Accent colors
  * Fonts & typography
  * Gradients & glow effects
  * Backgrounds & UI elements

| Theme          | Accent Color | Typography          |
| -------------- | ------------ | ------------------- |
| 🌐 Cyber Green | `#00ff88`    | Orbitron + Rajdhani |
| 🌊 Ocean Blue  | `#00aaff`    | Exo 2               |
| 💜 Neon Purple | `#cc00ff`    | Orbitron + Rajdhani |
| 🌲 Forest      | `#00cc55`    | Nunito              |
| ☀️ Light Mode  | `#4f38e8`    | Plus Jakarta Sans   |
| 🌊 Deep Ocean  | `#0066ff`    | Exo 2               |

---

### 🤖 AI Models (Free via OpenRouter)

| Model                | Provider   | Ideal Use Case                        |
| -------------------- | ---------- | ------------------------------------- |
| ⚡ Auto (Recommended) | OpenRouter | Automatically selects best free model |
| 🌟 Gemini 2.0 Flash  | Google     | Fast, balanced answers                |
| 🧠 DeepSeek Chat V3  | DeepSeek   | Advanced reasoning & coding           |
| 🔮 Mistral Small 3.1 | Mistral AI | Efficient & concise                   |
| 🦙 LLaMA 4 Maverick  | Meta       | Creative & versatile outputs          |

---

### ⚙️ Customization & Controls

* **Response Style** — Balanced · Concise · Detailed · Creative · Technical
* **Tone Selection** — Professional · Friendly · Casual · Academic · Creative
* **Creativity Slider** — Control temperature (0.0 → 1.0)
* **Session Statistics** — Live message count & activity tracking

---

### 🛡️ Reliability & Stability

* 🔁 **Automatic Model Fallback**
  If one model is rate-limited, the app seamlessly switches to the next.
* 🧯 **Graceful Error Handling**
  User-friendly messages, no crashes.
* 🔄 **Smart Retry System**
  Tries all available models before failing.

---

## 🛠️ Technology Stack

```
Frontend    → Streamlit · Custom CSS · Google Fonts
Backend     → Python 3.9+
AI Layer    → OpenRouter API (OpenAI-compatible)
Streaming   → Server-Sent Events (stream=True)
Styling     → CSS Injection · CSS Variables · Animations
Environment → python-dotenv
```

---

## 📁 Project Structure

```
neurachat/
│
├── app.py              # Main Streamlit application
├── .env                # Environment variables (not committed)
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🚀 Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Codeabhi096/neurachat.git
cd neurachat
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Get a Free OpenRouter API Key

1. Visit **[https://openrouter.ai](https://openrouter.ai)**
2. Sign up / log in
3. Go to **Keys → Create Key**
4. Copy your API key

### 5️⃣ Configure Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
```

### 6️⃣ Run the Application

```bash
streamlit run app.py
```

App will open at: **[http://localhost:8501](http://localhost:8501)** 🎉

---

## 📦 Requirements

```txt
streamlit>=1.32.0
openai>=1.14.0
python-dotenv>=1.0.0
```

---

## 💡 Example Prompts

```
📊 "Create a flowchart for user authentication"
💻 "Build a FastAPI REST API with JWT authentication"
🧮 "Explain gradient descent step by step"
✍️ "Write a professional cover letter for a software engineer"
📋 "Compare React, Vue, and Angular in a table"
🗺️ "Generate a mindmap of machine learning concepts"
```

---

## 🔑 API Usage & Limits

| Plan         | Approx. Limits                | Cost          |
| ------------ | ----------------------------- | ------------- |
| Free Tier    | ~20–50 requests / model / day | $0            |
| Paid Credits | Higher limits                 | Pay-as-you-go |

**Note:** NeuraChat uses `openrouter/auto` by default to maximize availability across free models.

---

## 🔒 Environment Variables

| Variable             | Required | Description             |
| -------------------- | -------- | ----------------------- |
| `OPENROUTER_API_KEY` | ✅ Yes    | Your OpenRouter API key |

---

## 🤝 Contributing

Contributions are welcome!

```bash
git checkout -b feature/your-feature
git commit -m "feat: add new feature"
git push origin feature/your-feature
# Open a Pull Request
```

---


## 👨‍💻 Author

**Abhishek Bhardwaj**

* 🌐 Portfolio: [https://mrabhi-7208.netlify.app](https://mrabhi-7208.netlify.app)
* 💼 LinkedIn: [https://linkedin.com/in/abhishekbhardwaj01](https://linkedin.com/in/abhishekbhardwaj01)
* 🧑‍💻 GitHub: [https://github.com/Codeabhi096](https://github.com/Codeabhi096)

---

<p align="center">
  <strong>Built with ❤️ using Python, Streamlit & OpenRouter</strong><br/>
  ⭐ Star this repository if you find it useful!
</p>

---

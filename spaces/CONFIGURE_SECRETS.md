# Configure Environment Variables for All Spaces

Now that all Spaces are running, you need to configure the environment variables/secrets for each Space.

## 🔧 Configuration Steps

### 1. Memory Layer
**URL:** https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-memory/settings

Click **Settings** → **Variables and secrets** → **New secret**

Add these secrets:
- **Name:** `MONGODB_URI`  
  **Value:** Your MongoDB Atlas connection string (e.g., `mongodb+srv://username:password@cluster.mongodb.net/`)

- **Name:** `DB_NAME`  
  **Value:** `portfolio_chatbot`

- **Name:** `COLLECTION_NAME`  
  **Value:** `portfolio_data`

- **Name:** `VECTOR_INDEX`  
  **Value:** `vector_index`

### 2. Orchestrator
**URL:** https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-orchestrator/settings

Click **Settings** → **Variables and secrets** → **New secret**

Add these secrets:
- **Name:** `PERCEPTION_API`  
  **Value:** `https://harithkavish-nlweb-perception.hf.space`

- **Name:** `MEMORY_API`  
  **Value:** `https://harithkavish-nlweb-memory.hf.space`

- **Name:** `REASONING_API`  
  **Value:** `https://harithkavish-nlweb-reasoning.hf.space`

- **Name:** `EXECUTION_API`  
  **Value:** `https://harithkavish-nlweb-execution.hf.space`

- **Name:** `MONITORING_API`  
  **Value:** `https://harithkavish-nlweb-monitoring.hf.space`

### 3. Execution Layer (Optional)
**URL:** https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-execution/settings

If you want GitHub integration:
- **Name:** `GITHUB_TOKEN`  
  **Value:** Your GitHub Personal Access Token (get from https://github.com/settings/tokens)

---

## ✅ After Configuration

Once you've added all the secrets:

1. Each Space will automatically restart
2. Wait 1-2 minutes for restarts to complete
3. Test the system!

## 🧪 Test Your System

### Test Individual Services

**Perception Layer:**
```powershell
py -c "import requests; r = requests.post('https://harithkavish-nlweb-perception.hf.space/embed', json={'text': 'Hello world'}); print(r.status_code, len(r.json()['embedding']))"
```

**Memory Layer:** (after adding MongoDB secrets)
```powershell
py -c "import requests; r = requests.get('https://harithkavish-nlweb-memory.hf.space/health'); print(r.status_code, r.json())"
```

**Reasoning Layer:**
```powershell
py -c "import requests; r = requests.post('https://harithkavish-nlweb-reasoning.hf.space/analyze', json={'query': 'What are your skills?'}); print(r.status_code, r.json())"
```

**Execution Layer:**
```powershell
py -c "import requests; r = requests.get('https://harithkavish-nlweb-execution.hf.space/tools'); print(r.status_code, len(r.json()['tools']))"
```

**Monitoring Layer:**
```powershell
py -c "import requests; r = requests.post('https://harithkavish-nlweb-monitoring.hf.space/validate/input', json={'text': 'Hello', 'session_id': 'test'}); print(r.status_code, r.json())"
```

### Test Complete System (Orchestrator)

**After all secrets are configured:**
```powershell
py -c "import requests; r = requests.post('https://harithkavish-nlweb-orchestrator.hf.space/chat', json={'message': 'What projects has Harith worked on?', 'session_id': 'test123'}); print(r.json())"
```

---

## 🌐 Update Your Website Widget

Once everything is working, update your website's widget loader to point to the new orchestrator:

**In `script.js` or wherever your widget is loaded:**

Change:
```javascript
const CHAT_API_URL = "https://harithkavish-nlweb-portfolio-chat.hf.space/chat";
```

To:
```javascript
const CHAT_API_URL = "https://harithkavish-nlweb-orchestrator.hf.space/chat";
```

Or use the orchestrator's widget endpoint directly:
```html
<script src="https://harithkavish-nlweb-orchestrator.hf.space/widget.js"></script>
```

---

## 📊 Monitor Your Spaces

Check the logs and status of each Space:

- 🧠 [Perception](https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-perception)
- 💾 [Memory](https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-memory)
- 🤔 [Reasoning](https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-reasoning)
- ⚡ [Execution](https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-execution)
- 🛡️ [Monitoring](https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-monitoring)
- 🎯 [Orchestrator](https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-orchestrator)

---

## 🎯 Quick Configuration Checklist

- [ ] Memory Layer: 4 MongoDB secrets added
- [ ] Orchestrator: 5 API URL secrets added
- [ ] Execution Layer: GitHub token added (optional)
- [ ] All Spaces restarted successfully
- [ ] Tested individual services
- [ ] Tested orchestrator end-to-end
- [ ] Updated website widget URL

**You're all set!** Your multi-agent chatbot architecture is live! 🚀

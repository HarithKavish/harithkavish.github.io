# 🎯 Quick Reference: Specialized Layer Architecture

## **TL;DR: What Changed?**

Each layer now uses **specialized models and prompts** instead of generic ones.

---

## 📋 Layer Quick Reference

| Layer | Model | Purpose | Speed | When Used |
|-------|-------|---------|-------|-----------|
| **Perception** | MiniLM + BART | Understand input | ⚡⚡⚡ | Every query |
| **Memory** | MongoDB | Store/retrieve data | ⚡⚡⚡ | Every query |
| **Reasoning** | FLAN-T5 | Generate responses | ⚡ | Every query |
| **Safety** | Pattern-based | Validate safety | ⚡⚡⚡ | Every query |
| **Execution** | None | Perform actions | ⚡⚡⚡ | When tools needed |

---

## 🔍 **Perception Layer**
**Model:** `sentence-transformers/all-MiniLM-L6-v2` + `facebook/bart-large-mnli`

**What it does:**
- Converts text to 384-dim embeddings
- Classifies user intent (greeting, question, farewell)

**Example:**
```
Input: "What projects has Harith worked on?"
Output: {
  embedding: [0.123, -0.456, ...],
  intent: "QUESTION",
  confidence: 0.92
}
```

**Why specialized?**
- MiniLM is 10x faster than large models for embeddings
- BART-MNLI excels at zero-shot classification

---

## 🗄️ **Memory Layer**
**Model:** None (MongoDB Atlas Vector Search)

**What it does:**
- Searches for relevant portfolio/project data
- Stores conversation history

**Example:**
```
Input: embedding=[0.123, -0.456, ...]
Output: [
  {content: "SkinNet project...", score: 0.89},
  {content: "Computer vision expertise...", score: 0.84}
]
```

**Why specialized?**
- No AI overhead - pure database speed
- Optimized for vector similarity search

---

## 🧠 **Reasoning Layer**
**Model:** `google/flan-t5-large` (780M parameters)

**What it does:**
- Synthesizes context into coherent responses
- Follows intent-specific prompts

**Specialized Prompts:**

### For Greetings:
```
"Be brief, welcome user, introduce as Neo AI"
```

### For Questions (RAG):
```
"Synthesize information from knowledge base.
Speak ABOUT Harith in third person.
Be detailed and accurate."
```

### For Farewells:
```
"Be brief, thank them, leave good impression"
```

**Why specialized?**
- FLAN-T5 is instruction-tuned for following prompts
- Different prompts for different intents = better responses

---

## 🔧 **Execution Layer**
**Model:** None (pure execution logic)

**What it does:**
- Checks if projects are online
- Fetches GitHub statistics
- Performs calculations
- Gets current time

**Example:**
```
Input: action="check_project_status", params={project: "SkinNet"}
Output: {status: "online", url: "...", response_time: 123ms}
```

**Why specialized?**
- No AI needed for simple actions
- Faster and more reliable than LLM tool-calling

---

## 🛡️ **Safety Layer**
**Model:** Pattern-based filtering (optional: `toxic-bert`)

**What it does:**
- Validates input isn't malicious
- Checks output quality
- Rate limiting (60 req/min)

**Example:**
```
Input: "'; DROP TABLE users--"
Output: {is_safe: false, issues: ["SQL injection detected"]}
```

**Why specialized?**
- Pattern matching is instant (<5ms)
- Can add toxicity model later if needed

---

## 🔄 **Complete Flow Example**

```
User: "What AI projects has Harith built?"
  ↓
Safety: ✓ Input is safe
  ↓
Perception: 
  • Embedding: [0.234, -0.123, ...]
  • Intent: QUESTION (92% confidence)
  ↓
Memory:
  • Found: SkinNet, Object Detection, Neo AI
  • Scores: [0.89, 0.87, 0.85]
  ↓
Reasoning (with specialized RAG prompt):
  "Harith Kavish has developed several AI projects:
   1. SkinNet-Analyzer - Deep learning for skin disease detection
   2. Multi-Object Detection using YOLO - Real-time object detection
   3. Neo AI - This intelligent portfolio assistant
   
   His work focuses on computer vision and deep learning..."
  ↓
Safety: ✓ Output is appropriate
  ↓
Memory: Stored conversation for context
  ↓
User receives response
```

---

## 💡 **Key Benefits**

| Benefit | Before | After |
|---------|--------|-------|
| **Speed** | ~1500ms | ~960ms |
| **Accuracy** | Generic | Specialized |
| **Cost** | Higher | Lower |
| **Debugging** | Hard | Easy |
| **Scalability** | Limited | Modular |

---

## 🚀 **Next Steps**

### To Deploy Updates:
```bash
# Each layer needs to be redeployed to HuggingFace Spaces
cd spaces/perception-layer
git add .
git commit -m "Add specialized models and prompts"
git push

# Repeat for other layers
```

### To Test Locally:
```bash
# Test each layer individually
python spaces/perception-layer/app.py
python spaces/memory-layer/app.py
python spaces/reasoning-layer/app.py
```

### To Monitor Performance:
- Check startup logs for model loading
- Monitor response times per layer
- Track intent classification accuracy

---

## 📚 **Related Documentation**

- Full details: `SPECIALIZED_ARCHITECTURE.md`
- Deployment: `DEPLOYMENT_GUIDE.md`
- Multi-agent overview: `MULTI_AGENT_ARCHITECTURE.md`

---

*Last Updated: November 6, 2025*

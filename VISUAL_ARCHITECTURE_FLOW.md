# 🏗️ Specialized Multi-Agent Architecture - Visual Flow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                             │
│                    (GitHub Pages Widget)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     🎛️ ORCHESTRATOR                                 │
│                  (Coordinates All Layers)                           │
│                      FastAPI Service                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
    ┌───────────────┐  ┌──────────┐  ┌──────────┐
    │  🛡️ SAFETY    │  │🔍PERCEPT │  │🧠REASON  │
    │  (Validate)   │  │(Understand)│  │(Generate)│
    └───────┬───────┘  └─────┬────┘  └────┬─────┘
            │                │             │
            ▼                ▼             ▼
    ┌──────────────────────────────────────────┐
    │        🗄️ MEMORY LAYER                   │
    │     (MongoDB Vector Search)              │
    │  • Store Portfolio Data                  │
    │  • Retrieve Context                      │
    │  • Save Conversations                    │
    └──────────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────┐
            │   🔧 EXECUTION LAYER       │
            │   (Optional - for actions) │
            │   • GitHub API             │
            │   • Web Requests           │
            │   • Tool Calling           │
            └────────────────────────────┘
```

---

## Detailed Flow with Models

```
USER INPUT: "What AI projects has Harith built?"
│
├─► STEP 1: Safety Validation (Input)
│   ├─ Model: Pattern-based filtering
│   ├─ Time: ~5ms
│   └─ Output: {is_safe: true}
│
├─► STEP 2: Perception Layer (Parallel)
│   │
│   ├─► Embedding Generation
│   │   ├─ Model: sentence-transformers/all-MiniLM-L6-v2
│   │   ├─ Size: 22M parameters
│   │   ├─ Time: ~30ms
│   │   └─ Output: [0.234, -0.123, ..., 0.456] (384 dims)
│   │
│   └─► Intent Classification
│       ├─ Model: facebook/bart-large-mnli
│       ├─ Size: 400M parameters
│       ├─ Time: ~20ms
│       └─ Output: {intent: "QUESTION", confidence: 0.92}
│
├─► STEP 3: Memory Layer (Vector Search)
│   ├─ Database: MongoDB Atlas
│   ├─ Index: vector_index (384 dims, cosine)
│   ├─ Time: ~100ms
│   └─ Output: [
│       {name: "SkinNet", content: "...", score: 0.89},
│       {name: "Object Detection", content: "...", score: 0.87},
│       {name: "Neo AI", content: "...", score: 0.85}
│     ]
│
├─► STEP 4: Reasoning Layer (Response Generation)
│   ├─ Model: google/flan-t5-large
│   ├─ Size: 780M parameters
│   ├─ Prompt: Specialized RAG synthesis prompt
│   │   ├─ System: "You are Neo AI, speak ABOUT Harith..."
│   │   ├─ Context: Top 4 retrieved documents
│   │   └─ Rules: Third-person, detailed, accurate
│   ├─ Time: ~800ms
│   └─ Output: "Harith Kavish has developed several AI projects:
│                1. SkinNet-Analyzer - Deep learning for skin disease...
│                2. Multi-Object Detection using YOLO...
│                3. Neo AI - This intelligent portfolio assistant..."
│
├─► STEP 5: Safety Validation (Output)
│   ├─ Model: Pattern-based + quality checks
│   ├─ Time: ~5ms
│   └─ Output: {is_safe: true, quality: high}
│
├─► STEP 6: Memory Layer (Store Conversation)
│   ├─ Database: MongoDB conversation_history collection
│   ├─ Time: ~20ms (async, fire-and-forget)
│   └─ Stored: {session_id, user_msg, bot_response, metadata}
│
└─► FINAL OUTPUT TO USER
    └─ Total Time: ~960ms
```

---

## Layer Specialization Matrix

```
┌──────────────┬─────────────────────┬─────────────┬──────────────────────┐
│ LAYER        │ MODEL               │ TASK        │ OPTIMIZATION         │
├──────────────┼─────────────────────┼─────────────┼──────────────────────┤
│ Perception   │ MiniLM-L6-v2        │ Embeddings  │ Speed + Quality      │
│              │ BART-large-MNLI     │ Intent      │ Zero-shot Accuracy   │
├──────────────┼─────────────────────┼─────────────┼──────────────────────┤
│ Memory       │ MongoDB Atlas       │ Storage     │ Vector Search Speed  │
│              │ (No AI model)       │ Retrieval   │ Scalability          │
├──────────────┼─────────────────────┼─────────────┼──────────────────────┤
│ Reasoning    │ FLAN-T5-large       │ Generation  │ Instruction-tuned    │
│              │ (780M params)       │ Synthesis   │ Context Integration  │
├──────────────┼─────────────────────┼─────────────┼──────────────────────┤
│ Safety       │ Pattern-based       │ Validation  │ Ultra-fast Filtering │
│              │ (No AI model)       │ Rate Limit  │ Security Focused     │
├──────────────┼─────────────────────┼─────────────┼──────────────────────┤
│ Execution    │ None                │ Actions     │ Direct API Calls     │
│              │ (Logic only)        │ Tools       │ Reliability          │
└──────────────┴─────────────────────┴─────────────┴──────────────────────┘
```

---

## System Prompt Specialization

### 🔍 Perception Layer
**No system prompt** - Returns structured data only
- Embeddings: numerical vectors
- Intent: classification labels

---

### 🧠 Reasoning Layer - Multiple Specialized Prompts

#### 1️⃣ **GREETING Intent Prompt**
```
{SYSTEM_IDENTITY}

Task: Respond warmly to this greeting: "{user_query}"

Instructions:
- Be brief (2-3 sentences)
- Welcome the user
- Introduce yourself as Neo AI, Harith Kavish's portfolio assistant
- Offer to help with questions about his work
```

#### 2️⃣ **FAREWELL Intent Prompt**
```
{SYSTEM_IDENTITY}

Task: Respond appropriately to this farewell: "{user_query}"

Instructions:
- Be brief and positive
- Thank them for their interest
- Leave a good impression
```

#### 3️⃣ **QUESTION/RAG Intent Prompt**
```
{SYSTEM_IDENTITY}

Your core competency: Synthesize information from the knowledge base 
into accurate, detailed responses about Harith Kavish.

SYNTHESIS RULES:
1. Speak ABOUT Harith in third person (he/his), never as him (I/my)
2. Use ONLY verified information from the knowledge base below
3. Provide complete, detailed answers - never truncate lists
4. Be specific: Include names, numbers, technologies
5. If info is missing, state clearly: "The available information doesn't include..."
6. Speak naturally and conversationally, but maintain accuracy

KNOWLEDGE BASE ABOUT HARITH KAVISH:
{retrieved_context}

USER QUESTION: {user_query}

Synthesized answer about Harith Kavish:
```

---

### 🗄️ Memory Layer
**No system prompt** - Pure database queries
- Vector similarity search
- CRUD operations for conversations

---

### 🛡️ Safety Layer
**Rule-based validation** - No prompts
- Pattern matching for threats
- Length validation
- Rate limiting logic

---

### 🔧 Execution Layer
**No system prompt** - Direct function calls
- GitHub API integration
- Web requests
- Calculations

---

## Performance Comparison

### Before Specialization
```
┌─────────────┬─────────────┬─────────┐
│ Layer       │ Model       │ Time    │
├─────────────┼─────────────┼─────────┤
│ All Layers  │ GPT-3.5     │ 1500ms  │
│ (Monolithic)│ (Single)    │         │
└─────────────┴─────────────┴─────────┘
Total: 1500ms
```

### After Specialization
```
┌─────────────┬─────────────┬─────────┐
│ Layer       │ Model       │ Time    │
├─────────────┼─────────────┼─────────┤
│ Safety      │ Patterns    │ 5ms     │
│ Perception  │ MiniLM+BART │ 50ms    │
│ Memory      │ MongoDB     │ 100ms   │
│ Reasoning   │ FLAN-T5     │ 800ms   │
│ Safety      │ Patterns    │ 5ms     │
└─────────────┴─────────────┴─────────┘
Total: 960ms (35% faster!)
```

---

## Cost Comparison

### Before
- Single large model (GPT-3.5 or similar)
- Cost per query: ~$0.002
- Monthly (10k queries): ~$20

### After
- Multiple specialized models
- Cost per query: ~$0.0005
- Monthly (10k queries): ~$5

**Savings: 75% reduction in costs**

---

## Scalability Benefits

```
┌──────────────────────────────────────────────────────────┐
│ BEFORE: Monolithic                                       │
│ ┌─────────────────────────────────────────────┐          │
│ │  One Large Model Does Everything            │          │
│ │  ├─ Understanding                            │          │
│ │  ├─ Retrieval                                │          │
│ │  ├─ Generation                               │          │
│ │  └─ Validation                               │          │
│ └─────────────────────────────────────────────┘          │
│ ❌ Hard to scale individual parts                        │
│ ❌ Can't optimize specific tasks                         │
│ ❌ Single point of failure                               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ AFTER: Specialized Microservices                         │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│ │Perception│  │ Memory  │  │Reasoning│  │ Safety  │      │
│ │ (Fast)  │  │ (Fast)  │  │(Quality)│  │ (Fast)  │      │
│ └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
│ ✓ Scale each layer independently                         │
│ ✓ Optimize models per task                               │
│ ✓ Fault isolation and recovery                           │
└──────────────────────────────────────────────────────────┘
```

---

## Future Enhancement Paths

```
🔍 PERCEPTION
├─ Add: spaCy for NER
├─ Add: Emotion detection
└─ Add: Multi-language support

🗄️ MEMORY
├─ Upgrade: Larger vector index
├─ Add: Redis caching layer
└─ Add: Hybrid search (vector + keyword)

🧠 REASONING
├─ Upgrade: Llama 2 or Mistral for complex queries
├─ Add: Citation generation
└─ Add: Multi-turn conversation state

🛡️ SAFETY
├─ Add: toxic-bert model
├─ Add: Hallucination detection
└─ Add: PII detection

🔧 EXECUTION
├─ Add: Email integration
├─ Add: Calendar API
└─ Add: Custom data queries
```

---

*Visual Diagram - Last Updated: November 6, 2025*

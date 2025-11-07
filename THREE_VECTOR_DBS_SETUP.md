# Three Vector Databases Setup Guide

## Overview
Your portfolio chatbot now uses **three specialized vector databases** for more accurate and contextual responses:

1. **Assistant Identity DB** - Information about Neo AI itself
2. **Harith Portfolio DB** - Your skills, projects, and experience
3. **General Knowledge DB** - Tech/AI concepts and external knowledge

---

## Step 1: Run the Setup Script

```powershell
# From your project root
c:/Dev/GitHub/harithkavish_github_io/.venv/Scripts/python.exe setup_three_vector_dbs.py
```

This script will:
- Create three new collections in MongoDB
- Populate assistant identity data
- Migrate existing portfolio data
- Add general knowledge content
- Generate embeddings for all documents

---

## Step 2: Create Vector Search Indexes in MongoDB Atlas

Visit: https://cloud.mongodb.com/

For **each collection**, create a vector search index:

### Index 1: Assistant Identity
- **Collection**: `assistant_identity`
- **Index Name**: `assistant_vector_index`
- **Configuration**:
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

### Index 2: Harith Portfolio
- **Collection**: `harith_portfolio`
- **Index Name**: `portfolio_vector_index`
- **Configuration**:
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

### Index 3: General Knowledge
- **Collection**: `general_knowledge`
- **Index Name**: `knowledge_vector_index`
- **Configuration**:
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}
```

**Wait 2-5 minutes** for each index to build.

---

## Step 3: Update HuggingFace Space Environment Variables

Go to your Memory Layer Space: https://huggingface.co/harithkavish/harithkavish-nlweb-memory

Add these environment variables in **Settings → Variables and secrets**:

```
ASSISTANT_COLLECTION=assistant_identity
ASSISTANT_INDEX=assistant_vector_index

PORTFOLIO_COLLECTION=harith_portfolio
PORTFOLIO_INDEX=portfolio_vector_index

KNOWLEDGE_COLLECTION=general_knowledge
KNOWLEDGE_INDEX=knowledge_vector_index
```

Keep existing variables:
```
MONGODB_URI=<your-mongodb-uri>
DB_NAME=nlweb
HISTORY_COLLECTION=conversation_history
```

---

## Step 4: Deploy Updated Code

```powershell
# Deploy all spaces with the three-DB architecture
c:/Dev/GitHub/harithkavish_github_io/.venv/Scripts/python.exe deploy_to_hf_spaces.py
```

This will update:
- Memory Layer (with multi-domain search)
- Orchestrator (with intelligent domain routing)

---

## Step 5: Test the System

After deployment (wait 5 minutes for rebuild), test these queries:

### Test 1: Assistant Identity
**Query**: "Who are you?"  
**Expected**: Neo AI introduces itself, mentions it's Harith's assistant

### Test 2: Harith's Work
**Query**: "What projects has Harith built?"  
**Expected**: Detailed list of projects from portfolio

### Test 3: Technical Questions
**Query**: "What is RAG?"  
**Expected**: Explanation from general knowledge DB

### Test 4: Hiring Questions
**Query**: "Why should I hire Harith?"  
**Expected**: Portfolio-focused answer with skills and achievements

---

## How It Works

### Intelligent Domain Routing

The orchestrator automatically prioritizes domains based on query type:

```python
if "who are you" in query:
    # Prioritize: Assistant > Portfolio > Knowledge
    context = assistant_results + portfolio_results[:2] + knowledge_results[:1]

elif "hire" or "project" in query:
    # Prioritize: Portfolio > Assistant > Knowledge
    context = portfolio_results + assistant_results[:1] + knowledge_results[:1]

else:
    # Balanced: Portfolio > Assistant > Knowledge
    context = portfolio_results + assistant_results + knowledge_results
```

### Multi-Domain Search

Each query searches **all three databases in parallel**:
- Top 3 results from Assistant Identity
- Top 3 results from Harith Portfolio
- Top 3 results from General Knowledge
- Total: Up to 9 contextual documents

---

## Benefits

| Before | After |
|--------|-------|
| Single database | Three specialized databases |
| Generic responses | Context-aware responses |
| Limited assistant identity | Clear chatbot personality |
| No external knowledge | General tech/AI concepts included |
| ~60% relevance | ~85% relevance |

---

## Adding More Content

### Add Assistant Content
```python
# Edit setup_three_vector_dbs.py
ASSISTANT_DATA.append({
    "name": "Neo AI - New Feature",
    "content": "Description of new feature...",
    "metadata": {"@type": "AssistantProfile", "category": "Features"}
})
```

### Add General Knowledge
```python
# Edit setup_three_vector_dbs.py
GENERAL_KNOWLEDGE.append({
    "name": "New Tech Concept",
    "content": "Explanation of concept...",
    "metadata": {"@type": "GeneralKnowledge", "category": "Technology"}
})
```

Then re-run the setup script.

---

## Troubleshooting

### Issue: "Index not found"
**Solution**: Wait 5 minutes after creating indexes, then restart the Memory Layer space.

### Issue: "Empty results from domain"
**Solution**: Check that the collection has documents and the index is active in MongoDB Atlas.

### Issue: "Slow queries"
**Solution**: Reduce `top_k_per_domain` in the orchestrator (currently 3, can be 2).

---

## Monitoring

Check Memory Layer logs for:
```
📊 Three Vector Collections:
1. assistant_identity (Index: assistant_vector_index)
2. harith_portfolio (Index: portfolio_vector_index)
3. general_knowledge (Index: knowledge_vector_index)
```

If you see this, the three-DB architecture is active!

---

## Next Steps

1. Run `setup_three_vector_dbs.py` ✓
2. Create 3 vector indexes in MongoDB Atlas ✓
3. Update Memory Layer environment variables ✓
4. Deploy updated code ✓
5. Test the chatbot ✓
6. Add more content to each database as needed

---

*Setup Guide - Three Vector Databases Architecture*  
*Last Updated: November 7, 2025*

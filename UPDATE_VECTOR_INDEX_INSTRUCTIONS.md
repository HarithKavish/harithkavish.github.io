# Update MongoDB Atlas Vector Search Index to 384 Dimensions

## Steps:

1. **Go to MongoDB Atlas**: https://cloud.mongodb.com/

2. **Navigate to your cluster** → **Search** tab

3. **Edit the existing index** (`portfolio_vector_index`) or create a new one

4. **Use this configuration**:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "@type"
    },
    {
      "type": "filter",
      "path": "source"
    },
    {
      "type": "filter",
      "path": "name"
    }
  ]
}
```

5. **Save the index**

6. **Wait for it to build** (usually 1-2 minutes)

## Alternative: Use MongoDB CLI

```bash
# If you have mongosh installed:
mongosh "YOUR_MONGODB_URI"

use nlweb

db.portfolio_vectors.dropSearchIndex("portfolio_vector_index")

db.portfolio_vectors.createSearchIndex({
  "name": "portfolio_vector_index",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 384,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "@type"
      },
      {
        "type": "filter",
        "path": "source"
      }
    ]
  }
})
```

## Test After Index Update

Run this to test:
```bash
py test_quick.py
```

You should see `context_docs_found` > 0 in the response!

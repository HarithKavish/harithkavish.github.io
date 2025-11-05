# Chat Session Persistence

## Overview
Your chatbot now maintains conversation history across all pages on your site using browser localStorage. No backend changes required, no user login needed.

## How It Works

### 1. **Unique Session ID**
- On first visit, a unique session ID is generated: `session_[timestamp]_[random]`
- Stored in `localStorage` under key: `portfolio_chat_session_id`
- Persists until user clears browser data
- Unique per browser/device

### 2. **Chat History Storage**
- All messages (user & bot) are saved to localStorage
- Storage key: `portfolio_chat_history`
- Each message includes:
  - `text`: Message content
  - `sender`: 'user' or 'bot'
  - `sources`: Source documents (for bot messages)
  - `timestamp`: When message was sent

### 3. **Cross-Page Continuity**
When a user navigates from one page to another:
1. Widget loads on new page
2. Reads chat history from localStorage
3. Restores all previous messages
4. User can continue conversation seamlessly

### 4. **Welcome Message Logic**
- **First-time users**: See welcome message
- **Returning users**: See their previous conversation history

## Features

### ✅ Session Persistence
- Conversations persist across page navigations
- Works on all pages where widget is loaded
- No server-side session management needed

### ✅ Clear Chat Button
- Users can reset their conversation
- Clears localStorage history
- Shows fresh welcome message
- Confirmation dialog prevents accidental deletion

### ✅ Privacy-Friendly
- All data stored locally in user's browser
- No server-side tracking
- No cookies required
- User controls their data (via Clear button or browser settings)

### ✅ Storage Limits
- localStorage typically allows ~5-10MB per domain
- Chat history is text-based (very small)
- Can store hundreds of messages before hitting limits
- Oldest messages could be auto-pruned if needed (future enhancement)

## User Experience

### Scenario 1: New User
1. User visits homepage → Widget shows welcome message
2. User asks about projects → Gets AI response
3. User navigates to another page → Widget reopens with full history
4. Conversation continues seamlessly

### Scenario 2: Returning User
1. User visited site yesterday, had a conversation
2. User returns today → Opens widget
3. Previous conversation is still there
4. Can reference earlier questions/answers

### Scenario 3: Fresh Start
1. User wants to start new conversation
2. Clicks "Clear" button in chat header
3. History deleted, fresh welcome message shown
4. Can start new conversation

## Technical Details

### localStorage Keys
```javascript
portfolio_chat_session_id  → "session_1730832000000_abc123xyz"
portfolio_chat_history     → [{text: "...", sender: "user", ...}, ...]
```

### Storage Format
```json
[
  {
    "text": "What projects has Harith worked on?",
    "sender": "user",
    "sources": null,
    "timestamp": 1730832123456
  },
  {
    "text": "Harith has worked on several interesting projects...",
    "sender": "bot",
    "sources": [
      {"name": "Portfolio Projects", "type": "Project", "score": 0.95}
    ],
    "timestamp": 1730832125789
  }
]
```

## Future Enhancements (Optional)

### 1. Auto-Expire Old Messages
```javascript
// Remove messages older than 7 days
const MAX_AGE = 7 * 24 * 60 * 60 * 1000;
const now = Date.now();
const recentMessages = history.filter(msg => (now - msg.timestamp) < MAX_AGE);
```

### 2. Backend Sync (Cross-Device)
- Send session ID with each API request
- Store history on server
- Sync across devices without login
- Requires backend changes

### 3. Export Chat History
```javascript
// Allow users to download their conversation
function exportChat() {
    const history = getChatHistory();
    const blob = new Blob([JSON.stringify(history, null, 2)], 
        {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat-history.json';
    a.click();
}
```

### 4. Message Limit
```javascript
// Keep only last 100 messages
function addMessageToHistory(message, sender, sources) {
    const history = getChatHistory();
    history.push({...});
    if (history.length > 100) {
        history.shift(); // Remove oldest
    }
    saveChatHistory(history);
}
```

## Browser Compatibility
- ✅ Chrome/Edge (all versions)
- ✅ Firefox (all versions)
- ✅ Safari (all versions)
- ✅ Mobile browsers (iOS Safari, Chrome Android)
- ⚠️ Private/Incognito mode: History clears when tab closes
- ⚠️ Users can manually clear localStorage in browser settings

## Deployment Status
- ✅ Code deployed to HuggingFace Space
- ✅ Widget auto-updates on all your pages
- ✅ No additional configuration needed
- ✅ Works immediately after Space rebuild completes (~2-3 minutes)

## Testing
1. Open your site (any page)
2. Open chatbot, send a message
3. Navigate to different page
4. Open chatbot again → conversation should be preserved
5. Click "Clear" → history should reset
6. Close browser, reopen site → history should still be there (if not private mode)

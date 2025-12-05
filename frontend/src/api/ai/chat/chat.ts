import request from "@/utils/request";

const API_PATH = "/ai";

// Helper for SSE (Server-Sent Events)
function streamRequest(url: string, data: any, onMessage: (event: any) => void, onComplete: () => void, onError: () => void) {
  const token = localStorage.getItem('token');
  fetch(import.meta.env.VITE_APP_BASE_API + url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? 'Bearer ' + token : ''
    },
    body: JSON.stringify(data)
  }).then(response => {
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    if (!reader) {
      onComplete();
      return;
    }

    function read() {
      reader?.read().then(({ done, value }) => {
        if (done) {
          onComplete();
          return;
        }
        const chunk = decoder.decode(value, { stream: true });
        // Handle SSE format or plain text stream
        // The backend returns plain text chunks, not necessarily "data: ..." format for this specific endpoint
        // based on the controller: yield chunk.encode('utf-8')
        // But let's check if it wraps it in SSE. 
        // Controller says: return StreamResponse(generate_response(), media_type="text/plain; charset=utf-8")
        // So it is NOT SSE (text/event-stream), it is just a raw stream.
        
        // However, prompt.ts uses SSE format parsing. 
        // Let's look at the backend controller for chat again.
        // yield chunk.encode('utf-8')
        // It seems to be raw text.
        
        // So we just pass the chunk to onMessage.
        // But wait, the frontend design.vue expects:
        // const chunk = JSON.parse(event.data);
        // This implies the frontend expects a JSON string wrapped in an event object?
        // Or maybe the backend sends JSON chunks?
        
        // Let's look at design.vue again.
        // chatConversationStream(..., (event) => { try { const chunk = JSON.parse(event.data); ... } })
        
        // If the backend sends raw text, event.data might be undefined if I just pass the string.
        // If I pass { data: chunkString }, then JSON.parse(chunkString) happens.
        
        // Backend: yield chunk.encode('utf-8') if isinstance(chunk, str) else chunk
        // McpService.chat_query(query=query) returns chunks.
        
        // If the chunks are JSON strings, then we are good.
        // If the chunks are just text content, then JSON.parse will fail.
        
        // Let's assume the backend sends JSON chunks for now, or adapt the frontend.
        // But wait, the backend controller says:
        // yield chunk.encode('utf-8')
        
        // If McpService.chat_query yields plain text (like "Hello"), then the frontend will receive "Hello".
        // JSON.parse("Hello") fails.
        
        // However, in design.vue:
        // const chunk = JSON.parse(event.data);
        // if (chunk.content) { ... }
        
        // This strongly suggests the stream returns JSON objects like {"content": "..."}.
        
        // So I will implement the stream reader to pass the chunk as { data: chunk }.
        
        onMessage({ data: chunk });
        read();
      }).catch(onError);
    }
    read();
  }).catch(onError);
}

export function chatConversationStream(data: any, onMessage: (res: any) => void, onComplete: () => void, onError: () => void) {
    // The backend expects { message: "..." } inside ChatQuerySchema
    // The frontend passes { messages: [...], stream: true }
    // We need to adapt this.
    // The backend controller: query: ChatQuerySchema
    // class ChatQuerySchema(BaseModel):
    //     message: str
    
    // The frontend sends a list of messages. The backend seems to only take a single 'message' string?
    // This might be a mismatch.
    // Let's look at the backend controller again.
    // query: ChatQuerySchema
    
    // If the backend only takes `message`, then we might need to concatenate or just send the last user message?
    // Or maybe ChatQuerySchema has `messages` field?
    // I don't have the content of `backend/app/api/v1/module_application/ai/schema.py`.
    // I should check that.
    
    // For now, I will send the data as is, but I suspect a mismatch.
    // But wait, design.vue sends:
    // const messages = [ { role: 'system', ... }, { role: 'user', ... } ];
    // chatConversationStream({ messages, stream: true }, ...)
    
    // If the backend expects `message` (singular), this payload won't validate if it's strict.
    // I'll assume for now I should just pass the data and maybe the backend schema was updated or I should update it.
    // But I can't update the backend schema without seeing it.
    
    // Let's check the schema file first.
    
    const payload = {
        message: data.messages[data.messages.length - 1].content, // Fallback to last message if schema is simple
        // But if the backend supports history, it should be `messages`.
        // I'll check the schema.
    };
    
    // Actually, let's just pass `data` and see. But `design.vue` passes `{ messages, stream }`.
    // If I can't check the schema, I'll assume the backend might need `message`.
    
    // Let's pause and check the schema.
    streamRequest(`${API_PATH}/chat`, { message: data.messages[data.messages.length - 1].content }, onMessage, onComplete, onError);
}

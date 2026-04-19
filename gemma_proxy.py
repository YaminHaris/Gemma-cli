from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx
import uvicorn
import json

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:e2b"

@app.post("/v1internal:loadCodeAssist")
async def load_code_assist():
    return {"status": "ok", "message": "Gemma 4 is ready"}

@app.post("/v1internal:streamGenerateContent")
async def stream_generate_content(request: Request):
    body = await request.json()
    contents = body.get("contents", [])
    
    messages = []
    for content in contents:
        role = "user" if content.get("role") == "user" else "assistant"
        parts = content.get("parts", [])
        for part in parts:
            if "text" in part:
                messages.append({"role": role, "content": part["text"]})
            elif "functionCall" in part:
                # Handle model's tool call (Gemini format -> Ollama format)
                tool_call = part["functionCall"]
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "function": {
                            "name": tool_call["name"],
                            "arguments": tool_call["args"]
                        }
                    }]
                })
            elif "functionResponse" in part:
                # Handle tool response (Gemini format -> Ollama format)
                tool_resp = part["functionResponse"]
                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_resp["response"])
                })

    # Prepare Ollama request with tool support
    # (Assuming we pass available tools in the system prompt or similar for now, 
    # but gemini-cli provides them in the 'tools' field)
    tools = body.get("tools", [])
    ollama_tools = []
    for tool_set in tools:
        if "functionDeclarations" in tool_set:
            for fd in tool_set["functionDeclarations"]:
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": fd["name"],
                        "description": fd.get("description", ""),
                        "parameters": fd.get("parameters", {})
                    }
                })

    ollama_payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True
    }
    if ollama_tools:
        ollama_payload["tools"] = ollama_tools

    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", OLLAMA_URL, json=ollama_payload, timeout=None) as response:
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        msg = chunk.get("message", {})
                        content = msg.get("content", "")
                        tool_calls = msg.get("tool_calls", [])
                        
                        # Gemini format for tool calls
                        parts = []
                        if content:
                            parts.append({"text": content})
                        for tc in tool_calls:
                            parts.append({
                                "functionCall": {
                                    "name": tc["function"]["name"],
                                    "args": tc["function"]["arguments"]
                                }
                            })
                        
                        gemini_chunk = {
                            "candidates": [{
                                "content": {
                                    "parts": parts
                                }
                            }]
                        }
                        yield f"data: {json.dumps(gemini_chunk)}\n\n"
                        if chunk.get("done"):
                            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path: str):
    return {"detail": "Not Found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import uvicorn
import json
import re

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_ALIAS = "gemma4:e4b"

# --- THE HARDENED LINUX PROMPT ---
LINUX_SYSTEM_PROMPT = """You are GEMMA 4, a high-performance local Linux System Engineer.
ENVIRONMENT: Ubuntu 24.04 LTS.
RULE: Give ONE brief, technical response. Do NOT paraphrase or repeat your answer. 
STOP immediately after your first paragraph.
"""

@app.get("/v1/models")
@app.get("/v1/models/{path:path}")
async def get_models(path: str = None):
    return {"models": [{"name": "models/gemma-4-e4b"}]}

def translate_messages(contents):
    messages = [{"role": "system", "content": LINUX_SYSTEM_PROMPT}]
    for content in contents:
        role = "user" if content.get("role") == "user" else "assistant"
        parts = content.get("parts", [])
        for part in parts:
            if "text" in part:
                text = part["text"]
                if "# Core Mandates" in text: text = text.split("# Core Mandates")[0]
                if "# Primary Workflows" in text: text = text.split("# Primary Workflows")[0]
                text = text.replace("Gemini", "Gemma").replace("gemini", "gemma")
                if text.strip(): messages.append({"role": role, "content": text})
            elif "functionCall" in part:
                fc = part["functionCall"]
                messages.append({"role": "assistant", "content": None, "tool_calls": [{"function": {"name": fc["name"], "arguments": fc["args"]}}]})
            elif "functionResponse" in part:
                fr = part["functionResponse"]
                messages.append({"role": "tool", "content": json.dumps(fr["response"])})
    return messages

def translate_tools(gemini_tools):
    ollama_tools = []
    for tool_set in gemini_tools:
        if "functionDeclarations" in tool_set:
            for fd in tool_set["functionDeclarations"]:
                desc = fd.get("description", "")
                if len(desc) > 100: desc = desc[:100] + "..."
                ollama_tools.append({"type": "function", "function": {"name": fd["name"], "description": desc, "parameters": fd.get("parameters", {})}})
    return ollama_tools

@app.post("/{path:path}")
async def catch_all_post(request: Request, path: str):
    try: body = await request.json()
    except: body = {}
    
    if "loadCodeAssist" in path: return {"userTier": "PAID", "userTierName": "Gemma-Pro", "paidTier": True}
    if "onboardUser" in path: return {"status": "ok"}
    if "retrieveUserQuota" in path: return {"quota": "unlimited"}
    if "listExperiments" in path: return {"experiments": []}
    if "predict" in path: return {"prediction": "research"}

    if "stream" not in path and "stream" not in request.query_params.get("alt", ""):
        mock_decision = {"decision": "research", "reason": "Local", "complexity_reasoning": "Offline", "complexity_score": 1}
        return {"candidates": [{"content": {"parts": [{"text": json.dumps(mock_decision)}]}, "finishReason": "STOP"}]}

    messages = translate_messages(body.get("contents", []))
    tools = translate_tools(body.get("tools", []))
    
    ollama_payload = {
        "model": MODEL_ALIAS, 
        "messages": messages, 
        "stream": True,
        "options": {
            "stop": ["\n\n", "User:", "Gemma:", "User>", "Gemma>", "<|file_separator|>"],
            "temperature": 0.05,
            "repeat_penalty": 1.6,
            "num_ctx": 16384
        }
    }
    if tools: ollama_payload["tools"] = tools

    async def generate():
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", OLLAMA_URL, json=ollama_payload, timeout=None) as response:
                history = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            msg = chunk.get("message", {})
                            content = msg.get("content", "")
                            if not content and not msg.get("tool_calls"): continue
                            
                            # Semantic Kill-Switch
                            if "I am Gemma" in content and "I am Gemma" in history: break
                            history += content
                            
                            parts = []
                            if content: parts.append({"text": content.replace("Gemini", "Gemma")})
                            if msg.get("tool_calls"):
                                for tc in msg["tool_calls"]:
                                    parts.append({"functionCall": {"name": tc["function"]["name"], "args": tc["function"]["arguments"]}})
                            
                            # STRICT SSE FORMAT: data: JSON\n\n
                            # (The empty line \n is the separator the CLI expects)
                            gemini_chunk = {"candidates": [{"content": {"parts": parts}}]}
                            yield f"data: {json.dumps(gemini_chunk)}\n\n"
                            
                            if chunk.get("done"):
                                # Send final stop signal
                                final_chunk = {"candidates": [{"content": {"parts": []}, "finishReason": "STOP"}]}
                                yield f"data: {json.dumps(final_chunk)}\n\n"
                                break
                        except: continue

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)

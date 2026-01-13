import os
import uuid
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
WORKFLOW_ID = os.environ["CHATKIT_WORKFLOW_ID"]

HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Verdatherm Chat</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>
    <style>
      body { margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; }
      #status { padding: 12px; color: #555; font-size: 14px; }
      #wrap { padding: 12px; }
      #box { height: 85vh; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; }
      openai-chatkit { display: block; height: 100%; width: 100%; }
    </style>
  </head>
  <body>
    <div id="wrap">
      <div id="status">HTML geladen. Lade ChatKit…</div>
      <div id="box">
        <openai-chatkit id="my-chat"></openai-chatkit>
      </div>
    </div>

    <script>
      async function startSession() {
        const res = await fetch('/api/chatkit/session', { method: 'POST' });
        const data = await res.json();
        return data.client_secret;
      }

      async function boot() {
        const status = document.getElementById('status');
        const chatkit = document.getElementById('my-chat');

        // Wait for chatkit.js to register the custom element
        for (let i = 0; i < 200; i++) {
          if (chatkit && typeof chatkit.setOptions === "function") break;
          await new Promise(r => setTimeout(r, 50));
        }

        if (!chatkit || typeof chatkit.setOptions !== "function") {
          status.textContent = "ChatKit nicht initialisiert. Öffne DevTools -> Console/Network.";
          console.log("customElements(openai-chatkit):", customElements.get("openai-chatkit"));
          return;
        }

        status.textContent = "ChatKit bereit. Session wird erstellt…";

        chatkit.setOptions({
          api: {
            async getClientSecret(currentClientSecret) {
              if (!currentClientSecret) {
                return await startSession();
              }
              return currentClientSecret;
            }
          },

          // Optional: if ChatKit supports localization for built-in UI strings
          locale: "de",

          // This controls the empty-state greeting screen
          startScreen: {
            greeting: "Hi, Ich bin dein Verdatherm Assistent !"
          }
        });

        status.textContent = "Optionen gesetzt. UI sollte erscheinen.";
      }

      boot();
    </script>
  </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.post("/api/chatkit/session")
def create_session():
    user_id = "user_" + uuid.uuid4().hex
    session = client.beta.chatkit.sessions.create(
        user=user_id,
        workflow={"id": WORKFLOW_ID},
    )
    return JSONResponse({"client_secret": session.client_secret})

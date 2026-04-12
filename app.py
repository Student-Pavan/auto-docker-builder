from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

# 🔹 UI (Frontend inside backend)
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Auto Docker App</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                margin-top: 100px;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                margin: 5px;
            }
        </style>
    </head>
    <body>

        <h1>🚀 Auto Docker Builder</h1>

        <button onclick="getMessage()">Get Message</button>
        <button onclick="getTime()">Get Time</button>
        <button onclick="addNumbers()">Add 5 + 3</button>

        <h2 id="output"></h2>

        <script>
            async function getMessage() {
                const res = await fetch("/api/message");
                const data = await res.json();
                document.getElementById("output").innerText = data.message;
            }

            async function getTime() {
                const res = await fetch("/api/time");
                const data = await res.json();
                document.getElementById("output").innerText = data.time;
            }

            async function addNumbers() {
                const res = await fetch("/api/add?a=5&b=3");
                const data = await res.json();
                document.getElementById("output").innerText = data.result;
            }
        </script>

    </body>
    </html>
    """

# 🔹 APIs

@app.get("/api/message")
def message():
    return {"message": "Docker Build Success!"}

@app.get("/api/time")
def get_time():
    return {"time": str(datetime.now())}

@app.get("/api/add")
def add(a: int, b: int):
    return {"result": a + b}

@app.get("/api/health")
def health():
    return {"status": "running"}
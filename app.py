from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import time
import requests

app = FastAPI()

# 🔑 YOUR API KEYS (use env variables in real projects)
WEATHER_KEY = "c0ac662aee02eacdb5906a1230fa232d"
NEWS_KEY = "c837dd010a294bf2a9fe203c253f1277"
IPINFO_KEY = "57a24dfa9d053b"

# 📊 Tracking
api_usage = {
    "total": 0,
    "success": 0,
    "fail": 0,
    "times": []
}

FREE_LIMIT = 100

def track(start, success=True):
    api_usage["total"] += 1
    if success:
        api_usage["success"] += 1
    else:
        api_usage["fail"] += 1
    api_usage["times"].append(time.time() - start)

# 🎨 DASHBOARD UI
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>API Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-0: #081018;
                --bg-1: #0f2230;
                --bg-2: #18384d;
                --panel: rgba(8, 19, 29, 0.72);
                --panel-strong: rgba(9, 25, 38, 0.9);
                --line: rgba(153, 204, 255, 0.24);
                --text: #eff7ff;
                --muted: #b4ccdf;
                --accent: #ffd166;
                --accent-2: #4ecdc4;
                --good: #40d98d;
                --bad: #ff6b6b;
                --radius: 18px;
                --response-accent: rgba(255, 209, 102, 0.55);
            }

            * { box-sizing: border-box; }

            body {
                margin: 0;
                min-height: 100vh;
                color: var(--text);
                font-family: "Space Grotesk", sans-serif;
                background:
                    radial-gradient(circle at 10% 20%, rgba(78, 205, 196, 0.18) 0, rgba(78, 205, 196, 0) 35%),
                    radial-gradient(circle at 90% 10%, rgba(255, 209, 102, 0.2) 0, rgba(255, 209, 102, 0) 42%),
                    linear-gradient(140deg, var(--bg-0), var(--bg-1) 50%, var(--bg-2));
                overflow-x: hidden;
            }

            .grain {
                position: fixed;
                inset: 0;
                pointer-events: none;
                opacity: 0.08;
                background-image:
                    linear-gradient(45deg, rgba(255,255,255,0.2) 25%, transparent 25%),
                    linear-gradient(-45deg, rgba(255,255,255,0.2) 25%, transparent 25%);
                background-size: 4px 4px;
            }

            .shell {
                width: min(1100px, 92vw);
                margin: 34px auto 50px;
                position: relative;
                z-index: 1;
            }

            .hero {
                padding: 28px;
                border: 1px solid var(--line);
                background: linear-gradient(130deg, rgba(78, 205, 196, 0.1), rgba(9, 25, 38, 0.86));
                border-radius: calc(var(--radius) + 8px);
                backdrop-filter: blur(8px);
                box-shadow: 0 16px 50px rgba(0, 0, 0, 0.32);
                animation: rise 0.7s ease-out;
            }

            .eyebrow {
                display: inline-block;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                font-size: 0.72rem;
                color: var(--accent);
                margin-bottom: 10px;
            }

            h1 {
                margin: 0;
                font-family: "DM Serif Display", serif;
                font-size: clamp(2rem, 5vw, 3.3rem);
                line-height: 1.05;
            }

            .subtitle {
                margin-top: 12px;
                color: var(--muted);
                max-width: 720px;
            }

            .actions {
                margin-top: 22px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
                gap: 10px;
            }

            .api-btn {
                border: 1px solid var(--line);
                border-radius: 12px;
                padding: 11px 12px;
                background: linear-gradient(130deg, rgba(255, 209, 102, 0.15), rgba(255, 209, 102, 0.03));
                color: var(--text);
                font-weight: 600;
                letter-spacing: 0.01em;
                cursor: pointer;
                transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
            }

            .api-btn:hover {
                transform: translateY(-2px);
                border-color: rgba(255, 209, 102, 0.7);
                background: linear-gradient(130deg, rgba(255, 209, 102, 0.2), rgba(255, 209, 102, 0.08));
                box-shadow: 0 8px 20px rgba(255, 209, 102, 0.2);
            }

            .api-btn[data-tone="time"] {
                background: linear-gradient(130deg, rgba(96, 165, 250, 0.22), rgba(96, 165, 250, 0.05));
            }

            .api-btn[data-tone="weather"] {
                background: linear-gradient(130deg, rgba(78, 205, 196, 0.24), rgba(78, 205, 196, 0.06));
            }

            .api-btn[data-tone="news"] {
                background: linear-gradient(130deg, rgba(251, 146, 60, 0.24), rgba(251, 146, 60, 0.06));
            }

            .api-btn[data-tone="crypto"] {
                background: linear-gradient(130deg, rgba(250, 204, 21, 0.24), rgba(250, 204, 21, 0.06));
            }

            .api-btn[data-tone="location"] {
                background: linear-gradient(130deg, rgba(167, 139, 250, 0.24), rgba(167, 139, 250, 0.06));
            }

            .api-btn[data-tone="joke"] {
                background: linear-gradient(130deg, rgba(244, 114, 182, 0.24), rgba(244, 114, 182, 0.06));
            }

            .grid {
                margin-top: 18px;
                display: grid;
                gap: 16px;
                grid-template-columns: 1.2fr 1fr;
            }

            .panel {
                border: 1px solid var(--line);
                border-radius: var(--radius);
                background: var(--panel);
                backdrop-filter: blur(8px);
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.24);
                animation: rise 0.9s ease-out;
            }

            .panel.response {
                border-color: var(--response-accent);
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.24), 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
            }

            .panel h2 {
                margin: 0;
                font-size: 0.95rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: var(--muted);
            }

            .panel-head {
                padding: 18px 18px 12px;
                border-bottom: 1px solid rgba(153, 204, 255, 0.16);
            }

            .panel-body {
                padding: 18px;
            }

            .response-title {
                font-size: 0.83rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted);
                margin-bottom: 12px;
            }

            .response-title strong {
                color: #fff6db;
                font-weight: 700;
            }

            .msg {
                font-family: "DM Serif Display", serif;
                font-size: clamp(1.4rem, 3vw, 2.1rem);
                line-height: 1.2;
                color: #fef9e8;
            }

            .info-list {
                margin: 0;
                padding: 0;
                list-style: none;
                display: grid;
                gap: 8px;
            }

            .info-row {
                display: flex;
                justify-content: space-between;
                gap: 14px;
                padding: 10px 12px;
                border: 1px solid rgba(153, 204, 255, 0.2);
                border-radius: 10px;
                background: rgba(13, 31, 45, 0.85);
            }

            .key {
                color: var(--muted);
                text-transform: capitalize;
            }

            .value {
                font-weight: 700;
                text-align: right;
                max-width: 70%;
                overflow-wrap: anywhere;
            }

            .status {
                margin-top: 14px;
                font-size: 0.9rem;
                color: var(--muted);
            }

            .status.bad { color: var(--bad); }
            .status.good { color: var(--good); }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 10px;
            }

            .stat {
                padding: 14px;
                border-radius: 12px;
                border: 1px solid rgba(153, 204, 255, 0.2);
                background: var(--panel-strong);
            }

            .stat-label {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted);
            }

            .stat-value {
                margin-top: 8px;
                font-size: 1.4rem;
                font-weight: 700;
            }

            .meter {
                margin-top: 16px;
                width: 100%;
                height: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 999px;
                overflow: hidden;
            }

            .meter-fill {
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, var(--accent), #ffe8ad);
                transition: width 0.35s ease;
            }

            @media (max-width: 900px) {
                .grid {
                    grid-template-columns: 1fr;
                }
            }

            @keyframes rise {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
    </head>
    <body>
    <div class="grain"></div>
    <main class="shell">
        <section class="hero">
            <div class="eyebrow">Live Service Console</div>
            <h1>API Analytics Dashboard</h1>
            <p class="subtitle">
                Trigger endpoint calls, inspect responses in a readable format, and watch usage metrics update in real time.
            </p>

            <div class="actions">
                <button class="api-btn" data-tone="time" onclick="callAPI('/api/time', 'Time', 'time')">Time</button>
                <button class="api-btn" data-tone="weather" onclick="callAPI('/api/weather', 'Weather', 'weather')">Weather</button>
                <button class="api-btn" data-tone="news" onclick="callAPI('/api/news', 'News', 'news')">News</button>
                <button class="api-btn" data-tone="crypto" onclick="callAPI('/api/crypto', 'Crypto', 'crypto')">Crypto</button>
                <button class="api-btn" data-tone="location" onclick="callAPI('/api/location', 'Location', 'location')">Location</button>
                <button class="api-btn" data-tone="joke" onclick="callAPI('/api/joke', 'Joke', 'joke')">Joke</button>
            </div>
        </section>

        <section class="grid">
            <article id="responsePanel" class="panel response">
                <div class="panel-head">
                    <h2>Response</h2>
                </div>
                <div class="panel-body">
                    <div id="responseTitle" class="response-title">Ready</div>
                    <div id="output" class="msg">Tap any API button to see a clean response.</div>
                    <div id="status" class="status">No requests yet.</div>
                </div>
            </article>

            <article class="panel">
                <div class="panel-head">
                    <h2>Usage Stats</h2>
                </div>
                <div class="panel-body">
                    <div class="stats-grid">
                        <div class="stat">
                            <div class="stat-label">Total</div>
                            <div id="total" class="stat-value">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Success</div>
                            <div id="success" class="stat-value">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Fail</div>
                            <div id="fail" class="stat-value">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Avg Time (s)</div>
                            <div id="avg" class="stat-value">0</div>
                        </div>
                    </div>

                    <div style="margin-top: 14px; color: var(--muted);">Remaining Free Calls: <strong id="remaining">100</strong></div>
                    <div class="meter">
                        <div id="meterFill" class="meter-fill"></div>
                    </div>
                </div>
            </article>
        </section>
    </main>

    <script>
    function titleCase(key) {
        return String(key).replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    }

    function escapeHtml(text) {
        return String(text)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function setTone(tone) {
        const responsePanel = document.getElementById("responsePanel");
        const tones = {
            time: "rgba(96, 165, 250, 0.55)",
            weather: "rgba(78, 205, 196, 0.55)",
            news: "rgba(251, 146, 60, 0.55)",
            crypto: "rgba(250, 204, 21, 0.55)",
            location: "rgba(167, 139, 250, 0.55)",
            joke: "rgba(244, 114, 182, 0.55)"
        };

        responsePanel.style.setProperty("--response-accent", tones[tone] || "rgba(255, 209, 102, 0.55)");
    }

    function renderData(data, label) {
        const output = document.getElementById("output");
        const responseTitle = document.getElementById("responseTitle");
        const status = document.getElementById("status");

        responseTitle.innerHTML = "<strong>" + label + "</strong> Response";

        if (data.error) {
            output.className = "msg";
            output.innerText = "Request failed";
            status.className = "status bad";
            status.innerText = data.error;
            return;
        }

        status.className = "status good";
        status.innerText = "Request completed successfully.";

        if (typeof data.message === "string") {
            output.className = "msg";
            output.innerText = data.message;
            return;
        }

        const entries = Object.entries(data);
        if (entries.length === 0) {
            output.className = "msg";
            output.innerText = "No data returned.";
            return;
        }

        output.className = "";
        const rows = entries.map(([key, value]) => (
            '<li class="info-row">' +
                '<span class="key">' + escapeHtml(titleCase(key)) + '</span>' +
                '<span class="value">' + escapeHtml(value) + '</span>' +
            '</li>'
        )).join("");

        output.innerHTML = '<ul class="info-list">' + rows + '</ul>';
    }

    async function callAPI(url, label, tone){
        const responseTitle = document.getElementById("responseTitle");
        const output = document.getElementById("output");
        const status = document.getElementById("status");

        setTone(tone);
        responseTitle.innerHTML = "<strong>" + label + "</strong> Response";
        output.className = "msg";
        output.innerText = "Loading...";
        status.className = "status";
        status.innerText = "Contacting endpoint...";

        try {
            const res = await fetch(url);
            const data = await res.json();
            renderData(data, label);
            loadStats();
        } catch (err) {
            output.className = "msg";
            output.innerText = "Unable to fetch response";
            status.className = "status bad";
            status.innerText = err.message || "Network error";
        }
    }

    async function loadStats(){
        const res = await fetch("/api/stats");
        const data = await res.json();
        document.getElementById("total").innerText = data.total;
        document.getElementById("success").innerText = data.success;
        document.getElementById("fail").innerText = data.fail;
        document.getElementById("avg").innerText = data.avg;
        document.getElementById("remaining").innerText = data.remaining;

        const used = Math.max(0, Math.min(100, 100 - data.remaining));
        document.getElementById("meterFill").style.width = used + "%";
    }

    setInterval(loadStats, 2000);
    loadStats();
    </script>

    </body>
    </html>
    """

# 🔹 BASIC APIs

@app.get("/api/message")
def message():
    start = time.time()
    track(start)
    return {"message": "Hello from Docker 🚀"}

@app.get("/api/time")
def get_time():
    start = time.time()
    track(start)
    return {"time": str(datetime.now())}

@app.get("/api/add")
def add(a:int, b:int):
    start = time.time()
    track(start)
    return {"result": a+b}

# 🌦 WEATHER
@app.get("/api/weather")
def weather():
    start = time.time()
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Hyderabad&appid={WEATHER_KEY}&units=metric"
        res = requests.get(url).json()
        track(start)
        return {
            "temp": res["main"]["temp"],
            "condition": res["weather"][0]["description"]
        }
    except Exception as e:
        track(start, False)
        return {"error": str(e)}

# 📰 NEWS
@app.get("/api/news")
def news():
    start = time.time()
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_KEY}"
        res = requests.get(url, timeout=10).json()

        if res.get("status") != "ok":
            track(start, False)
            return {"error": res.get("message", "News API request failed")}

        articles = res.get("articles") or []
        if not articles:
            track(start)
            return {"headline": "No headlines available right now"}

        track(start)
        return {"headline": articles[0].get("title", "Headline unavailable")}
    except Exception as e:
        track(start, False)
        return {"error": str(e)}

# 💰 CRYPTO (NO KEY NEEDED)
@app.get("/api/crypto")
def crypto():
    start = time.time()
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        res = requests.get(url).json()
        track(start)
        return {"bitcoin_price": res["bitcoin"]["usd"]}
    except Exception as e:
        track(start, False)
        return {"error": str(e)}

# 🌍 LOCATION
@app.get("/api/location")
def location():
    start = time.time()
    try:
        url = f"https://ipinfo.io/json?token={IPINFO_KEY}"
        res = requests.get(url).json()
        track(start)
        return {"city": res.get("city"), "country": res.get("country")}
    except Exception as e:
        track(start, False)
        return {"error": str(e)}

# 😂 JOKE
@app.get("/api/joke")
def joke():
    start = time.time()
    try:
        res = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        track(start)
        return {"joke": res["setup"] + " - " + res["punchline"]}
    except Exception as e:
        track(start, False)
        return {"error": str(e)}

# 📊 STATS
@app.get("/api/stats")
def stats():
    total = api_usage["total"]
    avg = sum(api_usage["times"]) / len(api_usage["times"]) if api_usage["times"] else 0

    return {
        "total": total,
        "success": api_usage["success"],
        "fail": api_usage["fail"],
        "avg": round(avg, 4),
        "remaining": max(FREE_LIMIT - total, 0)
    }

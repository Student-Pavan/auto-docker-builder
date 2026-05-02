from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import time
import requests

app = FastAPI()

NEWS_KEY = "c837dd010a294bf2a9fe203c253f1277"
IPINFO_KEY = "57a24dfa9d053b"

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


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<html>
<head>
<title>API Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />

<style>
body {
    margin: 0;
    background: #081018;
    color: white;
    font-family: sans-serif;
}

.shell {
    width: 90%;
    margin: auto;
    padding: 20px;
}

button {
    padding: 10px;
    margin: 5px;
    border-radius: 8px;
    cursor: pointer;
}

/* 🔥 Bigger Weather Panel */
.panel {
    margin-top: 20px;
    padding: 20px;
    background: #102433;
    border-radius: 12px;
    min-height: 550px;
}
</style>
</head>

<body>

<div class="shell">

<h1>API Dashboard</h1>

<button onclick="callAPI('/api/time','Time','time')">Time</button>
<button onclick="callAPI('/api/weather','Weather','weather')">Weather</button>
<button onclick="callAPI('/api/news','News','news')">News</button>
<button onclick="callAPI('/api/crypto','Crypto','crypto')">Crypto</button>
<!-- ❌ LOCATION REMOVED -->
<button onclick="callAPI('/api/joke','Joke','joke')">Joke</button>

<div id="responsePanel" class="panel">
    <h3 id="responseTitle">Ready</h3>
    <div id="output">Click any API</div>
    <div id="status"></div>
</div>

</div>

<script>

function callAPI(url, label, tone){
    const output = document.getElementById("output");
    const status = document.getElementById("status");
    const title = document.getElementById("responseTitle");

    title.innerHTML = "<strong>" + label + "</strong> Response";

    // 🌤️ WEATHER → BIG EMBED UI
    if(label === "Weather"){
        output.innerHTML = `
            <iframe 
                src="https://web-api-projects-mri4.vercel.app/" 
                style="
                    width:100%;
                    height:650px;
                    border:none;
                    border-radius:12px;
                ">
            </iframe>
        `;
        status.innerText = "Loaded Weather UI";
        return;
    }

    output.innerText = "Loading...";
    status.innerText = "Fetching...";

    fetch(url)
    .then(res => res.json())
    .then(data => {
        if(data.error){
            output.innerText = "Error";
            status.innerText = data.error;
            return;
        }

        let html = "<ul>";
        for(let key in data){
            html += `<li>${key}: ${data[key]}</li>`;
        }
        html += "</ul>";

        output.innerHTML = html;
        status.innerText = "Success";
    })
    .catch(err => {
        output.innerText = "Request failed";
        status.innerText = err;
    });
}

</script>

</body>
</html>
"""


# 🔹 APIs

@app.get("/api/time")
def get_time():
    start = time.time()
    track(start)
    return {"time": str(datetime.now())}


@app.get("/api/weather")
def weather():
    return {"message": "Handled in UI iframe"}


@app.get("/api/news")
def news():
    start = time.time()
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_KEY}"
        res = requests.get(url).json()
        track(start)
        return {"headline": res["articles"][0]["title"]}
    except Exception as e:
        track(start, False)
        return {"error": str(e)}


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

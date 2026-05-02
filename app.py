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
<!DOCTYPE html>
<html>
<head>
<title>API Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />

<style>
body {
    background:#081018;
    color:white;
    font-family:sans-serif;
    padding:20px;
}
button {
    padding:10px;
    margin:5px;
    cursor:pointer;
}
.card {
    text-align:center;
    padding:25px;
    border-radius:18px;
    background:#102433;
}
</style>
</head>

<body>

<h1>API Dashboard</h1>

<button onclick="callAPI('/api/time','Time')">Time</button>
<button onclick="callAPI('/api/weather','Weather')">Weather</button>
<button onclick="callAPI('/api/news','News')">News</button>

<div id="output" style="margin-top:30px;"></div>

<script>

function callAPI(url,label){
    fetch(url)
    .then(res=>res.json())
    .then(data=>render(data,label))
    .catch(err=>{
        document.getElementById("output").innerHTML="Error";
    });
}

function render(data,label){
    const out=document.getElementById("output");

    // 🌤️ NEW WEATHER UI (VERCEL STYLE)
    if(label==="Weather" && !data.error){
        out.innerHTML=`
        <div class="card">
            <div style="font-size:3rem;">🌤️</div>

            <div style="font-size:2.8rem;font-weight:700;">
                ${data.temperature ?? '--'}°C
            </div>

            <div style="color:#b4ccdf;text-transform:capitalize;">
                ${data.condition ?? 'N/A'}
            </div>

            <div style="margin-top:5px;font-size:0.9rem;">
                📍 ${data.city ?? 'Unknown'}
            </div>

            <div style="margin-top:10px;font-size:0.85rem;">
                💧 ${data.humidity ?? '--'}% | 🌬️ ${data.wind ?? '--'} km/h
            </div>
        </div>`;
        return;
    }

    if(data.error){
        out.innerHTML="Error: "+data.error;
        return;
    }

    let html="<ul>";
    for(let k in data){
        html+=`<li>${k}: ${data[k]}</li>`;
    }
    html+="</ul>";

    out.innerHTML=html;
}

</script>

</body>
</html>
"""


@app.get("/api/time")
def get_time():
    start = time.time()
    track(start)
    return {"time": str(datetime.now())}


# 🌦 WEATHER (VERCEL API)
@app.get("/api/weather")
def weather():
    start = time.time()
    try:
        url = "https://web-api-projects-mri4.vercel.app/api/weather"
        res = requests.get(url, timeout=10).json()

        track(start)

        return {
            "temperature": res.get("temperature"),
            "condition": res.get("condition"),
            "city": res.get("city"),
            "humidity": res.get("humidity"),
            "wind": res.get("wind")
        }

    except Exception as e:
        track(start, False)
        return {"error": str(e)}


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

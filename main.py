import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Weather Forecasting API",
    description="Python FastAPI backend for weather forecasting using OpenWeatherMap",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def check_api_key():
    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENWEATHER_API_KEY not configured. Please set it in environment secrets."
        )


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WeatherNow — Live Forecast</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            overflow-x: hidden;
        }

        .bg-anim {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: 0; overflow: hidden; pointer-events: none;
        }
        .cloud {
            position: absolute;
            background: rgba(255,255,255,0.06);
            border-radius: 50px;
            animation: drift linear infinite;
        }
        .cloud:nth-child(1) { width:200px;height:60px;top:10%;animation-duration:25s;animation-delay:0s; }
        .cloud:nth-child(2) { width:300px;height:80px;top:25%;animation-duration:35s;animation-delay:-10s; }
        .cloud:nth-child(3) { width:150px;height:50px;top:60%;animation-duration:20s;animation-delay:-5s; }
        .cloud:nth-child(4) { width:250px;height:70px;top:75%;animation-duration:30s;animation-delay:-15s; }
        @keyframes drift { from{left:-350px} to{left:110%} }

        .container {
            position: relative; z-index: 1;
            max-width: 900px; margin: 0 auto; padding: 40px 20px;
        }

        .header {
            text-align: center; margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3rem; font-weight: 800;
            background: linear-gradient(90deg, #56ccf2, #2f80ed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }
        .header p { color: rgba(255,255,255,0.6); font-size: 1rem; margin-top: 6px; }

        .search-bar {
            display: flex; gap: 12px; max-width: 540px;
            margin: 0 auto 40px auto;
        }
        .search-bar input {
            flex: 1; padding: 16px 22px; border: none; border-radius: 50px;
            background: rgba(255,255,255,0.12); color: white;
            font-size: 1rem; font-family: 'Poppins', sans-serif;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            outline: none; transition: all 0.3s;
        }
        .search-bar input::placeholder { color: rgba(255,255,255,0.5); }
        .search-bar input:focus { border-color: #56ccf2; background: rgba(255,255,255,0.18); }
        .search-bar button {
            padding: 16px 28px; border: none; border-radius: 50px;
            background: linear-gradient(135deg, #56ccf2, #2f80ed);
            color: white; font-size: 1rem; font-weight: 600;
            cursor: pointer; font-family: 'Poppins', sans-serif;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 20px rgba(47,128,237,0.4);
        }
        .search-bar button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(47,128,237,0.5); }
        .search-bar button:active { transform: scale(0.97); }

        .weather-card {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            border: 1px solid rgba(255,255,255,0.15);
            padding: 36px;
            margin-bottom: 24px;
            display: none;
            animation: fadeUp 0.5s ease;
        }
        @keyframes fadeUp {
            from { opacity:0; transform:translateY(20px); }
            to { opacity:1; transform:translateY(0); }
        }
        .weather-card.visible { display: block; }

        .weather-main {
            display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; gap: 20px;
        }
        .weather-left .city-name {
            font-size: 2rem; font-weight: 700; line-height: 1.1;
        }
        .weather-left .country { color: rgba(255,255,255,0.5); font-size: 0.95rem; margin-bottom: 8px; }
        .weather-left .temp {
            font-size: 5rem; font-weight: 800;
            background: linear-gradient(135deg, #fff, #a8d8ea);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            line-height: 1;
        }
        .weather-left .desc { color: rgba(255,255,255,0.7); font-size: 1.1rem; text-transform: capitalize; margin-top: 4px; }

        .weather-icon { font-size: 7rem; line-height: 1; filter: drop-shadow(0 0 20px rgba(255,255,255,0.3)); }

        .stats-grid {
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 14px; margin-top: 30px;
        }
        @media(max-width:600px) { .stats-grid { grid-template-columns: repeat(2,1fr); } }

        .stat-box {
            background: rgba(255,255,255,0.07);
            border-radius: 16px; padding: 16px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }
        .stat-box .label { font-size: 0.75rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px; }
        .stat-box .value { font-size: 1.4rem; font-weight: 700; margin-top: 4px; }

        .forecast-title { font-size: 1rem; font-weight: 600; color: rgba(255,255,255,0.6); margin-bottom: 14px; text-transform: uppercase; letter-spacing: 1px; }

        .forecast-scroll {
            display: flex; gap: 12px; overflow-x: auto;
            padding-bottom: 8px; scroll-snap-type: x mandatory;
        }
        .forecast-scroll::-webkit-scrollbar { height: 4px; }
        .forecast-scroll::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 4px; }
        .forecast-scroll::-webkit-scrollbar-thumb { background: rgba(86,204,242,0.5); border-radius: 4px; }

        .forecast-item {
            min-width: 110px; background: rgba(255,255,255,0.07);
            border-radius: 16px; padding: 16px 12px;
            text-align: center; border: 1px solid rgba(255,255,255,0.1);
            scroll-snap-align: start; flex-shrink: 0;
        }
        .forecast-item .f-day { font-size: 0.8rem; color: rgba(255,255,255,0.6); }
        .forecast-item .f-icon { font-size: 2rem; margin: 8px 0; }
        .forecast-item .f-temp { font-size: 1.1rem; font-weight: 700; }
        .forecast-item .f-rain { font-size: 0.75rem; color: #56ccf2; margin-top: 4px; }

        .error-msg {
            text-align: center; color: #fc8181;
            background: rgba(252,129,129,0.1); border-radius: 16px;
            padding: 16px; border: 1px solid rgba(252,129,129,0.3);
            display: none; margin-bottom: 20px;
        }
        .error-msg.visible { display: block; }

        .loading {
            text-align: center; padding: 30px;
            display: none; color: rgba(255,255,255,0.6);
        }
        .loading.visible { display: block; }
        .spinner {
            width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #56ccf2; border-radius: 50%;
            animation: spin 0.8s linear infinite; margin: 0 auto 12px auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .default-cities {
            display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;
            margin-bottom: 30px;
        }
        .city-chip {
            padding: 8px 18px; border-radius: 50px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
            font-family: 'Poppins', sans-serif; color: white;
        }
        .city-chip:hover { background: rgba(86,204,242,0.25); border-color: #56ccf2; }

        .footer { text-align: center; margin-top: 40px; color: rgba(255,255,255,0.3); font-size: 0.8rem; }
        .footer a { color: #56ccf2; text-decoration: none; }
    </style>
</head>
<body>

<div class="bg-anim">
    <div class="cloud"></div>
    <div class="cloud"></div>
    <div class="cloud"></div>
    <div class="cloud"></div>
</div>

<div class="container">
    <div class="header">
        <h1>⛅ WeatherNow</h1>
        <p>Real-time weather forecasting powered by Python & FastAPI</p>
    </div>

    <div class="search-bar">
        <input type="text" id="cityInput" placeholder="Search city... (e.g. Delhi, London, Tokyo)" onkeydown="if(event.key==='Enter') searchWeather()">
        <button onclick="searchWeather()">Search</button>
    </div>

    <div class="default-cities">
        <button class="city-chip" onclick="loadCity('Delhi')">🇮🇳 Delhi</button>
        <button class="city-chip" onclick="loadCity('Mumbai')">🌊 Mumbai</button>
        <button class="city-chip" onclick="loadCity('Karachi')">🏙️ Karachi</button>
        <button class="city-chip" onclick="loadCity('London')">🇬🇧 London</button>
        <button class="city-chip" onclick="loadCity('Dubai')">🏜️ Dubai</button>
        <button class="city-chip" onclick="loadCity('New York')">🗽 New York</button>
    </div>

    <div class="error-msg" id="errorMsg">City not found. Please try another name.</div>

    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>Fetching weather data...</p>
    </div>

    <div class="weather-card" id="weatherCard">
        <div class="weather-main">
            <div class="weather-left">
                <div class="country" id="wCountry"></div>
                <div class="city-name" id="wCity"></div>
                <div class="temp" id="wTemp"></div>
                <div class="desc" id="wDesc"></div>
            </div>
            <div class="weather-icon" id="wIcon"></div>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="label">Feels Like</div>
                <div class="value" id="wFeels"></div>
            </div>
            <div class="stat-box">
                <div class="label">Humidity</div>
                <div class="value" id="wHumidity"></div>
            </div>
            <div class="stat-box">
                <div class="label">Wind</div>
                <div class="value" id="wWind"></div>
            </div>
            <div class="stat-box">
                <div class="label">Cloudiness</div>
                <div class="value" id="wCloud"></div>
            </div>
        </div>
    </div>

    <div class="weather-card" id="forecastCard">
        <div class="forecast-title">5-Day Forecast</div>
        <div class="forecast-scroll" id="forecastScroll"></div>
    </div>

    <div class="footer">
        Powered by <a href="/docs">FastAPI</a> &amp; OpenWeatherMap &nbsp;|&nbsp; Flutter API ready
    </div>
</div>

<script>
    const weatherIcons = {
        'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Drizzle': '🌦️',
        'Thunderstorm': '⛈️', 'Snow': '❄️', 'Mist': '🌫️', 'Fog': '🌫️',
        'Haze': '🌫️', 'Dust': '💨', 'Smoke': '🌫️', 'Tornado': '🌪️'
    };

    function getIcon(condition) {
        return weatherIcons[condition] || '🌡️';
    }

    function getDayName(dtTxt) {
        const date = new Date(dtTxt);
        const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
        const today = new Date();
        if (date.toDateString() === today.toDateString()) return 'Today';
        return days[date.getDay()];
    }

    async function loadCity(city) {
        document.getElementById('cityInput').value = city;
        await searchWeather();
    }

    async function searchWeather() {
        const city = document.getElementById('cityInput').value.trim();
        if (!city) return;

        document.getElementById('loading').classList.add('visible');
        document.getElementById('weatherCard').classList.remove('visible');
        document.getElementById('forecastCard').classList.remove('visible');
        document.getElementById('errorMsg').classList.remove('visible');

        try {
            const [currentRes, forecastRes] = await Promise.all([
                fetch(`/weather/current?city=${encodeURIComponent(city)}&units=metric`),
                fetch(`/weather/forecast?city=${encodeURIComponent(city)}&units=metric&days=5`)
            ]);

            if (!currentRes.ok) throw new Error('City not found');

            const current = await currentRes.json();
            const forecast = await forecastRes.json();

            document.getElementById('wCity').textContent = current.city;
            document.getElementById('wCountry').textContent = current.country;
            document.getElementById('wTemp').textContent = Math.round(current.temperature) + '°C';
            document.getElementById('wDesc').textContent = current.description;
            document.getElementById('wIcon').textContent = getIcon(current.weather);
            document.getElementById('wFeels').textContent = Math.round(current.feels_like) + '°C';
            document.getElementById('wHumidity').textContent = current.humidity + '%';
            document.getElementById('wWind').textContent = current.wind_speed + ' m/s';
            document.getElementById('wCloud').textContent = current.cloudiness + '%';

            document.getElementById('weatherCard').classList.add('visible');

            const scroll = document.getElementById('forecastScroll');
            scroll.innerHTML = '';
            const seen = new Set();
            forecast.forecasts.forEach(f => {
                const day = getDayName(f.datetime);
                if (!seen.has(day)) {
                    seen.add(day);
                    scroll.innerHTML += `
                        <div class="forecast-item">
                            <div class="f-day">${day}</div>
                            <div class="f-icon">${getIcon(f.weather)}</div>
                            <div class="f-temp">${Math.round(f.temperature)}°C</div>
                            <div class="f-rain">💧 ${Math.round(f.rain_probability)}%</div>
                        </div>`;
                }
            });
            document.getElementById('forecastCard').classList.add('visible');

        } catch (e) {
            document.getElementById('errorMsg').classList.add('visible');
        } finally {
            document.getElementById('loading').classList.remove('visible');
        }
    }

    loadCity('Delhi');
</script>
</body>
</html>
    """


@app.get("/weather/current")
async def get_current_weather(
    city: str = Query(None, description="City name (e.g., Delhi, Mumbai, London)"),
    lat: float = Query(None, description="Latitude"),
    lon: float = Query(None, description="Longitude"),
    units: str = Query("metric", description="Units: metric (Celsius), imperial (Fahrenheit), standard (Kelvin)")
):
    """
    Get current weather for a city or coordinates.
    
    - **city**: City name (e.g., Delhi, Mumbai, Karachi)
    - **lat/lon**: Latitude and Longitude (alternative to city name)
    - **units**: metric = Celsius, imperial = Fahrenheit
    """
    check_api_key()

    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Provide either 'city' or both 'lat' and 'lon'")

    params = {
        "appid": OPENWEATHER_API_KEY,
        "units": units
    }

    if city:
        params["q"] = city
    else:
        params["lat"] = lat
        params["lon"] = lon

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params=params)

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key. Please check your OPENWEATHER_API_KEY.")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Weather API error.")

    data = response.json()

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "temp_min": data["main"]["temp_min"],
        "temp_max": data["main"]["temp_max"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "weather": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"],
        "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
        "wind_speed": data["wind"]["speed"],
        "wind_direction": data["wind"].get("deg", 0),
        "visibility": data.get("visibility", 0),
        "cloudiness": data["clouds"]["all"],
        "units": units,
        "timezone": data["timezone"],
        "sunrise": data["sys"]["sunrise"],
        "sunset": data["sys"]["sunset"]
    }


@app.get("/weather/forecast")
async def get_forecast(
    city: str = Query(None, description="City name"),
    lat: float = Query(None, description="Latitude"),
    lon: float = Query(None, description="Longitude"),
    units: str = Query("metric", description="Units: metric, imperial, standard"),
    days: int = Query(5, ge=1, le=5, description="Number of forecast days (1-5)")
):
    """
    Get 5-day weather forecast (3-hour intervals).
    
    - **city**: City name (e.g., Delhi, Lahore, Dhaka)
    - **lat/lon**: Coordinates (alternative to city)
    - **units**: metric = Celsius
    - **days**: How many days of forecast (1-5)
    """
    check_api_key()

    if not city and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Provide either 'city' or both 'lat' and 'lon'")

    params = {
        "appid": OPENWEATHER_API_KEY,
        "units": units,
        "cnt": days * 8
    }

    if city:
        params["q"] = city
    else:
        params["lat"] = lat
        params["lon"] = lon

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/forecast", params=params)

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Weather API error.")

    data = response.json()

    forecasts = []
    for item in data["list"]:
        forecasts.append({
            "datetime": item["dt_txt"],
            "timestamp": item["dt"],
            "temperature": item["main"]["temp"],
            "feels_like": item["main"]["feels_like"],
            "temp_min": item["main"]["temp_min"],
            "temp_max": item["main"]["temp_max"],
            "humidity": item["main"]["humidity"],
            "weather": item["weather"][0]["main"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"],
            "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
            "wind_speed": item["wind"]["speed"],
            "cloudiness": item["clouds"]["all"],
            "rain_probability": item.get("pop", 0) * 100
        })

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "units": units,
        "forecast_count": len(forecasts),
        "forecasts": forecasts
    }


@app.get("/weather/cities")
async def search_cities(
    q: str = Query(..., min_length=2, description="City name to search"),
    units: str = Query("metric", description="Units")
):
    """
    Search weather by partial city name.
    Returns current weather for the best matching city.
    """
    check_api_key()

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weather", params={
            "q": q,
            "appid": OPENWEATHER_API_KEY,
            "units": units
        })

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"No city found matching '{q}'")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Search error.")

    data = response.json()
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

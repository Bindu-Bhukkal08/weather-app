from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "39f975c0ce727af7dd78118571d13143"

@app.route('/', methods=['GET'])
def home():
    city = request.args.get('city', 'Delhi')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        error_msg = data.get('message', 'City not found')
        return f'''
        <html><head><meta charset="UTF-8">
        <style>body{{background:#1a1a2e;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}}
        .box{{background:rgba(255,0,0,0.1);border:1px solid red;border-radius:16px;padding:30px;text-align:center;}}
        form input{{padding:10px;border-radius:8px;border:none;margin-right:8px;}}
        form button{{padding:10px 20px;background:#e74c3c;border:none;border-radius:8px;color:white;cursor:pointer;}}</style></head>
        <body><div class="box"><h2>❌ Error: {error_msg}</h2>
        <form method="get"><input name="city" placeholder="City name" value="{city}"><button>Search</button></form>
        </div></body></html>
        '''

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    desc = data["weather"][0]["description"].title()
    wind = data["wind"]["speed"]
    city_name = data["name"]
    country = data["sys"]["country"]
    icon = data["weather"][0]["icon"]
    condition = data["weather"][0]["main"]

    emoji_map = {
        'Clear':'☀️','Clouds':'☁️','Rain':'🌧️','Drizzle':'🌦️',
        'Thunderstorm':'⛈️','Snow':'❄️','Mist':'🌫️','Fog':'🌫️',
        'Haze':'🌁','Dust':'💨','Smoke':'🌫️'
    }
    emoji = emoji_map.get(condition, '🌡️')

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flask Weather App</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                min-height: 100vh; display: flex;
                flex-direction: column; align-items: center;
                justify-content: center; padding: 20px; color: white;
            }}
            .badge {{
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px; padding: 6px 16px;
                font-size: 12px; letter-spacing: 2px;
                text-transform: uppercase; margin-bottom: 20px;
                color: rgba(255,255,255,0.6);
            }}
            .search-form {{
                display: flex; gap: 10px; margin-bottom: 30px;
            }}
            .search-form input {{
                padding: 12px 20px; border: 1px solid rgba(255,255,255,0.2);
                border-radius: 30px; background: rgba(255,255,255,0.1);
                color: white; font-size: 15px; outline: none; width: 240px;
            }}
            .search-form input::placeholder {{ color: rgba(255,255,255,0.4); }}
            .search-form button {{
                padding: 12px 24px; border: none; border-radius: 30px;
                background: linear-gradient(135deg, #56ccf2, #2f80ed);
                color: white; font-size: 15px; font-weight: bold;
                cursor: pointer;
            }}
            .card {{
                background: rgba(255,255,255,0.08);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 28px; padding: 36px;
                width: 100%; max-width: 420px; text-align: center;
            }}
            .location {{ font-size: 14px; color: rgba(255,255,255,0.5); margin-bottom: 4px; }}
            .city {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
            .emoji {{ font-size: 80px; margin: 10px 0; line-height: 1; }}
            .temp {{
                font-size: 72px; font-weight: 800; line-height: 1;
                background: linear-gradient(135deg, #fff, #a8d8ea);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }}
            .desc {{ font-size: 18px; color: rgba(255,255,255,0.7); margin: 8px 0 24px; }}
            .stats {{
                display: grid; grid-template-columns: 1fr 1fr;
                gap: 12px; margin-top: 10px;
            }}
            .stat {{
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px; padding: 14px;
            }}
            .stat .label {{
                font-size: 11px; color: rgba(255,255,255,0.4);
                text-transform: uppercase; letter-spacing: 1px;
            }}
            .stat .value {{
                font-size: 20px; font-weight: bold; margin-top: 4px;
            }}
            .footer {{
                margin-top: 24px; font-size: 12px;
                color: rgba(255,255,255,0.3);
            }}
        </style>
    </head>
    <body>
        <div class="badge">🐍 Flask Weather App</div>

        <form class="search-form" method="get">
            <input name="city" placeholder="Search city..." value="{city_name}">
            <button type="submit">Search</button>
        </form>

        <div class="card">
            <div class="location">📍 {country}</div>
            <div class="city">{city_name}</div>
            <div class="emoji">{emoji}</div>
            <div class="temp">{round(temp)}°C</div>
            <div class="desc">{desc}</div>
            <div class="stats">
                <div class="stat">
                    <div class="label">Feels Like</div>
                    <div class="value">{round(feels)}°C</div>
                </div>
                <div class="stat">
                    <div class="label">Humidity</div>
                    <div class="value">{humidity}%</div>
                </div>
                <div class="stat">
                    <div class="label">Wind</div>
                    <div class="value">{wind} m/s</div>
                </div>
                <div class="stat">
                    <div class="label">Condition</div>
                    <div class="value" style="font-size:14px;">{condition}</div>
                </div>
            </div>
        </div>
        <div class="footer">Powered by Flask &amp; OpenWeatherMap</div>
    </body>
    </html>
    '''

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City not provided"}), 400
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code != 200:
        return jsonify(data), response.status_code
    weather_data = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

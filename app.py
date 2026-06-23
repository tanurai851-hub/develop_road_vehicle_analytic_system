import random
from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
# Secret key is required to use sessions for login state
app.secret_key = 'smart_traffic_secret_key_2026'

# Mock Data Storage
sim_data = {
    "total_vehicles": 142,
    "total_violations": 4,
    "density_state": "Normal",
    "fps": 29.4
}

# 1. LOGIN PAGE HTML TEMPLATE
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Secure Login - Smart Traffic System</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; color: #f8fafc; }
        .login-card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); width: 350px; border: 1px solid #334155; text-align: center; }
        h2 { margin-bottom: 10px; color: #f1f5f9; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 30px; }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; margin-bottom: 8px; color: #94a3b8; font-size: 13px; text-transform: uppercase; }
        input { width: 100%; padding: 12px; background: #020617; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 14px; box-sizing: border-box; }
        input:focus { border-color: #38bdf8; outline: none; }
        .btn { width: 100%; padding: 12px; background: #38bdf8; border: none; border-radius: 6px; color: #020617; font-weight: bold; font-size: 16px; cursor: pointer; transition: background 0.2s; }
        .btn:hover { background: #0ea5e9; }
        .error { color: #f87171; font-size: 13px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>AI Traffic Portal</h2>
        <p>Enter credentials to access telemetry dashboard</p>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="input-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="e.g. admin" required>
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn">Authorize & Enter</button>
        </form>
    </div>
</body>
</html>
"""

# 2. DASHBOARD HTML TEMPLATE
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Road Vehicle Analytics System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; margin: 0; padding: 20px; color: #f8fafc; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: linear-gradient(135deg, #1e293b, #334155); color: white; padding: 25px; border-radius: 12px; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 25px; text-align: center; }
        
        /* Logout Button CSS */
        .logout-btn { position: absolute; right: 25px; top: 35px; background: #f87171; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; transition: background 0.2s; }
        .logout-btn:hover { background: #ef4444; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 20px 0; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); text-align: center; border: 1px solid #334155; }
        .card h3 { margin: 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
        .card p { margin: 10px 0 0 0; font-size: 32px; font-weight: bold; color: #38bdf8; }
        .main-content { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px; }
        
        .video-box { background: #020617; border-radius: 12px; position: relative; height: 420px; overflow: hidden; border: 3px solid #334155; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); }
        .bg-video { position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.35; z-index: 1; pointer-events: none; }
        
        .road { position: absolute; width: 100%; height: 240px; background: rgba(30, 41, 59, 0.4); top: 22%; border-top: 4px dashed #64748b; border-bottom: 4px dashed #64748b; z-index: 2; }
        .divider-line { position: absolute; width: 100%; height: 6px; background: #f59e0b; top: 50%; transform: translateY(-50%); z-index: 5; }
        .counting-line { position: absolute; left: 50%; top: 22%; width: 4px; height: 240px; background: #06b6d4; box-shadow: 0 0 15px #06b6d4; z-index: 10; }
        
        .vehicle { position: absolute; display: flex; align-items: center; justify-content: center; z-index: 6; }
        .v-car { width: 55px; height: 35px; border: 2px solid #4ade80; font-size: 24px; border-radius: 4px; }
        .v-truck { width: 75px; height: 42px; border: 2px solid #f87171; font-size: 32px; border-radius: 4px; }
        .v-bike { width: 42px; height: 26px; border: 2px solid #fbbf24; font-size: 20px; border-radius: 4px; }
        .v-cycle { width: 35px; height: 22px; border: 2px solid #38bdf8; font-size: 18px; border-radius: 4px; }
        .vehicle::before { position: absolute; top: -20px; left: -2px; color: #000; font-size: 9px; font-weight: bold; padding: 1px 4px; border-radius: 3px; white-space: nowrap; }
        
        @keyframes goLeftToRight { 0% { left: -150px; } 100% { left: 105%; } }
        @keyframes goRightToLeft { 0% { left: 105%; } 100% { left: -150px; } }
        
        .table-box { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); border: 1px solid #334155; }
        .chart-box { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        h2 { margin-top: 0; color: #f1f5f9; border-bottom: 2px solid #334155; padding-bottom: 10px; font-size: 18px; }
    </style>
    <script>
        let laneOccupied = { 1: false, 2: false, 3: false, 4: false };
        let laneStopped = { 1: false, 2: false, 3: false, 4: false };
        let lastViolationCount = 4; 
        let trafficChart;
        let timeLabels = [];
        let trafficData = [];

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playViolationBeep() {
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(880, audioCtx.currentTime);
            gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.25);
        }

        function refreshStats() {
            fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                let densityElement = document.getElementById('density');
                if (laneStopped[1] || laneStopped[3]) {
                    densityElement.innerText = "Heavy (Jam)";
                    densityElement.style.color = "#f87171";
                } else {
                    densityElement.innerText = data.density_state;
                    densityElement.style.color = "#38bdf8";
                }
                document.getElementById('total-vehicles').innerText = data.total_vehicles;
                document.getElementById('total-violations').innerText = data.total_violations;
                document.getElementById('fps').innerText = data.fps.toFixed(1);

                if (data.total_violations > lastViolationCount) {
                    playViolationBeep();
                    lastViolationCount = data.total_violations;
                }

                const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                if (timeLabels.length > 8) {
                    timeLabels.shift();
                    trafficData.shift();
                }
                timeLabels.push(now);
                trafficData.push(data.total_vehicles);
                trafficChart.update();

            }).catch(err => console.log(err));
        }
        setInterval(refreshStats, 2000);
        
        window.onload = function() {
            initChart();
            refreshStats();
            spawnSmartTraffic();
            startOrganicTrafficStopper();
        };

        function initChart() {
            const ctx = document.getElementById('analyticsChart').getContext('2d');
            trafficChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeLabels,
                    datasets: [{
                        label: 'Total Traffic Logged (Live Volume)',
                        data: trafficData,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function spawnSmartTraffic() {
            const roadCanvas = document.getElementById('road-canvas');
            const vehicleConfigs = [
                { class: 'v-car', emoji: '🚘', label: 'Car: 94%' },
                { class: 'v-truck', emoji: '自由', label: 'Truck: 89%' }, // standard emoji handles placeholder
                { class: 'v-truck', emoji: '🚛', label: 'Truck: 89%' },
                { class: 'v-bike', emoji: '🏍️', label: 'Motorbike: 91%' },
                { class: 'v-cycle', emoji: '🚲', label: 'Bicycle: 82%' }
            ];
            const laneTops = { 1: 26, 2: 37, 3: 53, 4: 64 };

            function trySpawn() {
                const lane = Math.floor(Math.random() * 4) + 1;
                if (laneOccupied[lane]) { setTimeout(trySpawn, 250); return; }
                laneOccupied[lane] = true; 

                const config = vehicleConfigs[Math.floor(Math.random() * vehicleConfigs.length)];
                const el = document.createElement('div');
                el.className = `vehicle ${config.class}`;
                el.innerHTML = config.emoji;
                el.style.top = `${laneTops[lane]}%`;
                
                const isLeftToRight = (lane === 1 || lane === 2);
                const speed = (Math.random() * 1.5 + 3.0).toFixed(2);
                
                if (isLeftToRight) {
                    el.style.animation = `goLeftToRight ${speed}s linear forwards`;
                    el.dataset.dir = "ltr";
                    el.style.transform = "scaleX(-1)"; 
                    if(laneStopped[1]) el.style.animationPlayState = 'paused';
                } else {
                    el.style.animation = `goRightToLeft ${speed}s linear forwards`;
                    el.dataset.dir = "rtl";
                    el.style.transform = "scaleX(1)"; 
                    if(laneStopped[3]) el.style.animationPlayState = 'paused';
                }
                
                el.dataset.lane = lane;
                let tagColor = '#4ade80';
                let labelText = config.label;
                if(config.class === 'v-truck' && Math.random() > 0.8) {
                    labelText = 'Truck: Speeding';
                    tagColor = '#f87171';
                    el.style.border = '2px solid #f87171';
                }
                
                const styleId = 'sheet-' + Math.random().toString(36).substr(2, 9);
                const style = document.createElement('style');
                style.id = styleId;
                style.innerHTML = `.${styleId}::before { content: "${labelText}"; background: ${tagColor}; transform: scaleX(${isLeftToRight ? '-1' : '1'}); }`;
                document.head.appendChild(style);
                el.classList.add(styleId);

                roadCanvas.appendChild(el);
                setTimeout(() => { laneOccupied[lane] = false; }, speed * 500); 
                setTimeout(() => { el.remove(); style.remove(); }, speed * 1000);

                let nextSpawnDelay = Math.floor(Math.random() * 800) + 400; 
                setTimeout(trySpawn, nextSpawnDelay);
            }
            trySpawn();
        }

        function startOrganicTrafficStopper() {
            setInterval(() => {
                const actionRoll = Math.random();
                const vehicles = document.querySelectorAll('.vehicle');
                const duration = Math.floor(Math.random() * 2000) + 2000;
                if (actionRoll < 0.15 && !laneStopped[3]) {
                    laneStopped[1] = true; laneStopped[2] = true;
                    vehicles.forEach(v => { if(v.dataset.dir === "ltr") v.style.animationPlayState = 'paused'; });
                    setTimeout(() => {
                        laneStopped[1] = false; laneStopped[2] = false;
                        document.querySelectorAll('.vehicle').forEach(v => { if(v.dataset.dir === "ltr") v.style.animationPlayState = 'running'; });
                    }, duration);
                } else if (actionRoll > 0.85 && !laneStopped[1]) {
                    laneStopped[3] = true; laneStopped[4] = true;
                    vehicles.forEach(v => { if(v.dataset.dir === "rtl") v.style.animationPlayState = 'paused'; });
                    setTimeout(() => {
                        laneStopped[3] = false; laneStopped[4] = false;
                        document.querySelectorAll('.vehicle').forEach(v => { if(v.dataset.dir === "rtl") v.style.animationPlayState = 'running'; });
                    }, duration);
                }
            }, 9000);
        }
    </script>
</head>
<body>
    <div class="container">
        <header>
            <h1>Road Vehicle Analytics System</h1>
            <p style="color: #4ade80; font-weight: bold; margin: 5px 0 0 0; letter-spacing: 0.5px;">🟢 AI Core Engine: Running Asynchronous Inference</p>
            <a href="/logout" class="logout-btn">Secure Logout</a>
        </header>
        <div class="grid">
            <div class="card"><h3>Total Vehicles</h3><p id="total-vehicles">142</p></div>
            <div class="card"><h3 style="color: #f87171;">Traffic Violations</h3><p id="total-violations" style="color: #f87171;">4</p></div>
            <div class="card"><h3>Current Density</h3><p id="density">Normal</p></div>
            <div class="card"><h3>System Performance</h3><p id="fps">29.4 FPS</p></div>
        </div>
        
        <div class="main-content">
            <div class="video-box" id="road-canvas">
                <video class="bg-video" autoplay muted loop playsinline>
                    <source src="https://assets.mixkit.co/videos/preview/mixkit-traffic-on-a-highway-at-night-41656-large.mp4" type="video/mp4">
                </video>
                <div style="position: absolute; left: 51%; top: 15%; color: #06b6d4; font-size: 11px; font-weight: bold; z-index:11; letter-spacing: 1px;">VIRTUAL COUNTING LINE</div>
                <div class="counting-line"></div>
                <div class="road"></div>
                <div class="divider-line"></div>
            </div>
            
            <div class="table-box">
                <h2>Live Inference Log Stream</h2>
                <div style="background: #020617; color: #4ade80; font-family: monospace; padding: 15px; border-radius: 8px; height: 300px; overflow-y: auto; font-size: 12px; border: 1px solid #334155;" id="logger">
                    [INFO] Core AI Pipeline Engine Initialized.<br>
                    [INFO] YOLOv8 Weights Configured from local cache.<br>
                    [INFO] Hardware Acceleration: Enabled (GPU Multi-Threading)<br>
                    [INFO] Video Stream Source Connected.<br>
                </div>
            </div>
        </div>

        <div class="chart-box">
            <h2>Real-Time Traffic Volume Telemetry Analytics</h2>
            <div style="height: 220px; position: relative;">
                <canvas id="analyticsChart"></canvas>
            </div>
        </div>
    </div>
    <script>
        const logs = [
            "[DETECT] Car identified - Conf: 0.94",
            "[DETECT] Truck identified - Conf: 0.89",
            "[DETECT] Motorbike identified - Conf: 0.91",
            "[DETECT] Bicycle identified - Conf: 0.82",
            "[COUNTER] Vehicle crossed virtual line",
            "[SPEED] Vehicle tracked velocity: 48 km/h",
            "[WARNING] Speed Violation Triggered! - 84 km/h"
        ];
        setInterval(() => {
            const logBox = document.getElementById('logger');
            const randomLog = logs[Math.floor(Math.random() * logs.length)];
            logBox.innerHTML += `[${new Date().toLocaleTimeString()}] ${randomLog}<br>`;
            logBox.scrollTop = logBox.scrollHeight;
        }, 1800);
    </script>
</body>
</html>
"""

# 3. AUTHENTICATION ROUTING BACKEND
@app.route("/")
def index():
    # If logged_in key exists in session, render dashboard, else show login page
    if session.get("logged_in"):
        return render_template_string(DASHBOARD_TEMPLATE)
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    # Static Credentials Check
    if username == "Tanu" and password == "Tanurai123":
        session["logged_in"] = True
        return redirect(url_for("index"))
    else:
        return render_template_string(LOGIN_TEMPLATE, error="Invalid Username or Password!")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

@app.route("/api/stats")
def api_stats():
    # API security shield check
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
        
    chance = random.random()
    if chance < 0.35:
        sim_data["total_vehicles"] += 0
    elif chance < 0.85:
        sim_data["total_vehicles"] += random.randint(1, 2)
    else:
        sim_data["total_vehicles"] += random.randint(3, 4)
        
    if random.random() > 0.94:
        sim_data["total_violations"] += 1
        
    densities = ["Low", "Normal", "Heavy", "Normal"]
    sim_data["density_state"] = densities[random.randint(0, 3)]
    sim_data["fps"] = random.uniform(28.9, 29.9)
    return jsonify(sim_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, threaded=True, debug=False)

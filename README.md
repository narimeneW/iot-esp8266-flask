# TP IoT System with ESP8266 and Flask

Full-stack IoT system with ESP8266 microcontroller sending sensor data to a Flask web application via HTTP, with Redis storage and Docker deployment.

## 📋 System Architecture
```
ESP8266 (WiFi Client)
    ↓ HTTP POST (JSON)
Flask Web App (Python)
    ↓
Redis Database
    ↓
Docker Containers
```

## 🛠️ Technologies

**Hardware**: ESP8266 (Wemos)  
**Embedded**: C++, ESP8266HTTPClient library  
**Backend**: Python, Flask framework  
**Database**: Redis (NoSQL key-value store)  
**Deployment**: Docker, docker-compose  
**Protocol**: HTTP over WiFi

## 🎯 Features

- **ESP8266 HTTP Client**: Sends JSON data wirelessly to Flask server
- **Flask Web Interface**: Receives and processes data from IoT devices
- **Redis Storage**: Lightweight database for IoT data persistence
- **Multi-container Deployment**: Microservices architecture with Docker
- **Real-time Communication**: POST/GET request handling

## 🚀 Quick Start

### ESP8266 Setup
```cpp
#include <ESP8266HTTPClient.h>

// Configure server and URL
http.begin(client, "http://192.168.50.226:5000/");

// Set JSON content type
http.addHeader("Content-Type", "application/json");

// Send POST request
int httpCode = http.POST("{\"name\":\"ham\"}");
```

### Server Deployment
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/iot-esp8266-flask.git
cd iot-esp8266-flask

# Launch services with Docker
docker-compose up -d

# Access web interface
# Open browser: http://RASPBERRY_IP:5000
```

## 📁 Project Structure
```
├── app.py                  # Flask application
├── Dockerfile              # Docker image configuration
├── docker-compose.yaml     # Multi-container orchestration
├── requirements.txt        # Python dependencies
├── templates/              # HTML pages
├── static/                 # CSS/JS files
└── esp8266_client/         # Arduino code for ESP8266
    └── http_client.ino
```

## 🔧 Configuration

**Docker Compose Services:**
- **app**: Flask application (port 5000)
- **redis**: Redis database (backend)
- **Networks**: frontend + backend isolation
- **Volumes**: Persistent data storage

**Flask Routes:**
- `POST /` - Receive data from ESP8266
- `GET /` - Display main page
- `GET /action` - Control interface


## 🎓 Key Learnings

- Embedded HTTP client implementation
- Full-stack IoT system design
- Microservices architecture with Docker
- Real-time data pipeline: Device → Server → Database
- WiFi communication protocols


## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [ESP8266 Arduino Core](https://arduino-esp8266.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)

# 🐳 HCM Chatbot - Docker Guide

Hướng dẫn sử dụng Docker để chạy hệ thống HCM Chatbot.

## 📋 Yêu cầu

- Docker Desktop hoặc Docker Engine
- Docker Compose
- Git

## 🚀 Cách sử dụng

### 1. Build Docker Images

#### Trên Linux/macOS:
```bash
chmod +x scripts/docker-build.sh
./scripts/docker-build.sh
```

#### Trên Windows:
```cmd
scripts\docker-build.bat
```

#### Hoặc build thủ công:
```bash
# Build Python AI Backend
docker build -t hcm-python-ai:latest ./backend

# Build .NET API
docker build -t hcm-dotnet-api:latest ./dotnet-api/hcm-chatbot-api

# Build Node.js API
docker build -t hcm-nodejs-api:latest ./nodejs-api

# Build Frontend
docker build -t hcm-frontend:latest ./frontend
```

### 2. Chạy Production Environment

```bash
# Tạo file .env với các biến môi trường cần thiết
echo "GEMINI_API_KEY=your-gemini-api-key-here" > .env
echo "JWT_SECRET_KEY=your-super-secret-jwt-key-here" >> .env

# Chạy tất cả services
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps
```

### 3. Chạy Development Environment

```bash
# Chạy development mode với hot reload
docker-compose -f docker-compose.dev.yml up -d

# Xem logs
docker-compose -f docker-compose.dev.yml logs -f
```

### 4. Quản lý Services

```bash
# Dừng tất cả services
docker-compose down

# Dừng và xóa volumes
docker-compose down -v

# Restart một service cụ thể
docker-compose restart python-ai

# Xem logs của một service
docker-compose logs -f python-ai

# Vào container để debug
docker-compose exec python-ai bash
```

## 🌐 Truy cập Services

Sau khi chạy `docker-compose up -d`, các services sẽ có sẵn tại:

- **Frontend**: http://localhost:3000
- **.NET API**: http://localhost:5000
- **Python AI**: http://localhost:8000
- **Node.js API**: http://localhost:3001 (nếu chạy)
- **PostgreSQL**: localhost:5432

### Development Mode:
- **Frontend**: http://localhost:3001
- **.NET API**: http://localhost:5001
- **Python AI**: http://localhost:8001
- **PostgreSQL**: localhost:5433

## 🔧 Cấu hình

### Environment Variables

Tạo file `.env` trong thư mục gốc:

```env
# Gemini AI API Key
GEMINI_API_KEY=your-gemini-api-key-here

# JWT Secret Key
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Database (optional - defaults are provided)
POSTGRES_DB=hcm_chatbot
POSTGRES_USER=hcm_user
POSTGRES_PASSWORD=hcm_password
```

### Ports

Mặc định:
- Frontend: 3000
- .NET API: 5000
- Python AI: 8000
- Node.js API: 3001
- PostgreSQL: 5432

Development:
- Frontend: 3001
- .NET API: 5001
- Python AI: 8001
- PostgreSQL: 5433

## 🐛 Troubleshooting

### 1. Port đã được sử dụng
```bash
# Kiểm tra port nào đang được sử dụng
netstat -tulpn | grep :3000

# Thay đổi port trong docker-compose.yml
```

### 2. Database connection issues
```bash
# Kiểm tra PostgreSQL container
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### 3. Build failures
```bash
# Xóa cache và build lại
docker system prune -f
docker-compose build --no-cache
```

### 4. Permission issues (Linux/macOS)
```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

## 📊 Monitoring

### Health Checks
Tất cả services đều có health checks:
```bash
# Kiểm tra health status
docker-compose ps

# Xem health check logs
docker inspect hcm-python-ai | grep -A 10 Health
```

### Logs
```bash
# Xem logs tất cả services
docker-compose logs

# Xem logs một service cụ thể
docker-compose logs python-ai

# Follow logs real-time
docker-compose logs -f --tail=100 python-ai
```

## 🔄 Updates

### Update images
```bash
# Pull latest base images
docker-compose pull

# Rebuild và restart
docker-compose up -d --build
```

### Update code
```bash
# Development mode tự động reload
# Production mode cần rebuild
docker-compose build python-ai
docker-compose up -d python-ai
```

## 🗑️ Cleanup

```bash
# Dừng và xóa containers
docker-compose down

# Xóa images
docker-compose down --rmi all

# Xóa volumes (CẢNH BÁO: Mất dữ liệu)
docker-compose down -v

# Xóa tất cả (containers, images, volumes, networks)
docker-compose down --rmi all -v --remove-orphans
```

## 📝 Notes

- Database data được lưu trong Docker volume `postgres_data`
- Development mode có hot reload cho Python và .NET
- Production mode tối ưu cho performance
- Tất cả services đều có health checks
- Nginx frontend có gzip compression và security headers


# 🪟 HCM Chatbot - Hướng dẫn cài đặt cho Windows

> Hướng dẫn đầy đủ để chạy HCM Chatbot trên Windows 10/11

---

## 📋 Yêu cầu hệ thống

- **Windows 10/11** (64-bit)
- **PowerShell 5.1+** (có sẵn trong Windows)
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)
- **Disk**: Tối thiểu 2GB trống

---

## 🔧 Cài đặt Prerequisites

### 1️⃣ Cài đặt PostgreSQL

**Tải về:**
- Truy cập: https://www.postgresql.org/download/windows/
- Tải **PostgreSQL 16** (installer)

**Cài đặt:**
1. Chạy file installer
2. **Quan trọng**: Ghi nhớ password cho user `postgres`
3. Port mặc định: `5432` (giữ nguyên)
4. Chọn cài đặt **pgAdmin 4** (để quản lý database)

**Khởi động PostgreSQL:**
```powershell
# Mở PowerShell as Administrator
net start postgresql-x64-16

# Hoặc sử dụng Services
# Win + R -> services.msc -> Tìm "postgresql-x64-16" -> Start
```

**Kiểm tra:**
```powershell
# Test kết nối PostgreSQL
Test-NetConnection -ComputerName localhost -Port 5432
# Nếu thành công, sẽ thấy "TcpTestSucceeded : True"
```

---

### 2️⃣ Cài đặt .NET 8.0 SDK

**Tải về:**
- Truy cập: https://dotnet.microsoft.com/download/dotnet/8.0
- Chọn **SDK** (không phải Runtime)
- Tải **Windows x64 Installer**

**Cài đặt:**
1. Chạy file installer
2. Làm theo hướng dẫn (Next, Next, Install)
3. Restart terminal sau khi cài

**Kiểm tra:**
```powershell
dotnet --version
# Output: 8.0.x (hoặc cao hơn)
```

---

### 3️⃣ Cài đặt Python 3.8+

**Tải về:**
- Truy cập: https://www.python.org/downloads/
- Tải **Python 3.11** hoặc **3.12** (khuyến nghị)

**Cài đặt:**
1. Chạy file installer
2. **✅ QUAN TRỌNG**: Tick vào **"Add Python to PATH"**
3. Chọn **"Install Now"**

**Kiểm tra:**
```powershell
python --version
# Output: Python 3.11.x (hoặc 3.12.x)

pip --version
# Output: pip 23.x.x
```

---

### 4️⃣ Cài đặt Git (tùy chọn)

**Tải về:**
- Truy cập: https://git-scm.com/download/windows
- Tải **64-bit Git for Windows Setup**

**Cài đặt:**
1. Chạy installer
2. Chọn mặc định cho tất cả options

---

## 📥 Clone và Setup Project

### Bước 1: Clone repository

```powershell
# Mở PowerShell
cd C:\Users\YourUsername\Documents

# Clone project
git clone https://github.com/your-username/hcm-chatbot.git
cd hcm-chatbot
```

**Hoặc tải ZIP:**
1. Vào GitHub repository
2. Click **Code** > **Download ZIP**
3. Giải nén vào `C:\Users\YourUsername\Documents\hcm-chatbot`

---

### Bước 2: Setup Python Virtual Environment

```powershell
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Quay về thư mục gốc
cd ..
```

**Lưu ý:** Nếu gặp lỗi execution policy:
```powershell
# Chạy PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Bước 3: Cấu hình Gemini API Key

1. **Lấy API Key:**
   - Truy cập: https://ai.google.dev/
   - Đăng nhập Google account
   - Click **"Get API Key"** > **"Create API Key"**
   - Copy API key

2. **Tạo file `.env`:**
```powershell
# Tạo file .env trong thư mục backend
cd backend
New-Item -Path .env -ItemType File

# Mở file bằng Notepad
notepad .env
```

3. **Thêm nội dung vào `.env`:**
```
GEMINI_API_KEY=your_api_key_here
```
- Thay `your_api_key_here` bằng API key vừa copy
- Lưu file (Ctrl + S)

---

### Bước 4: Setup Database

```powershell
# Mở PowerShell
cd C:\Users\YourUsername\Documents\hcm-chatbot

# Connect to PostgreSQL và tạo database
psql -U postgres -c "CREATE DATABASE hcm_chatbot_db;"

# Nếu cần password, nhập password đã tạo khi cài PostgreSQL
```

**Hoặc dùng pgAdmin:**
1. Mở **pgAdmin 4**
2. Kết nối với PostgreSQL (nhập password)
3. Right-click **Databases** > **Create** > **Database**
4. Tên database: `hcm_chatbot_db`
5. Click **Save**

---

### Bước 5: Cấu hình Connection String

**Mở file cấu hình .NET:**
```powershell
notepad dotnet-api\hcm-chatbot-api\Web_API\appsettings.json
```

**Kiểm tra `ConnectionStrings`:**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=hcm_chatbot_db;Username=postgres;Password=YOUR_PASSWORD"
  }
}
```

**Thay `YOUR_PASSWORD`** bằng password PostgreSQL của bạn.

---

## 🚀 Chạy HCM Chatbot

### ✨ Cách 1: Sử dụng PowerShell Scripts (Khuyến nghị)

```powershell
# Mở PowerShell trong thư mục project
cd C:\Users\YourUsername\Documents\hcm-chatbot

# Cho phép chạy scripts (chạy 1 lần)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Khởi động toàn bộ hệ thống
.\start-all.ps1
```

**Đợi khoảng 30-60 giây**, hệ thống sẽ khởi động 3 services:
- ✅ .NET API (port 9000)
- ✅ Python AI (port 8000)
- ✅ Frontend (port 3000)

**Kiểm tra trạng thái:**
```powershell
.\status.ps1
```

**Dừng hệ thống:**
```powershell
.\stop-all.ps1
```

---

### 🔧 Cách 2: Chạy từng service riêng lẻ (Development)

**Terminal 1 - .NET API:**
```powershell
cd dotnet-api\hcm-chatbot-api
dotnet run --project Web_API\Web_API.csproj --urls http://localhost:9000
```

**Terminal 2 - Python AI:**
```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend:**
```powershell
cd frontend
python -m http.server 3000
```

---

## 🌐 Truy cập hệ thống

Sau khi khởi động thành công:

- **🏠 Trang chủ**: http://localhost:3000/welcome.html
- **📚 API Docs**: http://localhost:9000/swagger
- **🤖 AI Docs**: http://localhost:8000/docs
- **💚 Health Check**: http://localhost:9000/health

---

## 👤 Đăng nhập

### Tài khoản Admin mặc định:
- **Username**: `admin`
- **Password**: `admin123`

### Tạo tài khoản User:
1. Mở http://localhost:3000/auth.html
2. Click tab **"Đăng ký"**
3. Điền thông tin:
   - Username
   - Email
   - Full Name
   - Password
4. Click **"Đăng ký"**

---

## 🐛 Troubleshooting

### ❌ Lỗi: "Port 5432 is not accessible"

**Nguyên nhân:** PostgreSQL chưa chạy

**Giải pháp:**
```powershell
# Khởi động PostgreSQL
net start postgresql-x64-16

# Hoặc dùng Services
Win + R -> services.msc -> postgresql-x64-16 -> Start
```

---

### ❌ Lỗi: "Cannot activate virtual environment"

**Nguyên nhân:** PowerShell execution policy

**Giải pháp:**
```powershell
# Chạy PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ Lỗi: ".NET API không kết nối database"

**Nguyên nhân:** Connection string sai hoặc database chưa tạo

**Giải pháp:**
1. Kiểm tra password trong `appsettings.json`
2. Tạo database:
```powershell
psql -U postgres -c "CREATE DATABASE hcm_chatbot_db;"
```

---

### ❌ Lỗi: "Python AI: No module named 'app'"

**Nguyên nhân:** Virtual environment chưa activate hoặc dependencies chưa cài

**Giải pháp:**
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

### ❌ Lỗi: "Port 9000/8000/3000 đã được sử dụng"

**Nguyên nhân:** Port bị chiếm bởi process khác

**Giải pháp:**
```powershell
# Kiểm tra process đang dùng port
Get-NetTCPConnection -LocalPort 9000

# Kill process theo PID
Stop-Process -Id <PID> -Force

# Hoặc dùng script stop
.\stop-all.ps1
```

---

### ❌ Lỗi: "Gemini API quota exceeded"

**Nguyên nhân:** Đã hết quota API miễn phí

**Giải pháp:**
1. Đợi 24h để quota reset
2. Hoặc tạo API key mới với Google account khác
3. Cập nhật `backend\.env` với API key mới

---

## 📊 Kiểm tra Logs

```powershell
# Xem log .NET API
Get-Content logs\dotnet-api.log -Tail 50

# Xem log Python AI
Get-Content logs\python-ai.log -Tail 50

# Xem log Frontend
Get-Content logs\frontend.log -Tail 50

# Theo dõi log realtime (Ctrl+C để thoát)
Get-Content logs\dotnet-api.log -Wait
```

---

## 🔄 Update và Restart

```powershell
# Pull latest code
git pull origin main

# Cập nhật Python dependencies
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt --upgrade
cd ..

# Cập nhật .NET packages
cd dotnet-api\hcm-chatbot-api
dotnet restore
cd ..\..

# Restart hệ thống
.\stop-all.ps1
.\start-all.ps1
```

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. **Kiểm tra trạng thái**: `.\status.ps1`
2. **Xem logs**: `Get-Content logs\*.log`
3. **Restart**: `.\stop-all.ps1` rồi `.\start-all.ps1`
4. **Issues**: Tạo issue trên GitHub

---

## ✅ Checklist Setup

- [ ] PostgreSQL đã cài và đang chạy
- [ ] .NET 8.0 SDK đã cài
- [ ] Python 3.8+ đã cài (with pip)
- [ ] Project đã clone/download
- [ ] Virtual environment đã tạo và activate
- [ ] Python dependencies đã cài (`pip install -r requirements.txt`)
- [ ] Gemini API key đã thêm vào `backend\.env`
- [ ] Database `hcm_chatbot_db` đã tạo
- [ ] Connection string trong `appsettings.json` đã cấu hình đúng
- [ ] Execution Policy đã set: `RemoteSigned`
- [ ] Chạy `.\start-all.ps1` thành công

---

**🇻🇳 Chúc bạn sử dụng HCM Chatbot thành công trên Windows! 🇻🇳**

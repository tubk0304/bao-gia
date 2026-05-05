# Hướng dẫn triển khai dự án (KHÔNG CẦN QUYỀN SUDO)

Tài liệu này hướng dẫn cách triển khai ứng dụng lên VPS khi bạn chỉ có quyền User thường (không có sudo).

## 1. Chuẩn bị mã nguồn trên VPS

### Bước 1: Kéo code từ GitHub
```bash
git clone https://github.com/tubk0304/bao-gia.git
cd bao-gia
```

### Bước 2: Tạo môi trường ảo và cài đặt thư viện
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 3: Cấu hình file môi trường và Database
*   **File .env:** Tạo file `backend/.env` và dán nội dung API Key vào.
*   **Database:** Dùng WinSCP/FileZilla copy file `catalog.db` vào thư mục `backend/` trên VPS.

## 2. Khởi chạy Backend (Phục vụ cả Frontend)

Vì không có sudo để cài Nginx hay Docker, chúng ta chạy trực tiếp bằng `uvicorn` và cho nó chạy ngầm bằng `nohup`.

```bash
# Đang ở trong thư mục backend và đã activate venv
nohup uvicorn main:app --host 0.0.0.0 --port 7883 > backend.log 2>&1 &
```
*Lúc này ứng dụng sẽ chạy tại port 7883 và tự phục vụ index.html.*

## 3. Cấu hình Cloudflare Tunnel (Bản Portable)

Vì không có sudo, chúng ta tải trực tiếp file thực thi của Cloudflare về thư mục cá nhân.

### Bước 1: Tải cloudflared
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
mv cloudflared-linux-amd64 cloudflared
```

### Bước 2: Xác thực và Tạo Tunnel
```bash
./cloudflared tunnel login
# Click vào link hiện ra để chọn domain

./cloudflared tunnel create bao-gia-tunnel
# Lưu lại ID của tunnel
```

### Bước 3: Tạo file cấu hình `config.yml`
Tạo file `config.yml` ngay tại thư mục hiện tại:
```yaml
tunnel: <MÃ_ID_TUNNEL>
credentials-file: /home/youruser/.cloudflared/<MÃ_ID_TUNNEL>.json

ingress:
  - hostname: baogia.yourdomain.com
    service: http://localhost:7883
  - service: http_status:404
```

### Bước 4: Chạy Tunnel ngầm
```bash
nohup ./cloudflared tunnel --config config.yml run bao-gia-tunnel > tunnel.log 2>&1 &
```

## 4. Cách kiểm tra và tắt ứng dụng

### Xem ứng dụng có đang chạy không:
```bash
ps aux | grep uvicorn
ps aux | grep cloudflared
```

### Xem log để fix lỗi:
```bash
tail -f backend.log
tail -f tunnel.log
```

### Tắt ứng dụng:
```bash
pkill uvicorn
pkill cloudflared
```

---
**Lưu ý:** Vì Backend đã được cập nhật để tự phục vụ file tĩnh, bạn chỉ cần trỏ 1 hostname duy nhất về port 7883 là có thể dùng được cả Web và API.

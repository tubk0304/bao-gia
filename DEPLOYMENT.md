# Hướng dẫn triển khai dự án lên VPS với Cloudflare Tunnel

Tài liệu này hướng dẫn cách đưa dự án "Báo Giá Nhanh" lên VPS Linux (Ubuntu/Debian) và sử dụng Cloudflare Tunnel để truy cập công khai an toàn mà không cần mở port.

## 1. Chuẩn bị trên VPS

### Cài đặt Docker và Docker Compose (Khuyên dùng)
Docker giúp quản lý môi trường Backend và Frontend đồng nhất, tránh lỗi xung đột thư viện.

```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài đặt Docker Compose
sudo apt install docker-compose-plugin -y
```

## 2. Cấu hình Docker cho dự án

Bạn nên tạo một file `docker-compose.yml` tại thư mục gốc của dự án trên VPS để chạy cả Backend và Frontend:

```yaml
services:
  backend:
    build: 
      context: .
      dockerfile: backend/Dockerfile
    restart: always
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    volumes:
      - ./backend/catalog.db:/app/catalog.db

  frontend:
    image: nginx:alpine
    restart: always
    ports:
      - "8080:80"
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html
      - ./Asset-14logo-khoa-duy-blackok-1024x461.png:/usr/share/nginx/html/logo.png
```

## 3. Cấu hình Cloudflare Tunnel (cloudflared)

Cloudflare Tunnel giúp bạn trỏ domain về VPS mà không cần mở Port (NAT) trên Firewall/Router của nhà mạng.

### Bước 1: Cài đặt cloudflared trên VPS
```bash
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
```

### Bước 2: Xác thực Cloudflare
```bash
cloudflared tunnel login
```
*Hệ thống sẽ hiện một đường link, bạn copy và dán vào trình duyệt để chọn domain muốn dùng.*

### Bước 3: Tạo Tunnel
```bash
cloudflared tunnel create bao-gia-tunnel
```
*Lưu lại mã ID (Chuỗi ký tự dài) được trả về.*

### Bước 4: Cấu hình File Config (`~/.cloudflared/config.yml`)
Tạo file config để map domain vào các dịch vụ Docker:
```yaml
tunnel: <MÃ_ID_TUNNEL_CỦA_BẠN>
credentials-file: /root/.cloudflared/<MÃ_ID_TUNNEL_CỦA_BẠN>.json

ingress:
  - hostname: app.yourdomain.com
    service: http://localhost:8080
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### Bước 5: Chạy Tunnel
```bash
# Tạo bản ghi DNS tự động
cloudflared tunnel route dns bao-gia-tunnel app.yourdomain.com
cloudflared tunnel route dns bao-gia-tunnel api.yourdomain.com

# Cài đặt tunnel thành dịch vụ hệ thống để tự khởi động cùng VPS
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## 4. Quy trình cập nhật (Workflow)

Mỗi khi bạn có thay đổi ở máy Local:
1.  **Local:** `git add .` -> `git commit -m "Cập nhật..."` -> `git push origin main`.
2.  **VPS:** `git pull origin main` -> `docker compose up -d --build`.

---
**Ngày cập nhật:** 05/05/2026

# Báo Giá Nhanh

Workspace này phục vụ quy trình bóc tách và lập báo giá thiết bị điện/smarthome, gồm:

- Giao diện báo giá tương tác ở file `Bao_Gia_Jay_Home_Truc_Quan.html`
- Backend FastAPI trong thư mục `backend/` để quản lý catalog, lưu báo giá và import catalog bằng AI
- Các tài liệu nguồn và script hỗ trợ để trích xuất nội dung báo giá

## Cấu trúc

- `Bao_Gia_Jay_Home_Truc_Quan.html`: giao diện báo giá chính
- `Bao_Gia_Jay_Home.md`: bản nháp nội dung báo giá đã trích xuất
- `backend/main.py`: điểm vào chính của ứng dụng FastAPI
- `backend/database.py`: model SQLite và cấu hình session
- `backend/ai_parser.py`: đọc PDF/Excel rồi trích xuất dữ liệu bằng Gemini
- `backend/admin.html`: giao diện admin/catalog
- `backend/catalog.db`: cơ sở dữ liệu SQLite local
- `backend/start_backend.ps1`: chạy backend
- `backend/stop_backend.ps1`: dừng tiến trình `uvicorn`
- `backend/create_venv.ps1`: tạo virtualenv mới tại `backend/.venv`
- `backend/.env.example`: mẫu biến môi trường cần thiết
- `backend/.env`: biến môi trường local, tự tạo từ file mẫu

## Yêu cầu

- Windows
- Một bản Python hoạt động được từ `python` hoặc virtualenv local

## Cách chạy nhanh

```powershell
cd backend
Copy-Item .env.example .env
.\start_backend.ps1
```

Điền giá trị vào `.env`:

- `GEMINI_API_KEY`
- `ADMIN_PASSWORD`

## Tạo môi trường mới

Không dùng lại `backend/venv` cũ. Nếu muốn tạo môi trường sạch:

```powershell
cd backend
.\create_venv.ps1
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Sau đó chạy:

```powershell
cd backend
.\start_backend.ps1
```

## Chạy trực tiếp

```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Truy cập

- Trang admin: `http://127.0.0.1:8000/admin`
- Trang báo giá: `http://127.0.0.1:8000/baogia`
- Tài liệu API: `http://127.0.0.1:8000/docs`

## Ghi chú

- Backend dùng SQLite local tại `backend/catalog.db`.
- Chức năng import AI cần `GEMINI_API_KEY` trong `backend/.env`.
- `backend/ai_parser.py` đã chuyển sang SDK `google.genai`.
- Một số file giao diện cũ vẫn còn chuỗi tiếng Việt bị lỗi mã hóa và cần dọn tiếp.
- Máy hiện tại không có interpreter Python dùng được qua `py -3.12`; nên ưu tiên virtualenv local hoặc `python` đã cài chuẩn trên `PATH`.
- Các tài nguyên local như `backend/venv`, `backend/.venv312`, file log và `.env` không nên đưa vào repo.

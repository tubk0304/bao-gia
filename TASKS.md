# Tasks

## Dang lam

- [x] Sua loi ma hoa tieng Viet trong:
  - `Bao_Gia_Jay_Home_Truc_Quan.html`
  - `Bao_Gia_Jay_Home.md`
  - `backend/admin.html`
  - mot so chuoi text trong backend

## Uu tien cao

- [x] Chuan hoa noi dung `README.md` va cac file Markdown ve UTF-8 dung.
- [x] Thay `google.generativeai` bang `google.genai` trong `backend/ai_parser.py`.
- [x] Kiem tra lai tinh tuong thich cua luong upload AI sau khi doi SDK.
- [x] Ra soat bao mat:
  - khong de lo `GEMINI_API_KEY`
  - bo mac dinh `ADMIN_PASSWORD`
  - dua secret ra khoi file chia se neu can

## Uu tien vua

- [x] Tach ro huong dan khoi tao moi truong local:
  - neu dung Python he thong
  - neu muon tao virtualenv moi dung cach
- [x] Don dep tai nguyen local khong nen dua vao repo:
  - `backend/venv`
  - file log tam
  - database mau neu khong can commit
- [ ] Khoi tao git repository neu muon quan ly phien ban.
- [x] Bo sung script chay/dung backend ro rang hon neu can.
- [ ] Bo sung test co ban cho:
  - import app
  - API health/doc
  - CRUD san pham

## Da xong

- [x] Them `README.md` mo ta cau truc repo, cach cai dependency va cach chay backend.
- [x] Chuyen `README.md` sang noi dung tieng Viet.
- [x] Them `.gitignore` de bo qua `venv`, `.env`, database local, file tam va file editor.
- [x] Kiem tra cau truc repo va xac dinh cac thanh phan chinh:
  - giao dien bao gia o thu muc goc
  - backend FastAPI trong `backend/`
  - SQLite local tai `backend/catalog.db`
- [x] Xac nhan `backend/venv` cu bi hong do tro toi duong dan Python khong con ton tai.
- [x] Tao cach chay backend moi bang Python he thong `3.12`.
- [x] Cap nhat `backend/requirements.txt` de phu hop hon voi Python `3.12` va code hien tai:
  - `greenlet` dung nhanh `3.x`
  - `pydantic` khoa ve nhanh `1.10.x`
- [x] Them script chay backend: `backend/start_backend.ps1`.
- [x] Cai dependency bang `py -3.12 -m pip install -r requirements.txt`.
- [x] Khoi dong backend thanh cong tren `http://127.0.0.1:8000`.
- [x] Kiem tra backend phan hoi thanh cong:
  - `/docs` tra `200`
  - `/api/categories` tra du lieu thanh cong
- [x] Them `backend/.env.example` va xoa secret that khoi `backend/.env`.
- [x] Loai bo mat khau admin mac dinh trong backend.
- [x] Chuyen `backend/ai_parser.py` sang SDK `google.genai`.
- [x] Xac nhan API `login` thanh cong voi gia tri trong `.env`.
- [x] Xac nhan API `upload` di toi buoc goi Gemini; loi hien tai la `503 UNAVAILABLE` tu phia dich vu.
- [x] Bo sung retry/backoff cho loi `503/UNAVAILABLE` tu Gemini.
- [x] Xac nhan API `upload` thanh cong sau khi them retry/backoff.
- [x] Them `backend/create_venv.ps1` de tao moi truong moi dung cach.
- [x] Them `backend/stop_backend.ps1` de dung backend ro rang.
- [x] Cap nhat `.gitignore` de bo qua `.venv312` va log tam.

## Ghi chu

- Backend hien dang chay duoc bang Python `3.12`.
- `backend/venv` cu khong con dang tin cay de su dung.
- Phan lon file nguon chinh da la UTF-8 dung; mojibake chu yeu den tu terminal Windows hoac du lieu cu.
- Da them bo test co ban tai `backend/tests/test_api.py`, nhung chua chay duoc bang `unittest` vi `py -3.12` va `.venv312` deu dang tro toi interpreter khong con ton tai tren may.
- Kiem tra live API tren `http://127.0.0.1:8000` xac nhan `POST/PUT/DELETE /api/products` va `GET /docs` co phan hoi, nhung co dau hieu moi truong dang dung lech process hoac lech file `catalog.db` khi doc lai du lieu.

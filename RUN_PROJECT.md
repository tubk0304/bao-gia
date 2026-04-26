# Quick Start

Run from the project root:

```powershell
.\run_project.ps1
```

Stop the backend:

```powershell
.\stop_project.ps1
```

If the Python 3.12 environment is missing or broken:

```powershell
.\backend\create_venv.ps1
.\backend\.venv312\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

Project URLs:

- Quote page: `http://127.0.0.1:8000/baogia`
- Admin: `http://127.0.0.1:8000/admin`
- API docs: `http://127.0.0.1:8000/docs`

Notes:

- `run_project.ps1` calls `backend/start_backend.ps1`.
- The backend now prefers `backend/.venv312` before older environments.
- Python 3.12 is required because `google-genai` in `backend/requirements.txt` does not support Python 3.9.

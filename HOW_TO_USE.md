# 🚀 AI Product Manager — Quick Start

## ✅ **#1 Easiest way (double-click)**

1. Open the folder: `D:\AI Product Manager`
2. **Double-click:**

```
📄 Launch AI Product Manager.bat
```

3. Wait 2–5 seconds. A black Command Prompt window will appear, then your default browser automatically opens to:

```
http://localhost:8501
```

> 💡 **Keep the black window open** while you use the app. When you're done, close that window (or press `Ctrl + C` inside it) to stop the server.

---

## 🔧 **#2 Manual launch (from PowerShell / CMD)**

Use this whenever you want, or if the `.bat` file ever fails on another machine.

```powershell
cd "D:\AI Product Manager"
& "C:\Users\prana\AppData\Local\Programs\Python\Python310\python.exe" run.py
```

If you set up a virtual environment later, use:

```powershell
.\.venv\Scripts\python.exe run.py
```

Then open **http://localhost:8501** in any browser.

---

## 📱 **#3 Open it from another device on your Wi‑Fi**

While the server is running on this PC, other devices (your phone, laptop) on the **same Wi‑Fi network** can open:

```
http://192.168.1.4:8501
```

---

## ⚙️ **How it works**

- **Entry point:** [run.py](file:///D:/AI%20Product%20Manager/run.py#L1-L19) launches Streamlit with [ui/app.py](file:///D:/AI%20Product%20Manager/ui/app.py)
- **Python version** (has streamlit + all dependencies): `C:\Users\prana\AppData\Local\Programs\Python\Python310\python.exe`
- **Data** (SQLite DB + RAG embeddings) is saved inside `D:\AI Product Manager\data\`
- **Sim mode:** If the Gemini / OpenAI API hits rate limits, the app auto-switches to simulation data so you can still walk through the full 7-step workflow.

---

## 🛠️ **Troubleshooting**

| Symptom | Fix |
|---|---|
| **Nothing opens / port 8501 is in use** | Open Task Manager → kill any `python.exe` processes, then try again. Or change the port: add `--server.port 8502` to the command in `run.py`. |
| **"`streamlit` not found" / missing packages** | Run: `& "C:\Users\prana\AppData\Local\Programs\Python\Python310\python.exe" -m pip install -r requirements.txt` from inside the project folder. |
| **Browser says "can't reach this page"** | Wait 2–3 seconds after launching — Streamlit needs a moment to start up. Then refresh. |
| **Black window flashes and disappears** | Open CMD first, then run `cd /d D:\AI Product Manager` + `"Launch AI Product Manager.bat"` so you can read the error before it closes. |

---

## 🧠 **Using the app (workflow)**

```
1. Configure  →  product name, goals, team size, capacity
2. Analyze    →  feedback + competitor + analytics agents run
3. Prioritize →  features are scored (P0/P1/P2/P3) & ranked
4. Approve    →  you pick which features to build (P0/P1/P2 pre-checked)
5. PRD        →  full 14-section PRD generated per approved feature
6. Sprint     →  sprint plan with tasks, story points, teams
7. Done       →  everything saved, data preserved in ./data
```

---

That's it. Two steps: **double-click the `.bat` file** → use the browser tab that opens.

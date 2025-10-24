# Project README — Setup & Run Instructions

Follow these steps **in order** to set up and run the projects for the client. These commands assume you're on **Windows** (PowerShell or CMD where shown). If Python 3.10 is already available on the machine, skip the installer step and proceed to cloning the repo.

> **TL;DR** — check for Python 3.10 first; if missing, install from the link below. Then clone, create venv, install deps, and run each app.

---

## 0. Quick check for installed Python versions

Run this to list installed Python launchers/versions:

```bash
py -0
```

If you **see `3.10`** in the output, skip the installer step and go straight to step 2.
If you **do NOT see `3.10`**, download & install Python 3.10 (step 1).

---

## 1. Install Python 3.10 (only if not present)

Download the Windows x64 installer:
https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe

Run the installer and be sure to:

- Check **"Add Python to PATH"** (recommended) or ensure `py` launcher installs.
- Choose the default options or customize if required.

After installation re-run:

```bash
py -0
```

to confirm `3.10` appears.

---

## 2. Clone the repository

```bash
git clone https://github.com/sameer-at-git/Python-Internship-Assignment.git
```

Change into the repository root:

```bash
cd Python-Internship-Assignment
```

---

## 3. Create a Python 3.10 virtual environment

Use the `py` launcher with the 3.10 interpreter:

```bash
py -3.10 -m venv venv
```

---

## 4. Activate the virtual environment

On Windows (CMD):

```bash
venv\Scripts\activate
```

(If PowerShell blocks script execution, run PowerShell as admin and `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once. Then re-run activation.)

---

## 5. Install required packages

```bash
pip install -r requirements.txt
```

---

## 6. Run the first app: Algorithmic Trading Adventure

```bash
cd Algorithmic-Trading-Adventure
python app.py
```

When finished, return to the repo root:

```bash
cd ..
```

---

## 7. Run the second app: Samsung Phone Advisor

```bash
cd Samsung-Phone-Advisor
```

### 7a. Create Groq Cloud API key

1. Open: https://console.groq.com/keys
2. Login (or create an account).
3. Create a new API key.
4. Copy the API key string (it starts with `gsk-...`).

### 7b. Store the key in a `.env` file (in the Samsung-Phone-Advisor project folder)

Replace the example key below with the real one you copied:

```bash
echo GROQ_API_KEY="gsk-dauidgawgdwagdag" > .env
```

> Note: If you prefer to edit the file manually, create a file named `.env` and add:
> GROQ_API_KEY="your-real-key-here"

### 7c. Run the app

```bash
python app.py
```

---

## 8. Troubleshooting & notes

- If `py -3.10` fails after installing Python:
  - Ensure the installer added the `py` launcher and Python 3.10 to PATH.
  - Try `python --version` and `python3 --version` to see other available executables.
- If `pip install -r requirements.txt` fails:
  - Make sure the venv is activated.
  - On Windows, if a package needs compilation and fails, install the Visual C++ Build Tools or use a prebuilt wheel.
- If Groq API requests fail, confirm:
  - The key saved in `.env` is correct and active.
  - The app reads the `.env` file (some apps require restarting after creating `.env`).

---

## 9. Clean up / Deactivate environment

To stop using the virtual environment:

```bash
deactivate
```

---

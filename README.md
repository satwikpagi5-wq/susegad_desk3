# Susegad Desk

**A privacy-first guest check-in prototype for independent homestays.** Susegad Desk turns an ID photo into editable guest details using OCR and a local language model, then requires human review before adding anything to the day register.

> **Prototype and privacy notice:** The Vercel version is a fictional-data demo only. It does not accept ID images and does not connect to the OCR service. The full OCR workflow runs on a reception computer on a trusted local network. This is not a legal or compliance product.

## Hosted demo

The static Vercel build is served from [web/](web/). It demonstrates the review form, session-only guest register, and CSV export with fictional values. It intentionally has no upload field: government ID images must not be sent to this public demo.

## Local app

The full local app is served by FastAPI from [server.py](server.py), with its UI in [static/](static/). Images are processed by Tesseract on the host computer, and OCR text is passed to Ollama running on that same computer. No cloud AI or OCR endpoint is configured.

### Requirements

- Python 3.10 or newer
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on the reception computer
- [Ollama](https://ollama.com/) installed and running locally
- The phi3:mini model downloaded in Ollama

### Run it locally


Run these commands in PowerShell from the project folder:

```powershell
ollama pull phi3:mini
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000 on the reception computer. A phone on the same trusted Wi-Fi can open http://<reception-computer-lan-ip>:8000.

Keep the computer firewall enabled, use a private Wi-Fi network, and do not forward port 8000 to the public internet. This prototype has no authentication or TLS. If Tesseract is not on PATH, set pytesseract.pytesseract.tesseract_cmd in server.py. OCR language defaults to English; set TESSERACT_LANG to an installed language code if needed. OLLAMA_MODEL and OLLAMA_URL can override the defaults.

## Features

- JPG, PNG, and WebP upload (up to 10 MB) in the local app
- Local Tesseract OCR followed by structured extraction from local Ollama
- Editable suggestions and required human review confirmation
- Session-only in-memory register, with CSV export
- Fictional sample mode, available in the local app and hosted demo
- Responsive interface without hosted font dependencies

## Data handling and limitations

Uploaded image bytes and OCR text are held in memory during the local extraction request and are not intentionally written to disk. The local register is held in browser memory and clears when the page is closed or refreshed. CSV exports contain personal data and need suitable access and deletion controls. The public Vercel build is a separate static demo with no OCR backend; use fictional values only.

OCR can misread identity documents, and model output can be wrong. Verify every field against the original document. Before real-world use, independently confirm the lawful purpose, notice or consent, required fields, retention policy, and current local requirements with qualified guidance. Do not assume this prototype meets police reporting or identity verification rules.

## Project layout

```text
server.py          Local FastAPI OCR service
static/            Full local app interface
web/               Static, fictional-data-only Vercel demo
requirements.txt   Python dependencies for local use
vercel.json        Vercel static output configuration
```

## Deploying the demo on Vercel

Import the GitHub repository into Vercel and deploy it as a static site. The included [vercel.json](vercel.json) points Vercel at web/; no build command or environment variables are needed. Vercel can create a deployment for each push to the connected Git branch. The hosted demo remains separate from the local OCR backend by design.

## License

No license has been added yet. All rights are reserved unless the repository owner chooses and adds a license.

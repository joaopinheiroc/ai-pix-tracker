# ai-pix-tracker

A Telegram bot that automatically reads Brazilian Pix payment receipts and logs them into a Google Sheets spreadsheet. Send a photo of a receipt, and the bot extracts the sender, date, amount, and receiver using Gemini's vision capabilities, then writes the transaction to your spreadsheet — no manual data entry required.

## Why this project

Manually tracking Pix transfers — for a small business, a shared expense, or personal bookkeeping — usually means copying numbers from a screenshot into a spreadsheet by hand. This project removes that step entirely: a photo in, a structured record out. It was built as a practical exercise in wiring together three distinct systems (a messaging platform, a vision-capable LLM, and a spreadsheet API) into a single reliable pipeline, with attention to error handling, retries, and clean separation of concerns.

## How it works

```
Telegram photo → Gemini (vision + structured extraction) → Google Sheets row
```

1. A user sends a photo of a Pix receipt to the bot.
2. The bot downloads the image and sends it to Gemini 3.5 Flash with a prompt instructing it to extract exactly four fields as JSON.
3. The response is parsed into a dictionary and appended as a new row in a Google Sheet via a Service Account connection.
4. The bot replies to the user confirming the amount and payer.
5. If the extraction fails (e.g. a transient server error from the model), the request is retried automatically with exponential backoff before falling back to an error message.

## Tech stack

| Layer | Technology |
|---|---|
| Bot framework | [python-telegram-bot](https://docs.python-telegram-bot.org/) (async, v20+) |
| Vision / extraction | [google-genai](https://googleapis.github.io/python-genai/) — Gemini 3.5 Flash |
| Spreadsheet storage | [gspread](https://docs.gspread.org/) + [google-auth](https://google-auth.readthedocs.io/) (Service Account) |
| Config management | python-dotenv |
| Language | Python 3.12 |

## Project structure

```
ai-pix-tracker/
├── src/
│   ├── ai_extractor.py    # Gemini-based image analysis and JSON extraction
│   ├── sheets_client.py   # Google Sheets authentication and row writing
│   └── bot.py              # Telegram handlers and orchestration
├── main.py                 # Application entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

Each module has a single responsibility: `ai_extractor.py` only talks to Gemini, `sheets_client.py` only talks to Google Sheets, and `bot.py` only talks to Telegram — orchestrating the other two. Neither `ai_extractor.py` nor `sheets_client.py` has any knowledge of Telegram, which keeps the pipeline easy to test and easy to extend to other messaging platforms in the future.

## Setup

### Prerequisites

- Python 3.12+
- A Telegram bot token (via [@BotFather](https://t.me/BotFather))
- A Google Cloud project with the Sheets and Drive APIs enabled, and a Service Account key
- A Gemini API key (via [Google AI Studio](https://aistudio.google.com/apikey))

### Installation

```bash
git clone https://github.com/joaopinheiroc/ai-pix-tracker.git
cd ai-pix-tracker
python3.12 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   GEMINI_API_KEY=your_key_here
   GOOGLE_SHEETS_ID=your_spreadsheet_id_here
   ```
2. Place your Service Account key in the project root as `credentials.json`.
3. Share your target Google Sheet with the Service Account's email address (found in `credentials.json`), granting Editor access.
4. Make sure row 1 of the sheet has a header: `Name | Date | Amount | Receiver`.

### Running

```bash
python main.py
```

Send a photo of a Pix receipt to your bot on Telegram to see it in action.


## Notes on model choice

This project originally targeted `gemini-2.5-flash`, per the initial project scope. During development, that model became unavailable to newly created API keys ahead of its official deprecation, so the project was migrated to `gemini-3.5-flash`, which shares the same free-tier rate limits.

## License

MIT.
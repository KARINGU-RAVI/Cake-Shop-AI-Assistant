# 🎂 AI-Powered WhatsApp Cake Shop Sales Agent

An autonomous, production-ready WhatsApp conversation agent built from scratch using **Python**, **FastAPI**, **SQLAlchemy ORM**, and the official **Google GenAI SDK (Gemini 2.5 Flash)**.

---

## 🚀 Key Features

* **Strict 11-step Ordering Flow**: Welcomes customers, handles flavor/size selections, custom writing, delivery type, payment links, and confirmations without skipping steps.
* **Auto-Language Detection**: Supports English, Hindi, Kannada, Telugu, Tamil, Bengali, and Malayalam.
* **Sales Intelligence**: Dynamically upsells larger cake sizes (e.g. 2kg or 3kg options) during weight selection.
* **Embedded FAQs**: Resolves delivery, refund, and location queries, then redirects the customer back to the current active step.
* **Robust Tool Calling**: Exposes native python methods (price calculation, order creation, status queries) directly to Gemini's reason loop.
* **Local Chat Simulator**: Includes a built-in interactive simulator inside the Swagger UI, allowing developer testing without requiring WhatsApp sandbox setup.

---

## 📁 Folder Structure

```
cake-shop-agent/
├── app/
│   ├── api/                    # Routers (Webhook + Simulator)
│   ├── core/                   # Security, exceptions, logger config
│   ├── models/                 # SQLAlchemy 2.0 models
│   ├── schemas/                # Pydantic validation schemas
│   ├── repositories/           # Repository pattern data layers
│   ├── services/               # Order & Payment business services
│   ├── agent/                  # Gemini Client, memory, tool executables
│   ├── database/               # DB connection and product catalogs
│   ├── main.py                 # FastAPI application root
│   └── config.py               # Env settings management
├── tests/                      # Automated unit/integration tests
├── Dockerfile                  # Multi-stage Docker package
├── docker-compose.yml          # Staging orchestrations
├── requirements.txt            # Package listings
└── README.md                   # This developer guide
```

---

## 🛠️ Local Installation & Startup

### Step 1: Install Dependencies
Ensure you have Python 3.11+ installed. Create and activate a virtual environment:

```bash
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install required libraries
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_whatsapp_business_account_id
WHATSAPP_TOKEN=your_whatsapp_token
VERIFY_TOKEN=my-secret-token
DATABASE_URL=sqlite:///./cake_shop.db
HOST=0.0.0.0
PORT=8000
```

### Step 3: Run the Application
Start the uvicorn development server:

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. The Swagger UI will appear!

---

## 🧪 Local Simulator Testing

To test the AI Agent's intelligence and ordering state-machine without setting up the Meta Developer Portal or Cloudflare tunnels:

1. Open **Swagger UI** (`/docs`).
2. Locate the `POST /api/v1/chat` endpoint.
3. Click **Try it out** and enter:
   * **phone_number**: `1234567890` (Used for session isolation and memory retrieval)
   * **name**: `Arjun`
   * **message**: `Hi, I need a cake for a birthday party.`
4. Click **Execute** and review the agent's welcome greeting.
5. In subsequent requests, send messages like:
   * `I want chocolate cake`
   * `1kg` (Watch the agent politely upsell the 2kg size!)
   * `Write 'Happy Birthday Riya' on it`
   * `I want home delivery`
   * `123 Baker's Street`
   * `Tomorrow at 5 PM`
   * `Yes, confirm the order summary!` (Triggers order creation and checkout sandbox link generation)

---

## 🌐 WhatsApp Cloud API Webhook Integration

### Step 1: Expose Local Host with Cloudflare Tunnel
To receive Meta webhook posts on your local development machine, configure a secure Cloudflare Tunnel:

```bash
# Download and install cloudflared
# Expose port 8000:
cloudflared tunnel --url http://localhost:8000
```

Copy the generated public URL (e.g., `https://xxxxx.trycloudflare.com`). Your webhook endpoint will be:
`https://xxxxx.trycloudflare.com/api/v1/webhook`

### Step 2: Meta App Configuration
1. Log in to the [Meta Developer Portal](https://developers.facebook.com/).
2. Create or select your **WhatsApp Business App**.
3. Under WhatsApp, go to **Configuration**.
4. In the **Webhook URL** field, paste your public Cloudflare address:
   `https://xxxxx.trycloudflare.com/api/v1/webhook`
5. In the **Verify Token** field, enter the value from your `.env` file (e.g. `my-secret-token`).
6. Click **Verify and Save**.
7. Under **Webhook Fields**, subscribe to **messages**.

---

## 📦 Production Deployment

### Option A: Docker Deployment
Build and run the application in a docker container:

```bash
# Build the container
docker build -t cake-shop-agent .

# Run the container
docker run -d -p 8000:8000 --env-file .env cake-shop-agent
```

### Option B: Render Setup
1. Create a new **Web Service** on Render.
2. Link your GitHub repository.
3. Configure the environment:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment keys (`GEMINI_API_KEY`, `WHATSAPP_TOKEN`, etc.) in the Render dashboard under **Environment Variables**.
5. Click **Deploy**.

# Employee Control Portal (`employee_control_portal`)

Production-ready enterprise web portal for managing the `emp_runexe` Windows Agent, providing real-time workforce monitoring, device management, agent lifecycle management, policies, attendance, audit trails, and role-based access control (RBAC).

---

## 🏛️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    React + TypeScript UI                    │
│      (Vite, Tailwind, TanStack Query, Recharts, WSS)        │
└──────────────┬───────────────────────────────▲──────────────┘
               │ HTTPS (REST API)              │ WSS (Live Updates)
               ▼                               │
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend Application                 │
│  - JWT Auth / RBAC Middleware  - Blueprints / Modules       │
│  - Validation (Pydantic)       - Service Layer              │
│  - Audit Logging Middleware    - WebSocket Event Handler    │
└──────┬───────────────────────┬────────────────────────▲─────┘
       │                       │                        │
       │ SQLAlchemy ORM        │ Redis Pub/Sub          │ Agent WSS / REST
       ▼                       ▼                        │
┌──────────────┐       ┌────────────────┐      ┌────────┴─────┐
│  PostgreSQL  │       │  Redis Cache & │      │  emp_runexe  │
│  (History,   │       │    Pub/Sub     │◄─────┤   Windows    │
│  Relational, │       │  (Live State,  │      │    Agent     │
│   Audit)     │       │  Heartbeats)   │      └──────────────┘
└──────────────┘       └────────────────┘
```

---

## 📁 Repository Structure

```text
employee_control_portal/
├── backend/                  # Flask REST API & WebSocket Server
│   ├── app/                  # Application core
│   │   ├── models/           # SQLAlchemy Data Models (PostgreSQL)
│   │   ├── modules/          # Domain Blueprints & APIs (/api/v1/*)
│   │   ├── services/         # Business & Real-time Services
│   │   ├── websocket/        # Real-time WebSocket connection manager
│   │   ├── middleware/       # Auth, RBAC, Error Handling & Auditing
│   │   └── utils/            # Pagination, Validation, Responses
│   ├── tests/                # Automated pytest suite
│   ├── requirements.txt      # Python dependencies
│   ├── seed.py               # Database seeder (Default roles, permissions, admin)
│   └── run.py                # Server entrypoint
│
├── frontend/                 # React + TypeScript Admin Portal
│   ├── src/
│   │   ├── api/              # Axios HTTP client & domain API services
│   │   ├── components/       # Reusable UI component library (Design system)
│   │   ├── pages/            # Enterprise views (Dashboard, Monitoring, Devices, etc.)
│   │   ├── websocket/        # Real-time WebSocket client
│   │   ├── hooks/            # Custom React hooks
│   │   ├── context/          # Auth & Real-time context providers
│   │   └── types/            # TypeScript interfaces & domain models
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
│
├── infrastructure/           # Docker & Nginx Deployment Configuration
│   ├── docker/               # Container Dockerfiles
│   ├── nginx/                # Nginx proxy & SSL/WSS configuration
│   └── docker-compose.yml    # Multi-service local/production orchestration
│
└── docs/                     # Comprehensive Architecture & API Documentation
    ├── ARCHITECTURE.md       # High-level architecture & design
    ├── DATABASE.md           # Database ER diagram & schema reference
    ├── API.md                # REST API endpoints & contracts
    ├── WEBSOCKET.md          # WebSocket protocol specification
    ├── SECURITY.md           # Security & Zero-Trust enrollment guide
    └── RBAC.md               # Roles & permissions matrix
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Initialize database & seed initial records
python seed.py

# Run development server
python run.py
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Docker Compose (Full Stack)

```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

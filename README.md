<p align="center">
  <img src="https://github.com/xycld/NanoVote/raw/refs/heads/master/logo.svg" width="120" alt="NanoVote Logo">
</p>

# NanoVote

Minimal anonymous voting system with frontend-backend separation and pure Redis storage

## Features

- No registration required, create polls instantly
- IP hash to prevent duplicate voting
- Customizable duration from 3 minutes to 10 days
- Auto-expire cleanup, zero maintenance

## Quick Start

```bash
git clone https://github.com/xycld/NanoVote
cd NanoVote
docker-compose up -d
```

Access: http://localhost:50000

API Docs: http://localhost:50000/docs

## Local Development

Backend:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

## License

MIT License

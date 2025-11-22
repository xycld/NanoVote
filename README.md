<p align="center">
  <img src="logo.svg" width="120" height="120" alt="NanoVote Logo">
</p>

# NanoVote

[English](README.md) | [简体中文](README.zh-CN.md)

Minimalist, anonymous, high-performance voting system.

**Lightning Fast | Modern UI**

## Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Build image
docker build -t nanovote .

# 2. Run container (persist data to local data directory)
docker run -d \
  -p 9527:9527 \
  -v $(pwd)/data:/data \
  --name nanovote \
  nanovote

# 3. Access application
# Open browser at: http://localhost:9527
```

### Option 2: Local Development

```bash
# 1. Install dependencies (recommend using uv, Python's equivalent to pnpm, or use pip)
pip install -r requirements.txt

# 2. Start service
python main.py

# 3. Access application
# Open browser at: http://localhost:9527
```

### Custom Port

```bash
# Option 1: Using environment variable
export APP_PORT=3000
python main.py

# Option 2: Specify when running Docker
docker run -d \
  -p 3000:3000 \
  -e APP_PORT=3000 \
  -v $(pwd)/data:/data \
  --name nanovote \
  nanovote
```

## Core Features

1. **Create Polls**

   - Support 2-20 options
   - Title max 100 characters
   - Option max 50 characters

2. **Anonymous Voting**

   - No registration/login required
   - localStorage-based duplicate vote prevention
   - Server-side IP rate limiting

3. **Real-time Statistics**

   - Results displayed immediately after voting
   - Percentage + vote count display
   - Smooth animation transitions

4. **Auto Cleanup**

   - Keeps maximum 1000 polls
   - Auto-deletes oldest polls
   - Background async execution

## Environment Variables

| Variable | Default | Description |
| ------------ | ----------- | -------------------- |
| `DATA_DIR` | `.` | Database storage directory |
| `APP_HOST` | `0.0.0.0` | Listen address |
| `APP_PORT` | `9527` | Listen port (customizable) |

## License

This project is licensed under the MIT License.

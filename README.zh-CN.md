<p align="center">
  <img src="https://github.com/xycld/NanoVote/raw/refs/heads/master/logo.svg" width="120" alt="NanoVote Logo">
</p>

# NanoVote

极简匿名投票系统，前后端分离，纯Redis存储

## 特性

- 无需注册，快速创建投票
- IP哈希防重复投票
- 支持3分钟到10天自定义时长
- 自动过期清理，无需维护

## 快速启动

```bash
git clone https://github.com/xycld/NanoVote
cd NanoVote
docker-compose up -d
```

访问地址: http://localhost:50000

API文档: http://localhost:50000/docs

## 本地开发

后端:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

前端:

```bash
cd frontend
pnpm install
pnpm dev
```

## 许可证

MIT License

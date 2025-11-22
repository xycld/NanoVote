<p align="center">
  <img src="logo.svg" width="120" height="120" alt="NanoVote Logo">
</p>

# NanoVote

[English](README.md) | [简体中文](README.zh-CN.md)

极简、匿名、高性能的投票系统。

**极速加载 | 美观现代**

## 快速开始

### 方式 1: Docker 部署（推荐）

```bash
# 1. 构建镜像
docker build -t nanovote .

# 2. 运行容器（数据持久化到本地 data 目录）
docker run -d \
  -p 9527:9527 \
  -v $(pwd)/data:/data \
  --name nanovote \
  nanovote

# 3. 访问应用
# 打开浏览器访问: http://localhost:9527
```

### 方式 2: 本地运行

```bash
# 1. 安装依赖（推荐使用 pnpm 的 Python 等效工具 uv，或使用 pip）
pip install -r requirements.txt

# 2. 启动服务
python main.py

# 3. 访问应用
# 打开浏览器访问: http://localhost:9527
```

### 自定义端口

```bash
# 方式 1: 使用环境变量
export APP_PORT=3000
python main.py

# 方式 2: Docker 运行时指定
docker run -d \
  -p 3000:3000 \
  -e APP_PORT=3000 \
  -v $(pwd)/data:/data \
  --name nanovote \
  nanovote
```

## 核心功能

1. **创建投票**

   - 支持 2-20 个选项
   - 标题最长 100 字符
   - 选项最长 50 字符
2. **匿名投票**

   - 无需注册/登录
   - 基于 localStorage 防重复投票
   - 服务端 IP 限流
3. **实时统计**

   - 投票后立即显示结果
   - 百分比 + 票数双重展示
   - 平滑动画过渡
4. **自动清理**

   - 最多保留 1000 个投票
   - 自动删除最旧的投票
   - 后台异步执行

## 环境变量

| 变量名       | 默认值      | 说明                 |
| ------------ | ----------- | -------------------- |
| `DATA_DIR` | `.`       | 数据库存储目录       |
| `APP_HOST` | `0.0.0.0` | 监听地址             |
| `APP_PORT` | `9527`    | 监听端口（可自定义） |

## 许可证

本项目基于 MIT 许可证开源。

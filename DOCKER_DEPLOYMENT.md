# 数据库学习系统 - Docker部署指南

## 概述

本文档提供了数据库学习系统的完整Docker容器化部署方案，包括开发环境和生产环境的配置。

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ 可用内存
- 10GB+ 可用磁盘空间

## 快速开始

### 1. 准备环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（根据实际情况修改）
nano .env
```

### 2. 启动应用（生产模式）

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问应用
# http://localhost:5000
```

### 3. 启动应用（开发模式）

```bash
# 使用开发配置启动
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

## 详细配置

### 环境变量配置

在 `.env` 文件中配置以下关键参数：

```bash
# Flask应用配置
SECRET_KEY=your-very-secure-secret-key
FLASK_ENV=production

# Ollama AI服务配置
OLLAMA_API_URL=http://host.docker.internal:11434/api/chat
OLLAMA_MODEL=qwen3:14b

# 其他配置
TZ=Asia/Shanghai
```

### Ollama服务连接配置

#### 场景1：Ollama运行在宿主机上（推荐）

```bash
# .env 文件配置
OLLAMA_API_URL=http://host.docker.internal:11434/api/chat
```

#### 场景2：Ollama运行在另一个Docker容器中

```yaml
# docker-compose.yml 添加ollama服务
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-service
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - db-learning-network

volumes:
  ollama_data:
```

```bash
# .env 文件配置
OLLAMA_API_URL=http://ollama-service:11434/api/chat
```

#### 场景3：Ollama运行在远程服务器上

```bash
# .env 文件配置
OLLAMA_API_URL=http://your-remote-server:11434/api/chat
```

## 数据持久化

### 数据目录结构

```
./data/                 # 数据库和缓存文件
├── database.db         # SQLite数据库
├── explanations/       # AI生成的讲解缓存
└── settings.json       # 系统设置

./static/uploads/       # 用户上传文件
./logs/                 # 应用日志
```

### 备份数据

```bash
# 备份数据目录
docker run --rm -v $(pwd)/data:/data -v $(pwd)/backup:/backup alpine \
  tar czf /backup/data-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# 备份上传文件
docker run --rm -v $(pwd)/static/uploads:/uploads -v $(pwd)/backup:/backup alpine \
  tar czf /backup/uploads-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /uploads .
```

### 恢复数据

```bash
# 恢复数据目录
docker run --rm -v $(pwd)/data:/data -v $(pwd)/backup:/backup alpine \
  tar xzf /backup/data-backup-YYYYMMDD-HHMMSS.tar.gz -C /data

# 恢复上传文件
docker run --rm -v $(pwd)/static/uploads:/uploads -v $(pwd)/backup:/backup alpine \
  tar xzf /backup/uploads-backup-YYYYMMDD-HHMMSS.tar.gz -C /uploads
```

## 常用命令

### 容器管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f database-learning-system

# 进入容器
docker-compose exec database-learning-system sh
```

### 镜像管理

```bash
# 构建镜像
docker-compose build

# 强制重新构建
docker-compose build --no-cache

# 拉取最新镜像
docker-compose pull

# 清理未使用的镜像
docker image prune -f
```

### 数据库管理

```bash
# 初始化数据库
docker-compose exec database-learning-system python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# 查看数据库状态
docker-compose exec database-learning-system python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('Tables:', db.engine.table_names())"
```

## 监控和健康检查

### 健康检查

应用内置了健康检查端点：

```bash
# 检查应用健康状态
curl http://localhost:5000/api/health

# 查看Docker健康状态
docker-compose ps
```

### 日志监控

```bash
# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f database-learning-system

# 查看最近100行日志
docker-compose logs --tail=100 database-learning-system
```

## 性能优化

### 资源限制

在 `docker-compose.yml` 中已配置资源限制：

```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### 缓存优化

- AI生成的内容会缓存到 `data/explanations/` 目录
- 静态文件通过Docker层缓存优化
- 数据库连接池配置优化

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker-compose logs database-learning-system
   
   # 检查配置文件
   docker-compose config
   ```

2. **无法连接Ollama服务**
   ```bash
   # 检查Ollama服务状态
   curl http://localhost:11434/api/tags
   
   # 测试容器内网络连接
   docker-compose exec database-learning-system curl http://host.docker.internal:11434/api/tags
   ```

3. **数据库问题**
   ```bash
   # 重新初始化数据库
   docker-compose exec database-learning-system python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
   ```

4. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R $USER:$USER data/ static/uploads/ logs/
   ```

### 调试模式

```bash
# 启动调试模式
docker-compose -f docker-compose.dev.yml up

# 进入容器调试
docker-compose exec database-learning-system sh
```

## 安全建议

1. **更改默认密钥**：修改 `.env` 中的 `SECRET_KEY`
2. **网络安全**：在生产环境中配置防火墙规则
3. **数据加密**：考虑对敏感数据进行加密存储
4. **定期备份**：设置自动备份计划
5. **更新维护**：定期更新Docker镜像和依赖

## 生产部署建议

1. **使用反向代理**：配置Nginx或Traefik
2. **SSL证书**：启用HTTPS
3. **监控告警**：集成Prometheus + Grafana
4. **日志收集**：使用ELK Stack或类似方案
5. **自动扩展**：配置Docker Swarm或Kubernetes

## 支持

如遇到问题，请检查：
1. Docker和Docker Compose版本
2. 系统资源使用情况
3. 网络连接状态
4. 日志文件内容

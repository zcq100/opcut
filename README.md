# opcut

[English Docs](README.rst) | [线上示例](https://opcut.kopic.xyz/) | [Docker 镜像](https://github.com/zcq100/opcut/pkgs/container/opcut)

`opcut` 是一个[切割下料问题](https://en.wikipedia.org/wiki/Cutting_stock_problem)优化器，支持多板材和闸刀式切割（贯穿式切割）。包含：

- 多种后端优化算法实现
- 命令行工具
- REST API 服务（OpenAPI 定义）
- 单页 Web 应用前端

源码仓库：<https://github.com/zcq100/opcut.git>

> 公开实例 <https://opcut.kopic.xyz/> 资源有限，仅供功能评估。复杂或重复计算建议自行部署。

## 运行环境

- Python >= 3.10

> Ubuntu 下如果 pycairo 不可用，需要先执行：`apt install gcc pkg-config libcairo2-dev`

## 安装

### Docker

```bash
docker run -p 8080:8080 ghcr.io/zcq100/opcut:latest
```

### Python wheel

```bash
pip install opcut
```

### Arch Linux

```bash
yay -S opcut
```

### Windows

从 [GitHub Releases](https://github.com/zcq100/opcut/releases) 下载 Windows 发行版，解压后运行 `opcut-server.cmd` 启动服务，或使用 `opcut.cmd` 执行各项操作。

## 使用

`opcut` 命令支持三种操作模式：

### 计算 (`opcut calculate`)

输入切割参数（JSON/YAML/TOML 格式），输出优化结果。

```bash
opcut calculate --input-format yaml --output result.json << EOF
cut_width: 1
panels:
    panel1:
        width: 100
        height: 100
items:
    item1:
        width: 10
        height: 10
        can_rotate: false
EOF
```

### 生成 (`opcut generate`)

根据计算结果生成可视化输出（SVG、PDF 等）。

```bash
opcut generate --output output.pdf result.json
```

### 服务 (`opcut server`)

启动 HTTP 服务器，提供 Web 前端和 OpenAPI 接口（默认监听 `http://0.0.0.0:8080`）。

```bash
opcut server
```

更多参数说明：

```bash
man 1 opcut
```

- JSON Schema 定义：[schemas/opcut.yaml](schemas/opcut.yaml)
- OpenAPI 定义：[schemas/openapi.yaml](schemas/openapi.yaml)

## 开发构建

### 开发依赖

- C99 编译器（gcc、clang 等）
- Node.js >= 7
- npm

### 构建步骤

```bash
pip install -r requirements.pip.txt
doit list     # 列出可用任务
doit          # 默认任务，构建 wheel 到 build/ 目录
```

## 许可证

[GPL-3.0](LICENSE)

Copyright (C) 2017-2025 Bozo Kopic

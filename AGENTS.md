## 项目目标
Mac 端渲染一张 1088×1448 的灰度卡片，通过 SSH 推送到越狱 Kindle Paperwhite 3，作为桌面墨水屏信息面板。

## 目录结构
```text
kindle-desk-card/
├── AGENTS.md
├── CLAUDE.md
├── config.yaml
├── config.example.yaml
├── requirements.txt
├── test_render.py
└── kindle_card/
    ├── config.py
    ├── daemon.py
    ├── push.py
    ├── data/
    └── render/
```

## 技术栈
- Python 3
- Pillow / PyYAML / paramiko / requests
- Kindle USBNetwork + OpenSSH
- FBInk + `/dev/fb0` 帧缓冲写入

## 命名规范
- Python 文件名用 `snake_case`
- widget 绘制函数用 `paint_<name>`
- 数据抓取函数用 `fetch(config=None) -> dict`
- 配置项统一放在 `config.yaml`

## 页面/模块规范
- `kindle_card/data/` 只负责取数，不负责绘制
- `kindle_card/render/` 只负责布局和绘制
- `kindle_card/push.py` 只负责 SSH、SFTP、帧缓冲写入和刷新
- `test_render.py` 只做本地预览，不触发远程推送
- `daemon.py` 负责调度：取数 → 渲染 → 推送

## 操作流程
1. 先确认 Kindle 侧环境：
   - 已越狱
   - 已安装 KUAL、USBNetwork、KOReader
   - `/mnt/us/koreader/fbink` 存在
2. 本机准备 Python 环境：
   - 优先使用可实际运行的虚拟环境
   - 当前仓库实测可用的是 `./.preview-venv/bin/python`
   - 如果 `./.venv/bin/python` 不存在或失效，直接重建，不要继续沿用坏环境
3. 配置 `config.yaml`：
   - `kindle.host` 以 Kindle `;711` 页面的当前 IP 为准
   - `key_path` 指向本机实际可用的私钥
4. 先跑本地预览：
   - `./.preview-venv/bin/python test_render.py`
5. 再跑单次推送或 daemon：
   - 单次推送：直接调用 `render()` + `push_to_kindle()`
   - 常驻刷新：`./.preview-venv/bin/python -m kindle_card.daemon`

## 质量标准
- Kindle 屏幕能稳定刷新，不出现只渲染不显示
- SSH 连接可复现，不依赖手工猜测 IP 或临时密码
- 文档中的命令必须能在当前仓库环境复现
- 文案改动后，README、教程、实际渲染内容保持一致

## Kindle 连接实测结论
- Wi-Fi IP 用 Kindle 搜索 `;711` 查看，实测格式为 `192.168.x.x`
- KUAL 中 `USBNetwork Status` 必须看到 `SSHD is up`，否则 Mac 侧再试也没用
- 如果显示 `usbms`，说明还在 USB 存储模式，先弹出磁盘、拔线，再 `Toggle USBNetwork`
- Kindle 挂载到 Mac 后，可以直接改 `/Volumes/Kindle/usbnet/etc/config` 和 `authorized_keys`
- 实测需要保证：
  - `USE_WIFI="true"`
  - `USE_WIFI_SSHD_ONLY="true"`
  - `USE_OPENSSH="true"`
- 这台设备上，RSA 密钥比新建的 ed25519 更稳定，建议优先用 RSA
- 当 `22` 端口是 `Connection refused` 时，优先判断 Kindle SSHD 没起来；当端口打开但 `Permission denied` 时，再看密钥

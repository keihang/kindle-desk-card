## 项目目标
Mac 端 Python 渲染 widget 图片，SSH 推送到越狱 Kindle (KPW3) 的墨水屏显示，实现桌面 ambient 副屏。

## 目录结构
```
kindle-desk-card/
├── config.yaml            # 配置（城市、刷新间隔、widget、Kindle IP）
├── kindle_card/
│   ├── config.py          # 配置加载
│   ├── data/              # 数据源（天气/时间/飞书任务/宝可梦/鸡汤）
│   ├── render/            # 画布 + widget 渲染
│   ├── push.py            # SSH 推送到 Kindle（dd 写帧缓冲 + fbink 刷新）
│   └── daemon.py          # 主循环
├── requirements.txt
└── test_render.py         # 本地预览
```

## 技术栈
- Python 3 / Pillow / PyYAML / paramiko / requests
- Kindle 端：`dd` 写原始帧缓冲 `/dev/fb0` + FBInk 刷新屏幕
- 数据源：wttr.in API（requests）/ lark-cli（飞书任务）/ PokeAPI（urllib）/ 硬编码鸡汤语录
- SSH 认证：优先使用 RSA 密钥；当前本机实测可用私钥是 `~/.ssh/kindle_usb_rsa`
- Kindle IP：不要写死，以 Kindle `;711` 页面显示结果为准

## 屏幕规格
- 帧缓冲：1088×1448（可见 1072×1448），8-bit 灰度
- 推送流程：SFTP 上传 `card.raw` → `dd if=/tmp/card.raw of=/dev/fb0` → `fbink -s -W GC16 -f`
- 推送前已实测必须：kill `JunoStatusBarDriver` + `pillowd`

## 命名规范
- widget 函数：`paint_<name>(draw, rect, data)`
- 数据函数：`fetch(config=None) -> dict`
- 文件名：snake_case

## 操作流程
1. 先确认 Kindle：
   - `;711` 能看到当前 Wi-Fi IP
   - KUAL → USBNetwork → `USBNetwork Status` 显示 `SSHD is up`
2. 如需修 SSH：
   - 挂载 Kindle 后直接检查 `/Volumes/Kindle/usbnet/etc/config`
   - 确保 `USE_WIFI="true"`、`USE_WIFI_SSHD_ONLY="true"`、`USE_OPENSSH="true"`
   - 公钥写入 `/Volumes/Kindle/usbnet/etc/authorized_keys`
3. 编辑 `config.yaml`（城市、刷新间隔、当前 Kindle IP、私钥路径）
4. `./.preview-venv/bin/python test_render.py` — 本地预览，生成 PNG 到桌面
5. `./.preview-venv/bin/python -m kindle_card.daemon` — 定时推送到 Kindle

## 模块规范
- widget 绘制：`paint_<name>(draw, rect, data)` — 接收 PIL ImageDraw、矩形区域、数据字典
- 数据采集：`fetch(config=None) -> dict` — 返回 widget 所需数据
- 头像路径：`~/path/to/avatar.jpg`（config.yaml 中配置）

## 质量标准
- 墨水屏上文字清晰可读
- 刷新无残影（用 GC16 waveform）
- SSH 断开不崩溃，静默重试
- 文档里的连接流程必须与这台 Kindle 的实测行为一致

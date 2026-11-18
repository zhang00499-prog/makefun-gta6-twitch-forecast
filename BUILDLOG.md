# BUILDLOG — gta6-twitch-ccu-forecast-01

- 核查（2026-11-19 约 07:30 CST）：GET competition → acceptingSubmissions=true、status=open、entryFeeUsd=null（免费）、$250 / 20 名额（50/35/25/10×7/7×10）、escrow 已锁 250 USDC、已 15,486 提交、截止 2026-11-19T01:00Z = 09:00 CST。requirements：harness=program/v1、handed_over_places=none、deliverables=公开 GitHub 仓库＋commit＋bundle；评分=log 尺度 pinball loss，须低于官方基线（第 1 小时持平＋随机游走展宽）与官方 AI 预测才有奖；配额 max 10/日、20 总。
- I/O：读 /input（或 MAKEFUN_INPUT_DIR）下 <id>.in（JSON，known 给第 1 小时 viewers，comparables 给 38 个历史大作首发日完整小时曲线），写 /output/<id>.out：{"hours":[{hour, q:[5 个分位数]}×23]}，≤8 秒/case、确定性、仅标准库。
- 模型：每 comparable 算 r_h = 首发日第 h 小时 / 第 1 小时；按 log10(第 1 小时量级) 距离高斯加权（WEIGHT_SCALE=0.5，+0.05 地板权重）；逐小时加权分位数作预测，中位数信任度 MEDIAN_TRUST=0.95，展宽下限 SPREAD_FLOOR_SHARE=0.65×基线 σ。
- 离线自测：对 37 个可用 comparable 做留一法（以其第 1 小时为 known、其余为 comparables，预测并与其真实全天比）：平均 log pinball **0.2263 vs 基线 0.4648，好 51.3%**。参数经两轮网格扫描选定（trust 0.95 / wscale 0.5）。
- 格式校验：kit 练习 case p00–p03 全部输出 VALID（23 行、小时 2–24、分位数单调、0<q≤1e9）；同 case 复跑字节一致（确定性）；单 case 远低于 8 秒。

# HALCON 依赖说明

本仓库的线稿轮廓提取模块 `src/halcon/line_to_path.py` 使用 **MVTec HALCON** 的 Python 接口。

## 为什么没有把 HALCON 放进仓库

原团队仓库里包含：

- `halcon.dll`、`halconc.dll`、`halconcpp.dll`、`hdevenginecpp.dll`
- `license/license_eval_halcon_progress_2024_07.dat`
- 约 50MB 的 `RoboArmDev.zip`

这些二进制和许可证文件不适合放入公开作品展示库：

1. HALCON 是商业软件，DLL 和许可证受 MVTec 许可约束；
2. 仓库体积会从几 MB 膨胀到上百 MB；
3. 换机器/换版本后 DLL 也不一定可用。

所以本仓库只保留源码，DLL 和许可证请在你自己有权限的环境中安装。**不要把公司的许可证文件或破解 DLL 提交到公开仓库。**

## 运行前准备

1. 安装 HALCON 23.05 Progress（或兼容版本），勾选 Python 接口；
2. 确认 Python 能 `import halcon`（HALCON 安装器会把对应 Python 版本的模块放到环境里）；
3. 激活有效许可证；
4. 安装轻量依赖：

```bash
pip install -r requirements.txt
```

## 运行

```bash
python -m src.halcon.line_to_path \
  --input examples/flower/lineart.png \
  --mirror examples/flower/mirror_halcon.png \
  --out examples/flower/path_halcon.txt \
  --sigma 5.0 --low 0.0 --high 3.0
```

参数说明：

| 参数 | 含义 |
|---|---|
| `--sigma` | `lines_gauss` 的高斯平滑系数；线宽/噪声不同需要调整 |
| `--low` / `--high` | 滞后阈值分割的低/高阈值 |
| `--mirror` | 镜像后的中间图 |
| `--out` | 轨迹点文件（Python 列表格式） |
| `--preview` | 可选 PNG 预览 |

没有 HALCON 时，可以用 `scripts/preview_path.py` 直接预览仓库里已有的路径文件；这不影响阅读和评审代码。

## 原始实现的边界

- 原始 `drawPic.py` 针对固定的线稿尺寸/线宽调过 `sigma`、`low`、`high`；换图后需要重新调参。
- 原项目用机械臂厂商 SDK 执行轨迹；本仓库只到“轨迹坐标 + 执行接口”为止，不包含硬件驱动。

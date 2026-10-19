# 团队分工与取材边界

本仓库是从团队私有仓库中整理出的**公开作品展示**，不是完整工程。整理原则：

- 以我负责的“图片/汉字 → 轨迹坐标”模块为主；
- 只引入必要的上下游文件，并在 README/本文件中标注原作者；
- 不发布公司/客户信息、HALCON 二进制或许可证、硬编码 Cookie、无关大文件；
- 不把队友的模块写成我的个人成果。

## 分支与模块

| 来源分支 | 作者/参与者 | 本仓库是否使用 | 说明 |
|---|---|---|---|
| `feature/Angeli_merge` | Jinyi（ningbojian） | 是 | 线稿 HALCON 轮廓、汉字笔顺、坐标归一化、README 整理 |
| `feature/chenxin` | Chenxin 等 | 仅演示数据 | 机械臂 IK / ArmPi / Hiwonder SDK / 执行脚本不纳入；只使用 `examples/cow/` 的轨迹和线稿作演示 |
| `feature/Yadi`、`feature/Angeli` | Dii / Yadi 等 | 仅上游接口 | 图片风格化/草图/笔顺素材；`src/vision/style_transfer.py` 标注作者 Dii |
| `feature/Mira` | qiu 等 | 否 | Canny / 超声测距等实验代码，和完整展示链路无关 |

## 演示素材出处

- `examples/flower/lineart.png`、`mirror.png`、`path.txt`：团队线稿/轨迹流程的输出。
- `examples/strokes/yong.gif`：团队分支中的 shufa-main 笔顺素材，用作输入示例。
- `examples/strokes/hua.txt`、`stroke-order-hua.gif`：仓库内用 `scripts/render_strokes_gif.py` 生成。
- `examples/cow/lineart.jpg`、`arm_path.txt`：团队执行层演示素材，用于说明“轨迹 → 机械臂”的后半段。
- `src/vision/style_transfer.py`：原作者 Dii；仅作为可选的图片 → 线稿上游模块保留。
- `docs/images/armpi-6dof.png`、`docs/images/arm-vertical-drawing.jpg`：从团队汇报 PPT 中提取的 ArmPi 整机图与垂直作画照片；已剔除人物和公司信息。

## 我的贡献（按原项目）

- HALCON 线状轮廓提取与轨迹点生成；
- 汉字笔顺 GIF 的镜像、帧差、形态学、轮廓中心提取与插值；
- 轨迹的缩放/平移、镜像坐标系适配；
- 模块合并与代码整理。

## 没有放进来的部分

- 机械臂 IK、ArmPi/Hiwonder SDK、末端执行器和真实硬件标定；
- HALCON DLL、许可证、原始 50MB 工程 ZIP；
- 原百度 GIF 爬虫（含历史 Cookie）；
- 公司 Logo、同事照片、客户数据、课程/公司内部文档。
- 团队汇报 PPT 源文件（含真实姓名，仅本地留存，未入库）。

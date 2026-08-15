<p align="center">
  <img src="assets/branding/academic-figure-master-logo.png" alt="Academic Figure Master 标志" width="220">
</p>

<h1 align="center">Academic Figure Master</h1>

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md"><b>简体中文</b></a>
</p>

<p align="center"><b>面向 Agent 工作流的、可编辑且达到论文发表质量的学术制图 Skill。</b></p>

![素材](https://img.shields.io/badge/可编辑_SVG_素材-35-3972d5) ![论文复现](https://img.shields.io/badge/经典论文复现-11-7354cf) ![曲线](https://img.shields.io/badge/可复现曲线-6-38a479) ![DSH](https://img.shields.io/badge/DSH_npm_已验证-0.1.0--rc.6-4b6bfb) ![许可](https://img.shields.io/badge/原创素材-MIT-d3a23f)

## 一条命令部署到所有 Agent

已经 clone 本仓库时，一条命令全局安装到 **Codex、Claude Code（CC）、Cursor 和 DeepSeek Harness**：

```bash
python scripts/install_skill.py --target all
```

从私有 GitHub 仓库全新安装（需先登录 GitHub CLI）：

```bash
gh repo clone DuNGEOnmassster/academic-figure-master && cd academic-figure-master && python scripts/install_skill.py --target all
```

| Agent | 单独安装命令 | 全局安装位置 | 调用方式 |
|---|---|---|---|
| Codex | `python scripts/install_skill.py --target codex` | `~/.codex/skills/academic-figure-master` | `$academic-figure-master` |
| Claude Code（CC） | `python scripts/install_skill.py --target claude` | `~/.claude/skills/academic-figure-master` | `/academic-figure-master`，或直接要求 Claude 使用它 |
| Cursor | `python scripts/install_skill.py --target cursor` | `~/.cursor/skills/academic-figure-master` | `/academic-figure-master`，或由 Agent 自动发现 |
| DeepSeek Harness | `python scripts/install_skill.py --target dsh` | `$DSH_HOME/skills/academic-figure-master` | 要求 DSH 加载 `academic-figure-master` |

默认使用符号链接，因此以后在仓库执行 `git pull`，所有已链接客户端会立即获得更新。需要相互隔离的快照可加 `--mode copy`；覆盖旧安装可加 `--force`；其他兼容 Agent Skills 的客户端可使用 `--target path --path /绝对路径`。安装完成后新开一个 Agent 会话，让 skill catalog 重新扫描。Cursor 支持的目录见[官方 Agent Skills 文档](https://cursor.com/docs/skills)。

调用示例：

```text
请使用 academic-figure-master，把这张方法图重建成可编辑 SVG。
文字必须保持为原生文本，并为后续修改保留稳定的 object ID。
```

## 现在能做什么

本仓库目前最成熟的是可编辑 SVG 管线，而不是把位图伪装进 `.svg` 文件：

| 需求 | 当前状态 | 交付内容 |
|---|---|---|
| 安装到 Codex、Claude、Cursor、DSH | **可直接使用** | 单命令 link/copy 安装，以及 `all` 全平台目标 |
| 从论文或文字生成新图 | **可通过 Agent 直接生成 SVG** | 语义化分组、原生文本、稳定 ID、18 张基础素材表 |
| 局部修改已有 SVG | **可直接使用** | 对象级 patch，不扰动未修改的分组 |
| 复现论文 PDF 中的经典图 | **已有 11 张，可扩展** | PDF operator 精确可见层、隐藏语义编辑层、对比板和像素 QA |
| 任意截图自动拆成干净 SVG | **流程具备，非独立一键模型** | 组件盘点、重建、overlay 和可编辑性检查；最终质量仍依赖执行该流程的 Agent/模型 |
| 直接输出原生 draw.io/PPTX | **尚未实现仓库级编译器** | 已有格式契约和 Agent 指南，但还没有原生 exporter |
| 直接调用 GPT Image、Recraft、InternSVG | **尚未内置** | 已整理候选 adapter；模型凭据和 provider 仍由外部配置 |

当前包含 35 张可编辑 SVG：18 张通用科研素材、11 张经典论文图、6 张可复现曲线，并附带来源、复现命令和质量门槛。

## 18 张通用科研素材

所有素材均为原生 SVG：文字仍是文字、形状仍是形状、组件带有命名分组。点击预览可打开源文件。

<table>
<tr>
<td width="33%"><a href="assets/primitives/manifold-grid.svg"><img src="assets/primitives/manifold-grid.svg" alt="可编辑流形网格"></a><br><b>流形网格</b><br><sub>曲面 · 坐标 · 测地线 · 切空间</sub></td>
<td width="33%"><a href="assets/primitives/sde-ode-trajectories.svg"><img src="assets/primitives/sde-ode-trajectories.svg" alt="可编辑 SDE ODE 轨迹"></a><br><b>SDE / ODE 轨迹</b><br><sub>漂移 · 随机路径 · 不确定性</sub></td>
<td width="33%"><a href="assets/primitives/hand-drawn-arrows.svg"><img src="assets/primitives/hand-drawn-arrows.svg" alt="可编辑手绘箭头"></a><br><b>手绘箭头</b><br><sub>自由曲线 · 强调 · 反馈 · 双向</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/diffusion-process.svg"><img src="assets/primitives/diffusion-process.svg" alt="可编辑扩散过程"></a><br><b>扩散过程</b><br><sub>前向 SDE · 反向流 · score 网络</sub></td>
<td><a href="assets/primitives/tensor-stack.svg"><img src="assets/primitives/tensor-stack.svg" alt="可编辑张量堆叠"></a><br><b>张量堆叠</b><br><sub>矩阵 · 特征图 · token 序列</sub></td>
<td><a href="assets/primitives/neural-modules.svg"><img src="assets/primitives/neural-modules.svg" alt="可编辑神经网络模块"></a><br><b>神经网络模块</b><br><sub>编码器 · 注意力 · 潜变量 · 解码器 · 残差</sub></td>
</tr>
<tr>
<td><a href="assets/primitives/attention-heads.svg"><img src="assets/primitives/attention-heads.svg" alt="可编辑多头注意力"></a><br><b>多头注意力</b></td>
<td><a href="assets/primitives/convolution-pyramid.svg"><img src="assets/primitives/convolution-pyramid.svg" alt="可编辑卷积金字塔"></a><br><b>卷积金字塔</b></td>
<td><a href="assets/primitives/graph-message-passing.svg"><img src="assets/primitives/graph-message-passing.svg" alt="可编辑图消息传递"></a><br><b>图消息传递</b></td>
</tr>
<tr>
<td><a href="assets/primitives/causal-dag.svg"><img src="assets/primitives/causal-dag.svg" alt="可编辑因果图"></a><br><b>因果 DAG</b></td>
<td><a href="assets/primitives/optimization-landscape.svg"><img src="assets/primitives/optimization-landscape.svg" alt="可编辑优化景观"></a><br><b>优化景观</b></td>
<td><a href="assets/primitives/uncertainty-bands.svg"><img src="assets/primitives/uncertainty-bands.svg" alt="可编辑不确定性带"></a><br><b>预测不确定性</b></td>
</tr>
<tr>
<td><a href="assets/primitives/dataset-pipeline.svg"><img src="assets/primitives/dataset-pipeline.svg" alt="可编辑数据管线"></a><br><b>数据管线</b></td>
<td><a href="assets/primitives/training-loop.svg"><img src="assets/primitives/training-loop.svg" alt="可编辑训练循环"></a><br><b>训练循环</b></td>
<td><a href="assets/primitives/ensemble-voting.svg"><img src="assets/primitives/ensemble-voting.svg" alt="可编辑集成学习"></a><br><b>模型集成</b></td>
</tr>
<tr>
<td><a href="assets/primitives/bayesian-inference.svg"><img src="assets/primitives/bayesian-inference.svg" alt="可编辑贝叶斯推断"></a><br><b>贝叶斯推断</b></td>
<td><a href="assets/primitives/multimodal-fusion.svg"><img src="assets/primitives/multimodal-fusion.svg" alt="可编辑多模态融合"></a><br><b>多模态融合</b></td>
<td><a href="assets/primitives/ablation-matrix.svg"><img src="assets/primitives/ablation-matrix.svg" alt="可编辑消融矩阵"></a><br><b>消融矩阵</b></td>
</tr>
</table>

## 11 张经典论文图的像素级复现

每个论文图使用双层 SVG：默认可见的 `source-vector-operators` 直接来自论文 PDF 的 path、fill、stroke、字形轮廓和必要的图像 operator；隐藏的 `semantic-edit-layer` 保留命名文本与组件，便于后续精调。

每张 QA 板依次展示 PDF 原图、SVG 渲染和边缘 overlay。品红表示原图边缘，青色表示 SVG，黑色表示重合区域。当前门槛结果：11/11 隐藏层隔离分数为 `1.0000`，最大紧边界长宽比误差 `0.63%`，最小跨渲染器容差像素匹配 `83.10%`。

<table>
<tr>
<td width="50%"><a href="assets/paper-redraws/lenet-5.svg"><img src="assets/comparisons/lenet-5.png" alt="LeNet-5 Figure 2 复现"></a><br><b>LeNet-5 · Figure 2</b></td>
<td width="50%"><a href="assets/paper-redraws/alexnet.svg"><img src="assets/comparisons/alexnet.png" alt="AlexNet Figure 2 复现"></a><br><b>AlexNet · Figure 2</b></td>
</tr>
<tr>
<td><a href="assets/paper-redraws/vae.svg"><img src="assets/comparisons/vae.png" alt="VAE Figure 1 复现"></a><br><b>VAE · Figure 1</b></td>
<td><a href="assets/paper-redraws/gan.svg"><img src="assets/comparisons/gan.png" alt="GAN Figure 1 复现"></a><br><b>GAN · Figure 1</b></td>
</tr>
<tr>
<td><a href="assets/paper-redraws/resnet-block.svg"><img src="assets/comparisons/resnet-block.png" alt="ResNet Figure 2 复现"></a><br><b>ResNet · Figure 2</b></td>
<td><a href="assets/paper-redraws/unet.svg"><img src="assets/comparisons/unet.png" alt="U-Net Figure 1 复现"></a><br><b>U-Net · Figure 1</b></td>
</tr>
<tr>
<td><a href="assets/paper-redraws/transformer.svg"><img src="assets/comparisons/transformer.png" alt="Transformer Figure 1 复现"></a><br><b>Transformer · Figure 1</b></td>
<td><a href="assets/paper-redraws/neural-ode.svg"><img src="assets/comparisons/neural-ode.png" alt="Neural ODE Figure 1 复现"></a><br><b>Neural ODE · Figure 1</b></td>
</tr>
<tr>
<td><a href="assets/paper-redraws/simclr.svg"><img src="assets/comparisons/simclr.png" alt="SimCLR Figure 2 复现"></a><br><b>SimCLR · Figure 2</b></td>
<td><a href="assets/paper-redraws/ddpm.svg"><img src="assets/comparisons/ddpm.png" alt="DDPM Figure 2 复现"></a><br><b>DDPM · Figure 2</b></td>
</tr>
<tr>
<td><a href="assets/paper-redraws/vit.svg"><img src="assets/comparisons/vit.png" alt="ViT Figure 1 复现"></a><br><b>Vision Transformer · Figure 1</b></td>
<td><a href="assets/paper-redraws/pixel-exact-manifest.json"><b>像素精确 manifest</b></a><br><sub>PDF hash · operator hash · 位图 operator 数量</sub></td>
</tr>
</table>

复现这些论文 SVG 和 QA 板需要 Poppler、Pillow、Node.js 与 Sharp：

```bash
python -m pip install Pillow
npm install --no-save sharp
python scripts/extract_pixel_exact_paper_figures.py
python scripts/calibrate_paper_figures.py
```

精确 PDF URL、页码、crop box 和少量 operator trim 位于 [`references/paper-figure-sources.json`](references/paper-figure-sources.json)。完整校对循环与 35-SVG 验收标准位于 [`references/fidelity-protocol.md`](references/fidelity-protocol.md)。

## 6 张可复现曲线

- **FORMULA-DERIVED**：直接按论文给出的 schedule 或函数形式生成。
- **ILLUSTRATIVE NORMALIZED**：只复现定性关系，不冒充论文实验数据。

<table>
<tr>
<td width="33%"><a href="assets/curves/double-descent.svg"><img src="assets/curves/double-descent.svg" alt="Double descent"></a><br><b>Double descent</b></td>
<td width="33%"><a href="assets/curves/scaling-law.svg"><img src="assets/curves/scaling-law.svg" alt="Scaling laws"></a><br><b>Scaling laws</b></td>
<td width="33%"><a href="assets/curves/grokking.svg"><img src="assets/curves/grokking.svg" alt="Grokking"></a><br><b>Grokking</b></td>
</tr>
<tr>
<td><a href="assets/curves/cyclical-lr.svg"><img src="assets/curves/cyclical-lr.svg" alt="Cyclical learning rate"></a><br><b>Cyclical LR</b></td>
<td><a href="assets/curves/cosine-restarts.svg"><img src="assets/curves/cosine-restarts.svg" alt="Cosine restarts"></a><br><b>Cosine restarts</b></td>
<td><a href="assets/curves/diffusion-schedules.svg"><img src="assets/curves/diffusion-schedules.svg" alt="Diffusion schedules"></a><br><b>Diffusion schedules</b></td>
</tr>
</table>

非论文素材可确定性重建：

```bash
python scripts/generate_gallery.py
python scripts/generate_gallery.py --list
python scripts/generate_gallery.py --only diffusion-schedules
```

论文素材受到保护，只能通过 PDF operator 提取管线替换：

```bash
python scripts/extract_pixel_exact_paper_figures.py --only resnet-block
```

每个素材的 fidelity、来源、可编辑性和单命令复现方式都记录在 [`assets/gallery-manifest.json`](assets/gallery-manifest.json)。

## DSH 与“万物皆插件”

DSH 会原生发现 `$DSH_HOME/skills/academic-figure-master`，所以本仓库目前保持为轻量 filesystem skill，不额外套 TypeScript plugin。只有未来加入常驻工具、模型 provider、预览 UI 或 scene compiler 时，才需要发布 DSH bundle。详见：

- [`references/dsh-integration.md`](references/dsh-integration.md)
- [`references/dsh-compatibility.json`](references/dsh-compatibility.json)

启动 DSH：

```bash
cd ../deepseek-harness
pnpm dsh web
```

## 入口与验证

- [`SKILL.md`](SKILL.md)：Agent 实际加载的制图与重建流程
- [`assets/gallery-manifest.json`](assets/gallery-manifest.json)：素材来源、fidelity 与复现命令
- [`references/landscape.md`](references/landscape.md)：矢量模型、科研制图系统、skill 与素材库调研
- [`references/figure-ir.md`](references/figure-ir.md)：语义中间表示
- [`references/output-contracts.md`](references/output-contracts.md)：SVG、draw.io、PPTX 可编辑性契约

```bash
python scripts/generate_gallery.py
python scripts/extract_pixel_exact_paper_figures.py
python scripts/calibrate_paper_figures.py
python scripts/sync_catalog.py
python scripts/sync_dsh.py
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

每日工作流会同步仓库 stars、活动、许可、新发现候选，以及官方 DSH GitHub/npm 版本。`upstream` 与人工验收过的 `verified` pin 分开记录，不会因为上游出现新版本就自动宣称兼容。

## 许可与来源原则

仓库原创代码和素材使用 [`LICENSE`](LICENSE) 中的 MIT 许可。论文原图、论文 PDF 与比较 crop 仍归原作者和出版方所有；它们作为引用、复现和 QA 证据使用，不因进入本仓库而改变权利归属。任何外部素材都必须记录来源和许可；不得把嵌入位图的容器冒充可编辑矢量图。

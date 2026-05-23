# 妙绘童心：简笔成画

妙绘童心是一个基于 Stable Diffusion XL 的儿童创意绘画生成项目。项目面向“用简单线稿生成完整插画”的场景：用户上传一张简笔画或草图，输入想象中的画面描述，系统会保留原始构图和轮廓，并生成更完整、更生动的卡通风格图像。

项目当前提供 Flask 后端接口，可接收 Base64 图片与文本提示词，并返回生成后的 PNG 图像。底层使用 Diffusers 加载 SDXL、T2I-Adapter、VAE 与 LoRA 权重，实现“草图结构控制 + 文本语义引导 + 风格化生成”。

## 项目特点

- 简笔画转插画：将儿童线稿、草图或简单图形转换为完整卡通图像。
- 结构保持：使用 T2I-Adapter Sketch 和 PidiNet 提取草图结构，让生成结果尽量贴合原图轮廓。
- 文本可控：通过 prompt 描述画面主体、场景和细节。
- 风格迁移：通过 LoRA 权重支持 Web Cartoon、Pixar、Japanese Cartoon 等风格。
- 接口调用：使用 Flask 暴露 HTTP API，方便接入 Web、移动端或其他前端应用。

## 技术栈

- Python 3.8
- Flask / Flask-Cors
- PyTorch
- Hugging Face Diffusers
- Stable Diffusion XL
- T2I-Adapter Sketch SDXL
- SDXL VAE fp16 fix
- LoRA
- ControlNet Aux / PidiNet
- Pillow / OpenCV / NumPy

## 核心流程

```text
用户上传简笔画
    ↓
Flask 接收 Base64 图片和 prompt
    ↓
PidiNet 提取线稿结构
    ↓
T2I-Adapter 将线稿作为结构控制条件
    ↓
Stable Diffusion XL 根据 prompt 生成图像
    ↓
加载 LoRA 强化卡通风格
    ↓
返回生成后的 PNG 图片
```

## 效果示例

下面展示了一组“生成前草图 -> 生成后插画”的效果。输入是一张简单的猫头鹰线稿，模型在保留大眼睛、尖嘴、翅膀和站立姿态的基础上，补充了完整的卡通角色造型、森林背景和明亮色彩。

| 生成前草图 | 生成后效果 |
| --- | --- |
| <img src="assets/examples/input-sketch.png" alt="生成前草图" width="360"> | <img src="assets/examples/generated-owl.jpg" alt="生成后效果" width="360"> |

## 目录说明

```text
.
├── apistart.py                       # 最终 Flask API 服务入口
├── img2img.py                        # 最终图生图生成流程
├── assets/examples/                  # README 展示图片
├── requirements.txt
└── README.md
```

本地目录中还保留了一些早期实验脚本和模型目录，例如 `operate/`、`main_t2i_sketch.py`、`switchstyle.py`、`useLora.py`、`lora/`、`sdxl-vae-fp16-fix/`、`t2i-adapter-sketch-sdxl-1.0/` 等。这些文件用于本地追溯和运行备份，默认已被 `.gitignore` 忽略，不会上传到 GitHub。

## 模型文件下载

为了避免 GitHub 仓库过大，模型权重不会提交到仓库。运行前需要把下面的目录放到项目根目录，目录名需要和代码中的相对路径保持一致：

```text
stable-diffusion-xl-base-1.0/
Annotators/
lora/
sdxl-vae-fp16-fix/
t2i-adapter-sketch-sdxl-1.0/
```

推荐使用 Hugging Face CLI 下载公开模型：

```bash
pip install -U huggingface_hub

huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0 \
  --local-dir stable-diffusion-xl-base-1.0

huggingface-cli download TencentARC/t2i-adapter-sketch-sdxl-1.0 \
  --local-dir t2i-adapter-sketch-sdxl-1.0

huggingface-cli download madebyollin/sdxl-vae-fp16-fix \
  --local-dir sdxl-vae-fp16-fix

huggingface-cli download lllyasviel/Annotators \
  --local-dir Annotators
```

LoRA 风格权重需要单独准备。当前最终脚本 `img2img.py` 默认加载：

```text
lora/Web_Cartoon.safetensors
```

如果你有原服务器访问权限，可以从原项目复制：

```bash
mkdir -p lora
scp hdu@117:/data/cyy/aigc/lora/Web_Cartoon.safetensors lora/
```

如果使用自己的 LoRA，请把文件放到 `lora/` 目录，并在 `img2img.py` 中修改 `weight_name`。所有模型目录和 LoRA 权重都已被 `.gitignore` 忽略，不会被提交到 GitHub。

可选的深度控制脚本 `operate/main_t2i_depth.py` 还会用到下面两个目录，但它们不是当前最终 Flask 服务的必需项：

```bash
huggingface-cli download TencentARC/t2i-adapter-depth-midas-sdxl-1.0 \
  --local-dir t2i-adapter-depth-midas-sdxl-1.0

huggingface-cli download TencentARC/t2iadapter-aux-models \
  --local-dir t2iadapter-aux-models
```

## 环境安装

建议使用 Conda 或 venv 创建独立环境：

```bash
conda create -n miaohui python=3.8
conda activate miaohui
pip install -r requirements.txt
```

如果使用 CUDA，需要根据本机显卡和 CUDA 版本安装匹配的 PyTorch。原服务器环境使用的是：

```text
Python 3.8.19
torch 2.2.2 + cu118
diffusers 0.27.2
transformers 4.46.3
xformers 0.0.25.post1
controlnet_aux 0.0.7
```

## 启动服务

确认模型目录已经放到项目根目录后，启动 Flask 服务：

```bash
python apistart.py
```

默认监听：

```text
http://0.0.0.0:5000
```

生成接口：

```text
POST /generate_image
```

请求 JSON 示例：

```json
{
  "prompt": "a cute duck walking in a colorful forest",
  "style": "webcartoon",
  "image": "base64 encoded image"
}
```

返回内容为 PNG 图片二进制流。

## 最终运行脚本

当前整理后的 GitHub 版本只保留两个核心脚本：

```text
apistart.py -> Flask 后端入口，接收 Base64 图片、prompt 和 style 参数
img2img.py  -> SDXL + T2I-Adapter + PidiNet + LoRA 的图生图生成流程
```

`apistart.py` 暴露 `/generate_image` 接口，解析请求中的 `image` 字段并转换为 PIL 图像，然后调用 `img2img.py` 中的 `runimg` 函数生成图片。旧版测试脚本、单独文生图脚本和多风格实验脚本保留在本地，但不作为最终 GitHub 版本提交。

## 注意事项

- 项目需要 NVIDIA GPU 才能较流畅运行。
- SDXL 和相关 adapter/LoRA 权重体积较大，不建议直接提交到 GitHub。
- `operate/main_t2i_depth.py` 引用了 `t2i-adapter-depth-midas-sdxl-1.0/`，当前本地精简迁移版本未包含该目录，使用深度控制功能前需要单独补齐。
- 部分脚本中存在固定相对路径，请尽量保持模型目录名称和 README 中一致。

## 项目定位

妙绘童心希望降低儿童创意表达的门槛：孩子只需要画出简单线条，系统就可以将它扩展为更完整、更有想象力的插画。它不是替代绘画，而是把“随手一画”变成可以继续讲故事、做绘本、做互动展示的视觉起点。

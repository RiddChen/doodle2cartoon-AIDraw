from diffusers import StableDiffusionXLAdapterPipeline, T2IAdapter, EulerAncestralDiscreteScheduler, AutoencoderKL
from diffusers.utils import load_image, make_image_grid
from controlnet_aux.pidi import PidiNetDetector
import torch


def runimg(img, prompt,style):
    # load adapter
    adapter = T2IAdapter.from_pretrained(
        "t2i-adapter-sketch-sdxl-1.0", torch_dtype=torch.float16, varient="fp16"
    ).to("cuda")

    # load euler_a scheduler
    model_id = 'stable-diffusion-xl-base-1.0'
    euler_a = EulerAncestralDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
    vae = AutoencoderKL.from_pretrained("sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
        model_id,
        vae=vae,
        adapter=adapter,
        scheduler=euler_a,
        torch_dtype=torch.float16,
        variant="fp16",
    ).to("cuda")
    pipe.enable_xformers_memory_efficient_attention()

    pidinet = PidiNetDetector.from_pretrained("Annotators").to("cuda")

    pipe.load_lora_weights("lora", weight_name="Web_Cartoon.safetensors", adapter_name="webcartoon")
    lora_scale = 0.9

    image = load_image(img)  # 使用传递过来的图像文件路径

    image = pidinet(
        image, detect_resolution=1024, image_resolution=1024, apply_filter=True
    )

    # generator = torch.Generator(device="cuda").manual_seed(0)
    generator = torch.Generator(device="cuda")

    original_prompt = "web_cartoon,positive,4k, highly detailed"  # 原有的 prompt
    original_negative_prompt = "tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, blurry, bad anatomy, blurred, watermark, signature, cut off, draft, worst quality, low quality:1.4, extra limbs, bad anatomy, multicolored fur, feral, extra ears, extra eyes, extra eyebrows"  # 原有的 negative_prompt

    # 将传递过来的 prompt 插入到初始 prompt 的前面
    prompt = f"{prompt}, {original_prompt}"
    print('prompt:',prompt)

    gen_images = pipe(
        prompt=prompt,
        negative_prompt=original_negative_prompt,
        image=image,
        num_inference_steps=20,
        cross_attention_kwargs={"scale": lora_scale},
        generator=generator,
        adapter_conditioning_scale=0.8,
        guidance_scale=5,
        adapter_conditioning_factor=0.8,
    ).images[0]

    return gen_images

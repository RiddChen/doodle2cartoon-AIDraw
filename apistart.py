from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import base64
from io import BytesIO
from img2img import runimg
# from switchstyle import runimg

app = Flask(__name__)
CORS(app)

@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        # 解析 POST 请求中的 JSON 数据
        request_data = request.json
        prompt = request_data.get('prompt')
        style = request_data.get('style')
        base64_image = request_data.get('image')

        if not base64_image:
            return jsonify({"error": "No image provided"}), 400

        # 确保 base64 字符串长度是 4 的倍数
        missing_padding = len(base64_image) % 4
        if missing_padding:
            base64_image += '=' * (4 - missing_padding)

        # 解码 base64 图片并转换为 PIL 图像对象
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        # 调用 runimg 函数生成图像
        generated_image = runimg(image, prompt, style)

        # 将生成的图像以二进制形式直接返回给调用方
        buffered = BytesIO()
        generated_image.save(buffered, format="PNG")
        buffered.seek(0)

        return send_file(buffered, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

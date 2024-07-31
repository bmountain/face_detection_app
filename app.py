import uuid, os, cv2
from io import BytesIO
from PIL import Image
from flask import Flask, Response, session, request, render_template, redirect, url_for
from yunet_camera import Video

# 画像保存フォルダ
IMAGE_DIR = "images"
# フォルダ作成
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

app=Flask(__name__)

# secret_keyをランダムに生成
app.secret_key = str(uuid.uuid4())

# /にアクセスするとindex.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')

# 画像のアップロード
@app.route('/upload', methods=["POST"])
def upload():
    # secret_keyからファイル名を作成
    name = app.secret_key + '.png'
    # 画像のパスを作る
    path = os.path.join(IMAGE_DIR, name)
    # セッションにパスとファイル名を保存
    session['path'] = path
    # アップロードされた画像をバイトとして読み込む
    img = request.files.get('img').read()
    # 画像をアルファチャネル付きで読み込みリサイズして保存
    img = Image.open(BytesIO(img)).convert('RGBA')
    img = img.resize((500, 500 * img.height // img.width))
    img.save(format ='PNG', optimize=True, quality=95, fp = path)
    # 表示ページへ
    return render_template('video.html')

# 表示する画像を含むHTTP responseを逐次出力するジェネレータ
def gen(camera):
    while True:
        frame=camera.get_frame_overlay()
        yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')

# /videoにアクセスするとResponse(gen(Video))を返す
@app.route('/video')
def video():
    # 画像をロード
    path = session['path']
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    # 画像ファイルを削除
    os.remove(path)
    video = Video(img)
    return Response(gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8000)

import uuid
from io import BytesIO
from PIL import Image
import os
from os.path import join, dirname, realpath
from flask import Flask, redirect, render_template, request, url_for, session

app=Flask(__name__)
# secret_keyがsessionの使用に必要
app.secret_key = 'usr'


# /にアクセスするとindex.htmlを返す
@app.route('/')
def index():
    return render_template('index.html')
        
# 画像ののアップロードを行う
@app.route('/upload', methods=["POST"])
def upload():
    # アップロードされた画像をバイトとして読み込む
    img = request.files.get('img').read()
    # ファイル名をランダムに付ける
    name = str(uuid.uuid4()) + '.png'
    # 画像のパスを得る
    path = os.path.join('temp', name)
    # セッションにパスとファイル名を保存
    session['path'] = path
    session['name'] = name
    # 画像を保存
    img = Image.open(BytesIO(img))
    img.thumbnail((500,500))
    img.save(optimize=True, quality=40, fp = path)
    # 表示サービスにリダイレクト
    return redirect(url_for('view'))

# アップロードされた画像を表示
@app.route('/view')
def view():
    # セッションからパスとファイル名を取得
    path = session.get('path')
    name = session.get('name')
    print('path:', path)
    print('name:', name)
    # htmlに変数を渡してレンダリング
    return render_template('view.html', path = path)

app.run(debug=True)
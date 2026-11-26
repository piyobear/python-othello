# Pythonオセロ（iPhone対応Webアプリ）

このアプリはPython + Streamlitで作った2人対戦オセロです。
iPhoneのSafariから遊ぶには、Streamlit対応のホスティング先に公開します。

## いちばん簡単な公開方法：Streamlit Community Cloud

1. GitHubに新しいリポジトリを作成
2. `app.py` と `requirements.txt` をアップロード
3. https://share.streamlit.io/ にアクセスしてGitHubでログイン
4. `Create app` からリポジトリ、`app.py` を選んでDeploy
5. 発行されたURLをiPhoneのSafariで開く
6. Safariの共有メニューから「ホーム画面に追加」するとアプリ風に使えます

## PCで試す場合

```bash
pip install -r requirements.txt
streamlit run app.py
```

同じWi-Fi内のiPhoneから試す場合は、PC側で次のように起動し、
PCのローカルIPアドレスとポート8501をSafariで開きます。

```bash
streamlit run app.py --server.address 0.0.0.0
```

この版は同じ画面で黒白が交互に遊ぶ2人対戦です。CPU対戦はまだ入れていません。

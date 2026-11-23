# devin-app-deploy-example

## FastAPI でスライドを配信する

[uv](https://docs.astral.sh/uv/) をインストールし、リポジトリのルートで実行します。

```sh
PORT=8000 uv run app.py
```

ローカルでは <http://localhost:8000/> でスライドを開けます。
Devin Apps で動かす場合は、Devin に上記のコマンドで起動し、ポート `8000` を配信するよう依頼します。
待ち受けアドレスは `HOST`（既定値 `0.0.0.0`）、ポートは `PORT`（既定値 `8000`）で変更できます。

## スライドごとの OGP

SNS で個別のスライドを共有するには、`/#/1/1` ではなく `/share/1/1` を使います。
`/share/{h}/{v}` の `h` と `v` は Reveal.js の 0 始まりの横・縦インデックスです。
共有ページは OGP メタタグを返し、ブラウザでは対象スライドへ移動します。
公開 URL がリクエストの URL と異なる場合は、`BASE_URL=https://slides.example.com` のように指定します。

サインインが必要な Devin Apps では未認証のクローラーに 401 が返るため、SNS のプレビュー確認には、共有ページと PNG の両方へ未認証でアクセスできる公開ホスティングを使ってください。

### 画像を再生成する

スライドを更新したら、Playwright の Chromium を使って画像を再生成し、`og/` の PNG をスライドと一緒にコミットします。
スクリプトはスライドを一時的にローカル配信するため、FastAPI の起動は不要です。

```sh
uv run --with playwright playwright install chromium
uv run scripts/generate_og.py
```

### テスト

```sh
uv run --with 'fastapi>=0.138.0' --with uvicorn --with pytest --with httpx python -m pytest
```

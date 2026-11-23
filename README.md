# devin-app-deploy-example

## FastAPI でスライドを配信する

[uv](https://docs.astral.sh/uv/) をインストールし、リポジトリのルートで実行します。

```sh
PORT=8000 uv run app.py
```

ローカルでは <http://localhost:8000/> でスライドを開けます。
Devin Apps で動かす場合は、Devin に上記のコマンドで起動し、ポート `8000` を配信するよう依頼します。
待ち受けアドレスは `HOST`（既定値 `0.0.0.0`）、ポートは `PORT`（既定値 `8000`）で変更できます。

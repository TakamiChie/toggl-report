# TogglReport

Toggl APIを使って、先週と先々週の情報からレポートを作成するプログラム。
ほとんどBing Copilotにて作成。ただし、そのままでは全然動かなかったので、一部調整している。

* [Toggl APIの利用について](https://takamichie.notion.site/Toggl-API-5204f207c930427199f52410ff03f50f)
* [当時の会話ログ](https://sl.bing.net/g38o6qFc3SC)

そのうちAzure Functionsなどにデプロイして、毎週土曜日にメールが届くような感じにしてみたい。

## つかいかた
1. `.env.sample`ファイルを`.env`にリネームし、APIキーとワークスペースのIDを設定する。
2. `pipenv install`を実行する
3. `pipenv run python toggl-report.py`を実行する

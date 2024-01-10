# iManage
石川研 マシン管理システムデータベース(B4研修)

## テスト環境の実行

以下を順に行ってください．
  - `docker-compose up -d db && sleep 20 && docker-compose up`
    - 起動順序を制御する必要があるけど、面倒なのである程度待つ or やり直すと正常に動く（本当は`db`が立ち上がるまで`web`側は待機するorエラー処理する必要がある。）
  - 実行中のコンテナに入って（`docker-compose exec web bash`）`export DJANGO_SETTINGS_MODULE=im_site.settings  && python3 insert-data.py` を実行する
  - 手元のPCで`http://localhost:8000/imapp/`にアクセス
  - （遊び終わったら`ctrl+C`）`docker-compose down`

## 管理ユーザーの設定

（`web`コンテナ内で）`python manage.py createsuperuser`を実行し、適当に入力する

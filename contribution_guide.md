1. issueを作成
```
# 概要
変更する目的と端的な内容

# 設計
実装までのタスクの一覧 (チェックリスト)

# 変更予定
編集・追加・削除する予定のファイルなど

# 補足
伝えておきたいこと
```

2. ブランチ`issues/#<issue_No>[/<topic_name>]`を作成
    - `issues/#10`
    - `issues/#10/log_save_function` (一つのissueに対して複数のMerge Requestを設けるとき)
3. `git commit --allow-empty -m "[WIP]#<issue_No>"`で空コミットを作成
4. `git push`
5. マージリクエスト`[WIP]#<issue_No>[/<topic_name>]:<merge_request_title>`を作成
```
# tasks
issueに書かれたタスクのうち、どのタスクをこのマージリクエストで解決するか
```

6. レビュー
    - マージリクエストへのコメント
7. issueの[設計]に書いたタスクの完了ごとにプッシュ
8. 実装が完了したらマージリクエストから[WIP]を取ってレビュー依頼
10. レビュワーは問題あれば修正依頼、なければマージリクエスト承認
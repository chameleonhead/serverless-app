# サーバーレスアプリケーション

仕様を実行するためにはプロジェクトのルートフォルダ配下の `gauge` フォルダで以下のコマンドを実行する。

```bash
gauge run specs
```

以下のステップはすべてのシナリオで共通する

* アプリケーションにアクセスする
* ユーザー "admin@example.com" でログインする
* 初期ページが表示される

## 新規に連絡先を追加し変更する

* 新規に連絡先を追加する
* "No Name" という連絡先がサイドバーに表示される
* サイドバーから "No Name" という連絡先を選択する
* "No Name" という連絡先の詳細画面が表示される
* 詳細画面で編集ボタンを押下する
* すべて空欄の編集画面が表示される
* First "Taro"、Last "Tanaka"、Twitter "@tanakataro"、アバターURL "https://robohash.org/abcde.png?size=200x200"、Notes "Notes\nNotes" として登録する
* "Taro Tanaka" という連絡先の詳細画面が表示される
* 詳細画面には Twitter "@tanakataro"、アバターURL "https://robohash.org/abcde.png?size=200x200"、Notes "Notes\nNotes" が表示されている

## 連絡先を検索する

* 以下の連絡先を追加する

   |First  |Last     |Twitter          |
   |-------|---------|-----------------|
   |Taro   |Yamada   |@taroyamada      |
   |Jiro   |Tanaka   |@jirotanaka      |
   |Saburo |Sato     |@saburosato      |
   |Hanako |Kimura   |@hanakokimura    |
   |Sachiko|Takahashi|@sachikotakahashi|

* 以下の連絡先がサイドバーに表示されること

   |Name             |
   |-----------------|
   |Taro Yamada      |
   |Jiro Tanaka      |
   |Saburo Sato      |
   |Hanako Kimura    |
   |Sachiko Takahashi|

* "Taro" を検索する
* 以下の連絡先がサイドバーに表示されること

   |Name       |
   |-----------|
   |Taro Yamada|

* "Taro Yamada" を削除する
* 以下の連絡先がサイドバーに表示されること

   |Name             |
   |-----------------|
   |Jiro Tanaka      |
   |Saburo Sato      |
   |Hanako Kimura    |
   |Sachiko Takahashi|

___

以下のタスクをすべてのシナリオの後に実行する

* すべての連絡先を削除する

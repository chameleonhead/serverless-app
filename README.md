# serverless-app

## CodePipeline の作成

AWS の認証情報が取得できる状態で以下を実行する。

```
cd pipeline
terraform init
terraform apply
```

上記で CodePipeline を作成後、CodePipeline （デベロッパー用ツール）の設定から接続を変更し、GitHub との接続を完成させる必要がある。（その際は「新しいアプリをインストールする」ボタンを押下する必要があるので注意。理由は不明だが試したときはそのように設定する必要があった。）

## Terraform のローカルでの実行方法

リソースには接頭辞として変数 `env_code` に設定された文字列を付与して環境を分けている。
ローカル環境で実行する場合は以下のようにして変数を上書きする。

```
echo -e "variable \"env_code\" {\n  default = \"naga\"\n}" > terraform/_override.tf
```

変数を上書きしたあとは以下のコマンドでデプロイを実行する。（デプロイ実行前に各プロジェクトのビルドをしておく必要があるので注意。）

```
cd terraform
terraform init
terraform apply
```

## CodeBuild のローカルでの確認方法

環境変数ファイル `codebuild_local.env` を作成する

```
S3_BUCKET_TFSTATE=dev-s3-tfstate-bucket-xxx
S3_KEY_TFSTATE=serverless-app/terraform.tfstate
```

ローカル実行用のファイルをダウンロードして実行する

```
wget https://raw.githubusercontent.com/aws/aws-codebuild-docker-images/master/local_builds/codebuild_build.sh
chmod +x codebuild_build.sh
./codebuild_build.sh -c -i public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0 -s $(pwd) -a ./artifacts -e codebuild_local.env
```

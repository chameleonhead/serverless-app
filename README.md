# serverless-app


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

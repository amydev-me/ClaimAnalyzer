resource "aws_lambda_function" "upload_handler" {
  function_name = "${var.project_name}-upload-handler"
  handler       = "upload_handler.lambda_handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_exec.arn

  filename         = var.upload_handler_zip_path
  source_code_hash = filebase64sha256(var.upload_handler_zip_path)


  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.app_bucket.bucket
    }
  }

  timeout     = 30
  memory_size = 128

  tags = {
    Name = "${var.project_name}-upload-handler"
  }
}
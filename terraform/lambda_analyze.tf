resource "aws_lambda_function" "submission_analyzer" {
  function_name    = "${var.project_name}-submission-analyzer"
  handler          = "submission_analyzer.lambda_handler"
  runtime          = "python3.12"
  role            = aws_iam_role.lambda_exec.arn 

  filename        = "../artifacts/submission_analyzer.zip"
  source_code_hash = filebase64sha256("../artifacts/submission_analyzer.zip")
  
  environment {
    variables = {
      OPENAI_API_KEY = var.openai_api_key
      BUCKET_NAME    = aws_s3_bucket.app_bucket.bucket
    }
  }

  timeout     = 60
  memory_size = 1024

  tags = {
    Name = "${var.project_name}-submission-analyzer"
  }
}
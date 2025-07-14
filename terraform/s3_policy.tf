# s3_policy.tf
resource "aws_s3_bucket_policy" "allow_lambda_access" {
  bucket = aws_s3_bucket.app_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowLambdaS3Access",
        Effect = "Allow",
        Principal = {
          AWS = aws_iam_role.lambda_exec.arn
        },
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        Resource = [
          "${aws_s3_bucket.app_bucket.arn}/*"
        ]
      },
      {
        Sid    = "AllowLambdaListBucket",
        Effect = "Allow",
        Principal = {
          AWS = aws_iam_role.lambda_exec.arn
        },
        Action = [
          "s3:ListBucket"
        ],
        Resource = aws_s3_bucket.app_bucket.arn
      }
    ]
  })
}
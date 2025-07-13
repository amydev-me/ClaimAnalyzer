variable "aws_region" {
  description = "The AWS region to deploy resources to."
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "A prefix for all resources."
  type        = string
  default     = "claim-analyzer"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "openai_api_key" {
  description = "API key for OpenAI GPT-4o (use TF_VAR_openai_api_key env var for demo, AWS Parameter Store for production)"
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "Name for the S3 bucket (leave empty for auto-generated unique name)"
  type        = string
  default     = ""
}

variable "allowed_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = ["*"]  # Change to your domain in production
} 

variable "upload_handler_zip_path" {
  description = "Path to upload handler zip file"
  type        = string
  default     = "../artifacts/upload_handler.zip"
}
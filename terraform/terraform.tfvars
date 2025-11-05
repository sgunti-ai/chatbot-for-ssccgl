# Copy this file to terraform.tfvars and update values

# Environment
environment = "dev"
aws_region  = "us-east-1"

# ECS Configuration
backend_cpu    = 512
backend_memory = 1024

frontend_cpu    = 256  
frontend_memory = 512

# Auto Scaling
backend_desired_count  = 1
backend_min_capacity   = 1
backend_max_capacity   = 3
frontend_desired_count = 1

# RDS Configuration (set to true if you need database)
create_rds = false

# S3 Bucket
s3_bucket_name = "ssc-question-papers-12345"

# Tags
common_tags = {
  Project     = "ssc-rag-chatbot"
  Environment = "dev"
  ManagedBy   = "terraform"
  Owner       = "your-team"
}
# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# ECR Outputs
output "backend_ecr_repository_url" {
  description = "URL of the backend ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_ecr_repository_url" {
  description = "URL of the frontend ECR repository"
  value       = aws_ecr_repository.frontend.repository_url
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

# S3 Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket for question papers"
  value       = aws_s3_bucket.question_papers.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.question_papers.arn
}

# ALB Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "backend_url" {
  description = "URL for the backend API"
  value       = "http://${aws_lb.main.dns_name}:8000"
}

output "frontend_url" {
  description = "URL for the frontend application"
  value       = "http://${aws_lb.main.dns_name}"
}

# Security Group Outputs
output "alb_security_group_id" {
  description = "Security group ID of the ALB"
  value       = aws_security_group.alb.id
}

output "backend_security_group_id" {
  description = "Security group ID for backend tasks"
  value       = aws_security_group.backend.id
}

output "frontend_security_group_id" {
  description = "Security group ID for frontend tasks"
  value       = aws_security_group.frontend.id
}

# IAM Outputs
output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

# CloudWatch Outputs
output "backend_log_group_name" {
  description = "Name of the backend CloudWatch log group"
  value       = aws_cloudwatch_log_group.backend.name
}

output "frontend_log_group_name" {
  description = "Name of the frontend CloudWatch log group"
  value       = aws_cloudwatch_log_group.frontend.name
}

# Deployment Instructions Output
output "deployment_instructions" {
  description = "Instructions for deploying the application"
  value = <<EOT

🎉 SSC RAG Infrastructure deployed successfully!

📋 Next Steps:

1. 🐳 Build and push Docker images:
   Backend:
   aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.backend.repository_url}
   docker build -t ${aws_ecr_repository.backend.repository_url}:latest ./backend
   docker push ${aws_ecr_repository.backend.repository_url}:latest

   Frontend:
   docker build -t ${aws_ecr_repository.frontend.repository_url}:latest ./frontend  
   docker push ${aws_ecr_repository.frontend.repository_url}:latest

2. 🌐 Access your application URLs:
   Frontend: http://${aws_lb.main.dns_name}
   Backend API: http://${aws_lb.main.dns_name}:8000
   API Documentation: http://${aws_lb.main.dns_name}:8000/docs

3. 📁 Upload question papers to S3:
   aws s3 cp your-file.pdf s3://${aws_s3_bucket.question_papers.bucket}/

🔧 Configuration:
- Environment: ${var.environment}
- Region: ${var.aws_region}
- VPC: ${aws_vpc.main.id}
- ECS Cluster: ${aws_ecs_cluster.main.name}

EOT
}
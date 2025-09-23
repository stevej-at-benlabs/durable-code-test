# AWS Deployment Infrastructure - PR Breakdown

## Overview
This document breaks down the AWS deployment setup into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward production deployment
- Revertible if needed

---

## PR1: Terraform Foundation and AWS Provider Setup

### Context
Establish the Terraform infrastructure foundation with AWS provider configuration, state management, and basic networking setup. This PR creates the groundwork for all subsequent infrastructure.

### Files to Create/Modify
```
infra/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── networking.tf
├── environments/
│   ├── dev.tfvars
│   └── .gitignore
└── README.md
```

### Implementation Steps
1. **Set up Terraform backend for state management**
   ```hcl
   # main.tf
   terraform {
     required_version = ">= 1.0"
     backend "s3" {
       bucket = "durable-code-terraform-state"
       key    = "infrastructure/terraform.tfstate"
       region = "us-west-2"
     }
   }
   ```

2. **Configure AWS Provider**
   ```hcl
   provider "aws" {
     region = var.aws_region
     default_tags {
       tags = {
         Project     = "durable-code-test"
         Environment = var.environment
         ManagedBy   = "terraform"
       }
     }
   }
   ```

3. **Create VPC and networking resources**
   - VPC with public/private subnets
   - Internet Gateway
   - NAT Gateway for private subnets
   - Security groups for ALB and ECS

### Testing
- Run `terraform init` successfully
- Run `terraform plan` with no errors
- Validate VPC creation in AWS Console

### Success Criteria
- [ ] Terraform state backend configured
- [ ] VPC and subnets created
- [ ] Security groups defined
- [ ] All resources properly tagged

---

## PR2: ECR Repositories and Container Registry Setup

### Context
Create Elastic Container Registry (ECR) repositories for storing Docker images. Set up lifecycle policies to manage image retention and reduce storage costs.

### Files to Create/Modify
```
infra/terraform/
├── ecr.tf
└── variables.tf (update)
```

### Implementation Steps
1. **Create ECR repositories**
   ```hcl
   # ecr.tf
   resource "aws_ecr_repository" "backend" {
     name = "${var.project_name}-backend"
     image_scanning_configuration {
       scan_on_push = true
     }
   }

   resource "aws_ecr_repository" "frontend" {
     name = "${var.project_name}-frontend"
     image_scanning_configuration {
       scan_on_push = true
     }
   }
   ```

2. **Add lifecycle policies**
   - Keep last 10 images
   - Remove untagged images after 7 days

3. **Create push/pull policies**
   - Allow GitHub Actions to push
   - Allow ECS to pull

### Testing
- Manually push a test image to ECR
- Verify image scanning works
- Check lifecycle policy application

### Success Criteria
- [ ] ECR repositories created
- [ ] Lifecycle policies active
- [ ] Image scanning enabled
- [ ] Permissions configured correctly

---

## PR3: ECS Cluster and Fargate Service Configuration

### Context
Set up the ECS cluster with Fargate launch type, task definitions for both frontend and backend services, and service configurations with proper health checks.

### Files to Create/Modify
```
infra/terraform/
├── ecs.tf
├── iam.tf
└── task-definitions/
    ├── backend.json
    └── frontend.json
```

### Implementation Steps
1. **Create ECS Cluster**
   ```hcl
   # ecs.tf
   resource "aws_ecs_cluster" "main" {
     name = "${var.project_name}-cluster"

     setting {
       name  = "containerInsights"
       value = "enabled"
     }
   }
   ```

2. **Define Task Definitions**
   - Backend: 512 CPU, 1024 Memory
   - Frontend: 256 CPU, 512 Memory
   - Environment variables from Parameter Store

3. **Create ECS Services**
   - Desired count: 2 for high availability
   - Deployment configuration for rolling updates
   - Health check grace period

4. **Set up IAM roles**
   - Task execution role
   - Task role for application permissions

### Testing
- Deploy sample containers to ECS
- Verify health checks pass
- Test container logs in CloudWatch

### Success Criteria
- [ ] ECS cluster operational
- [ ] Task definitions valid
- [ ] Services running with desired count
- [ ] CloudWatch logs configured

---

## PR4: Application Load Balancer and DNS Configuration

### Context
Configure the Application Load Balancer (ALB) for routing traffic to ECS services, set up target groups with health checks, and configure Route53 for DNS management.

### Files to Create/Modify
```
infra/terraform/
├── alb.tf
├── route53.tf
└── acm.tf
```

### Implementation Steps
1. **Create Application Load Balancer**
   ```hcl
   # alb.tf
   resource "aws_lb" "main" {
     name               = "${var.project_name}-alb"
     internal           = false
     load_balancer_type = "application"
     security_groups    = [aws_security_group.alb.id]
     subnets           = aws_subnet.public[*].id
   }
   ```

2. **Configure Target Groups**
   - Backend: Port 8000, health check on /health
   - Frontend: Port 3000, health check on /

3. **Set up SSL/TLS**
   - Request ACM certificate
   - Configure HTTPS listener
   - Redirect HTTP to HTTPS

4. **Configure Route53** (if domain available)
   - Create hosted zone
   - Add A record for ALB

### Testing
- Access application via ALB DNS
- Verify SSL certificate works
- Test health check endpoints

### Success Criteria
- [ ] ALB accessible from internet
- [ ] HTTPS working with valid certificate
- [ ] Target groups healthy
- [ ] DNS resolution working (if configured)

---

## PR5: GitHub Actions CI/CD Pipeline

### Context
Implement continuous integration and deployment using GitHub Actions with OIDC for secure, passwordless AWS authentication. Automate the build, test, and deployment process.

### Files to Create/Modify
```
.github/workflows/
├── deploy.yml
├── build-and-test.yml
infra/terraform/
├── iam.tf (update for OIDC)
```

### Implementation Steps
1. **Configure GitHub OIDC Provider**
   ```hcl
   # iam.tf
   resource "aws_iam_openid_connect_provider" "github" {
     url = "https://token.actions.githubusercontent.com"
     client_id_list = ["sts.amazonaws.com"]
     thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
   }
   ```

2. **Create GitHub Actions Role**
   - Trust relationship with GitHub
   - Permissions for ECR push and ECS deploy

3. **Build and Test Workflow**
   ```yaml
   # .github/workflows/build-and-test.yml
   name: Build and Test
   on:
     pull_request:
     push:
       branches: [main]
   ```

4. **Deploy Workflow**
   - Build and push to ECR
   - Update ECS task definition
   - Wait for deployment completion

### Testing
- Create test PR to trigger build
- Verify OIDC authentication works
- Test full deployment pipeline

### Success Criteria
- [ ] OIDC authentication configured
- [ ] Build workflow passes
- [ ] Images pushed to ECR
- [ ] ECS deployment successful

---

## PR6: Monitoring, Alerting, and Observability

### Context
Set up comprehensive monitoring using CloudWatch, configure alerts for critical metrics, and implement logging aggregation for debugging and troubleshooting.

### Files to Create/Modify
```
infra/terraform/
├── cloudwatch.tf
├── sns.tf
```

### Implementation Steps
1. **Configure CloudWatch Dashboards**
   - ECS service metrics
   - ALB request metrics
   - Container resource utilization

2. **Set up CloudWatch Alarms**
   ```hcl
   # cloudwatch.tf
   resource "aws_cloudwatch_metric_alarm" "high_cpu" {
     alarm_name          = "${var.project_name}-high-cpu"
     comparison_operator = "GreaterThanThreshold"
     evaluation_periods  = "2"
     metric_name        = "CPUUtilization"
     threshold          = "80"
   }
   ```

3. **Configure SNS for Notifications**
   - Email notifications for alarms
   - Slack integration (optional)

4. **Set up Log Groups**
   - Application logs
   - ALB access logs
   - Log retention policies

### Testing
- Trigger test alarm
- Verify notifications received
- Check dashboard displays correctly

### Success Criteria
- [ ] Dashboards displaying metrics
- [ ] Alarms configured and tested
- [ ] Notifications working
- [ ] Logs aggregated and searchable

---

## PR7: Security Hardening and Compliance

### Context
Implement security best practices including secrets management, WAF configuration, security scanning, and compliance controls.

### Files to Create/Modify
```
infra/terraform/
├── secrets.tf
├── waf.tf
├── security-scanning.tf
```

### Implementation Steps
1. **Secrets Management with Parameter Store**
   ```hcl
   # secrets.tf
   resource "aws_ssm_parameter" "api_key" {
     name  = "/${var.environment}/${var.project_name}/api_key"
     type  = "SecureString"
     value = var.api_key
   }
   ```

2. **Configure AWS WAF** (optional)
   - Rate limiting rules
   - IP filtering
   - Common attack protection

3. **Enable Security Hub**
   - AWS Foundational Security Best Practices
   - CIS AWS Foundations Benchmark

4. **Container Security**
   - Enable ECR image scanning
   - Runtime security with GuardDuty

### Testing
- Run security scan on infrastructure
- Test secret rotation
- Verify WAF rules (if implemented)

### Success Criteria
- [ ] Secrets stored securely
- [ ] Security scanning enabled
- [ ] Compliance checks passing
- [ ] No hardcoded credentials

---

## PR8: Cost Optimization and Auto-scaling

### Context
Implement cost optimization strategies including auto-scaling, spot instances for non-production environments, and resource right-sizing based on metrics.

### Files to Create/Modify
```
infra/terraform/
├── autoscaling.tf
├── cost-optimization.tf
```

### Implementation Steps
1. **Configure Auto-scaling**
   ```hcl
   # autoscaling.tf
   resource "aws_appautoscaling_target" "ecs_target" {
     max_capacity       = 4
     min_capacity       = 1
     resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
     scalable_dimension = "ecs:service:DesiredCount"
   }
   ```

2. **Implement Scaling Policies**
   - Target tracking for CPU
   - Target tracking for memory
   - Schedule-based scaling

3. **Cost Optimization**
   - Use Fargate Spot for dev/staging
   - Right-size task definitions
   - Set up Cost and Usage Reports

4. **Resource Tagging Strategy**
   - Cost center tags
   - Environment tags
   - Owner tags

### Testing
- Load test to trigger scaling
- Verify spot instances work (dev)
- Check cost allocation tags

### Success Criteria
- [ ] Auto-scaling functional
- [ ] Costs reduced in non-prod
- [ ] Resource tags applied
- [ ] Scaling metrics visible

---

## PR9: Backup, Disaster Recovery, and Rollback

### Context
Implement backup strategies, disaster recovery procedures, and automated rollback capabilities to ensure application resilience and data protection.

### Files to Create/Modify
```
infra/terraform/
├── backup.tf
├── disaster-recovery/
│   └── runbook.md
.github/workflows/
├── rollback.yml
```

### Implementation Steps
1. **Container Image Backup**
   - ECR replication to another region
   - Image export to S3

2. **Infrastructure Backup**
   ```hcl
   # backup.tf
   resource "aws_backup_plan" "main" {
     name = "${var.project_name}-backup-plan"
     rule {
       rule_name         = "daily_backup"
       target_vault_name = aws_backup_vault.main.name
       schedule          = "cron(0 2 * * ? *)"
     }
   }
   ```

3. **Automated Rollback**
   - CloudWatch alarm triggers
   - Automatic ECS service rollback
   - GitHub workflow for manual rollback

4. **Disaster Recovery Documentation**
   - RTO/RPO definitions
   - Recovery procedures
   - Contact information

### Testing
- Test backup restoration
- Perform rollback drill
- Validate DR procedures

### Success Criteria
- [ ] Backups running automatically
- [ ] Rollback tested successfully
- [ ] DR documentation complete
- [ ] Recovery time meets requirements

---

## PR10: Production Readiness and Documentation

### Context
Final preparation for production deployment including performance testing, documentation completion, runbooks, and handover materials.

### Files to Create/Modify
```
docs/
├── deployment-guide.md
├── operations-manual.md
├── troubleshooting-guide.md
├── architecture-decisions.md
infra/
├── Makefile
└── scripts/
    ├── deploy.sh
    └── rollback.sh
```

### Implementation Steps
1. **Create Operational Documentation**
   - Deployment procedures
   - Monitoring guidelines
   - Incident response playbooks

2. **Performance Testing**
   - Load testing with k6 or JMeter
   - Identify bottlenecks
   - Document performance baselines

3. **Create Helper Scripts**
   ```bash
   # scripts/deploy.sh
   #!/bin/bash
   terraform plan -var-file=environments/prod.tfvars
   terraform apply -var-file=environments/prod.tfvars
   ```

4. **Final Checklist**
   - Security review complete
   - Cost estimates documented
   - Runbooks tested
   - Team training completed

### Testing
- End-to-end deployment test
- Load test at expected traffic
- Failover testing

### Success Criteria
- [ ] All documentation complete
- [ ] Performance benchmarks met
- [ ] Helper scripts functional
- [ ] Team trained on operations

---

## Implementation Timeline

| PR | Title | Duration | Dependencies |
|----|-------|----------|--------------|
| PR1 | Terraform Foundation | 2 days | None |
| PR2 | ECR Setup | 1 day | PR1 |
| PR3 | ECS Configuration | 3 days | PR2 |
| PR4 | ALB and DNS | 2 days | PR3 |
| PR5 | CI/CD Pipeline | 3 days | PR4 |
| PR6 | Monitoring | 2 days | PR5 |
| PR7 | Security | 2 days | PR5 |
| PR8 | Cost Optimization | 2 days | PR6 |
| PR9 | Backup & DR | 2 days | PR5 |
| PR10 | Production Ready | 2 days | All |

**Total estimated time**: 21 days (can be parallelized to ~12 days)

## Risk Mitigation

### Technical Risks
- **Risk**: Terraform state corruption
  - **Mitigation**: Use S3 backend with versioning and locking

- **Risk**: Failed deployments blocking production
  - **Mitigation**: Blue/green deployment strategy

- **Risk**: High AWS costs
  - **Mitigation**: Start with minimal resources, use auto-scaling

### Operational Risks
- **Risk**: Lack of expertise in team
  - **Mitigation**: Comprehensive documentation and training

- **Risk**: Security vulnerabilities
  - **Mitigation**: Security scanning at multiple layers

## Success Metrics
- Deployment time < 10 minutes
- Zero-downtime deployments
- Monthly costs < $60
- 99.9% uptime
- Recovery time < 30 minutes

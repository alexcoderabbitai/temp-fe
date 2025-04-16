## This is a sample Terraform file to check CHECKOV with intentional vulnerabilities.
## Run checkov:
## checkov --directory /user/path/to/iac/code
## checkov --file /user/tf/example.tf
## checkov -f /user/cloudformation/example1.yml -f /user/cloudformation/example2.yml
##
## Refer: https://www.checkov.io/2.Basics/Installing%20Checkov.html

locals {
  sg_name    = "checkov-test"
  aws_vpc_id = "vpc-#####" #enter vpc id here
  cidr_block = ["0.0.0.0/0"]
  from_port  = "80"
  to_port    = "80"
}

##################################################################
# Insecure provider block with hardcoded AWS credentials 
# (should be retrieved from environment variables or a secure store)
##################################################################
provider "aws" {
  region     = "us-east-1"
  access_key = "AKIA123456789EXAMPLE"      # Vulnerability: Hardcoded AWS access key
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # Vulnerability: Hardcoded AWS secret key
}

##################################################################
# A security group with minimal restrictions in the first resource.
##################################################################
resource "aws_security_group" "this" {
  name        = local.sg_name
  description = "Security group "
  vpc_id      = local.aws_vpc_id

  ingress {
    description = "Ingress from VPC"
    from_port   = local.from_port
    to_port     = local.to_port
    protocol    = "tcp"
    cidr_blocks = local.cidr_block
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

##################################################################
# An additional security group with an overly permissive rule.
# This rule allows ALL TCP ports (0-65535) from ANY source.
##################################################################
resource "aws_security_group" "insecure" {
  name        = "insecure-sg"
  description = "Insecure SG exposing all TCP ports to the world"
  vpc_id      = local.aws_vpc_id

  ingress {
    description = "Allow all TCP traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

##################################################################
# A public S3 bucket configuration with unsafe ACL and disabled block public access.
##################################################################
resource "aws_s3_bucket" "public" {
  bucket = "checkov-public-bucket-demo-12345"
  acl    = "public-read"   # Vulnerability: Bucket is publicly readable

  versioning {
    enabled = false
  }

  # Intentionally not configuring block public access to expose potential risk
  website {
    index_document = "index.html"
  }
}

##################################################################
# Terraform configuration, with required versions and providers.
##################################################################
terraform {
  required_version = "~> 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.20.0"
    }
  }
}

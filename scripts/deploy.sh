#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-ap-southeast-1}

echo -e "${GREEN}🚀 Deploying Claim Analyzer to ${ENVIRONMENT} environment${NC}"

# Check prerequisites
command -v terraform >/dev/null 2>&1 || { echo -e "${RED}❌ Terraform is required but not installed.${NC}" >&2; exit 1; }
command -v aws >/dev/null 2>&1 || { echo -e "${RED}❌ AWS CLI is required but not installed.${NC}" >&2; exit 1; }
command -v zip >/dev/null 2>&1 || { echo -e "${RED}❌ zip is required but not installed.${NC}" >&2; exit 1; }

# Check AWS credentials
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build Lambda functions
echo -e "${YELLOW}📦 Building Lambda functions...${NC}"

# Create artifacts directory
mkdir -p artifacts

# Build upload handler
echo "Building upload_handler..."
cd lambda
zip -r ../artifacts/upload_handler.zip upload_handler.py
echo -e "${GREEN}✅ upload_handler.zip created${NC}"

# Build submission analyzer
echo "Building submission_analyzer..."
zip -r ../artifacts/submission_analyzer.zip submission_analyzer.py
echo -e "${GREEN}✅ submission_analyzer.zip created${NC}"

cd ..

# List artifacts
echo -e "${YELLOW}📋 Artifacts created:${NC}"
ls -la artifacts/

# Deploy with Terraform
echo -e "${YELLOW}🏗️  Initializing Terraform...${NC}"
cd terraform

terraform init

echo -e "${YELLOW}📋 Terraform Plan...${NC}"
terraform plan \
    -var="upload_handler_zip_path=../artifacts/upload_handler.zip" \
    -var="submission_analyzer_zip_path=../artifacts/submission_analyzer.zip" \
    -var="environment=${ENVIRONMENT}" \
    -out=tfplan

echo -e "${YELLOW}🚀 Applying Terraform changes...${NC}"
terraform apply tfplan

# Get outputs
echo -e "${GREEN}📋 Deployment outputs:${NC}"
API_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "Not available")
BUCKET_NAME=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "Not available")

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 API Gateway URL: ${API_URL}${NC}"
echo -e "${GREEN}📦 S3 Bucket: ${BUCKET_NAME}${NC}"

# Basic smoke test
if [ "$API_URL" != "Not available" ]; then
    echo -e "${YELLOW}🧪 Running basic smoke test...${NC}"
    
    # Test upload endpoint
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/upload?filename=test.jpg" || echo "000")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✅ Upload endpoint is responding${NC}"
    else
        echo -e "${RED}❌ Upload endpoint test failed (HTTP ${HTTP_STATUS})${NC}"
    fi
fi

echo -e "${GREEN}🎉 Deployment script completed!${NC}"
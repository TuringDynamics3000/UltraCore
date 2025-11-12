#!/bin/bash

echo "🚀 DEPLOYING ULTRACORE TO AWS"
echo "=============================="

# Configuration
REGION="ap-southeast-2"  # Sydney
CLUSTER_NAME="ultracore-prod"
ECR_REPO="ultracore"

# Step 1: Build Docker images
echo "📦 Building Docker images..."
docker build -t ultracore/banking:latest ./src/ultracore
docker build -t ultracore/wealth:latest ./src/ultrawealth

# Step 2: Push to ECR
echo "📤 Pushing to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO
docker tag ultracore/banking:latest $ECR_REPO/banking:latest
docker tag ultracore/wealth:latest $ECR_REPO/wealth:latest
docker push $ECR_REPO/banking:latest
docker push $ECR_REPO/wealth:latest

# Step 3: Deploy to EKS
echo "☸️ Deploying to Kubernetes..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
kubectl apply -f k8s-deployment.yaml

# Step 4: Setup RDS
echo "🗄️ Setting up RDS..."
aws rds create-db-instance \
  --db-instance-identifier ultracore-prod \
  --db-instance-class db.t3.large \
  --engine postgres \
  --master-username ultracore \
  --master-user-password $DB_PASSWORD \
  --allocated-storage 100

# Step 5: Setup ElastiCache
echo "💾 Setting up Redis..."
aws elasticache create-cache-cluster \
  --cache-cluster-id ultracore-redis \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --num-cache-nodes 1

# Step 6: Setup Route53
echo "🌐 Configuring DNS..."
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file://route53-records.json

# Step 7: Setup CloudFront
echo "🚀 Setting up CDN..."
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

echo "✅ DEPLOYMENT COMPLETE!"
echo "🔗 Access at: https://ultracore.com"

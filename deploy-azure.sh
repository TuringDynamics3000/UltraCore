#!/bin/bash

echo "🚀 DEPLOYING ULTRACORE TO AZURE"
echo "================================"

# Configuration
RESOURCE_GROUP="ultracore-prod-rg"
LOCATION="australiasoutheast"  # Melbourne
AKS_CLUSTER="ultracore-aks"
ACR_NAME="ultracoreacr"

# Step 1: Create Resource Group
echo "📦 Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Step 2: Create Container Registry
echo "📤 Creating ACR..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Premium

# Step 3: Build and Push Images
echo "🏗️ Building images..."
az acr build --registry $ACR_NAME --image banking:latest ./src/ultracore
az acr build --registry $ACR_NAME --image wealth:latest ./src/ultrawealth

# Step 4: Create AKS Cluster
echo "☸️ Creating AKS cluster..."
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Step 5: Deploy to AKS
echo "🚀 Deploying to AKS..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
kubectl apply -f k8s-deployment.yaml

# Step 6: Setup Azure Database for PostgreSQL
echo "🗄️ Creating PostgreSQL..."
az postgres server create \
  --resource-group $RESOURCE_GROUP \
  --name ultracore-db \
  --location $LOCATION \
  --admin-user ultracore \
  --admin-password $DB_PASSWORD \
  --sku-name GP_Gen5_4

# Step 7: Setup Azure Cache for Redis
echo "💾 Creating Redis cache..."
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name ultracore-redis \
  --location $LOCATION \
  --sku Premium \
  --vm-size P1

# Step 8: Setup Application Gateway
echo "🌐 Setting up Application Gateway..."
az network application-gateway create \
  --resource-group $RESOURCE_GROUP \
  --name ultracore-gateway \
  --location $LOCATION \
  --sku WAF_v2

echo "✅ AZURE DEPLOYMENT COMPLETE!"

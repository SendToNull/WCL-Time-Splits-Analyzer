#!/bin/bash

# WCL Time Splits Analyzer - Google Cloud Run Deployment Script
# Usage: ./deploy.sh [PROJECT_ID] [WCL_API_KEY] [SECRET_KEY]

set -e

# Check if required arguments are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <PROJECT_ID> <WCL_API_KEY> <SECRET_KEY>"
    echo "Example: $0 my-gcp-project abc123def456 your-secret-key"
    echo ""
    echo "Arguments:"
    echo "  PROJECT_ID   - Your Google Cloud Project ID"
    echo "  WCL_API_KEY  - Your WarcraftLogs API key"
    echo "  SECRET_KEY   - A secure random string for Flask sessions"
    exit 1
fi

PROJECT_ID=$1
WCL_API_KEY=$2
SECRET_KEY=$3
SERVICE_NAME="wcl-analyzer"
REGION="us-central1"

echo "🚀 Deploying WCL Time Splits Analyzer to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Build and submit to Google Container Registry
echo "🔨 Building and pushing container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars WCL_API_KEY=$WCL_API_KEY,SECRET_KEY=$SECRET_KEY \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300

# Get the service URL
echo "✅ Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo ""
echo "🌐 Your application is available at: $SERVICE_URL"
echo "🔍 Health check: $SERVICE_URL/health"
echo ""
echo "📊 To view logs:"
echo "gcloud logs tail --follow --project=$PROJECT_ID --resource-type=cloud_run_revision --resource-labels=service_name=$SERVICE_NAME"
echo ""
echo "🗑️  To delete the service:"
echo "gcloud run services delete $SERVICE_NAME --platform managed --region $REGION"

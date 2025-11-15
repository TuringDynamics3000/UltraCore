# UltraCore ESG Optimization: Deployment Guide

This guide provides instructions for deploying and running the event-driven ESG optimization workflow.

## 1. Prerequisites

*   A running Kafka cluster
*   A Data Mesh storage backend (e.g., S3)
*   A container orchestration platform (e.g., Kubernetes)

## 2. Deployment Steps

1.  **Build the Optimization Service Docker Image:**

    ```bash
    docker build -t ultracore-esg-optimization-service:latest -f Dockerfile.optimization_service .
    ```

2.  **Deploy the Service to Kubernetes:**

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: esg-optimization-service
    spec:
      replicas: 3 # Start with 3 replicas for high availability
      selector:
        matchLabels:
          app: esg-optimization-service
      template:
        metadata:
          labels:
            app: esg-optimization-service
        spec:
          containers:
          - name: optimization-service
            image: ultracore-esg-optimization-service:latest
            env:
            - name: KAFKA_BOOTSTRAP_SERVERS
              value: "kafka-service:9092"
            - name: DATA_MESH_PATH
              value: "s3://ultracore-data-mesh"
    ```

3.  **Create the Data Mesh Data Products:**

    Run the data pipelines to generate the `financial_data_product.parquet` and `esg_data_product.parquet` files in the Data Mesh.

4.  **Update the MCP Server:**

    Deploy the updated MCP server with the asynchronous `optimize_portfolio_esg` tool.

## 3. Running the Workflow

1.  **Initiate an Optimization:**

    An AI agent calls the `optimize_portfolio_esg` MCP tool. This publishes a `PortfolioOptimizationRequested` event to Kafka.

2.  **Monitor the Service:**

    Check the logs of the `esg-optimization-service` pods to see the optimization request being processed.

3.  **Verify the Output:**

    A `PortfolioOptimizationCompleted` event will be published to Kafka. Downstream services can consume this event to update dashboards, execute trades, and notify the user.

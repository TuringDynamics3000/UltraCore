import { DataProvider } from 'react-admin';
import { baseDataProvider } from './dataProvider';
import { kafkaDataProvider } from './kafkaDataProvider';
import { dataMeshProvider } from './dataMeshProvider';

/**
 * Composite Data Provider
 * Routes requests to the appropriate specialized provider based on resource name
 * 
 * Resource Routing:
 * - kafka-* → Kafka provider (event streams)
 * - data-products, etf-data, market-data → Data Mesh provider (S3/Parquet)
 * - portfolios, securities, loans, users, esg, agents, mcp-tools → Base provider (PostgreSQL via tRPC)
 */

export const compositeDataProvider: DataProvider = {
  getList: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.getList(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.getList(resource, params);
    }
    
    return baseDataProvider.getList(resource, params);
  },

  getOne: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.getOne(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.getOne(resource, params);
    }
    
    return baseDataProvider.getOne(resource, params);
  },

  getMany: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.getMany(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.getMany(resource, params);
    }
    
    return baseDataProvider.getMany(resource, params);
  },

  getManyReference: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.getManyReference(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.getManyReference(resource, params);
    }
    
    return baseDataProvider.getManyReference(resource, params);
  },

  create: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.create(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.create(resource, params);
    }
    
    return baseDataProvider.create(resource, params);
  },

  update: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.update(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.update(resource, params);
    }
    
    return baseDataProvider.update(resource, params);
  },

  updateMany: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.updateMany(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.updateMany(resource, params);
    }
    
    return baseDataProvider.updateMany(resource, params);
  },

  delete: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.delete(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.delete(resource, params);
    }
    
    return baseDataProvider.delete(resource, params);
  },

  deleteMany: async (resource, params) => {
    if (resource.startsWith('kafka-')) {
      return kafkaDataProvider.deleteMany(resource, params);
    }
    
    if (['data-products', 'etf-data', 'market-data'].includes(resource)) {
      return dataMeshProvider.deleteMany(resource, params);
    }
    
    return baseDataProvider.deleteMany(resource, params);
  },
};

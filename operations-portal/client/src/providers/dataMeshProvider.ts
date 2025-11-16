import { DataProvider } from 'react-admin';
import * as duckdb from '@duckdb/duckdb-wasm';

/**
 * Data Mesh Provider for React Admin
 * Provides access to S3/Parquet data products via DuckDB WASM
 * 
 * Resources:
 * - data-products → catalog of all data products
 * - etf-data → query ETF Parquet files
 * - market-data → query market data products
 * 
 * This provider uses DuckDB WASM for zero-backend-load analytics
 */

let db: duckdb.AsyncDuckDB | null = null;
let conn: duckdb.AsyncDuckDBConnection | null = null;

// Initialize DuckDB WASM
const initDuckDB = async () => {
  if (db) return { db, conn };

  const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
  const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);
  const worker_url = URL.createObjectURL(
    new Blob([`importScripts("${bundle.mainWorker}");`], { type: 'text/javascript' })
  );

  const worker = new Worker(worker_url);
  const logger = new duckdb.ConsoleLogger();
  db = new duckdb.AsyncDuckDB(logger, worker);
  await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
  
  conn = await db.connect();

  // Register S3 access (if credentials available)
  // await conn.query(`
  //   INSTALL httpfs;
  //   LOAD httpfs;
  //   SET s3_region='us-east-1';
  // `);

  return { db, conn };
};

const getAuthToken = () => localStorage.getItem('auth_token');

const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = getAuthToken();
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
};

export const dataMeshProvider: DataProvider = {
  getList: async (resource, params) => {
    if (resource === 'data-products') {
      // Get catalog from PostgreSQL
      const { page, perPage } = params.pagination;
      const query = new URLSearchParams({
        page: page.toString(),
        perPage: perPage.toString(),
      });

      const response = await fetchWithAuth(`/api/data-mesh/products?${query}`);
      const data = await response.json();

      return {
        data: data.products || [],
        total: data.total || 0,
      };
    }

    // Query Parquet files with DuckDB
    const { db: duckDB, conn: connection } = await initDuckDB();
    
    const { page, perPage } = params.pagination;
    const offset = (page - 1) * perPage;

    // Get data product URL from catalog
    const catalogResponse = await fetchWithAuth(`/api/data-mesh/products/${resource}`);
    const product = await catalogResponse.json();

    if (!product.parquetUrl) {
      throw new Error('Data product has no Parquet file');
    }

    // Query Parquet file
    const result = await connection!.query(`
      SELECT * FROM read_parquet('${product.parquetUrl}')
      LIMIT ${perPage} OFFSET ${offset}
    `);

    const countResult = await connection!.query(`
      SELECT COUNT(*) as total FROM read_parquet('${product.parquetUrl}')
    `);

    const rows = result.toArray().map((row: any) => row.toJSON());
    const total = countResult.toArray()[0].total;

    return {
      data: rows,
      total,
    };
  },

  getOne: async (resource, params) => {
    if (resource === 'data-products') {
      const response = await fetchWithAuth(`/api/data-mesh/products/${params.id}`);
      const data = await response.json();
      return { data };
    }

    throw new Error('getOne not supported for Parquet queries');
  },

  getMany: async (resource, params) => {
    if (resource === 'data-products') {
      const promises = params.ids.map(id =>
        fetchWithAuth(`/api/data-mesh/products/${id}`)
          .then(res => res.json())
      );
      const products = await Promise.all(promises);
      return { data: products };
    }

    throw new Error('getMany not supported for Parquet queries');
  },

  getManyReference: async (resource, params) => {
    throw new Error('getManyReference not supported for Data Mesh');
  },

  // Data products are read-only
  create: async () => {
    throw new Error('Data products are read-only');
  },

  update: async () => {
    throw new Error('Data products are read-only');
  },

  updateMany: async () => {
    throw new Error('Data products are read-only');
  },

  delete: async () => {
    throw new Error('Data products are read-only');
  },

  deleteMany: async () => {
    throw new Error('Data products are read-only');
  },
};

/**
 * Execute custom SQL query on a data product
 */
export const queryDataProduct = async (productId: string, sql: string) => {
  const { conn: connection } = await initDuckDB();
  
  // Get data product URL
  const response = await fetchWithAuth(`/api/data-mesh/products/${productId}`);
  const product = await response.json();

  if (!product.parquetUrl) {
    throw new Error('Data product has no Parquet file');
  }

  // Execute query
  const result = await connection!.query(sql.replace('{{parquet_url}}', product.parquetUrl));
  return result.toArray().map((row: any) => row.toJSON());
};

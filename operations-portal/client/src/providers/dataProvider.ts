import { DataProvider } from 'react-admin';

/**
 * Base tRPC Data Provider for React Admin
 * Bridges React Admin's data provider interface with our tRPC backend
 * 
 * This will be extended with specific providers for:
 * - PostgreSQL (portfolios, securities, loans, users)
 * - Kafka (event streams)
 * - Data Mesh (S3/Parquet data products)
 * - RL Metrics (agent training data)
 */

// Helper to get auth token
const getAuthToken = () => localStorage.getItem('auth_token');

// Helper to make authenticated requests
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

/**
 * Base data provider - will be composed with specialized providers
 */
export const baseDataProvider: DataProvider = {
  getList: async (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const filter = params.filter;

    // Build query string
    const query = new URLSearchParams({
      _page: page.toString(),
      _perPage: perPage.toString(),
      _sort: field,
      _order: order,
      ...filter,
    });

    const response = await fetchWithAuth(`/api/${resource}?${query}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    return {
      data: data.items || [],
      total: data.total || 0,
    };
  },

  getOne: async (resource, params) => {
    const response = await fetchWithAuth(`/api/${resource}/${params.id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data };
  },

  getMany: async (resource, params) => {
    const query = new URLSearchParams();
    params.ids.forEach(id => query.append('id', id.toString()));

    const response = await fetchWithAuth(`/api/${resource}?${query}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data: data.items || [] };
  },

  getManyReference: async (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const filter = params.filter;

    const query = new URLSearchParams({
      _page: page.toString(),
      _perPage: perPage.toString(),
      _sort: field,
      _order: order,
      [params.target]: params.id.toString(),
      ...filter,
    });

    const response = await fetchWithAuth(`/api/${resource}?${query}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    return {
      data: data.items || [],
      total: data.total || 0,
    };
  },

  create: async (resource, params) => {
    const response = await fetchWithAuth(`/api/${resource}`, {
      method: 'POST',
      body: JSON.stringify(params.data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data };
  },

  update: async (resource, params) => {
    const response = await fetchWithAuth(`/api/${resource}/${params.id}`, {
      method: 'PUT',
      body: JSON.stringify(params.data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data };
  },

  updateMany: async (resource, params) => {
    const responses = await Promise.all(
      params.ids.map(id =>
        fetchWithAuth(`/api/${resource}/${id}`, {
          method: 'PUT',
          body: JSON.stringify(params.data),
        })
      )
    );

    return { data: params.ids };
  },

  delete: async (resource, params) => {
    const response = await fetchWithAuth(`/api/${resource}/${params.id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return { data: params.previousData };
  },

  deleteMany: async (resource, params) => {
    await Promise.all(
      params.ids.map(id =>
        fetchWithAuth(`/api/${resource}/${id}`, {
          method: 'DELETE',
        })
      )
    );

    return { data: params.ids };
  },
};

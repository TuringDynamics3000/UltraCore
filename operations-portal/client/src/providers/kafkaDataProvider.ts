import { DataProvider } from 'react-admin';

/**
 * Kafka Data Provider for React Admin
 * Provides read-only access to Kafka event streams
 * 
 * Resources map to Kafka topics:
 * - kafka-events → all events
 * - securities-prices → securities.prices topic
 * - securities-lifecycle → securities.lifecycle topic
 * - portfolio-events → ultrawealth-portfolio-events topic
 * - loan-events → ultragrow-* topics
 */

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

export const kafkaDataProvider: DataProvider = {
  getList: async (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const filter = params.filter;

    // Map resource to Kafka topic
    const topicMap: Record<string, string> = {
      'kafka-events': 'all',
      'securities-prices': 'securities.prices',
      'securities-lifecycle': 'securities.lifecycle',
      'portfolio-events': 'ultrawealth-portfolio-events',
      'loan-events': 'ultragrow-loan-events',
    };

    const topic = topicMap[resource] || resource;

    const query = new URLSearchParams({
      topic,
      page: page.toString(),
      perPage: perPage.toString(),
      sort: field,
      order,
      ...filter,
    });

    const response = await fetchWithAuth(`/api/kafka/events?${query}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    return {
      data: data.events || [],
      total: data.total || 0,
    };
  },

  getOne: async (resource, params) => {
    const response = await fetchWithAuth(`/api/kafka/events/${params.id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data };
  },

  getMany: async (resource, params) => {
    // Fetch multiple events by ID
    const promises = params.ids.map(id =>
      fetchWithAuth(`/api/kafka/events/${id}`)
        .then(res => res.json())
    );

    const events = await Promise.all(promises);
    return { data: events };
  },

  getManyReference: async (resource, params) => {
    // Get events related to a specific entity (e.g., all events for a security)
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;

    const query = new URLSearchParams({
      [params.target]: params.id.toString(),
      page: page.toString(),
      perPage: perPage.toString(),
      sort: field,
      order,
    });

    const response = await fetchWithAuth(`/api/kafka/events?${query}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    return {
      data: data.events || [],
      total: data.total || 0,
    };
  },

  // Kafka is read-only, so these operations are not supported
  create: async () => {
    throw new Error('Kafka events are read-only');
  },

  update: async () => {
    throw new Error('Kafka events are read-only');
  },

  updateMany: async () => {
    throw new Error('Kafka events are read-only');
  },

  delete: async () => {
    throw new Error('Kafka events are read-only');
  },

  deleteMany: async () => {
    throw new Error('Kafka events are read-only');
  },
};

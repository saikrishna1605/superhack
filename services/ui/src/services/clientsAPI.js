/**
 * API Service for Client Management
 * Integrates with FastAPI backend
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/clients';
const MSP_API_BASE = 'http://localhost:8000/api/msp';

// Simple in-memory cache
let clientsCache = null;
let cacheTimestamp = null;
const CACHE_DURATION = 30000; // 30 seconds

const isCacheValid = () => {
  return clientsCache && cacheTimestamp && (Date.now() - cacheTimestamp < CACHE_DURATION);
};

export const clientsAPI = {
  /**
   * Get all clients
   */
  async getAll() {
    try {
      // Try cache first
      if (isCacheValid()) {
        return clientsCache;
      }

      const response = await axios.get(API_BASE);
      clientsCache = response.data;
      cacheTimestamp = Date.now();
      return response.data;
    } catch (error) {
      console.error('Error fetching clients from API:', error);
      // Fallback to localStorage if API fails
      return this.getFromLocalStorage();
    }
  },

  /**
   * Get client by ID
   */
  async getById(id) {
    try {
      const response = await axios.get(`${API_BASE}/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching client ${id} from API:`, error);
      // Fallback to localStorage
      const clients = this.getFromLocalStorage();
      return clients.find(c => c.id === parseInt(id));
    }
  },

  /**
   * Create a new client
   */
  async create(clientData) {
    try {
      const response = await axios.post(API_BASE, clientData);
      // Invalidate cache
      clientsCache = null;
      return response.data;
    } catch (error) {
      console.error('Error creating client via API:', error);
      // Fallback to localStorage
      return this.createInLocalStorage(clientData);
    }
  },

  /**
   * Update a client
   */
  async update(id, clientData) {
    try {
      const response = await axios.put(`${API_BASE}/${id}`, clientData);
      // Invalidate cache
      clientsCache = null;
      return response.data;
    } catch (error) {
      console.error(`Error updating client ${id} via API:`, error);
      // Fallback to localStorage
      return this.updateInLocalStorage(id, clientData);
    }
  },

  /**
   * Delete a client
   */
  async delete(id) {
    try {
      await axios.delete(`${API_BASE}/${id}`);
      // Invalidate cache
      clientsCache = null;
      return { success: true };
    } catch (error) {
      console.error(`Error deleting client ${id} via API:`, error);
      // Fallback to localStorage
      return this.deleteFromLocalStorage(id);
    }
  },

  /**
   * Get dashboard statistics
   */
  async getStats() {
    try {
      const clients = await this.getAll();
      
      // Filter active and inactive clients
      const activeClients = clients.filter(c => (c.status || 'Active').toLowerCase() === 'active');
      const inactiveClients = clients.filter(c => (c.status || 'Active').toLowerCase() === 'inactive');
      
      const stats = {
        totalClients: activeClients.length,
        inactiveClients: inactiveClients.length,
        totalRevenue: activeClients.reduce((sum, c) => sum + (c.monthly_spend || c.revenue || 0), 0),
        totalLicenses: activeClients.reduce((sum, c) => sum + (c.total_licenses || c.licenses || 0), 0),
        avgHealthScore: activeClients.length > 0 
          ? activeClients.reduce((sum, c) => sum + (c.health_score || c.healthScore || 0), 0) / activeClients.length 
          : 0,
        highRiskClients: activeClients.filter(c => {
          const risk = c.churn_risk || c.churnRisk;
          return risk === 'high' || (typeof risk === 'number' && risk > 25);
        }).length
      };
      
      return stats;
    } catch (error) {
      console.error('Error calculating stats:', error);
      return {
        totalClients: 0,
        inactiveClients: 0,
        totalRevenue: 0,
        totalLicenses: 0,
        avgHealthScore: 0,
        highRiskClients: 0
      };
    }
  },

  // LocalStorage fallback methods
  getFromLocalStorage() {
    const data = localStorage.getItem('pulseops_clients');
    return data ? JSON.parse(data) : [];
  },

  createInLocalStorage(clientData) {
    const clients = this.getFromLocalStorage();
    const newId = clients.length > 0 ? Math.max(...clients.map(c => c.id)) + 1 : 1;
    const newClient = { id: newId, ...clientData };
    clients.push(newClient);
    localStorage.setItem('pulseops_clients', JSON.stringify(clients));
    return newClient;
  },

  updateInLocalStorage(id, clientData) {
    const clients = this.getFromLocalStorage();
    const index = clients.findIndex(c => c.id === parseInt(id));
    if (index !== -1) {
      clients[index] = { ...clients[index], ...clientData };
      localStorage.setItem('pulseops_clients', JSON.stringify(clients));
      return clients[index];
    }
    return null;
  },

  deleteFromLocalStorage(id) {
    const clients = this.getFromLocalStorage();
    const filtered = clients.filter(c => c.id !== parseInt(id));
    localStorage.setItem('pulseops_clients', JSON.stringify(filtered));
    return { success: true };
  },

  /**
   * Get priority alerts
   */
  async getAlerts(status = 'active') {
    try {
      const response = await axios.get(`${MSP_API_BASE}/alerts`, {
        params: { status_filter: status }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts from API:', error);
      // Return empty array if API fails
      return [];
    }
  },

  /**
   * Resolve an alert
   */
  async resolveAlert(alertId) {
    try {
      const response = await axios.post(`${MSP_API_BASE}/alerts/${alertId}/resolve`);
      return response.data;
    } catch (error) {
      console.error(`Error resolving alert ${alertId}:`, error);
      throw error;
    }
  }
};

export default clientsAPI;

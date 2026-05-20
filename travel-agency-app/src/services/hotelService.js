import api from './api';
import { tenantConfig } from '../config/tenantConfig';

export const hotelService = {
  async search(params) {
    try {
      const response = await api.get('/hotels/search', {
        params: {
          destination: params.destination,
          checkin: params.fromDate,
          checkout: params.toDate,
          agency_id: tenantConfig.key 
        }
      });

      return response.results || [];
    } catch (error) {
      console.error("Error fetching hotels:", error);
      throw new Error("Hotel data currently unavailable. Please try again later.");
    }
  }
};
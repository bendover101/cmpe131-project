import api from './api';
import { tenantConfig } from '../config/tenantConfig';

export const bookingService = {
  async createBooking(bookingData) {
    try {
      const payload = {
        ...bookingData,
        agency_id: tenantConfig.key,
        user_id: bookingData.user_id || 1 
      };
      
      const response = await api.post('/bookings', payload);
      return response.data;
    } catch (error) {
      console.error("Error saving booking:", error);
      throw error;
    }
  },

  async getUserBookings(userId = 1) {
    try {
      const response = await api.get('/bookings/by-agent-user', {
        params: {
          user_id: userId,
          agency_id: tenantConfig.key 
        }
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching bookings:", error);
      throw error;
    }
  }
};
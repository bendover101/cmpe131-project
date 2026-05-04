import api from './api';

export const flightService = {
  async search(params) {
    try {
      const response = await api.get('/flights/search', {
        params: {
          origin: params.origin,
          destination: params.destination,
          departure_date: params.fromDate
        }
      });

      return response.results || [];

    } catch (error) {
      console.error("Error fetching flights:", error);
      return [];
    }
  }
};
import axios from "axios";

const API_BASE_URL = "http://localhost:8080/api";

const api = {
  // Portfolio endpoints
  getPortfolio: async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/portfolio/get-portfolio`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching portfolio:", error);
      throw error;
    }
  },

  // Stock endpoints
  getStockInfo: async (symbol) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/stock/stock-info/${symbol}`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching stock info:", error);
      throw error;
    }
  },

  getStockNews: async (symbol) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/stock/stock-news/${symbol}`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching stock news:", error);
      throw error;
    }
  },

  // Trading endpoints
  addStock: async (stockData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/portfolio/add-stock`,
        stockData
      );
      return response.data;
    } catch (error) {
      console.error("Error adding stock:", error);
      throw error;
    }
  },

  sellStock: async (stockData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/portfolio/sell-stock`,
        stockData
      );
      return response.data;
    } catch (error) {
      console.error("Error selling stock:", error);
      throw error;
    }
  },

  shortStock: async (stockData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/portfolio/short-stock`,
        stockData
      );
      return response.data;
    } catch (error) {
      console.error("Error shorting stock:", error);
      throw error;
    }
  },

  coverStock: async (stockData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/portfolio/cover-stock`,
        stockData
      );
      return response.data;
    } catch (error) {
      console.error("Error covering stock:", error);
      throw error;
    }
  },

  // Price updates
  updatePrices: async () => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/portfolio/update-prices`
      );
      return response.data;
    } catch (error) {
      console.error("Error updating prices:", error);
      throw error;
    }
  },

  // Transactions
  getTransactions: async (filters = {}) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/portfolio/get-transactions`,
        {
          params: filters,
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching transactions:", error);
      throw error;
    }
  },
};

export default api;

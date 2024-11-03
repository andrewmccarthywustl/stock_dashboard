// src/services/api.js
import axios from "axios";
import { logError, logInfo, logDebug } from "../utils/logger";

const API_BASE_URL = "/api/portfolio";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor for logging and handling
apiClient.interceptors.request.use(
  (config) => {
    logDebug(
      `Making ${config.method.toUpperCase()} request to: ${config.url}`,
      {
        params: config.params,
        data: config.data,
      }
    );
    return config;
  },
  (error) => {
    logError("Request configuration error:", error);
    return Promise.reject(new Error("Failed to setup request"));
  }
);

// Response interceptor for logging and error handling
apiClient.interceptors.response.use(
  (response) => {
    logDebug(`Response from ${response.config.url}:`, {
      status: response.status,
      data: response.data,
    });
    return response;
  },
  (error) => {
    if (error.response) {
      logError("API Error Response:", {
        url: error.config?.url,
        status: error.response.status,
        data: error.response.data,
        method: error.config?.method,
      });
    } else if (error.request) {
      logError("API No Response:", {
        url: error.config?.url,
        method: error.config?.method,
        message: "No response received from server",
      });
    } else {
      logError("API Request Setup Error:", {
        message: error.message,
        config: error.config,
      });
    }
    return Promise.reject(error);
  }
);

const api = {
  // Portfolio endpoints
  getPortfolio: async () => {
    try {
      logInfo("Fetching portfolio data");
      const response = await apiClient.get("/portfolio"); // Updated to match new endpoint
      return response.data;
    } catch (error) {
      logError("Failed to fetch portfolio:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch portfolio data"
      );
    }
  },

  // Transactions
  getTransactions: async (filters = {}) => {
    try {
      logInfo("Fetching transactions with filters:", filters);
      const response = await apiClient.get("/transactions", {
        params: {
          symbol: filters.symbol,
          transaction_type: filters.transaction_type,
          start_date: filters.start_date,
          end_date: filters.end_date,
        },
      });

      // Transform the response to ensure consistent structure
      const transactions = Array.isArray(response.data)
        ? response.data.map((transaction) => ({
            ...transaction,
            transaction_type: transaction.transaction_type || transaction.type, // Handle both possible field names
            total_value:
              transaction.total_value ||
              transaction.quantity * transaction.price,
            realized_gain: transaction.realized_gain || null,
          }))
        : response.data.transactions || [];

      const summary =
        !Array.isArray(response.data) && response.data.summary
          ? response.data.summary
          : {
              total_value: 0,
              realized_gains: 0,
              total_transactions: transactions.length,
              last_updated: new Date().toISOString(),
            };

      return {
        transactions,
        summary,
      };
    } catch (error) {
      logError("Failed to fetch transactions:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch transactions"
      );
    }
  },

  // Trade execution
  executeTrade: async (tradeData) => {
    try {
      logInfo("Executing trade:", tradeData);
      const response = await apiClient.post("/trade", {
        ...tradeData,
        date: tradeData.date || new Date().toISOString(),
        quantity: Number(tradeData.quantity),
        price: Number(tradeData.price),
      });
      return response.data;
    } catch (error) {
      logError("Failed to execute trade:", error);
      throw new Error(error.response?.data?.error || "Failed to execute trade");
    }
  },

  // Price updates
  updatePrices: async () => {
    try {
      logInfo("Updating portfolio prices");
      const response = await apiClient.post("/update-prices");
      return response.data;
    } catch (error) {
      logError("Failed to update prices:", error);
      throw new Error(error.response?.data?.error || "Failed to update prices");
    }
  },

  // Analytics
  getMetrics: async () => {
    try {
      logInfo("Fetching portfolio metrics");
      const response = await apiClient.get("/metrics");
      return response.data;
    } catch (error) {
      logError("Failed to fetch metrics:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch portfolio metrics"
      );
    }
  },

  getSectorExposure: async () => {
    try {
      logInfo("Fetching sector exposure");
      const response = await apiClient.get("/sector-exposure");
      return response.data;
    } catch (error) {
      logError("Failed to fetch sector exposure:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch sector exposure"
      );
    }
  },

  getBetaExposure: async () => {
    try {
      logInfo("Fetching beta exposure");
      const response = await apiClient.get("/beta-exposure");
      return response.data;
    } catch (error) {
      logError("Failed to fetch beta exposure:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch beta exposure"
      );
    }
  },

  // Position-specific endpoints
  getPosition: async (symbol, positionType) => {
    try {
      logInfo(`Fetching position: ${symbol} (${positionType})`);
      const response = await apiClient.get(
        `/position/${symbol}/${positionType}`
      );
      return response.data;
    } catch (error) {
      logError("Failed to fetch position:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch position data"
      );
    }
  },

  getAllPositions: async (positionType = null) => {
    try {
      logInfo(
        "Fetching all positions",
        positionType ? `of type: ${positionType}` : ""
      );
      const params = positionType ? { type: positionType } : {};
      const response = await apiClient.get("/positions", { params });
      return response.data;
    } catch (error) {
      logError("Failed to fetch positions:", error);
      throw new Error(
        error.response?.data?.error || "Failed to fetch positions"
      );
    }
  },
};

export default api;

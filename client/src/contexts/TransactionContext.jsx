// src/contexts/TransactionContext.jsx
import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import api from "../services/api";
import { logError, logInfo, logPerformance } from "../utils/logger";

/**
 * Transaction Context Interface
 * @typedef {Object} TransactionContextType
 * @property {Array} transactions - List of transactions
 * @property {boolean} isLoading - Loading state
 * @property {string|null} error - Error message
 * @property {Function} fetchTransactions - Function to fetch transactions
 * @property {Function} executeTrade - Function to execute a trade
 * @property {Object} summary - Transaction summary
 * @property {Function} clearError - Function to clear error
 */

const TransactionContext = createContext(null);

/**
 * Initial summary state
 */
const initialSummary = {
  total_value: 0,
  realized_gains: 0,
  total_transactions: 0,
  last_updated: new Date().toISOString(),
};

/**
 * Transaction Provider Component
 */
export const TransactionProvider = ({ children }) => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(initialSummary);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Fetch transactions with optional filters
   * @param {Object} filters - Filter criteria
   * @returns {Promise<Object>} Transaction data
   */
  const fetchTransactions = useCallback(async (filters = {}) => {
    setIsLoading(true);
    clearError();

    try {
      const response = await logPerformance("Fetch Transactions", async () => {
        return await api.getTransactions(filters);
      });

      logInfo("Transactions fetched successfully", {
        count: response.transactions.length,
        filters,
      });

      setTransactions(response.transactions);
      setSummary(response.summary || initialSummary);
      setLastUpdated(new Date());

      return response;
    } catch (error) {
      const errorMessage = error.message || "Failed to fetch transactions";
      logError("Error fetching transactions:", error);
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Execute a trade
   * @param {Object} tradeData - Trade details
   * @returns {Promise<Object>} Trade response
   */
  const executeTrade = useCallback(
    async (tradeData) => {
      clearError();

      try {
        logInfo("Executing trade:", tradeData);

        const response = await logPerformance("Execute Trade", async () => {
          return await api.executeTrade(tradeData);
        });

        // Refresh transactions after successful trade
        await fetchTransactions();

        logInfo("Trade executed successfully", {
          symbol: tradeData.symbol,
          type: tradeData.trade_type,
        });

        return response;
      } catch (error) {
        const errorMessage = error.message || "Failed to execute trade";
        logError("Error executing trade:", error);
        setError(errorMessage);
        throw error;
      }
    },
    [fetchTransactions]
  );

  /**
   * Auto-refresh transactions periodically
   */
  useEffect(() => {
    const REFRESH_INTERVAL = 60000; // 1 minute
    let refreshTimer;

    const autoRefresh = async () => {
      try {
        if (!isLoading) {
          await fetchTransactions();
        }
      } catch (error) {
        logError("Auto-refresh failed:", error);
      }
    };

    refreshTimer = setInterval(autoRefresh, REFRESH_INTERVAL);

    return () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
      }
    };
  }, [fetchTransactions, isLoading]);

  /**
   * Calculate transaction statistics
   * @returns {Object} Transaction statistics
   */
  const getTransactionStats = useCallback(() => {
    try {
      const totalTransactions = transactions.length;
      const buyTransactions = transactions.filter(
        (t) => t.type === "buy"
      ).length;
      const sellTransactions = transactions.filter(
        (t) => t.type === "sell"
      ).length;
      const shortTransactions = transactions.filter(
        (t) => t.type === "short"
      ).length;
      const coverTransactions = transactions.filter(
        (t) => t.type === "cover"
      ).length;

      return {
        total: totalTransactions,
        buy: buyTransactions,
        sell: sellTransactions,
        short: shortTransactions,
        cover: coverTransactions,
      };
    } catch (error) {
      logError("Error calculating transaction stats:", error);
      return {
        total: 0,
        buy: 0,
        sell: 0,
        short: 0,
        cover: 0,
      };
    }
  }, [transactions]);

  const value = {
    transactions,
    isLoading,
    error,
    fetchTransactions,
    executeTrade,
    summary,
    clearError,
    lastUpdated,
    getTransactionStats,
  };

  return (
    <TransactionContext.Provider value={value}>
      {children}
    </TransactionContext.Provider>
  );
};

/**
 * Hook to use transaction context
 * @returns {TransactionContextType} Transaction context
 */
export const useTransactions = () => {
  const context = useContext(TransactionContext);
  if (!context) {
    throw new Error(
      "useTransactions must be used within a TransactionProvider"
    );
  }
  return context;
};

/**
 * Hook to use transaction statistics
 * @returns {Object} Transaction statistics
 */
export const useTransactionStats = () => {
  const { getTransactionStats } = useTransactions();
  return getTransactionStats();
};

/**
 * Hook to use transaction summary
 * @returns {Object} Transaction summary
 */
export const useTransactionSummary = () => {
  const { summary } = useTransactions();
  return summary;
};

export default {
  TransactionProvider,
  useTransactions,
  useTransactionStats,
  useTransactionSummary,
};

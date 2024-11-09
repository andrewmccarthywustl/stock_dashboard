// src/pages/TransactionHistory.jsx
import React, { useState, useEffect } from "react";
import { useTransactions } from "../contexts/TransactionContext";
import { formatCurrency, formatDate } from "../utils/formatters";
import { logError, logInfo } from "../utils/logger";

const TransactionHistory = () => {
  const {
    transactions,
    isLoading,
    error: contextError,
    fetchTransactions,
  } = useTransactions();

  const [filters, setFilters] = useState({
    symbol: "",
    transaction_type: "",
    start_date: "",
    end_date: "",
  });

  const [error, setError] = useState(null);
  const [summary, setSummary] = useState({
    realized_gains: 0,
    total_transactions: 0,
    last_updated: new Date().toISOString(),
  });

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        logInfo("Loading transactions with filters:", filters);
        const validFilters = Object.entries(filters).reduce(
          (acc, [key, value]) => {
            if (value) acc[key] = value;
            return acc;
          },
          {}
        );

        if (validFilters.start_date) {
          validFilters.start_date = new Date(
            validFilters.start_date
          ).toISOString();
        }
        if (validFilters.end_date) {
          validFilters.end_date = new Date(validFilters.end_date).toISOString();
        }

        const response = await fetchTransactions(validFilters);
        setSummary(
          response.summary || {
            realized_gains: 0,
            total_transactions: 0,
            last_updated: new Date().toISOString(),
          }
        );
      } catch (err) {
        logError("Failed to load transactions:", err);
        setError(err.message || "Failed to load transactions");
      }
    };

    loadTransactions();
  }, [filters, fetchTransactions]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    logInfo(`Updating filter ${name}:`, value);
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const getTransactionTypeColor = (transactionType) => {
    if (!transactionType) return "bg-gray-100 text-gray-800";

    switch (transactionType.toLowerCase()) {
      case "buy":
        return "bg-green-100 text-green-800";
      case "sell":
        return "bg-red-100 text-red-800";
      case "short":
        return "bg-purple-100 text-purple-800";
      case "cover":
        return "bg-blue-100 text-blue-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const renderSummary = () => {
    if (!summary) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Realized Gains</h3>
          <p
            className={`mt-1 text-lg font-semibold ${
              Number(summary.realized_gains) >= 0
                ? "text-green-600"
                : "text-red-600"
            }`}
          >
            {formatCurrency(summary.realized_gains)}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">
            Transaction Count
          </h3>
          <p className="mt-1 text-lg font-semibold text-gray-900">
            {summary.total_transactions}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Transaction History</h1>
      </div>

      {renderSummary()}

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-4 bg-white p-4 rounded-lg shadow">
        <div>
          <label
            htmlFor="symbol"
            className="block text-sm font-medium text-gray-700"
          >
            Symbol
          </label>
          <input
            type="text"
            id="symbol"
            name="symbol"
            value={filters.symbol}
            onChange={handleFilterChange}
            className="mt-1 block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="Enter symbol"
          />
        </div>

        <div>
          <label
            htmlFor="transaction_type"
            className="block text-sm font-medium text-gray-700"
          >
            Type
          </label>
          <select
            id="transaction_type"
            name="transaction_type"
            value={filters.transaction_type}
            onChange={handleFilterChange}
            className="mt-1 block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="">All</option>
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
            <option value="short">Short</option>
            <option value="cover">Cover</option>
          </select>
        </div>

        <div>
          <label
            htmlFor="start_date"
            className="block text-sm font-medium text-gray-700"
          >
            Start Date
          </label>
          <input
            type="date"
            id="start_date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
            className="mt-1 block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label
            htmlFor="end_date"
            className="block text-sm font-medium text-gray-700"
          >
            End Date
          </label>
          <input
            type="date"
            id="end_date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
            className="mt-1 block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Error Display */}
      {(error || contextError) && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
          {error || contextError}
        </div>
      )}

      {/* Transactions Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Date
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Symbol
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Type
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Quantity
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Price
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Total
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Realized Gain/Loss
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center">
                    <div className="flex justify-center items-center space-x-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-500"></div>
                      <span>Loading...</span>
                    </div>
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td
                    colSpan="7"
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    No transactions found
                  </td>
                </tr>
              ) : (
                transactions.map((transaction) => (
                  <tr
                    key={transaction.transaction_id}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatDate(transaction.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {transaction.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getTransactionTypeColor(
                          transaction.transaction_type
                        )}`}
                      >
                        {(transaction.transaction_type || "").toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {transaction.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatCurrency(transaction.price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatCurrency(transaction.total_value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {transaction.realized_gain !== null ? (
                        <span
                          className={
                            Number(transaction.realized_gain) >= 0
                              ? "text-green-600"
                              : "text-red-600"
                          }
                        >
                          {formatCurrency(transaction.realized_gain)}
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TransactionHistory;

import React, { useState, useEffect } from "react";
import api from "../services/api";
import { formatCurrency, formatDate } from "../utils/formatters";

const TransactionHistory = () => {
  const [transactions, setTransactions] = useState([]);
  const [filters, setFilters] = useState({
    symbol: "",
    type: "", // 'buy', 'sell', 'short', or 'cover'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTransactions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.getTransactions(filters);
      setTransactions(response.transactions);
    } catch (error) {
      setError("Failed to load transactions");
      console.error("Error fetching transactions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const getTransactionTypeColor = (type) => {
    switch (type) {
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

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Transaction History</h1>

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
            htmlFor="type"
            className="block text-sm font-medium text-gray-700"
          >
            Type
          </label>
          <select
            id="type"
            name="type"
            value={filters.type}
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
      </div>

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
              ) : error ? (
                <tr>
                  <td
                    colSpan="7"
                    className="px-6 py-4 text-center text-red-600"
                  >
                    {error}
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
                transactions.map((transaction, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatDate(transaction.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {transaction.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span
                        className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getTransactionTypeColor(
                          transaction.type
                        )}`}
                      >
                        {transaction.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {transaction.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatCurrency(transaction.price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatCurrency(transaction.price * transaction.quantity)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {(transaction.type === "sell" ||
                        transaction.type === "cover") &&
                      transaction.realized_gain !== undefined ? (
                        <span
                          className={
                            transaction.realized_gain >= 0
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

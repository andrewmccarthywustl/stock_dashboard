// src/components/TradeForm.jsx
import React, { useState } from "react";
import api from "../services/api";

const TRADE_TYPES = {
  BUY: {
    type: "buy",
    label: "Buy Stock",
    buttonClass: "bg-indigo-600 hover:bg-indigo-700",
  },
  SELL: {
    type: "sell",
    label: "Sell Stock",
    buttonClass: "bg-red-600 hover:bg-red-700",
  },
  SHORT: {
    type: "short",
    label: "Short Stock",
    buttonClass: "bg-red-600 hover:bg-red-700",
  },
  COVER: {
    type: "cover",
    label: "Cover Short",
    buttonClass: "bg-green-600 hover:bg-green-700",
  },
};

const TradeForm = () => {
  const initialFormData = {
    tradeType: "BUY",
    stockSymbol: "",
    quantity: "",
    price: "",
    date: new Date().toISOString().split("T")[0],
  };

  const [formData, setFormData] = useState(initialFormData);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setError(null);
    setSuccessMessage(null);
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!formData.stockSymbol) {
      setError("Stock symbol is required");
      return false;
    }

    if (!formData.quantity || formData.quantity <= 0) {
      setError("Valid quantity is required");
      return false;
    }

    if (!formData.price || formData.price <= 0) {
      setError("Valid price is required");
      return false;
    }

    if (!formData.date) {
      setError("Date is required");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const tradeData = {
        symbol: formData.stockSymbol.toUpperCase(),
        quantity: parseFloat(formData.quantity),
        price: parseFloat(formData.price),
        trade_type: TRADE_TYPES[formData.tradeType].type,
        date: formData.date,
      };

      console.log("Sending trade data:", tradeData); // Debug log

      const response = await api.executeTrade(tradeData);
      console.log("Trade response:", response); // Debug log

      setSuccessMessage(
        `Successfully ${TRADE_TYPES[formData.tradeType].type} ${
          formData.quantity
        } shares of ${formData.stockSymbol}`
      );
      setFormData(initialFormData);
    } catch (error) {
      console.error("Error details:", error.response?.data);
      setError(
        error.response?.data?.error ||
          error.response?.data?.message ||
          `Error processing ${formData.tradeType.toLowerCase()} transaction`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const tradeConfig = TRADE_TYPES[formData.tradeType];

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
          {successMessage}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Transaction Type:
        </label>
        <select
          name="tradeType"
          value={formData.tradeType}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          {Object.entries(TRADE_TYPES).map(([key, config]) => (
            <option key={key} value={key}>
              {config.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Symbol:
        </label>
        <input
          type="text"
          name="stockSymbol"
          value={formData.stockSymbol}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="e.g., AAPL"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Quantity:
        </label>
        <input
          type="number"
          name="quantity"
          value={formData.quantity}
          onChange={handleChange}
          required
          min="0"
          step="1"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Price Per Share:
        </label>
        <input
          type="number"
          name="price"
          value={formData.price}
          onChange={handleChange}
          required
          min="0"
          step="0.01"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Date:</label>
        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
                    ${
                      isLoading
                        ? "opacity-50 cursor-not-allowed"
                        : `${
                            tradeConfig.buttonClass
                          } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${
                            tradeConfig.buttonClass.includes("indigo")
                              ? "indigo"
                              : tradeConfig.buttonClass.includes("red")
                              ? "red"
                              : "green"
                          }-500`
                    }`}
      >
        {isLoading ? "Processing..." : tradeConfig.label}
      </button>
    </form>
  );
};

export default TradeForm;

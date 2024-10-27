import React, { useState } from "react";
import api from "../services/api";

const ShortStockForm = ({ onPositionOpened }) => {
  const initialFormData = {
    stockSymbol: "",
    stockShortQuantity: "",
    stockShortPrice: "",
    stockShortDate: "",
  };

  const [formData, setFormData] = useState(initialFormData);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await api.shortStock({
        stockSymbol: formData.stockSymbol,
        stockShortQuantity: formData.stockShortQuantity,
        stockShortPrice: formData.stockShortPrice,
        stockShortDate: formData.stockShortDate,
      });
      setFormData(initialFormData);
      if (onPositionOpened) onPositionOpened();
    } catch (error) {
      setError(error.response?.data?.error || "Error shorting stock");
      console.error("Error shorting stock:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}

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
          Short Quantity:
        </label>
        <input
          type="number"
          name="stockShortQuantity"
          value={formData.stockShortQuantity}
          onChange={handleChange}
          required
          min="0"
          step="1"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Entry Price:
        </label>
        <input
          type="number"
          name="stockShortPrice"
          value={formData.stockShortPrice}
          onChange={handleChange}
          required
          min="0"
          step="0.01"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Short Date:
        </label>
        <input
          type="date"
          name="stockShortDate"
          value={formData.stockShortDate}
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
              ? "bg-red-400 cursor-not-allowed"
              : "bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          }`}
      >
        {isLoading ? "Processing..." : "Short Stock"}
      </button>
    </form>
  );
};

export default ShortStockForm;

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
    stockPurchaseQuantity: "",
    stockPurchasePrice: "",
    stockPurchaseDate: "",
    stockSellQuantity: "",
    stockSellPrice: "",
    stockSellDate: "",
    stockShortQuantity: "",
    stockShortPrice: "",
    stockShortDate: "",
    stockCoverQuantity: "",
    stockCoverPrice: "",
    stockCoverDate: "",
  };

  const [formData, setFormData] = useState(initialFormData);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const getFieldNames = (tradeType) => {
    const typeMap = {
      BUY: "Purchase",
      SELL: "Sell",
      SHORT: "Short",
      COVER: "Cover",
    };
    const prefix = `stock${typeMap[tradeType]}`;
    return {
      quantity: `${prefix}Quantity`,
      price: `${prefix}Price`,
      date: `${prefix}Date`,
    };
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    // For tradeType, we need to preserve existing values
    if (name === "tradeType") {
      const oldFields = getFieldNames(formData.tradeType);
      const newFields = getFieldNames(value);

      setFormData((prev) => ({
        ...prev,
        tradeType: value,
        [newFields.quantity]: prev[oldFields.quantity],
        [newFields.price]: prev[oldFields.price],
        [newFields.date]: prev[oldFields.date],
      }));
      return;
    }

    // For other fields, map them to the correct name based on trade type
    const fields = getFieldNames(formData.tradeType);
    if (name === "quantity") {
      setFormData((prev) => ({
        ...prev,
        [fields.quantity]: value,
      }));
    } else if (name === "price") {
      setFormData((prev) => ({
        ...prev,
        [fields.price]: value,
      }));
    } else if (name === "date") {
      setFormData((prev) => ({
        ...prev,
        [fields.date]: value,
      }));
    } else {
      // For stockSymbol
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
    setError(null);
  };

  const getCurrentValue = (fieldType) => {
    const fields = getFieldNames(formData.tradeType);
    switch (fieldType) {
      case "quantity":
        return formData[fields.quantity] || "";
      case "price":
        return formData[fields.price] || "";
      case "date":
        return formData[fields.date] || "";
      default:
        return "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const apiMethod = {
        BUY: api.addStock,
        SELL: api.sellStock,
        SHORT: api.shortStock,
        COVER: api.coverStock,
      }[formData.tradeType];

      // Get only the relevant fields for the current trade type
      const fields = getFieldNames(formData.tradeType);
      const relevantData = {
        stockSymbol: formData.stockSymbol,
        [fields.quantity]: formData[fields.quantity],
        [fields.price]: formData[fields.price],
        [fields.date]: formData[fields.date],
      };

      console.log("Sending data:", relevantData);
      const response = await apiMethod(relevantData);
      console.log("Response:", response);

      setFormData(initialFormData);
    } catch (error) {
      console.error("Error details:", error.response?.data);
      const errorMessage =
        error.response?.data?.error ||
        error.response?.data?.message ||
        `Error processing ${formData.tradeType.toLowerCase()} transaction`;
      setError(errorMessage);
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
          value={getCurrentValue("quantity")}
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
          value={getCurrentValue("price")}
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
          value={getCurrentValue("date")}
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

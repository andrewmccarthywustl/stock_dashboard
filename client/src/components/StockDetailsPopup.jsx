// src/components/StockDetailsPopup.jsx
import React from "react";
import { formatCurrency } from "../utils/formatters";

const StockDetailsPopup = ({ stock, onClose }) => {
  if (!stock) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Popup Content */}
      <div className="bg-[#1a1a1a] rounded-lg shadow-xl w-full max-w-2xl mx-4 z-10">
        <div className="flex justify-between items-center p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white">{stock.symbol}</h2>
            <span
              className={`px-2 py-0.5 text-sm rounded-full ${
                stock.position_type === "short"
                  ? "bg-purple-100 text-purple-800"
                  : "bg-blue-100 text-blue-800"
              }`}
            >
              {stock.position_type.toUpperCase()}
            </span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* Position Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Position Value</p>
              <p className="text-white text-lg font-medium">
                {formatCurrency(stock.position_value)}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Cost Basis</p>
              <p className="text-white text-lg font-medium">
                {formatCurrency(stock.cost_basis)}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Current Price</p>
              <p className="text-white text-lg font-medium">
                {formatCurrency(stock.current_price)}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Quantity</p>
              <p className="text-white text-lg font-medium">
                {stock.quantity?.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
            <div>
              <p className="text-gray-400 text-sm">Change</p>
              <p
                className={`text-lg font-medium ${
                  stock.percent_change >= 0 ? "text-green-500" : "text-red-500"
                }`}
              >
                {stock.percent_change >= 0 ? "+" : ""}
                {stock.percent_change?.toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Beta</p>
              <p className="text-white text-lg font-medium">
                {stock.beta?.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Sector</p>
              <p className="text-white text-lg font-medium">{stock.sector}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Industry</p>
              <p className="text-white text-lg font-medium">{stock.industry}</p>
            </div>
          </div>

          {/* Running Total Gains */}
          <div className="pt-4 border-t border-gray-700">
            <p className="text-gray-400 text-sm">Running Total Gains</p>
            <p
              className={`text-lg font-medium ${
                stock.running_total_gains >= 0
                  ? "text-green-500"
                  : "text-red-500"
              }`}
            >
              {stock.running_total_gains >= 0 ? "+" : ""}$
              {stock.running_total_gains?.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDetailsPopup;

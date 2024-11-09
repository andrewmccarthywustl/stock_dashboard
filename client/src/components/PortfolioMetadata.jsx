import React from "react";
import { formatCurrency } from "../utils/formatters";

// src/components/PortfolioMetadata.jsx
const PortfolioMetadata = ({ metadata = {} }) => {
  // Format beta values with proper precision
  const formatBeta = (beta) => {
    if (beta === undefined || beta === null) return "0.00";
    return Number(beta).toFixed(2);
  };

  // Format ratio properly
  const formatRatio = (ratio) => {
    if (ratio === "N/A") return "N/A";
    if (ratio === null || ratio === undefined) return "0.00";
    const numRatio = Number(ratio);
    if (isNaN(numRatio)) return "N/A";
    if (!isFinite(numRatio)) return "∞";
    return numRatio.toFixed(2);
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Portfolio Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Long Positions Value */}
        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Long Positions Value</p>
          <p className="text-2xl font-bold text-green-600">
            {formatCurrency(metadata.total_long_value || 0)}
          </p>
          <div className="mt-2 text-sm">
            <span className="text-gray-600">Positions: </span>
            <span className="font-medium">
              {metadata.long_positions_count || 0}
            </span>
          </div>
          <div className="mt-1 text-sm">
            <span className="text-gray-600">Beta: </span>
            <span className="font-medium">
              {formatBeta(metadata.long_beta_exposure)}
            </span>
          </div>
        </div>

        {/* Short Positions Value */}
        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Short Positions Value</p>
          <p className="text-2xl font-bold text-red-600">
            {formatCurrency(metadata.total_short_value || 0)}
          </p>
          <div className="mt-2 text-sm">
            <span className="text-gray-600">Positions: </span>
            <span className="font-medium">
              {metadata.short_positions_count || 0}
            </span>
          </div>
          <div className="mt-1 text-sm">
            <span className="text-gray-600">Beta: </span>
            <span className="font-medium">
              {formatBeta(metadata.short_beta_exposure)}
            </span>
          </div>
        </div>

        {/* Portfolio Metrics */}
        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Portfolio Metrics</p>
          <div className="mt-2">
            <div className="text-sm">
              <span className="text-gray-600">Long/Short Ratio: </span>
              <span className="font-medium">
                {formatRatio(metadata.long_short_ratio)}
              </span>
            </div>
          </div>
        </div>

        {/* Last Updated */}
        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Last Updated</p>
          <p className="text-lg">
            {new Date(metadata.last_updated).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PortfolioMetadata;

import React from "react";
import { formatCurrency } from "../utils/formatters";

const PortfolioMetadata = ({ metadata = {} }) => {
  const renderSectorAllocation = (sectors, title) => {
    if (!sectors) return null;

    return (
      <div className="mt-4">
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(sectors)
            .sort(([, a], [, b]) => b - a)
            .map(([sector, percentage]) => (
              <div key={sector} className="flex justify-between text-sm">
                <span className="text-gray-600">{sector}</span>
                <span className="font-medium">{percentage.toFixed(1)}%</span>
              </div>
            ))}
        </div>
      </div>
    );
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
            <span className="text-gray-600">Avg Beta: </span>
            <span className="font-medium">
              {metadata.weighted_long_beta?.toFixed(2) || "0.00"}
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
            <span className="text-gray-600">Avg Beta: </span>
            <span className="font-medium">
              {metadata.weighted_short_beta?.toFixed(2) || "0.00"}
            </span>
          </div>
        </div>

        {/* Long/Short Ratio and Total Realized Gains */}
        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Long/Short Ratio</p>
          <p className="text-2xl font-bold">
            {metadata.long_short_ratio === "N/A"
              ? "N/A"
              : metadata.long_short_ratio?.toFixed(2)}
          </p>
          <div className="mt-2">
            <p className="text-gray-600">Total Realized Gains</p>
            <p
              className={`text-lg font-bold ${
                metadata.total_realized_gains >= 0
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {formatCurrency(metadata.total_realized_gains)}
            </p>
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

      {/* Sector Allocations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        {/* Long Sectors */}
        {renderSectorAllocation(
          metadata.long_sectors,
          "Long Portfolio Sectors"
        )}
        {/* Short Sectors */}
        {renderSectorAllocation(
          metadata.short_sectors,
          "Short Portfolio Sectors"
        )}
      </div>
    </div>
  );
};

export default PortfolioMetadata;

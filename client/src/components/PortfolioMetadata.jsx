import React from "react";
import { formatCurrency } from "../utils/formatters";

const PortfolioMetadata = ({ metadata = {} }) => {
  const renderSectorAllocation = () => {
    if (!metadata.sectors) return null;

    return (
      <div className="mt-4">
        <h3 className="text-lg font-semibold mb-2">Sector Allocation</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(metadata.sectors)
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
        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Total Value</p>
          <p className="text-2xl font-bold">
            {formatCurrency(metadata.total_value)}
          </p>
        </div>

        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Total Realized Gains</p>
          <p
            className={`text-2xl font-bold ${
              metadata.total_realized_gains >= 0
                ? "text-green-600"
                : "text-red-600"
            }`}
          >
            {formatCurrency(metadata.total_realized_gains)}
          </p>
        </div>

        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Number of Positions</p>
          <p className="text-2xl font-bold">{metadata.total_positions || 0}</p>
        </div>

        <div className="p-4 bg-white rounded-lg shadow">
          <p className="text-gray-600">Last Updated</p>
          <p className="text-lg">
            {new Date(metadata.last_updated).toLocaleString()}
          </p>
        </div>
      </div>

      {renderSectorAllocation()}
    </div>
  );
};

export default PortfolioMetadata;

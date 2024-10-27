import React from "react";
import { formatCurrency } from "../utils/formatters";

const PortfolioList = ({ portfolioData = { stocks: [] } }) => {
  const { stocks = [] } = portfolioData;

  if (stocks.length === 0) {
    return (
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-4">Portfolio</h2>
        <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
          No positions in portfolio
        </div>
      </div>
    );
  }

  const getPositionColor = (type, value) => {
    if (type === "short") {
      return value >= 0
        ? "bg-red-100 text-red-800"
        : "bg-green-100 text-green-800";
    }
    return value >= 0
      ? "bg-green-100 text-green-800"
      : "bg-red-100 text-red-800";
  };

  return (
    <div className="mt-6">
      <h2 className="text-xl font-semibold mb-4">Portfolio</h2>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {stocks.map((stock) => (
          <div
            key={`${stock.symbol}-${stock.position_type}`}
            className="p-4 bg-white rounded-lg shadow"
          >
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center">
                <h3 className="text-lg font-bold">{stock.symbol}</h3>
                <span
                  className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                    stock.position_type === "short"
                      ? "bg-red-100 text-red-800"
                      : "bg-blue-100 text-blue-800"
                  }`}
                >
                  {stock.position_type === "short" ? "SHORT" : "LONG"}
                </span>
              </div>
              <span
                className={`px-2 py-1 rounded ${getPositionColor(
                  stock.position_type,
                  stock.running_total_gains
                )}`}
              >
                {stock.running_total_gains >= 0 ? "+" : ""}
                {formatCurrency(stock.running_total_gains)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <p className="text-gray-600">Quantity</p>
                <p>{stock.quantity}</p>
              </div>
              <div>
                <p className="text-gray-600">Current Price</p>
                <p>{formatCurrency(stock.current_price)}</p>
              </div>
              <div>
                <p className="text-gray-600">Cost Basis</p>
                <p>{formatCurrency(stock.cost_basis)}</p>
              </div>
              <div>
                <p className="text-gray-600">Market Value</p>
                <p>{formatCurrency(stock.quantity * stock.current_price)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-600">Sector</p>
                <p>{stock.sector}</p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-600">Industry</p>
                <p>{stock.industry}</p>
              </div>
              <div className="col-span-2">
                <div
                  className={`text-sm ${
                    stock.percent_change >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {stock.percent_change >= 0 ? "↑" : "↓"}{" "}
                  {Math.abs(stock.percent_change).toFixed(2)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioList;

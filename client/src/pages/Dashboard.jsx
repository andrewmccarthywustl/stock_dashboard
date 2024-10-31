// src/pages/Dashboard.jsx - Check the data structure
import React, { useState, useEffect } from "react";
import api from "../services/api";
import PortfolioMetadata from "../components/PortfolioMetadata";
import PortfolioList from "../components/PortfolioList";
import UpdatePriceButton from "../components/UpdatePriceButton";

const Dashboard = () => {
  const [portfolioData, setPortfolioData] = useState({
    metadata: {},
    stocks: [], // Changed from positions to stocks to match backend
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPortfolio = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.getPortfolio();
      // Transform the data structure if needed
      setPortfolioData({
        metadata: response.metadata,
        stocks: response.positions || [], // Map positions to stocks
      });
    } catch (error) {
      setError("Failed to load portfolio data");
      console.error("Error fetching portfolio:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
        <p>{error}</p>
        <button
          onClick={fetchPortfolio}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Portfolio Dashboard</h1>
        <UpdatePriceButton onPricesUpdated={fetchPortfolio} />
      </div>
      <PortfolioMetadata metadata={portfolioData.metadata} />
      <PortfolioList portfolioData={portfolioData} />
    </div>
  );
};

export default Dashboard;

import React, { useState } from "react";
import api from "../services/api";

const UpdatePriceButton = ({ onPricesUpdated }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleClick = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await api.updatePrices();
      if (onPricesUpdated) onPricesUpdated();
    } catch (error) {
      setError(error.response?.data?.error || "Error updating prices");
      console.error("Error updating prices:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {error && <div className="text-red-600 text-sm mb-2">{error}</div>}
      <button
        onClick={handleClick}
        disabled={isLoading}
        className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white 
          ${
            isLoading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          }`}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Updating...
          </>
        ) : (
          "Update Prices"
        )}
      </button>
    </div>
  );
};

export default UpdatePriceButton;

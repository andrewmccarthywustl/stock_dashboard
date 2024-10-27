import React, { useState } from "react";
import BuyStockForm from "../components/BuyStockForm";
import SellStockForm from "../components/SellStockForm";
import ShortStockForm from "../components/ShortStockForm";
import CoverShortForm from "../components/CoverShortForm";

const TradeEntry = () => {
  const [activeTab, setActiveTab] = useState("long"); // 'long' or 'short'

  const tabs = [
    { id: "long", label: "Long Positions" },
    { id: "short", label: "Short Positions" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Trade Entry</h1>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                ${
                  activeTab === tab.id
                    ? "border-indigo-500 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Long Position Forms */}
      {activeTab === "long" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Buy Stock</h2>
            <BuyStockForm />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Sell Stock</h2>
            <SellStockForm />
          </div>
        </div>
      )}

      {/* Short Position Forms */}
      {activeTab === "short" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Short Stock</h2>
            <ShortStockForm />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Cover Short</h2>
            <CoverShortForm />
          </div>
        </div>
      )}
    </div>
  );
};

export default TradeEntry;

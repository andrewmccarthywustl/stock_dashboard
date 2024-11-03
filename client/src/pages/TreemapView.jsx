// TreemapView.jsx
import React, { useState } from "react";
import PortfolioTreemap from "../components/PortfolioTreemap";

const TreemapView = () => {
  const [activeView, setActiveView] = useState("long");

  return (
    <div className="fixed inset-0 top-16">
      <div className="w-full h-full">
        <div className="w-full h-full">
          <div className="flex items-center justify-between px-4 py-2 bg-[#121212] border-b border-[#2A2A2A]">
            <div className="flex-1" />
            <div className="flex gap-6">
              <button
                className={`text-sm font-medium ${
                  activeView === "long" ? "text-white" : "text-gray-400"
                }`}
                onClick={() => setActiveView("long")}
              >
                Long Positions
              </button>
              <button
                className={`text-sm font-medium ${
                  activeView === "short" ? "text-white" : "text-gray-400"
                }`}
                onClick={() => setActiveView("short")}
              >
                Short Positions
              </button>
            </div>
            <div className="flex-1 text-right text-gray-400 text-sm">
              Last Updated: {new Date().toLocaleTimeString()}
            </div>
          </div>
          <div className="px-4">
            <PortfolioTreemap positionType={activeView} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TreemapView;

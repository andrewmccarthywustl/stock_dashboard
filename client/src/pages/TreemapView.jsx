import React, { useEffect, useRef } from "react";
import PortfolioTreemap from "../components/PortfolioTreemap";

const TreemapView = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      const { clientWidth, clientHeight } = containerRef.current;
      console.log("Container dimensions:", { clientWidth, clientHeight });
    }
  }, []);

  return (
    <div className="fixed inset-0 top-16 bg-[#121212]">
      <div
        ref={containerRef}
        className="w-full h-full p-2"
        style={{ height: "calc(100vh - 4rem)" }}
      >
        <div className="w-full h-full relative bg-[#121212] overflow-hidden border border-[#2A2A2A]">
          <div className="flex items-center justify-between px-4 py-2 border-b border-[#2A2A2A]">
            <h1 className="text-white text-lg font-medium">
              Portfolio Treemap
            </h1>
            <div className="text-gray-400 text-sm">
              Last Updated: {new Date().toLocaleTimeString()}
            </div>
          </div>
          <div className="absolute inset-0 top-10 p-2">
            <PortfolioTreemap />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TreemapView;

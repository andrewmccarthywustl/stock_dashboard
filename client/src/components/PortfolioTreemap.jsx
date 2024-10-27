// src/components/PortfolioTreemap/PortfolioTreemap.jsx
import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import axios from "axios";

const PortfolioTreemap = () => {
  const svgRef = useRef(null);
  const [portfolioData, setPortfolioData] = useState({ stocks: [] });
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [error, setError] = useState(null);

  // Sector abbreviations
  const sectorAbbreviations = {
    Technology: "TECH",
    Healthcare: "HLTH",
    Industrials: "INDU",
    "Consumer Discretionary": "COND",
    "Consumer Staples": "CONS",
    Energy: "ENGY",
    Materials: "MAT",
    Finance: "FIN",
    "Real Estate": "REAL",
    Utilities: "UTIL",
    "Communication Services": "COMM",
    Unknown: "UNK",
  };

  // Percentage-based color scale
  const getPercentageColor = (percentage) => {
    const p = Number(percentage);

    if (p <= -10) return "#632726"; // Darker red
    if (p <= -5) return "#892E2D"; // Dark red
    if (p <= -2) return "#AA3937"; // Medium red
    if (p < 0) return "#C44"; // Light red
    if (p === 0) return "#1F2937"; // Neutral
    if (p <= 2) return "#255D3A"; // Light green
    if (p <= 5) return "#1E4D30"; // Medium green
    if (p <= 10) return "#194227"; // Dark green
    return "#143C22"; // Darker green
  };

  // Sector colors
  const sectorColors = {
    Technology: "#2A3441",
    Healthcare: "#2D3440",
    Industrials: "#2C3440",
    "Consumer Discretionary": "#2E3441",
    "Consumer Staples": "#2D3339",
    Energy: "#2C3338",
    Materials: "#2B3338",
    Finance: "#2A3337",
    "Real Estate": "#293336",
    Utilities: "#283235",
    "Communication Services": "#273134",
    Unknown: "#263033",
  };

  // Dimension handling
  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const container = svgRef.current.parentElement;
        const width = container.clientWidth;
        const height = container.clientHeight;
        console.log("Setting dimensions:", { width, height });
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  // Data fetching
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("/api/get-portfolio");
        console.log("Portfolio data fetched:", response.data);
        setPortfolioData(response.data);
      } catch (error) {
        console.error("Error fetching portfolio:", error);
        setError(error.message);
      }
    };

    fetchData();
  }, []);

  // Data transformation
  const transformDataForD3 = (stocks) => {
    const sectors = {};

    stocks.forEach((stock) => {
      const sector = stock.sector || "Unknown";
      if (!sectors[sector]) {
        sectors[sector] = [];
      }

      sectors[sector].push({
        name: stock.symbol.toUpperCase(),
        value: stock.quantity * stock.current_price,
        percentChange: stock.percent_change,
        industry: stock.industry || "Unknown",
      });
    });

    const totalValue = Object.values(sectors)
      .flat()
      .reduce((sum, stock) => sum + stock.value, 0);

    return {
      name: "Portfolio",
      children: Object.entries(sectors)
        .filter(([_, stocks]) => stocks.length > 0)
        .map(([sector, stocks]) => {
          const sectorTotal = stocks.reduce(
            (sum, stock) => sum + stock.value,
            0
          );
          const sectorPercentage = ((sectorTotal / totalValue) * 100).toFixed(
            1
          );
          return {
            name: sector,
            children: stocks,
            total: sectorTotal,
            percentage: sectorPercentage,
          };
        })
        .sort((a, b) => b.total - a.total),
    };
  };

  // Treemap creation
  useEffect(() => {
    if (
      !portfolioData.stocks?.length ||
      !dimensions.width ||
      !dimensions.height
    ) {
      console.log("Missing required data:", {
        hasStocks: Boolean(portfolioData.stocks?.length),
        width: dimensions.width,
        height: dimensions.height,
      });
      return;
    }

    console.log("Creating treemap with dimensions:", dimensions);

    const createTreemap = () => {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();

      svg
        .attr("width", dimensions.width)
        .attr("height", dimensions.height)
        .style("font-family", "Inter, sans-serif")
        .style("background-color", "#121212");

      const data = transformDataForD3(portfolioData.stocks);

      const root = d3
        .hierarchy(data)
        .sum((d) => d.value)
        .sort((a, b) => b.value - a.value);

      const treemapLayout = d3
        .treemap()
        .size([dimensions.width, dimensions.height])
        .paddingTop(24)
        .paddingInner(1)
        .round(true);

      treemapLayout(root);

      // Create sectors
      const sectors = svg
        .selectAll("g.sector")
        .data(root.children)
        .join("g")
        .attr("class", "sector");

      // Sector backgrounds
      sectors
        .append("rect")
        .attr("x", (d) => d.x0)
        .attr("y", (d) => d.y0)
        .attr("width", (d) => d.x1 - d.x0)
        .attr("height", (d) => d.y1 - d.y0)
        .attr("fill", (d) => sectorColors[d.data.name])
        .attr("stroke", "#2A2A2A")
        .attr("stroke-width", 1);

      // Sector headers
      sectors
        .append("rect")
        .attr("x", (d) => d.x0)
        .attr("y", (d) => d.y0)
        .attr("width", (d) => d.x1 - d.x0)
        .attr("height", 24)
        .attr("fill", (d) => sectorColors[d.data.name])
        .attr("opacity", 0.8);

      // Sector titles with truncation
      sectors.each(function (d) {
        const sectorGroup = d3.select(this);
        const width = d.x1 - d.x0 - 16; // Available width minus padding
        const fullText = `${d.data.name.toUpperCase()} ${d.data.percentage}%`;
        const abbreviated = `${sectorAbbreviations[d.data.name]} ${
          d.data.percentage
        }%`;

        // Create a temporary text element to measure text width
        const tempText = svg
          .append("text")
          .attr("font-size", "11px")
          .text(fullText);

        const textWidth = tempText.node().getComputedTextLength();
        tempText.remove();

        // Add the actual text element
        sectorGroup
          .append("text")
          .attr("x", d.x0 + 8)
          .attr("y", d.y0 + 16)
          .attr("fill", "#FFFFFF")
          .attr("font-size", "11px")
          .attr("font-weight", "500")
          .text(textWidth > width ? abbreviated : fullText);
      });

      // Create stock tiles
      const stocks = sectors
        .selectAll("g.stock")
        .data((d) => d.leaves())
        .join("g")
        .attr("class", "stock");

      // Stock backgrounds
      stocks
        .append("rect")
        .attr("x", (d) => d.x0)
        .attr("y", (d) => d.y0)
        .attr("width", (d) => d.x1 - d.x0)
        .attr("height", (d) => d.y1 - d.y0)
        .attr("fill", (d) => getPercentageColor(d.data.percentChange))
        .attr("stroke", "#1A1A1A")
        .attr("stroke-width", 0.5);

      // Stock symbol
      stocks
        .append("text")
        .attr("x", (d) => (d.x0 + d.x1) / 2)
        .attr("y", (d) => (d.y0 + d.y1) / 2 - 8)
        .attr("text-anchor", "middle")
        .text((d) => d.data.name)
        .attr("fill", "#FFFFFF")
        .attr("font-weight", "bold")
        .attr("font-size", "12px");

      // Percentage change
      stocks
        .append("text")
        .attr("x", (d) => (d.x0 + d.x1) / 2)
        .attr("y", (d) => (d.y0 + d.y1) / 2 + 8)
        .attr("text-anchor", "middle")
        .text(
          (d) =>
            `${
              d.data.percentChange >= 0 ? "+" : ""
            }${d.data.percentChange.toFixed(2)}%`
        )
        .attr("fill", "#FFFFFF")
        .attr("font-size", "11px");

      // Industry label
      stocks
        .append("text")
        .attr("x", (d) => (d.x0 + d.x1) / 2)
        .attr("y", (d) => (d.y0 + d.y1) / 2 + 22)
        .attr("text-anchor", "middle")
        .text((d) => d.data.industry)
        .attr("fill", "#999999")
        .attr("font-size", "9px");
    };

    createTreemap();
  }, [portfolioData, dimensions]);

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-[#121212] text-white">
        <div className="text-center">
          <h3 className="text-xl mb-2">Error Loading Treemap</h3>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-[#121212]">
      <svg
        ref={svgRef}
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
      />
    </div>
  );
};

export default PortfolioTreemap;

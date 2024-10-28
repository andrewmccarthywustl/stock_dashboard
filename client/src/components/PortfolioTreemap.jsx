// PortfolioTreemap.jsx
import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import axios from "axios";
import StockDetailsPopup from "./StockDetailsPopup";

const PortfolioTreemap = ({ positionType = "long" }) => {
  const svgRef = useRef(null);
  const [portfolioData, setPortfolioData] = useState({ stocks: [] });
  const [hoveredId, setHoveredId] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);

  // Abbreviations for sectors and stock names
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

  // Abbreviate stock name if needed
  const getAbbreviatedName = (name, width) => {
    if (width < 50 && name.length > 4) {
      return name.substring(0, 4);
    }
    return name;
  };

  // Percentage-based color scale
  const getPercentageColor = (percentage, isShort = false) => {
    const p = Number(percentage);

    if (isShort) {
      if (p >= 10) return "#4c1d95";
      if (p >= 5) return "#5b21b6";
      if (p >= 2) return "#6d28d9";
      if (p > 0) return "#7c3aed";
      if (p === 0) return "#1F2937";
      if (p >= -2) return "#60a5fa";
      if (p >= -5) return "#3b82f6";
      if (p >= -10) return "#2563eb";
      return "#1e3a8a";
    } else {
      if (p <= -10) return "#632726";
      if (p <= -5) return "#892E2D";
      if (p <= -2) return "#AA3937";
      if (p < 0) return "#C44";
      if (p === 0) return "#1F2937";
      if (p <= 2) return "#255D3A";
      if (p <= 5) return "#1E4D30";
      if (p <= 10) return "#194227";
      return "#143C22";
    }
  };

  // Data fetching
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("/api/portfolio/get-portfolio");
        setPortfolioData(response.data);
      } catch (error) {
        console.error("Error fetching portfolio:", error);
      }
    };

    fetchData();
  }, []);

  // Handle stock selection
  const handleStockClick = (stock) => {
    const fullStockData = portfolioData.stocks.find(
      (s) => s.symbol === stock.name && s.position_type === positionType
    );
    setSelectedStock(fullStockData);
  };

  useEffect(() => {
    if (!portfolioData.stocks?.length) return;

    // Filter stocks based on position type
    const filteredStocks = portfolioData.stocks.filter(
      (stock) => stock.position_type === positionType
    );

    // Clear previous SVG
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // If no positions exist, display the message
    if (filteredStocks.length === 0) {
      const container = svgRef.current.parentElement;
      const width = container.clientWidth;
      const height = container.clientHeight;

      svg
        .attr("width", width)
        .attr("height", height)
        .style("background", "#121212");

      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .style("fill", "#6B7280") // Using Tailwind's gray-500 color
        .style("font-size", "16px")
        .style("font-family", "Inter, sans-serif")
        .text(`No ${positionType} positions in portfolio`);

      return;
    }

    // Get container dimensions
    const container = svgRef.current.parentElement;
    const width = container.clientWidth;
    const height = container.clientHeight;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Set SVG dimensions
    svg
      .attr("width", width)
      .attr("height", height)
      .style("background", "#121212")
      .style("font-family", "Inter, sans-serif");

    // Create group for margins
    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Transform data to hierarchy structure
    const data = {
      name: "Portfolio",
      children: Array.from(
        d3.group(filteredStocks, (d) => d.sector || "Unknown"),
        ([key, values]) => ({
          name: key,
          children: values.map((stock) => ({
            name: stock.symbol,
            value: stock.position_value,
            percentChange: stock.percent_change,
            beta: stock.beta || 0,
            id: `${stock.symbol}-${stock.position_type}`,
          })),
        })
      ),
    };

    // Create hierarchy and treemap layout
    const root = d3
      .hierarchy(data)
      .sum((d) => d.value)
      .sort((a, b) => b.value - a.value);

    const treemap = d3
      .treemap()
      .size([
        width - margin.left - margin.right,
        height - margin.top - margin.bottom,
      ])
      .paddingTop(20)
      .paddingInner(1);

    treemap(root);

    // Create groups for each leaf
    const leaf = g
      .selectAll("g")
      .data(root.leaves())
      .join("g")
      .attr("transform", (d) => `translate(${d.x0},${d.y0})`)
      .style("cursor", "pointer");

    // Add rectangles
    leaf
      .append("rect")
      .attr("id", (d) => d.data.id)
      .attr("width", (d) => d.x1 - d.x0)
      .attr("height", (d) => d.y1 - d.y0)
      .attr("fill", (d) =>
        getPercentageColor(d.data.percentChange, positionType === "short")
      )
      .style("stroke", (d) => (hoveredId === d.data.id ? "#ffffff" : "#121212")) // White border on hover
      .style("stroke-width", (d) => (hoveredId === d.data.id ? "2" : "1")) // Thicker border on hover
      .attr("opacity", (d) => (hoveredId && hoveredId !== d.data.id ? 0.7 : 1))
      .on("mouseenter", (event, d) => setHoveredId(d.data.id))
      .on("mouseleave", () => setHoveredId(null))
      .on("click", (event, d) => {
        event.stopPropagation();
        handleStockClick(d.data);
      });

    // Add sector labels
    root.children?.forEach((sector) => {
      const sectorX = sector.x0;
      const sectorY = sector.y0;
      const sectorWidth = sector.x1 - sector.x0;

      // Calculate sector percentage
      const sectorPercentage = ((sector.value / root.value) * 100).toFixed(1);
      const sectorName =
        sectorWidth < 100
          ? sectorAbbreviations[sector.data.name] || sector.data.name
          : sector.data.name;

      g.append("rect")
        .attr("x", sectorX)
        .attr("y", sectorY)
        .attr("width", sectorWidth) // Add some padding
        .attr("height", 20)
        .attr("fill", "#1f1f1f") // Background color
        .attr("rx", 2);
      g.append("text")
        .attr("x", sectorX + 4)
        .attr("y", sectorY + 14)
        .attr("fill", "#808080")
        .style("font-size", "12px")
        .text(`${sectorName} ${sectorPercentage}%`);
    });

    // Add stock labels
    leaf.each(function (d) {
      const width = d.x1 - d.x0;
      const height = d.y1 - d.y0;
      const g = d3.select(this);

      if (width < 30 || height < 30) return;

      // Create a group for the text elements
      const textGroup = g.append("g").on("click", (event) => {
        event.stopPropagation();
        handleStockClick(d.data);
      });

      // Symbol
      const symbolName = getAbbreviatedName(d.data.name, width);
      textGroup
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2 - 10)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .style("font-weight", "bold")
        .style("font-size", "12px")
        .text(symbolName);

      // Percentage
      textGroup
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2 + 10)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .style("font-size", "12px")
        .text(
          `${
            d.data.percentChange >= 0 ? "+" : ""
          }${d.data.percentChange.toFixed(2)}%`
        );

      // Beta (if enough space)
      if (height >= 70) {
        textGroup
          .append("text")
          .attr("x", width / 2)
          .attr("y", height / 2 + 25)
          .attr("text-anchor", "middle")
          .attr("fill", "#666666")
          .style("font-size", "11px")
          .text(`β: ${d.data.beta.toFixed(2)}`);
      }
    });
  }, [portfolioData, positionType, hoveredId]);

  return (
    <div className="absolute inset-0 top-10" style={{ background: "#121212" }}>
      <svg
        ref={svgRef}
        className="w-full h-full"
        onClick={() => setSelectedStock(null)}
      />
      {selectedStock && (
        <StockDetailsPopup
          stock={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}
    </div>
  );
};

export default PortfolioTreemap;

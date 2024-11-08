// src/components/__tests__/PortfolioMetadata.test.jsx
import React from "react";
import { render, screen } from "@testing-library/react";
import PortfolioMetadata from "../PortfolioMetadata";

describe("PortfolioMetadata", () => {
  const mockMetadata = {
    total_long_value: 100000,
    total_short_value: 50000,
    long_positions_count: 5,
    short_positions_count: 3,
    long_beta_exposure: 1.2,
    short_beta_exposure: 2.5,
    net_beta_exposure: -1.3,
    long_short_ratio: 2.0,
    long_sectors: {
      Technology: 60.5,
      Healthcare: 39.5,
    },
    short_sectors: {
      "Consumer Cyclical": 100,
    },
    last_updated: "2024-01-01T12:00:00Z",
  };

  it("renders portfolio metrics correctly", () => {
    render(<PortfolioMetadata metadata={mockMetadata} />);
    expect(screen.getByText("$100,000.00")).toBeInTheDocument();
    expect(screen.getByText("$50,000.00")).toBeInTheDocument();
  });
});

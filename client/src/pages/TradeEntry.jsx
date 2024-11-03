import React from "react";
import TradeForm from "../components/TradeForm";

const TradeEntry = () => {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Trade Entry</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <TradeForm />
      </div>
    </div>
  );
};

export default TradeEntry;

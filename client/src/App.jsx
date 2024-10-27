// src/App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import TreemapView from "./pages/TreemapView";
import TransactionHistory from "./pages/TransactionHistory";
import TradeEntry from "./pages/TradeEntry";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <main className="relative">
          {" "}
          {/* Remove default padding for treemap page */}
          <Routes>
            {/* Other routes keep their padding */}
            <Route
              path="/"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <Dashboard />
                </div>
              }
            />
            {/* Treemap route takes full width/height */}
            <Route path="/treemap" element={<TreemapView />} />
            <Route
              path="/transactions"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <TransactionHistory />
                </div>
              }
            />
            <Route
              path="/trade"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <TradeEntry />
                </div>
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

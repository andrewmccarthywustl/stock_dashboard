// src/App.jsx
import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { TransactionProvider } from "./contexts/TransactionContext";
import Header from "./components/Header";
import ErrorBoundary, { ErrorFallback } from "./components/ErrorBoundary";
import LoadingSpinner from "./components/LoadingSpinner";
import { logError } from "./utils/logger";

// Lazy load pages for better performance
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const TreemapView = React.lazy(() => import("./pages/TreemapView"));
const TransactionHistory = React.lazy(() =>
  import("./pages/TransactionHistory")
);
const TradeEntry = React.lazy(() => import("./pages/TradeEntry"));

// Fallback loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="large" />
  </div>
);

function App() {
  // Error handler for the entire app
  const handleError = (error, errorInfo) => {
    logError("App Error:", { error, errorInfo });
  };

  return (
    <ErrorBoundary onError={handleError} FallbackComponent={ErrorFallback}>
      <TransactionProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-gray-100">
            <Header />
            <Suspense fallback={<PageLoader />}>
              <main className="relative">
                <Routes>
                  {/* Dashboard Route */}
                  <Route
                    path="/"
                    element={
                      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                        <ErrorBoundary
                          FallbackComponent={ErrorFallback}
                          onError={(error) =>
                            logError("Dashboard Error:", error)
                          }
                        >
                          <Dashboard />
                        </ErrorBoundary>
                      </div>
                    }
                  />

                  {/* Treemap Route */}
                  <Route
                    path="/treemap"
                    element={
                      <ErrorBoundary
                        FallbackComponent={ErrorFallback}
                        onError={(error) => logError("Treemap Error:", error)}
                      >
                        <TreemapView />
                      </ErrorBoundary>
                    }
                  />

                  {/* Transactions Route */}
                  <Route
                    path="/transactions"
                    element={
                      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                        <ErrorBoundary
                          FallbackComponent={ErrorFallback}
                          onError={(error) =>
                            logError("Transactions Error:", error)
                          }
                        >
                          <TransactionHistory />
                        </ErrorBoundary>
                      </div>
                    }
                  />

                  {/* Trade Entry Route */}
                  <Route
                    path="/trade"
                    element={
                      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                        <ErrorBoundary
                          FallbackComponent={ErrorFallback}
                          onError={(error) =>
                            logError("Trade Entry Error:", error)
                          }
                        >
                          <TradeEntry />
                        </ErrorBoundary>
                      </div>
                    }
                  />

                  {/* 404 Route */}
                  <Route
                    path="*"
                    element={
                      <div className="min-h-screen flex items-center justify-center">
                        <div className="text-center">
                          <h2 className="text-2xl font-bold text-gray-900 mb-4">
                            Page Not Found
                          </h2>
                          <p className="text-gray-600 mb-4">
                            The page you're looking for doesn't exist or has
                            been moved.
                          </p>
                          <Link
                            to="/"
                            className="text-indigo-600 hover:text-indigo-500"
                          >
                            Go back home
                          </Link>
                        </div>
                      </div>
                    }
                  />
                </Routes>
              </main>
            </Suspense>
          </div>
        </BrowserRouter>
      </TransactionProvider>
    </ErrorBoundary>
  );
}

export default App;

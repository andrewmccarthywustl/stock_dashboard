// src/components/ErrorBoundary.jsx
import React from "react";
import { logError } from "../utils/logger";

// Error fallback component
export const ErrorFallback = ({ error }) => (
  <div className="min-h-screen flex items-center justify-center bg-red-50">
    <div className="text-center p-8 rounded-lg bg-white shadow-lg">
      <h2 className="text-2xl font-bold text-red-600 mb-4">
        Something went wrong
      </h2>
      <p className="text-gray-600 mb-4">{error.message}</p>
      <button
        onClick={() => window.location.reload()}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
      >
        Refresh Page
      </button>
    </div>
  </div>
);

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    logError("Error Boundary caught error:", { error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.FallbackComponent || ErrorFallback;
      return <FallbackComponent error={this.state.error} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

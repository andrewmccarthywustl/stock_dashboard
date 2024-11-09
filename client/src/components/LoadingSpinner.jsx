// src/components/LoadingSpinner.jsx
import React from "react";
import PropTypes from "prop-types";

const LoadingSpinner = ({
  size = "medium",
  text = "Loading...",
  fullScreen = false,
  className = "",
}) => {
  const sizeClasses = {
    small: "h-4 w-4",
    medium: "h-8 w-8",
    large: "h-12 w-12",
  };

  const containerClasses = fullScreen
    ? "fixed inset-x-0 top-16 bottom-0 flex items-center justify-center bg-gray-900"
    : "flex items-center justify-center p-4";

  return (
    <div className={`${containerClasses} ${className}`}>
      <div className="flex flex-col items-center space-y-4">
        <div
          className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-gray-200 border-t-indigo-600`}
        />
        {text && <span className="text-gray-200 font-medium">{text}</span>}
      </div>
    </div>
  );
};

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(["small", "medium", "large"]),
  text: PropTypes.string,
  fullScreen: PropTypes.bool,
  className: PropTypes.string,
};

export default LoadingSpinner;

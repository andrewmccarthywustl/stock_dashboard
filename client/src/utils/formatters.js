// src/utils/formatters.js
import { logError } from "./logger";

/**
 * Format a number as currency
 * @param {number|string} value - The value to format
 * @param {Object} options - Formatting options
 * @param {string} options.currency - Currency code (default: 'USD')
 * @param {number} options.minimumFractionDigits - Minimum decimal places (default: 2)
 * @param {number} options.maximumFractionDigits - Maximum decimal places (default: 2)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value, options = {}) => {
  try {
    if (value === null || value === undefined) {
      return "-";
    }

    const {
      currency = "USD",
      minimumFractionDigits = 2,
      maximumFractionDigits = 2,
    } = options;

    // Convert string to number if needed
    const numericValue = typeof value === "string" ? parseFloat(value) : value;

    if (isNaN(numericValue)) {
      logError("Invalid currency value:", value);
      return "-";
    }

    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits,
      maximumFractionDigits,
    }).format(numericValue);
  } catch (error) {
    logError("Error formatting currency:", error);
    return `$${Number(value).toFixed(2)}`;
  }
};

/**
 * Format a date string
 * @param {string|Date} dateString - The date to format
 * @param {Object} options - Formatting options
 * @param {boolean} options.includeTime - Whether to include time (default: false)
 * @param {string} options.locale - Locale code (default: 'en-US')
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, options = {}) => {
  try {
    if (!dateString) {
      return "-";
    }

    const { includeTime = false, locale = "en-US" } = options;

    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
      logError("Invalid date value:", dateString);
      return "-";
    }

    const formatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric",
      ...(includeTime && {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
    };

    return date.toLocaleDateString(locale, formatOptions);
  } catch (error) {
    logError("Error formatting date:", error);
    return dateString || "-";
  }
};

/**
 * Format a number as a percentage
 * @param {number|string} value - The value to format
 * @param {Object} options - Formatting options
 * @param {number} options.decimals - Number of decimal places (default: 2)
 * @param {boolean} options.includeSymbol - Whether to include % symbol (default: true)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, options = {}) => {
  try {
    if (value === null || value === undefined) {
      return "-";
    }

    const { decimals = 2, includeSymbol = true } = options;

    // Convert string to number if needed
    const numericValue = typeof value === "string" ? parseFloat(value) : value;

    if (isNaN(numericValue)) {
      logError("Invalid percentage value:", value);
      return "-";
    }

    const formattedNumber = numericValue.toFixed(decimals);
    return includeSymbol ? `${formattedNumber}%` : formattedNumber;
  } catch (error) {
    logError("Error formatting percentage:", error);
    return `${Number(value).toFixed(2)}%`;
  }
};

/**
 * Format a number with thousands separators
 * @param {number|string} value - The value to format
 * @param {Object} options - Formatting options
 * @param {number} options.decimals - Number of decimal places (default: 0)
 * @param {string} options.locale - Locale code (default: 'en-US')
 * @returns {string} Formatted number string
 */
export const formatNumber = (value, options = {}) => {
  try {
    if (value === null || value === undefined) {
      return "-";
    }

    const { decimals = 0, locale = "en-US" } = options;

    // Convert string to number if needed
    const numericValue = typeof value === "string" ? parseFloat(value) : value;

    if (isNaN(numericValue)) {
      logError("Invalid numeric value:", value);
      return "-";
    }

    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(numericValue);
  } catch (error) {
    logError("Error formatting number:", error);
    return value?.toString() || "-";
  }
};

/**
 * Format a file size in bytes to human readable format
 * @param {number} bytes - The file size in bytes
 * @param {Object} options - Formatting options
 * @param {number} options.decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted file size string
 */
export const formatFileSize = (bytes, options = {}) => {
  try {
    if (bytes === 0) return "0 Bytes";
    if (!bytes) return "-";

    const { decimals = 2 } = options;
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${
      sizes[i]
    }`;
  } catch (error) {
    logError("Error formatting file size:", error);
    return `${bytes} Bytes`;
  }
};

/**
 * Format a duration in milliseconds to human readable format
 * @param {number} ms - Duration in milliseconds
 * @param {Object} options - Formatting options
 * @param {boolean} options.short - Use short format (default: false)
 * @returns {string} Formatted duration string
 */
export const formatDuration = (ms, options = {}) => {
  try {
    if (!ms && ms !== 0) return "-";

    const { short = false } = options;

    const seconds = Math.floor((ms / 1000) % 60);
    const minutes = Math.floor((ms / (1000 * 60)) % 60);
    const hours = Math.floor((ms / (1000 * 60 * 60)) % 24);
    const days = Math.floor(ms / (1000 * 60 * 60 * 24));

    if (short) {
      return [
        days && `${days}d`,
        hours && `${hours}h`,
        minutes && `${minutes}m`,
        seconds && `${seconds}s`,
      ]
        .filter(Boolean)
        .join(" ");
    }

    return [
      days && `${days} day${days !== 1 ? "s" : ""}`,
      hours && `${hours} hour${hours !== 1 ? "s" : ""}`,
      minutes && `${minutes} minute${minutes !== 1 ? "s" : ""}`,
      seconds && `${seconds} second${seconds !== 1 ? "s" : ""}`,
    ]
      .filter(Boolean)
      .join(", ");
  } catch (error) {
    logError("Error formatting duration:", error);
    return ms?.toString() || "-";
  }
};

export default {
  formatCurrency,
  formatDate,
  formatPercentage,
  formatNumber,
  formatFileSize,
  formatDuration,
};

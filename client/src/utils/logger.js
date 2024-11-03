// src/utils/logger.js

/**
 * Log levels with corresponding styles for console output
 */
const LOG_LEVELS = {
  DEBUG: {
    name: "DEBUG",
    color: "#7986CB",
    background: "#E8EAF6",
    style:
      "color: #7986CB; background: #E8EAF6; padding: 2px 5px; border-radius: 3px;",
  },
  INFO: {
    name: "INFO",
    color: "#4CAF50",
    background: "#E8F5E9",
    style:
      "color: #4CAF50; background: #E8F5E9; padding: 2px 5px; border-radius: 3px;",
  },
  WARN: {
    name: "WARN",
    color: "#FFA000",
    background: "#FFF3E0",
    style:
      "color: #FFA000; background: #FFF3E0; padding: 2px 5px; border-radius: 3px;",
  },
  ERROR: {
    name: "ERROR",
    color: "#D32F2F",
    background: "#FFEBEE",
    style:
      "color: #D32F2F; background: #FFEBEE; padding: 2px 5px; border-radius: 3px;",
  },
};

/**
 * Current environment (development/production)
 */
const IS_DEVELOPMENT = process.env.NODE_ENV === "development";

/**
 * Maximum length for logged objects before truncation
 */
const MAX_OBJECT_LENGTH = 1000;

/**
 * Format a timestamp for logging
 * @returns {string} Formatted timestamp
 */
const getTimestamp = () => {
  return new Date().toISOString();
};

/**
 * Safely stringify an object for logging
 * @param {any} data - The data to stringify
 * @returns {string} Stringified data
 */
const safeStringify = (data) => {
  try {
    if (data === undefined) return "undefined";
    if (data === null) return "null";

    if (typeof data === "object") {
      const stringified = JSON.stringify(data, null, 2);
      if (stringified.length > MAX_OBJECT_LENGTH) {
        return stringified.substring(0, MAX_OBJECT_LENGTH) + "... (truncated)";
      }
      return stringified;
    }

    return String(data);
  } catch (error) {
    return `[Unable to stringify: ${error.message}]`;
  }
};

/**
 * Create a log entry with consistent formatting
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {any} [data] - Additional data to log
 * @param {Error} [error] - Error object if applicable
 */
const createLogEntry = (level, message, data = null, error = null) => {
  const logLevel = LOG_LEVELS[level];
  const timestamp = getTimestamp();

  // Base console styling
  const baseStyle = logLevel.style;

  // Format the message
  let formattedMessage = `[${timestamp}] %c${logLevel.name}%c ${message}`;
  const styles = [baseStyle, ""];

  // Add data if present
  if (data !== null) {
    formattedMessage += "\nData:";
    console.groupCollapsed(formattedMessage, ...styles);
    console.log(data);
    console.groupEnd();
  } else {
    console.log(formattedMessage, ...styles);
  }

  // Add error details if present
  if (error) {
    console.group("Error Details:");
    console.error(error);
    if (error.stack) {
      console.log("Stack Trace:", error.stack);
    }
    console.groupEnd();
  }

  // Log to backend or monitoring service in production
  if (!IS_DEVELOPMENT) {
    // Here you would add code to send logs to your backend or monitoring service
    // Example: sendToLoggingService({ level, message, data, error, timestamp });
  }
};

/**
 * Debug level logging
 * @param {string} message - Log message
 * @param {any} [data] - Additional data to log
 */
export const logDebug = (message, data = null) => {
  if (IS_DEVELOPMENT) {
    createLogEntry("DEBUG", message, data);
  }
};

/**
 * Info level logging
 * @param {string} message - Log message
 * @param {any} [data] - Additional data to log
 */
export const logInfo = (message, data = null) => {
  createLogEntry("INFO", message, data);
};

/**
 * Warning level logging
 * @param {string} message - Log message
 * @param {any} [data] - Additional data to log
 */
export const logWarn = (message, data = null) => {
  createLogEntry("WARN", message, data);
};

/**
 * Error level logging
 * @param {string} message - Log message
 * @param {Error|any} error - Error object or error data
 */
export const logError = (message, error = null) => {
  if (error instanceof Error) {
    createLogEntry("ERROR", message, null, error);
  } else {
    createLogEntry("ERROR", message, error);
  }
};

/**
 * Group related logs together
 * @param {string} label - Group label
 * @param {Function} callback - Callback containing grouped logs
 * @param {boolean} [collapsed=true] - Whether to collapse the group by default
 */
export const logGroup = (label, callback, collapsed = true) => {
  if (collapsed) {
    console.groupCollapsed(label);
  } else {
    console.group(label);
  }

  try {
    callback();
  } finally {
    console.groupEnd();
  }
};

/**
 * Log performance measurements
 * @param {string} label - Measurement label
 * @param {Function} callback - Function to measure
 * @returns {Promise<any>} Result of the callback
 */
export const logPerformance = async (label, callback) => {
  const start = performance.now();
  try {
    const result = await callback();
    const duration = performance.now() - start;
    logInfo(`Performance: ${label}`, { duration: `${duration.toFixed(2)}ms` });
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    logError(`Performance Error: ${label}`, {
      error,
      duration: `${duration.toFixed(2)}ms`,
    });
    throw error;
  }
};

export default {
  logDebug,
  logInfo,
  logWarn,
  logError,
  logGroup,
  logPerformance,
};

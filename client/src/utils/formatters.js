export const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
};

export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

export const formatPercentage = (value) => {
  return `${(value || 0).toFixed(2)}%`;
};

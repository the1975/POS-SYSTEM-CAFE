// QR hanya untuk order yang siap diambil. Token pickup dari backend hanya ada pada status itu.
export const QR_STATUSES = ["READY", "OVERDUE"];

export const shouldShowPickupQr = (order) =>
  Boolean(order?.pickup_token) && QR_STATUSES.includes(order.status);

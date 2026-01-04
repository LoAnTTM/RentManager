// Format currency (VND)
export function formatCurrency(amount: number | string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(num);
}

// Format number
export function formatNumber(num: number | string): string {
  const n = typeof num === 'string' ? parseFloat(num) : num;
  return new Intl.NumberFormat('vi-VN').format(n);
}

// Format date
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(d);
}

// Get month name
export function getMonthName(month: number): string {
  const months = [
    'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4',
    'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8',
    'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
  ];
  return months[month - 1] || '';
}

// Get current month/year
export function getCurrentPeriod(): { month: number; year: number } {
  const now = new Date();
  return {
    month: now.getMonth() + 1,
    year: now.getFullYear(),
  };
}

// Room status labels
export const roomStatusLabels: Record<string, string> = {
  vacant: 'Trống',
  occupied: 'Đang thuê',
};

// Invoice status labels
export const invoiceStatusLabels: Record<string, string> = {
  unpaid: 'Chưa thu',
  partial: 'Thu một phần',
  paid: 'Đã thu',
};

// Expense category labels
export const expenseCategoryLabels: Record<string, string> = {
  repair: 'Sửa chữa',
  utility: 'Điện nước chung',
  maintenance: 'Bảo trì',
  other: 'Khác',
};

// Meter type labels
export const meterTypeLabels: Record<string, string> = {
  electric: 'Điện',
  water: 'Nước',
};

// Fee labels
export const feeLabels: Record<string, string> = {
  room_fee: 'Tiền phòng',
  electric_fee: 'Tiền điện',
  water_fee: 'Tiền nước',
  garbage_fee: 'Tiền rác',
  wifi_fee: 'Tiền wifi',
  tv_fee: 'Tiền TV',
  laundry_fee: 'Tiền giặt',
  other_fee: 'Phí khác',
  previous_debt: 'Nợ tháng trước',
  previous_credit: 'Thừa tháng trước',
  absent_deduction: 'Trừ ngày vắng',
};

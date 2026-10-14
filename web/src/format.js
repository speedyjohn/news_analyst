const MONTHS = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
];

export function isoDate(value) {
  const d = value instanceof Date ? value : new Date(value);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function longDate(value) {
  if (!value) return '';
  const d = new Date(value);
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

export function shortDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  return `${d.getDate()} ${MONTHS[d.getMonth()]}`;
}

export function numericDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`;
}

export function timeOnly(value) {
  if (!value) return '';
  const d = new Date(value);
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function shiftDay(isoValue, days) {
  const d = new Date(`${isoValue}T12:00:00`);
  d.setDate(d.getDate() + days);
  return isoDate(d);
}

export function score(value) {
  return value == null ? '—' : (value / 10).toFixed(1);
}

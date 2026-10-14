export const BADGE = {
  pol: { background: '#e7eef8', color: '#14509b', fontWeight: 500, letterSpacing: '0.06em' },
  other: { background: '#eef1f4', color: '#6b7280', fontWeight: 500, letterSpacing: '0.06em' },
  country: { background: '#f4f6f8', color: '#4b5563', fontWeight: 500, letterSpacing: '0.06em' },
  open: { background: '#fdf3e0', color: '#8a6a12', fontWeight: 500, letterSpacing: '0.06em' },
  closed: { background: '#e6f2ea', color: '#166534', fontWeight: 500, letterSpacing: '0.06em' },
  off: { background: '#f4f6f8', color: '#8a929c', fontWeight: 500, letterSpacing: '0.06em' },
};

export const NAV_BASE = {
  fontSize: '13.5px',
  padding: '7px 11px',
  borderRadius: '6px',
  cursor: 'pointer',
  color: '#4b5563',
  whiteSpace: 'nowrap',
  textDecoration: 'none',
};
export const NAV_ON = { ...NAV_BASE, background: '#f0f3f7', color: '#14509b', fontWeight: 600 };

export const SEG_OFF = { borderColor: '#dfe3e8', color: '#4b5563', background: '#fff', fontSize: '13px' };
export const SEG_ON = { borderColor: '#14509b', color: '#fff', background: '#14509b', fontSize: '13px' };

export const CARD = { background: '#fff', border: '1px solid #dfe3e8', borderRadius: '8px' };
export const META_ROW = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  flexWrap: 'wrap',
  fontSize: '11px',
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  color: '#8a929c',
};
export const SECTION_LABEL = {
  fontSize: '11px',
  letterSpacing: '0.12em',
  textTransform: 'uppercase',
  color: '#8a929c',
};
export const PAGE = { maxWidth: '1180px', margin: '0 auto', padding: '28px 24px 72px' };
export const PAGE_NARROW = { maxWidth: '860px', margin: '0 auto', padding: '28px 24px 72px' };

export const CATEGORY_LABEL = {
  politics: 'Политика',
  economy: 'Экономика',
  business: 'Бизнес и маркетинг',
  other: 'Остальное',
  // старая категория, ещё встречается в архиве
  political_economic: 'Политика и экономика',
};

export const REGION_LABEL = {
  kz: 'Казахстан',
  cis: 'СНГ',
  europe: 'Европа',
  america: 'Америка',
};

export function categoryBadge(category) {
  return category && category !== 'other' ? BADGE.pol : BADGE.other;
}

export function statusBadge(status) {
  return status === 'closed' ? BADGE.closed : BADGE.open;
}

export const STATUS_LABEL = { open: 'Открыт', closed: 'Закрыт' };

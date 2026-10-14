import { Spinner } from 'react-bootstrap';
import { CARD } from '../theme';

export function Loading({ label = 'Загружаем' }) {
  return (
    <div style={{ ...CARD, padding: '48px 24px', textAlign: 'center' }}>
      <Spinner style={{ color: '#14509b', width: 26, height: 26, borderWidth: 3 }} />
      <div style={{ fontSize: 14, color: '#6b7280', marginTop: 14 }}>{label}</div>
    </div>
  );
}

export function ErrorBox({ error }) {
  if (!error) return null;
  return (
    <div
      className="alert alert-warning"
      style={{ background: '#fdf6e7', borderColor: '#e8d49a', color: '#5c4708', borderRadius: 8, padding: '16px 18px', fontSize: 14, lineHeight: 1.6 }}
    >
      <b style={{ display: 'block', marginBottom: 4 }}>
        <i className="bi bi-exclamation-triangle-fill" style={{ marginRight: 8 }} />
        Не удалось выполнить запрос
      </b>
      {error.message}
    </div>
  );
}

export function Empty({ title, text, action }) {
  return (
    <div style={{ ...CARD, padding: '64px 24px', textAlign: 'center' }}>
      <i className="bi bi-inbox" style={{ fontSize: 28, color: '#c4cad2' }} />
      <div style={{ fontSize: 17, fontWeight: 600, margin: '14px 0 6px' }}>{title}</div>
      <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 18 }}>{text}</div>
      {action}
    </div>
  );
}

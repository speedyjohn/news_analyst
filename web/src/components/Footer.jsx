import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer style={{ borderTop: '1px solid #e6e9ed', background: '#fff' }}>
      <div style={{ maxWidth: 1180, margin: '0 auto', padding: '20px 24px', display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 12, color: '#8a929c' }}>
        <span>Данные собираются только с официальных источников. Обновление ежедневно в 07:00 по Астане.</span>
        <span style={{ marginLeft: 'auto' }}>
          <Link to="/sources" style={{ color: '#14509b', textDecoration: 'none' }}>Список источников</Link>
        </span>
      </div>
    </footer>
  );
}

import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';
import { NAV_BASE, NAV_ON } from '../theme';
import { longDate } from '../format';

const LINKS = [
  { to: '/', label: 'Лента', end: true },
  { to: '/questions/mine', label: 'Мои вопросы' },
  { to: '/legal', label: 'Законодательные предложения' },
  { to: '/sources', label: 'Источники' },
];

export default function Header({ date }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const onUserClick = () => (user ? logout() : navigate('/auth'));

  return (
    <header style={{ background: '#fff', borderBottom: '1px solid #dfe3e8', position: 'sticky', top: 0, zIndex: 20 }}>
      <div style={{ maxWidth: 1180, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', gap: 32, height: 60 }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'baseline', gap: 8, textDecoration: 'none', color: 'inherit' }}>
          <span style={{ fontSize: 16, fontWeight: 700, letterSpacing: '-0.01em' }}>Новостной аналитик</span>
          <span style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#8a929c' }}>
            официальные источники
          </span>
        </Link>

        <nav style={{ display: 'flex', gap: 4, marginLeft: 8 }}>
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} style={({ isActive }) => (isActive ? NAV_ON : NAV_BASE)}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 12, color: '#6b7280', letterSpacing: '0.04em' }}>
            <i className="bi bi-calendar3" style={{ marginRight: 6 }} />
            {longDate(date ?? new Date())}
          </span>
          <div
            onClick={onUserClick}
            style={{
              display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 13,
              color: '#191d23', borderLeft: '1px solid #e6e9ed', paddingLeft: 16,
            }}
            title={user ? 'Выйти' : 'Войти'}
          >
            <i className="bi bi-person-circle" style={{ fontSize: 16, color: '#8a929c' }} />
            {user ? user.display_name : 'Гость'}
            <i className="bi bi-chevron-down" style={{ fontSize: 10, color: '#8a929c' }} />
          </div>
        </div>
      </div>
    </header>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';

export default function AuthPage() {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (user) navigate('/');
  }, [user, navigate]);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await (mode === 'signin' ? login(email, password) : register(email, password));
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'center', padding: '80px 24px' }}>
      <form onSubmit={submit} style={{ width: 380 }}>
        <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: '-0.015em', margin: '0 0 20px', textAlign: 'center' }}>
          {mode === 'signin' ? 'Вход' : 'Регистрация'}
        </h1>

        <div style={{ background: '#fff', border: '1px solid #dfe3e8', borderRadius: 8, padding: 24 }}>
          <label style={{ fontSize: 12, color: '#4b5563', display: 'block', marginBottom: 6 }}>Email</label>
          <input
            className="form-control"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@org.kz"
            style={{ fontSize: 14, borderColor: '#dfe3e8', marginBottom: 14 }}
          />

          <label style={{ fontSize: 12, color: '#4b5563', display: 'block', marginBottom: 6 }}>Пароль</label>
          <input
            className="form-control"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ fontSize: 14, borderColor: '#dfe3e8', marginBottom: 18 }}
          />

          {error && (
            <div
              className="alert alert-warning"
              style={{ background: '#fdf6e7', borderColor: '#e8d49a', color: '#5c4708', borderRadius: 6, padding: '10px 12px', fontSize: 12.5 }}
            >
              {error}
            </div>
          )}

          <button className="btn btn-primary w-100" type="submit" disabled={busy} style={{ fontSize: 14 }}>
            {mode === 'signin' ? 'Войти' : 'Создать аккаунт'}
          </button>
        </div>

        <div style={{ textAlign: 'center', marginTop: 14, fontSize: 13, color: '#6b7280' }}>
          <span
            onClick={() => {
              setMode(mode === 'signin' ? 'signup' : 'signin');
              setError('');
            }}
            style={{ color: '#14509b', cursor: 'pointer' }}
          >
            {mode === 'signin' ? 'Нет аккаунта — зарегистрироваться' : 'Уже есть аккаунт — войти'}
          </span>
        </div>
      </form>
    </main>
  );
}

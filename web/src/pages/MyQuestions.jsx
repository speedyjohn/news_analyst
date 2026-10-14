import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import { ErrorBox, Loading } from '../components/State';
import { numericDate } from '../format';
import { CARD, PAGE, SEG_OFF, SEG_ON, statusBadge, STATUS_LABEL } from '../theme';

const FILTERS = [
  { key: 'all', label: 'Все' },
  { key: 'open', label: 'Открытые' },
  { key: 'closed', label: 'Закрытые' },
];

const TH = {
  fontSize: 10.5,
  letterSpacing: '0.1em',
  textTransform: 'uppercase',
  color: '#8a929c',
  fontWeight: 500,
  borderColor: '#eef0f2',
};
const TD = { borderColor: '#f2f4f6' };

export default function MyQuestions() {
  const { user, ready } = useAuth();
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (ready && !user) navigate('/auth');
  }, [ready, user, navigate]);

  useEffect(() => {
    if (!user) return;
    setData(null);
    api
      .myQuestions(filter === 'all' ? null : filter)
      .then(setData)
      .catch(setError);
  }, [filter, user]);

  if (!user) return null;

  return (
    <main style={PAGE}>
      <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 18px' }}>Мои вопросы</h1>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18, flexWrap: 'wrap' }}>
        <Counter value={data?.open ?? 0} label="Открыто" color="#b98a12" />
        <Counter value={data?.closed ?? 0} label="Закрыто" color="#166534" />
        <div className="btn-group btn-group-sm" role="group" style={{ marginLeft: 'auto' }}>
          {FILTERS.map((item) => (
            <button
              key={item.key}
              type="button"
              className="btn btn-sm"
              onClick={() => setFilter(item.key)}
              style={filter === item.key ? SEG_ON : SEG_OFF}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <ErrorBox error={error} />
      {!data && !error && <Loading />}

      {data && data.items.length > 0 && (
        <div style={{ ...CARD, overflow: 'hidden' }}>
          <table className="table table-hover" style={{ margin: 0, fontSize: 13.5 }}>
            <thead>
              <tr style={{ background: '#fafbfc' }}>
                <th style={TH}>Вопрос</th>
                <th style={{ ...TH, width: 230 }}>Новость</th>
                <th style={{ ...TH, width: 110 }}>Статус</th>
                <th style={{ ...TH, width: 110 }}>Задан</th>
                <th style={{ ...TH, width: 110 }}>Закрыт</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((row) => (
                <tr key={row.id} onClick={() => navigate('/questions/' + row.id)} style={{ cursor: 'pointer', ...TD }}>
                  <td style={{ ...TD, lineHeight: 1.45 }}>{row.text}</td>
                  <td style={{ ...TD, color: '#6b7280', fontSize: 12.5 }}>{row.news.title}</td>
                  <td style={TD}>
                    <span className="badge" style={statusBadge(row.status)}>{STATUS_LABEL[row.status]}</span>
                  </td>
                  <td style={{ ...TD, color: '#6b7280', fontSize: 12.5, fontVariantNumeric: 'tabular-nums' }}>
                    {numericDate(row.created_at)}
                  </td>
                  <td style={{ ...TD, color: '#6b7280', fontSize: 12.5, fontVariantNumeric: 'tabular-nums' }}>
                    {numericDate(row.closed_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && data.items.length === 0 && (
        <div style={{ ...CARD, padding: '56px 24px', textAlign: 'center', marginTop: 10 }}>
          <div style={{ fontSize: 17, fontWeight: 600, marginBottom: 6 }}>Вы пока не задавали вопросов</div>
          <div style={{ fontSize: 14, color: '#6b7280', marginBottom: 18 }}>
            Откройте любую новость в дайджесте и задайте вопрос по её содержанию.
          </div>
          <Link className="btn btn-primary btn-sm" to="/">
            Перейти в ленту
          </Link>
        </div>
      )}
    </main>
  );
}

function Counter({ value, label, color }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #dfe3e8', borderRadius: 7, padding: '12px 18px' }}>
      <div style={{ fontSize: 22, fontWeight: 700, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{value}</div>
      <div style={{ fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color, marginTop: 5 }}>{label}</div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { api } from '../api';
import { ErrorBox, Loading } from '../components/State';
import { numericDate, timeOnly } from '../format';
import { BADGE, CARD, PAGE } from '../theme';

const TH = {
  fontSize: 10.5,
  letterSpacing: '0.1em',
  textTransform: 'uppercase',
  color: '#8a929c',
  fontWeight: 500,
  borderColor: '#eef0f2',
};
const TD = { borderColor: '#f2f4f6' };

export default function Sources() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.sources().then(setData).catch(setError);
  }, []);

  const items = data?.items ?? [];

  return (
    <main style={PAGE}>
      <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 6px' }}>Источники</h1>
      <p style={{ fontSize: 14, color: '#6b7280', margin: '0 0 20px' }}>
        {items.length} источников, только официальные сайты государственных органов и международных организаций. Раздел
        доступен для просмотра.
      </p>

      <ErrorBox error={error} />
      {!data && !error && <Loading />}

      {data && (
        <div style={{ ...CARD, overflow: 'hidden' }}>
          <table className="table" style={{ margin: 0, fontSize: 13.5 }}>
            <thead>
              <tr style={{ background: '#fafbfc' }}>
                <th style={TH}>Название</th>
                <th style={{ ...TH, width: 90 }}>Страна</th>
                <th style={{ ...TH, width: 90 }}>Тип</th>
                <th style={{ ...TH, width: 120 }}>Статус</th>
                <th style={{ ...TH, width: 150 }}>Последний сбор</th>
                <th style={{ ...TH, width: 140 }}>Сайт</th>
              </tr>
            </thead>
            <tbody>
              {items.map((source) => (
                <tr key={source.code} style={TD}>
                  <td style={{ ...TD, fontWeight: 500 }}>{source.name}</td>
                  <td style={TD}>
                    <span className="badge" style={BADGE.country}>{source.country}</span>
                  </td>
                  <td style={{ ...TD, color: '#6b7280', fontSize: 12.5 }}>{source.type}</td>
                  <td style={TD}>
                    <span className="badge" style={source.enabled ? BADGE.closed : BADGE.off}>
                      {source.enabled ? 'Активен' : 'Отключён'}
                    </span>
                  </td>
                  <td style={{ ...TD, color: '#6b7280', fontSize: 12.5, fontVariantNumeric: 'tabular-nums' }}>
                    {source.last_success_at
                      ? numericDate(source.last_success_at) + ' ' + timeOnly(source.last_success_at)
                      : '—'}
                  </td>
                  <td style={TD}>
                    <a href={source.url} target="_blank" rel="noreferrer" style={{ fontSize: 12.5, textDecoration: 'none' }}>
                      {source.host} <i className="bi bi-box-arrow-up-right" style={{ fontSize: 9 }} />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import { Empty, ErrorBox, Loading } from '../components/State';
import { isoDate, longDate, numericDate, score, shiftDay, timeOnly } from '../format';
import { BADGE, CARD, CATEGORY_LABEL, META_ROW, PAGE, REGION_LABEL, SEG_OFF, SEG_ON, categoryBadge } from '../theme';

const VIEWS = [
  { key: '3', label: 'Топ-3' },
  { key: '5', label: 'Топ-5' },
  { key: '10', label: 'Топ-10' },
  { key: 'all', label: 'Вся лента' },
];

const CATEGORIES = ['politics', 'economy', 'business', 'other'];
const SELECT = { width: 'auto', borderColor: '#dfe3e8', fontSize: 13 };

export default function Feed() {
  const [params, setParams] = useSearchParams();
  const top = params.get('top') ?? '5';
  const date = params.get('date') ?? isoDate(new Date());
  const category = params.get('category') ?? 'all';
  const region = params.get('region') ?? 'all';
  const page = Number(params.get('page') ?? 1);

  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const update = (patch) => {
    const next = new URLSearchParams(params);
    Object.entries(patch).forEach(([key, value]) => {
      if (value == null || value === '') next.delete(key);
      else next.set(key, value);
    });
    if (!('page' in patch)) next.delete('page');
    setParams(next);
  };

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .feed({ date, top: top === 'all' ? null : top, category, region, page })
      .then((result) => {
        if (cancelled) return;
        setData(result);
        setError(null);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [date, top, category, region, page]);

  const isTop = top !== 'all';
  const items = data?.items ?? [];
  const pages = Math.ceil((data?.total ?? 0) / (data?.page_size ?? 20));

  return (
    <main style={PAGE}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          gap: 24,
          flexWrap: 'wrap',
          marginBottom: 20,
        }}
      >
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 6px' }}>
            Дайджест за {longDate(date).replace(/\s\d{4}$/, '')}
          </h1>
          <div style={{ fontSize: 12, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#8a929c' }}>
            {isTop ? 'Топ-' + top + ' по важности' : (data?.total ?? 0) + ' публикаций'}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <div className="btn-group" role="group">
            {VIEWS.map((view) => (
              <button
                key={view.key}
                type="button"
                className="btn btn-sm"
                onClick={() => update({ top: view.key })}
                style={top === view.key ? SEG_ON : SEG_OFF}
              >
                {view.label}
              </button>
            ))}
          </div>

          <div className="btn-group" role="group">
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={() => update({ date: shiftDay(date, -1) })}
              style={{ borderColor: '#dfe3e8', color: '#4b5563' }}
            >
              <i className="bi bi-chevron-left" />
            </button>
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              style={{ borderColor: '#dfe3e8', color: '#191d23', fontVariantNumeric: 'tabular-nums', minWidth: 112 }}
            >
              {numericDate(date)}
            </button>
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={() => update({ date: shiftDay(date, 1) })}
              style={{ borderColor: '#dfe3e8', color: '#4b5563' }}
            >
              <i className="bi bi-chevron-right" />
            </button>
          </div>

          <select
            className="form-select form-select-sm"
            value={region}
            onChange={(e) => update({ region: e.target.value })}
            style={SELECT}
          >
            <option value="all">Все регионы</option>
            {Object.entries(REGION_LABEL).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>

          <select
            className="form-select form-select-sm"
            value={category}
            onChange={(e) => update({ category: e.target.value })}
            style={SELECT}
          >
            <option value="all">Все категории</option>
            {CATEGORIES.map((key) => (
              <option key={key} value={key}>
                {CATEGORY_LABEL[key]}
              </option>
            ))}
          </select>
        </div>
      </div>

      <ErrorBox error={error} />
      {loading && <Loading label="Собираем дайджест" />}

      {!loading && !error && items.length === 0 && (category !== 'all' || region !== 'all') && (
        <Empty
          title="По выбранным фильтрам новостей нет"
          text="За эту дату нет материалов выбранного региона или категории."
          action={
            <button className="btn btn-primary btn-sm" onClick={() => update({ category: null, region: null })}>
              Сбросить фильтры
            </button>
          }
        />
      )}

      {!loading && !error && items.length === 0 && category === 'all' && region === 'all' && (
        <Empty
          title="За выбранную дату новостей нет"
          text="Официальные источники не публиковали материалов. Выберите другую дату."
          action={
            <button className="btn btn-primary btn-sm" onClick={() => update({ date: shiftDay(date, -1) })}>
              Предыдущий день
            </button>
          }
        />
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {items.map((item, index) => (
          <NewsCard key={item.id} item={item} num={isTop ? index + 1 : null} />
        ))}
      </div>

      {!isTop && pages > 1 && (
        <nav style={{ marginTop: 24, display: 'flex', justifyContent: 'center' }}>
          <ul className="pagination pagination-sm" style={{ margin: 0 }}>
            <li className={page <= 1 ? 'page-item disabled' : 'page-item'}>
              <button className="page-link" onClick={() => update({ page: page - 1 })}>
                Назад
              </button>
            </li>
            {Array.from({ length: Math.min(pages, 8) }, (_, i) => i + 1).map((n) => (
              <li key={n} className={n === page ? 'page-item active' : 'page-item'}>
                <button className="page-link" onClick={() => update({ page: n })}>
                  {n}
                </button>
              </li>
            ))}
            <li className={page >= pages ? 'page-item disabled' : 'page-item'}>
              <button className="page-link" onClick={() => update({ page: page + 1 })}>
                Вперёд
              </button>
            </li>
          </ul>
        </nav>
      )}
    </main>
  );
}

function NewsCard({ item, num }) {
  const hasQuestions = item.questions.total > 0;
  return (
    <article className="card" style={CARD}>
      <div style={{ display: 'flex', gap: 20, padding: '18px 20px' }}>
        {num != null && (
          <div
            style={{
              fontSize: 30,
              fontWeight: 700,
              color: '#ccd2da',
              lineHeight: 1,
              minWidth: 38,
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {num}
          </div>
        )}
        <div style={{ flex: 1, minWidth: 0 }}>
          <h2
            style={{
              fontSize: 19,
              fontWeight: 600,
              letterSpacing: '-0.015em',
              lineHeight: 1.3,
              margin: '0 0 8px',
              textWrap: 'pretty',
            }}
          >
            <Link to={'/news/' + item.id} style={{ color: 'inherit', textDecoration: 'none' }}>
              {item.title}
            </Link>
          </h2>

          <div style={{ ...META_ROW, marginBottom: 10 }}>
            <span style={{ color: '#4b5563', fontWeight: 500 }}>{item.source.name}</span>
            <span>{timeOnly(item.published_at)}</span>
            <span className="badge" style={BADGE.country}>
              {item.country}
            </span>
            {item.category && (
              <span className="badge" style={categoryBadge(item.category)}>
                {CATEGORY_LABEL[item.category]}
              </span>
            )}
          </div>

          {item.summary && (
            <p
              style={{
                fontSize: 14,
                lineHeight: 1.55,
                color: '#4b5563',
                margin: '0 0 14px',
                maxWidth: '76ch',
                textWrap: 'pretty',
              }}
            >
              {item.summary}
            </p>
          )}

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 18,
              flexWrap: 'wrap',
              paddingTop: 12,
              borderTop: '1px solid #eef0f2',
              fontSize: 12.5,
            }}
          >
            <span style={{ color: '#6b7280' }}>
              Важность{' '}
              <b style={{ color: '#191d23', fontVariantNumeric: 'tabular-nums' }}>{score(item.importance_score)}</b>
            </span>
            <a href={item.url} target="_blank" rel="noreferrer" style={{ textDecoration: 'none', fontWeight: 500 }}>
              {item.source.host} <i className="bi bi-box-arrow-up-right" style={{ fontSize: 10 }} />
            </a>
            {hasQuestions && (
              <Link
                to={'/news/' + item.id}
                style={{ color: '#6b7280', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 6 }}
              >
                <i className="bi bi-chat-square-text" style={{ fontSize: 11 }} />
                Вопросы {item.questions.closed}/{item.questions.total}
              </Link>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

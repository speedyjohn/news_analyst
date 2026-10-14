import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import { ErrorBox, Loading } from '../components/State';
import { longDate, shortDate, timeOnly } from '../format';
import { BADGE, CARD, CATEGORY_LABEL, META_ROW, categoryBadge, statusBadge, STATUS_LABEL } from '../theme';

const MAX_LEN = 300;

export default function NewsPage() {
  const { id } = useParams();
  const [news, setNews] = useState(null);
  const [error, setError] = useState(null);

  const reload = () => api.news(id).then(setNews).catch(setError);

  useEffect(() => {
    setNews(null);
    api.news(id).then(setNews).catch(setError);
  }, [id]);

  if (error) return <main style={{ maxWidth: 1180, margin: '0 auto', padding: '24px' }}><ErrorBox error={error} /></main>;
  if (!news) return <main style={{ maxWidth: 1180, margin: '0 auto', padding: '24px' }}><Loading /></main>;

  return (
    <main style={{ maxWidth: 1180, margin: '0 auto', padding: '24px 24px 72px' }}>
      <Link to="/" style={{ fontSize: 12.5, color: '#6b7280', textDecoration: 'none', display: 'inline-block', marginBottom: 18 }}>
        <i className="bi bi-arrow-left" style={{ marginRight: 6 }} />К дайджесту за {longDate(news.published_at).replace(/\s\d{4}$/, '')}
      </Link>

      <div
        className="news-layout"
        style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 340px', gap: 28, alignItems: 'start' }}
      >
        <Article news={news} />
        <QuestionsAside news={news} onAsked={reload} />
      </div>
    </main>
  );
}

function Article({ news }) {
  return (
    <div>
      <div style={{ ...CARD, padding: '28px 30px' }}>
        <div style={{ ...META_ROW, marginBottom: 14 }}>
          <span style={{ color: '#4b5563', fontWeight: 500 }}>{news.source.name}</span>
          <span>{timeOnly(news.published_at)}</span>
          <span className="badge" style={BADGE.country}>{news.country}</span>
          {news.category && (
            <span className="badge" style={categoryBadge(news.category)}>{CATEGORY_LABEL[news.category]}</span>
          )}
        </div>

        <h1
          style={{
            fontSize: 30,
            fontWeight: 700,
            letterSpacing: '-0.025em',
            lineHeight: 1.22,
            margin: '0 0 22px',
            textWrap: 'pretty',
          }}
        >
          {news.title}
        </h1>

        <a
          href={news.url}
          target="_blank"
          rel="noreferrer"
          className="btn btn-primary"
          style={{ fontSize: 14, fontWeight: 500, padding: '10px 18px', marginBottom: 24 }}
        >
          Открыть первоисточник на {news.source.host}
          <i className="bi bi-box-arrow-up-right" style={{ fontSize: 12, marginLeft: 6 }} />
        </a>

        {news.summary && (
          <div
            style={{
              background: '#f7f8f9',
              borderLeft: '3px solid #14509b',
              borderRadius: '0 6px 6px 0',
              padding: '16px 18px',
              margin: '0 0 26px',
            }}
          >
            <div style={{ fontSize: 10.5, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#8a929c', marginBottom: 7 }}>
              Кратко
            </div>
            <p style={{ margin: 0, fontSize: 15, lineHeight: 1.6, color: '#191d23' }}>{news.summary}</p>
          </div>
        )}

        <div style={{ fontSize: 15.5, lineHeight: 1.72, color: '#232830', maxWidth: '74ch' }}>
          {(news.full_text || '')
            .split(/\n+/)
            .filter((p) => p.trim())
            .map((paragraph, index) => (
              <p key={index}>{paragraph}</p>
            ))}
          {!news.full_text && (
            <p style={{ color: '#6b7280' }}>
              Источник опубликовал только заголовок и краткое описание. Полный текст доступен по ссылке на первоисточник.
            </p>
          )}
        </div>

        <div
          style={{
            marginTop: 26,
            paddingTop: 18,
            borderTop: '1px solid #eef0f2',
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontSize: 12.5,
            color: '#6b7280',
          }}
        >
          <i className="bi bi-shield-check" style={{ color: '#14509b' }} />
          Текст приведён по публикации официального источника без редактуры.
          <a href={news.url} target="_blank" rel="noreferrer" style={{ marginLeft: 'auto', textDecoration: 'none' }}>
            {news.source.host} <i className="bi bi-box-arrow-up-right" style={{ fontSize: 10 }} />
          </a>
        </div>
      </div>
    </div>
  );
}

function QuestionsAside({ news, onAsked }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const questions = news.questions_list ?? [];
  const closed = questions.filter((q) => q.status === 'closed').length;

  return (
    <aside className="news-aside" style={{ position: 'sticky', top: 84, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={CARD}>
        <div
          style={{
            padding: '16px 18px',
            borderBottom: '1px solid #eef0f2',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span style={{ fontSize: 14, fontWeight: 600 }}>Вопросы по новости</span>
          <span style={{ fontSize: 11, letterSpacing: '0.06em', color: '#8a929c' }}>
            {closed} закрыто · {questions.length - closed} открыто
          </span>
        </div>

        <div>
          {questions.map((question) => (
            <Link
              key={question.id}
              to={'/questions/' + question.id}
              style={{ display: 'block', padding: '13px 18px', borderBottom: '1px solid #f2f4f6', textDecoration: 'none', color: 'inherit' }}
            >
              <div style={{ fontSize: 13.5, lineHeight: 1.45, marginBottom: 7, textWrap: 'pretty' }}>{question.text}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span className="badge" style={statusBadge(question.status)}>{STATUS_LABEL[question.status]}</span>
                <span style={{ fontSize: 11, color: '#8a929c', letterSpacing: '0.04em' }}>{shortDate(question.created_at)}</span>
              </div>
            </Link>
          ))}
          {questions.length === 0 && (
            <div style={{ padding: '16px 18px', fontSize: 13, color: '#8a929c' }}>Вопросов пока нет.</div>
          )}
        </div>

        {user ? (
          <AskForm newsId={news.id} onAsked={onAsked} />
        ) : (
          <div style={{ padding: 18, background: '#f7f8f9', borderTop: '1px solid #eef0f2', borderRadius: '0 0 8px 8px' }}>
            <div style={{ fontSize: 13.5, fontWeight: 600, marginBottom: 4 }}>Войдите, чтобы задавать вопросы</div>
            <div style={{ fontSize: 12.5, color: '#6b7280', lineHeight: 1.5, marginBottom: 12 }}>
              Ответ придёт письмом, когда вопрос закроет официальная публикация.
            </div>
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/auth')}>
              Войти
            </button>
          </div>
        )}
      </div>

      <div style={{ fontSize: 11.5, color: '#8a929c', lineHeight: 1.5, padding: '0 4px' }}>
        Вопросы видны всем пользователям. Ответ ИИ опирается только на публикации официальных источников.
      </div>
    </aside>
  );
}

function AskForm({ newsId, onAsked }) {
  const [draft, setDraft] = useState('');
  const [rejection, setRejection] = useState(null);
  const [sending, setSending] = useState(false);

  const submit = async () => {
    setSending(true);
    setRejection(null);
    try {
      await api.askQuestion(newsId, draft);
      setDraft('');
      onAsked();
    } catch (err) {
      setRejection(err.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ padding: '16px 18px' }}>
      <label style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#8a929c', display: 'block', marginBottom: 8 }}>
        Задать вопрос
      </label>
      <textarea
        className="form-control"
        rows={4}
        value={draft}
        maxLength={MAX_LEN}
        onChange={(e) => {
          setDraft(e.target.value);
          setRejection(null);
        }}
        placeholder="Например: как пониженная ставка 10% соотносится с действующими льготами СЭЗ?"
        style={{ fontSize: 13.5, borderColor: '#dfe3e8', resize: 'vertical' }}
      />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
        <span style={{ fontSize: 11, color: '#8a929c', fontVariantNumeric: 'tabular-nums' }}>
          {draft.length} / {MAX_LEN}
        </span>
        <button className="btn btn-primary btn-sm" onClick={submit} disabled={sending || !draft.trim()}>
          {sending ? 'Отправляем…' : 'Отправить'}
        </button>
      </div>

      {rejection && (
        <div
          className="alert alert-warning"
          style={{
            margin: '12px 0 0',
            fontSize: 12.5,
            lineHeight: 1.5,
            background: '#fdf6e7',
            borderColor: '#e8d49a',
            color: '#5c4708',
            borderRadius: 6,
            padding: '11px 13px',
          }}
        >
          <b style={{ display: 'block', marginBottom: 3 }}>
            <i className="bi bi-exclamation-triangle" style={{ marginRight: 6 }} />
            Вопрос отклонён модерацией
          </b>
          {rejection}
        </div>
      )}
    </div>
  );
}

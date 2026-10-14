import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api';
import { ErrorBox, Loading } from '../components/State';
import { longDate } from '../format';
import { CARD, statusBadge, STATUS_LABEL } from '../theme';

const WRAP = { maxWidth: 860, margin: '0 auto', padding: '24px 24px 72px' };

export default function QuestionPage() {
  const { id } = useParams();
  const [question, setQuestion] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setQuestion(null);
    api.question(id).then(setQuestion).catch(setError);
  }, [id]);

  if (error) return <main style={WRAP}><ErrorBox error={error} /></main>;
  if (!question) return <main style={WRAP}><Loading /></main>;

  const isClosed = question.status === 'closed';

  return (
    <main style={WRAP}>
      <Link
        to={'/news/' + question.news.id}
        style={{ fontSize: 12.5, color: '#6b7280', textDecoration: 'none', display: 'inline-block', marginBottom: 18 }}
      >
        <i className="bi bi-arrow-left" style={{ marginRight: 6 }} />К новости
      </Link>

      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 10 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.3, margin: 0, textWrap: 'pretty' }}>
          {question.text}
        </h1>
        <span
          className="badge"
          style={{ ...statusBadge(question.status), fontSize: 11, padding: '6px 10px', whiteSpace: 'nowrap', marginTop: 6 }}
        >
          {STATUS_LABEL[question.status]}
        </span>
      </div>

      <div style={{ fontSize: 12.5, color: '#6b7280', marginBottom: 24 }}>
        задан {question.author} · {longDate(question.created_at)} · к новости{' '}
        <Link to={'/news/' + question.news.id} style={{ textDecoration: 'none' }}>
          «{question.news.title}»
        </Link>
      </div>

      {isClosed && <OfficialAnswer question={question} />}

      <AiAnswer answer={question.ai_answer} />

      {!isClosed && (
        <section style={{ ...CARD, padding: '18px 20px', marginTop: 16, display: 'flex', gap: 12, alignItems: 'flex-start' }}>
          <i className="bi bi-hourglass-split" style={{ color: '#8a929c', marginTop: 2 }} />
          <div style={{ fontSize: 13.5, lineHeight: 1.6, color: '#4b5563' }}>
            Вопрос ещё не закрыт официальным источником. Мы проверяем новые публикации ежедневно и пришлём письмо, когда
            появится ответ. <Link to="/questions/mine" style={{ textDecoration: 'none' }}>Все мои вопросы</Link>
          </div>
        </section>
      )}
    </main>
  );
}

function OfficialAnswer({ question }) {
  const closing = question.closing_news;
  return (
    <section
      style={{
        background: '#fff',
        border: '1px solid #b7d8c2',
        borderLeft: '3px solid #1a7a43',
        borderRadius: 8,
        padding: '22px 24px',
        marginBottom: 16,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontSize: 11,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: '#166534',
          marginBottom: 12,
        }}
      >
        <i className="bi bi-patch-check-fill" />
        Ответ официального источника
      </div>
      <p style={{ fontSize: 16, lineHeight: 1.65, margin: '0 0 16px', color: '#191d23' }}>{question.official_answer}</p>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap', fontSize: 12.5, color: '#4b5563' }}>
        <span>Закрыт {longDate(question.closed_at)}</span>
        {closing && (
          <a href={closing.url} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
            {closing.source} · {closing.title} <i className="bi bi-box-arrow-up-right" style={{ fontSize: 10 }} />
          </a>
        )}
      </div>
    </section>
  );
}

function AiAnswer({ answer }) {
  if (!answer) {
    return (
      <section style={{ ...CARD, overflow: 'hidden' }}>
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #eef0f2', fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#8a929c' }}>
          Ответ ИИ
        </div>
        <div style={{ padding: '22px 24px', fontSize: 14, color: '#6b7280' }}>
          Ответ пока не сформирован. Он появится после ближайшей обработки.
        </div>
      </section>
    );
  }

  return (
    <section style={{ ...CARD, overflow: 'hidden' }}>
      <div style={{ padding: '16px 24px', borderBottom: '1px solid #eef0f2', fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#8a929c' }}>
        Ответ ИИ
      </div>
      <div style={{ padding: '22px 24px' }}>
        <div style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#4b5563', marginBottom: 12 }}>
          Факты
        </div>
        <div style={{ fontSize: 15, lineHeight: 1.7, color: '#232830' }}>
          {answer.facts.map((fact, index) => (
            <p key={index} style={{ marginBottom: index === answer.facts.length - 1 ? 0 : 14 }}>
              {fact.text}{' '}
              {fact.source && <SourcePill source={fact.source} />}
            </p>
          ))}
        </div>

        {answer.assessment && (
          <div style={{ marginTop: 22, border: '1px solid #e8d49a', background: '#fdf9ef', borderRadius: 7, padding: '16px 18px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                fontSize: 11,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: '#8a6a12',
                marginBottom: 10,
              }}
            >
              <i className="bi bi-exclamation-triangle-fill" />
              Оценка
            </div>
            <p style={{ fontSize: 14.5, lineHeight: 1.65, margin: '0 0 10px', color: '#3a3218' }}>{answer.assessment}</p>
            <div style={{ fontSize: 11.5, color: '#8a6a12' }}>
              Предположение на основе фактов выше, а не официальная позиция.
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function SourcePill({ source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noreferrer"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        fontSize: 11.5,
        textDecoration: 'none',
        border: '1px solid #c9d4e2',
        borderRadius: 20,
        padding: '2px 10px',
        verticalAlign: 'middle',
        whiteSpace: 'nowrap',
      }}
    >
      {source.title} <i className="bi bi-box-arrow-up-right" style={{ fontSize: 9 }} />
    </a>
  );
}

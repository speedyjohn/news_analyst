import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import { longDate, numericDate, timeOnly } from '../format';
import { BADGE, CARD, PAGE_NARROW } from '../theme';

const STAGES = ['Ищем релевантные нормы', 'Готовим предложение', 'Проверяем ссылки на статьи'];
const SECTION_TITLE = {
  fontSize: 12,
  letterSpacing: '0.1em',
  textTransform: 'uppercase',
  color: '#14509b',
  fontWeight: 600,
};
const BODY = { fontSize: 15, lineHeight: 1.7, margin: 0, color: '#232830' };

export default function Legal() {
  const { user, ready } = useAuth();
  const navigate = useNavigate();
  const [draft, setDraft] = useState('');
  const [state, setState] = useState('idle'); // idle | loading | result | error
  const [stage, setStage] = useState(0);
  const [note, setNote] = useState(null);
  const [errorText, setErrorText] = useState('');
  const [history, setHistory] = useState(null);
  const [openId, setOpenId] = useState(null);
  const timers = useRef([]);

  useEffect(() => {
    if (ready && !user) navigate('/auth');
  }, [ready, user, navigate]);

  const loadHistory = () =>
    api
      .myLegal()
      .then((result) => setHistory(result.items))
      .catch(() => setHistory((current) => current ?? []));

  useEffect(() => {
    if (user) loadHistory();
  }, [user]);

  const show = (item) => {
    setOpenId(item.id);
    setDraft(item.input_text);
    if (item.verified) {
      setNote(item);
      setState('result');
    } else {
      setErrorText(item.error ?? 'Нет достаточной опоры в загруженной базе НПА.');
      setState('error');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const run = async () => {
    setState('loading');
    setStage(0);
    timers.current = [
      setTimeout(() => setStage(1), 4000),
      setTimeout(() => setStage(2), 12000),
    ];

    try {
      const result = await api.legalSuggest(draft);
      show(result);
    } catch (err) {
      setOpenId(null);
      setErrorText(err.message);
      setState('error');
    } finally {
      timers.current.forEach(clearTimeout);
      loadHistory();
    }
  };

  if (!user) return null;

  return (
    <main style={PAGE_NARROW}>
      <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 8px' }}>
        Законодательные предложения
      </h1>
      <p style={{ fontSize: 14.5, lineHeight: 1.6, color: '#4b5563', maxWidth: '70ch', margin: '0 0 22px' }}>
        Раздел готовит записку по описанной вами проблеме регулирования: находит действующие нормы в базе НПА, показывает
        пробел и предлагает формулировку. Каждая ссылка ведёт на статью в Adilet.
      </p>

      <div style={{ ...CARD, padding: '22px 24px', marginBottom: 16 }}>
        <label style={{ fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#8a929c', display: 'block', marginBottom: 9 }}>
          Опишите проблему в регулировании, которую вы видите
        </label>
        <textarea
          className="form-control"
          rows={4}
          value={draft}
          maxLength={2000}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Например: закон не устанавливает срок, в течение которого госорган обязан опубликовать методику расчёта тарифа, из-за чего сроки различаются от региона к региону. Можно писать на русском или казахском, своими словами."
          style={{ fontSize: 14, borderColor: '#dfe3e8', resize: 'vertical' }}
        />
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 12 }}>
          <button
            className="btn btn-primary"
            onClick={run}
            disabled={state === 'loading' || !draft.trim()}
            style={{ fontSize: 14 }}
          >
            Подготовить записку
          </button>
          <span style={{ fontSize: 12, color: '#8a929c' }}>Не больше 5 запросов в сутки</span>
        </div>
      </div>

      {state === 'loading' && (
        <div style={{ ...CARD, padding: '34px 24px', textAlign: 'center' }}>
          <div className="spinner-border" role="status" style={{ color: '#14509b', width: 26, height: 26, borderWidth: 3 }} />
          <div style={{ fontSize: 15, fontWeight: 600, margin: '16px 0 14px' }}>{STAGES[stage]}</div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 22, fontSize: 12, color: '#8a929c', flexWrap: 'wrap' }}>
            {STAGES.map((label, index) => (
              <span
                key={label}
                style={
                  stage === index
                    ? { color: '#14509b', fontWeight: 600 }
                    : stage > index
                      ? { color: '#4b5563' }
                      : { color: '#b6bcc4' }
                }
              >
                {label}
              </span>
            ))}
          </div>
        </div>
      )}

      {state === 'error' && (
        <div
          className="alert alert-warning"
          style={{ background: '#fdf6e7', borderColor: '#e8d49a', color: '#5c4708', borderRadius: 8, padding: '16px 18px', fontSize: 14, lineHeight: 1.6 }}
        >
          <b style={{ display: 'block', marginBottom: 4 }}>
            <i className="bi bi-exclamation-triangle-fill" style={{ marginRight: 8 }} />
            Не удалось подготовить обоснованное предложение
          </b>
          {errorText}
        </div>
      )}

      {state === 'result' && note && <Note request={note} />}

      <History items={history} activeId={openId} onOpen={show} />
    </main>
  );
}

function statusOf(item) {
  if (item.verified) return { label: 'Записка готова', style: BADGE.closed };
  if (item.failed) return { label: 'Сбой, повторите', style: BADGE.open };
  return { label: 'Нет опоры в НПА', style: BADGE.off };
}

function History({ items, activeId, onOpen }) {
  if (items == null) return null;
  return (
    <section style={{ marginTop: 34 }}>
      <h2 style={{ fontSize: 17, fontWeight: 700, letterSpacing: '-0.01em', margin: '0 0 12px' }}>Мои запросы</h2>
      {items.length === 0 ? (
        <div style={{ ...CARD, padding: '22px 24px', fontSize: 14, color: '#6b7280' }}>
          Здесь будут сохраняться все ваши запросы и подготовленные записки.
        </div>
      ) : (
        <div style={{ ...CARD, overflow: 'hidden' }}>
          {items.map((item, index) => {
            const status = statusOf(item);
            return (
              <div
                key={item.id}
                onClick={() => onOpen(item)}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 16,
                  padding: '14px 18px',
                  cursor: 'pointer',
                  borderTop: index === 0 ? 'none' : '1px solid #f2f4f6',
                  background: item.id === activeId ? '#f2f6fb' : '#fff',
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: item.verified ? 600 : 400, lineHeight: 1.45, marginBottom: 4 }}>
                    {item.note?.title ?? item.input_text}
                  </div>
                  {item.note?.title && (
                    <div
                      style={{
                        fontSize: 12.5,
                        color: '#6b7280',
                        lineHeight: 1.45,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {item.input_text}
                    </div>
                  )}
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <span className="badge" style={status.style}>
                    {status.label}
                  </span>
                  <div style={{ fontSize: 12, color: '#8a929c', marginTop: 6, fontVariantNumeric: 'tabular-nums' }}>
                    {numericDate(item.created_at)} {timeOnly(item.created_at)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function Note({ request }) {
  const data = request.note;
  return (
    <article style={{ ...CARD, padding: '34px 40px' }}>
      <div style={{ fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#8a929c', marginBottom: 8 }}>
        Записка · {longDate(request.created_at)}
      </div>
      <h2 style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.3, margin: '0 0 28px', textWrap: 'pretty' }}>
        {data.title}
      </h2>

      <section style={{ marginBottom: 26 }}>
        <div style={{ ...SECTION_TITLE, marginBottom: 9 }}>1. Суть проблемы</div>
        <p style={BODY}>{data.problem}</p>
      </section>

      <section style={{ marginBottom: 26 }}>
        <div style={{ ...SECTION_TITLE, marginBottom: 12 }}>2. Действующее регулирование</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(data.current_regulation ?? []).map((item, index) => (
            <div key={index} style={{ background: '#f7f8f9', border: '1px solid #e6e9ed', borderRadius: 7, padding: '15px 17px' }}>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 3 }}>{item.act}</div>
              <div style={{ fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#8a929c', marginBottom: 9 }}>
                Статья {item.article}
                {item.point ? ', пункт ' + item.point : ''}
              </div>
              <blockquote
                style={{
                  margin: '0 0 10px',
                  fontSize: 14,
                  lineHeight: 1.6,
                  color: '#3a4149',
                  borderLeft: '2px solid #c9d4e2',
                  paddingLeft: 12,
                }}
              >
                «{item.quote}»
              </blockquote>
              {item.comment && (
                <div style={{ fontSize: 12.5, color: '#6b7280', marginBottom: 8 }}>{item.comment}</div>
              )}
              {item.adilet_url && (
                <a href={item.adilet_url} target="_blank" rel="noreferrer" style={{ fontSize: 12, textDecoration: 'none' }}>
                  Adilet · текст статьи <i className="bi bi-box-arrow-up-right" style={{ fontSize: 9 }} />
                </a>
              )}
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: 26 }}>
        <div style={{ ...SECTION_TITLE, marginBottom: 9 }}>3. В чём пробел</div>
        <p style={BODY}>{data.gap}</p>
      </section>

      <section style={{ marginBottom: 26 }}>
        <div style={{ ...SECTION_TITLE, marginBottom: 12 }}>4. Предложение</div>
        <blockquote
          style={{
            margin: 0,
            background: '#f2f6fb',
            borderLeft: '3px solid #14509b',
            borderRadius: '0 7px 7px 0',
            padding: '18px 20px',
            fontSize: 15.5,
            lineHeight: 1.7,
            color: '#191d23',
          }}
        >
          {data.proposal}
        </blockquote>
      </section>

      <section>
        <div style={{ ...SECTION_TITLE, marginBottom: 9 }}>5. Обоснование</div>
        <p style={{ ...BODY, marginBottom: 12 }}>{data.rationale}</p>
      </section>

      <div
        style={{
          marginTop: 32,
          background: '#fafbfc',
          border: '1px solid #eef0f2',
          borderRadius: 7,
          padding: '14px 16px',
          fontSize: 12.5,
          lineHeight: 1.6,
          color: '#6b7280',
        }}
      >
        Материал носит рекомендательный характер и не является юридическим заключением. Формулировки требуют проверки
        уполномоченным органом и юридической экспертизы.
      </div>
    </article>
  );
}

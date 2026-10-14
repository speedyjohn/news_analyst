const BASE = '/api';

class ApiError extends Error {
  constructor(code, message, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(BASE + path, {
    method,
    credentials: 'include', // JWT в httpOnly-cookie
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const error = payload?.error ?? {};
    throw new ApiError(error.code ?? 'error', error.message ?? 'Ошибка запроса', response.status);
  }
  return payload;
}

export const api = {
  feed: ({ date, top, category, region, page }) => {
    const params = new URLSearchParams();
    if (date) params.set('date', date);
    if (top) params.set('top', top);
    if (category && category !== 'all') params.set('category', category);
    if (region && region !== 'all') params.set('region', region);
    if (page && page > 1) params.set('page', page);
    return request(`/news?${params}`);
  },
  news: (id) => request(`/news/${id}`),
  dates: () => request('/news/dates'),
  question: (id) => request(`/questions/${id}`),
  askQuestion: (newsId, text) => request(`/news/${newsId}/questions`, { method: 'POST', body: { text } }),
  myQuestions: (status) => request(`/questions/mine${status ? `?status=${status}` : ''}`),
  sources: () => request('/sources'),
  legalSuggest: (text) => request('/legal/suggest', { method: 'POST', body: { text } }),
  myLegal: () => request('/legal/requests/mine'),
  me: () => request('/auth/me'),
  login: (email, password) => request('/auth/login', { method: 'POST', body: { email, password } }),
  register: (email, password) => request('/auth/register', { method: 'POST', body: { email, password } }),
  logout: () => request('/auth/logout', { method: 'POST' }),
};

export { ApiError };

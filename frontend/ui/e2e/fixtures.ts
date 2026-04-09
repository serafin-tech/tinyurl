// Shared mock data used across all e2e tests

export const MOCK_SHORT_URL = 'http://localhost:8000/abc123'
export const MOCK_EDIT_TOKEN = 'AbCdEfGhIjKlMnOpQrStUvWx'
export const MOCK_LINK_ID = 'abc123'
export const MOCK_TARGET_URL = 'https://example.com/long/path'
export const MOCK_REDIRECT_CODE = 301

export const MOCK_CREATE_RESPONSE = {
  link_id: MOCK_LINK_ID,
  short_url: MOCK_SHORT_URL,
  edit_token: MOCK_EDIT_TOKEN,
  redirect_code: MOCK_REDIRECT_CODE,
  created_at: '2026-01-01T00:00:00Z',
}

export const MOCK_LINK_OUT = {
  link_id: MOCK_LINK_ID,
  target_url: MOCK_TARGET_URL,
  redirect_code: MOCK_REDIRECT_CODE,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  active: true,
  expires_at: null,
}

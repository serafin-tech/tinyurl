export type CreateLinkPayload = {
  target_url: string;
  link_id?: string;
  redirect_code?: 301 | 302 | 307 | 308;
};

export type CreateLinkResponse = {
  link_id: string;
  short_url: string;
  edit_token: string;
  redirect_code: number;
  created_at: string;
};

export type LinkOut = {
  link_id: string;
  target_url: string;
  redirect_code: number;
  created_at: string;
  updated_at: string;
  active: boolean;
  expires_at: string | null;
};

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function createLink(payload: CreateLinkPayload): Promise<CreateLinkResponse> {
  const res = await fetch(`${API_BASE}/api/links`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateLink(linkId: string, token: string, data: Partial<Omit<CreateLinkPayload, 'link_id'>> & { new_link_id?: string }): Promise<LinkOut> {
  const res = await fetch(`${API_BASE}/api/links/${encodeURIComponent(linkId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'X-Edit-Token': token },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteLink(linkId: string, token: string): Promise<{ status: string; link_id: string }> {
  const res = await fetch(`${API_BASE}/api/links/${encodeURIComponent(linkId)}`, {
    method: 'DELETE',
    headers: { 'X-Edit-Token': token }
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

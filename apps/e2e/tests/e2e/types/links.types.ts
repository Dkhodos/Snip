export interface CreateLinkOptions {
  title: string;
  targetUrl: string;
  shortCode?: string;
}

export interface UpdateLinkOptions {
  title?: string;
  targetUrl?: string;
}

export type LinkStatus = 'All' | 'Active' | 'Inactive' | 'Expired';

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Profile {
  id: string;
  name: string;
  email?: string;
  resume_text?: string;
  resume_url?: string;
  career_goals?: any;
  interests: string[];
  strengths: string[];
  weaknesses: string[];
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  profile_id: string;
  title: string;
  company_name: string;
  company_id?: string;
  description?: string;
  url?: string;
  location?: string;
  salary_range?: string;
  source: 'manual' | 'search';
  status: 'interested' | 'applied' | 'interviewing' | 'rejected' | 'offered';
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  website?: string;
  industry?: string;
  size?: string;
  description?: string;
  culture_notes?: string;
  recent_news: any[];
  key_people: any[];
  research_summary?: string;
  last_researched_at?: string;
  created_at: string;
}

export interface STARAnswer {
  id: string;
  profile_id: string;
  situation: string;
  task: string;
  action: string;
  result: string;
  tags: string[];
  created_at: string;
}

export interface Application {
  id: string;
  job_id: string;
  profile_id: string;
  cover_letter?: string;
  outreach_emails: any[];
  notes?: string;
  status?: string;
  applied_at?: string;
  created_at: string;
}

// Profile API
export const profilesApi = {
  list: () => api.get<Profile[]>('/profiles'),
  get: (id: string) => api.get<Profile>(`/profiles/${id}`),
  create: (data: Partial<Profile>) => api.post<Profile>('/profiles', data),
  update: (id: string, data: Partial<Profile>) => api.patch<Profile>(`/profiles/${id}`, data),
  delete: (id: string) => api.delete(`/profiles/${id}`),
  uploadResume: (id: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/profiles/${id}/upload-resume`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  buildProfile: (id: string, data: { resume_text?: string; user_response?: string }) =>
    api.post(`/profiles/${id}/build`, data),
};

// STAR Answers API
export const starAnswersApi = {
  list: (profileId: string) => api.get<STARAnswer[]>(`/profiles/${profileId}/star-answers`),
  create: (profileId: string, data: Partial<STARAnswer>) =>
    api.post<STARAnswer>(`/profiles/${profileId}/star-answers`, data),
  delete: (id: string) => api.delete(`/profiles/star-answers/${id}`),
};

// Jobs API
export const jobsApi = {
  list: (params?: { profile_id?: string; status?: string; company_name?: string }) =>
    api.get<Job[]>('/jobs', { params }),
  get: (id: string) => api.get<Job>(`/jobs/${id}`),
  getFull: (id: string) => api.get(`/jobs/${id}/full`),
  create: (data: Partial<Job>) => api.post<Job>('/jobs', data),
  update: (id: string, data: Partial<Job>) => api.patch<Job>(`/jobs/${id}`, data),
  delete: (id: string) => api.delete(`/jobs/${id}`),
};

// Companies API
export const companiesApi = {
  list: () => api.get<Company[]>('/companies'),
  get: (id: string) => api.get<Company>(`/companies/${id}`),
  getByName: (name: string) => api.get<Company>(`/companies/by-name/${name}`),
  create: (data: Partial<Company>) => api.post<Company>('/companies', data),
  update: (id: string, data: Partial<Company>) => api.patch<Company>(`/companies/${id}`, data),
  delete: (id: string) => api.delete(`/companies/${id}`),
  research: (params: { company_name: string; website?: string; job_title?: string }) =>
    api.post('/companies/research', null, { params }),
};

// Content API
export const contentApi = {
  listApplications: (params?: { profile_id?: string; job_id?: string }) =>
    api.get<Application[]>('/content/applications', { params }),
  getApplication: (id: string) => api.get<Application>(`/content/applications/${id}`),
  createApplication: (data: Partial<Application>) =>
    api.post<Application>('/content/applications', data),
  updateApplication: (id: string, data: Partial<Application>) =>
    api.patch<Application>(`/content/applications/${id}`, data),
  deleteApplication: (id: string) => api.delete(`/content/applications/${id}`),
  generateContent: (params: { job_id: string; profile_id: string }) =>
    api.post('/content/generate', null, { params }),
};

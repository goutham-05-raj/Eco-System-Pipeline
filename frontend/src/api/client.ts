import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

export const fetchOverview = () => api.get('/overview').then(res => res.data);
export const fetchStartups = () => api.get('/startups').then(res => res.data);
export const fetchProducts = () => api.get('/products').then(res => res.data);
export const fetchResearch = () => api.get('/research').then(res => res.data);
export const fetchJobs = () => api.get('/jobs').then(res => res.data);
export const fetchNews = () => api.get('/news').then(res => res.data);

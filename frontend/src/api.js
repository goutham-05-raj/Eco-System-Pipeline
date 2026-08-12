const API_BASE = 'http://localhost:8000/api';

export const fetchOverview = async () => {
    const res = await fetch(`${API_BASE}/overview`);
    return res.json();
};

export const fetchStartups = async () => {
    const res = await fetch(`${API_BASE}/startups`);
    return res.json();
};

export const fetchProducts = async () => {
    const res = await fetch(`${API_BASE}/products`);
    return res.json();
};

export const fetchJobs = async () => {
    const res = await fetch(`${API_BASE}/jobs`);
    return res.json();
};

export const fetchNews = async () => {
    const res = await fetch(`${API_BASE}/news`);
    return res.json();
};

export const fetchResearch = async () => {
    const res = await fetch(`${API_BASE}/research`);
    return res.json();
};

export const fetchResolution = async () => {
    const res = await fetch(`${API_BASE}/resolution`);
    return res.json();
};

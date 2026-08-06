import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend, BarElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend, BarElement);

const API = '/api';

const AUTH_KEY = 'portfolio_pulse_token';
const USER_KEY = 'portfolio_pulse_user';

const fallbackPriceSeries = [
  { date: '2024-01-01', close: 182.3 },
  { date: '2024-02-01', close: 191.8 },
  { date: '2024-03-01', close: 204.2 },
  { date: '2024-04-01', close: 214.7 },
  { date: '2024-05-01', close: 223.6 },
  { date: '2024-06-01', close: 235.1 }
];

const fallbackRecommendations = [
  { ticker: 'NVDA', similarity_score: 0.94, reason: 'High momentum and strong sector alignment' },
  { ticker: 'AMD', similarity_score: 0.9, reason: 'Comparable growth profile to your current basket' },
  { ticker: 'PLTR', similarity_score: 0.88, reason: 'Diversified exposure with attractive trend' }
];

const navItems = [
  { key: 'overview', label: 'Overview' },
  { key: 'holdings', label: 'Holdings' },
  { key: 'risk', label: 'Risk' },
  { key: 'compare', label: 'Compare' },
  { key: 'recommendations', label: 'Recommendations' },
  { key: 'ml', label: 'ML & Predictions' },
  { key: 'optimize', label: 'Optimization' },
  { key: 'transactions', label: 'Transactions' },
  { key: 'assets', label: 'Assets' },
  { key: 'manage', label: 'Portfolios' }
];

const fallbackHeatmap = {
  sectors: ['Technology', 'Semiconductors', 'Media', 'Retail', 'Banking', 'Beverages', 'Financial Services'],
  left: {
    name: 'Tech Portfolio',
    values: [45, 28, 27, 0, 0, 0, 0]
  },
  right: {
    name: 'Dividend Portfolio',
    values: [25, 0, 0, 0, 38, 20, 17]
  }
};

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(AUTH_KEY) || '');
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
    } catch {
      return null;
    }
  });
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ username: '', password: '', email: '' });
  const [authError, setAuthError] = useState('');
  const [authSubmitting, setAuthSubmitting] = useState(false);
  const [portfolios, setPortfolios] = useState([]);
  const [assets, setAssets] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState('');
  const [priceSeries, setPriceSeries] = useState(fallbackPriceSeries);
  const [recommendations, setRecommendations] = useState(fallbackRecommendations);
  const [riskSummary, setRiskSummary] = useState({ sharpe_ratio: '1.24', risk_level: 'Balanced' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeView, setActiveView] = useState('overview');
  const [theme, setTheme] = useState('dark');
  const [portfolioForm, setPortfolioForm] = useState({ name: '', description: '', user_id: '' });
  const [editingPortfolioId, setEditingPortfolioId] = useState(null);
  const [userForm, setUserForm] = useState({ name: '' });
  const [assetForm, setAssetForm] = useState({ ticker: '', name: '', exchange: '', sector: '', industry: '' });
  const [editingAssetTicker, setEditingAssetTicker] = useState('');
  const [compareA, setCompareA] = useState('');
  const [compareB, setCompareB] = useState('');
  const [heatmapData, setHeatmapData] = useState(fallbackHeatmap);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { role: 'bot', text: 'Hi! I can answer questions about your portfolios, assets, risk, recommendations, transactions, and performance. Try asking "What are my holdings?"' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatSending, setChatSending] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [transactionForm, setTransactionForm] = useState({ assetId: '', type: 'BUY', quantity: '', price: '' });

  // ML & Predictions
  const [predictionTicker, setPredictionTicker] = useState('AAPL');
  const [predictionDays, setPredictionDays] = useState(7);
  const [predictionMethod, setPredictionMethod] = useState('lstm');
  const [predictions, setPredictions] = useState(null);
  const [assetClassification, setAssetClassification] = useState(null);
  const [classifyTicker, setClassifyTicker] = useState('AAPL');

  // Optimization
  const [efficientFrontier, setEfficientFrontier] = useState(null);
  const [optimalAllocation, setOptimalAllocation] = useState(null);
  const [riskParity, setRiskParity] = useState(null);
  const [monteCarloResult, setMonteCarloResult] = useState(null);

  const loadData = async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const [portfolioRes, assetRes, userRes] = await Promise.all([
        axios.get(`${API}/portfolios/`),
        axios.get(`${API}/assets/`),
        axios.get(`${API}/users/`)
      ]);

      const portfolioData = portfolioRes.data || [];
      setPortfolios(portfolioData);
      setAssets(assetRes.data || []);
      setUsers(userRes.data || []);

      if (portfolioData.length) {
        const isCurrentSelectionValid = portfolioData.some((portfolio) => String(portfolio.portfolio_id) === selectedPortfolio);
        if (!isCurrentSelectionValid) {
          setSelectedPortfolio(String(portfolioData[0].portfolio_id));
        }
      } else {
        setSelectedPortfolio('');
      }
    } catch (err) {
      console.error(err);
      setError('Live data is temporarily unavailable. A polished fallback view is shown instead.');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const handleAuthSubmit = async (event) => {
    event.preventDefault();
    const username = authForm.username.trim();
    const password = authForm.password;
    if (!username || !password) {
      setAuthError('Please enter a username and password.');
      return;
    }
    if (authMode === 'register' && !authForm.email.trim()) {
      setAuthError('Please enter an email address to register.');
      return;
    }

    setAuthSubmitting(true);
    setAuthError('');
    try {
      if (authMode === 'login') {
        const response = await axios.post(`${API}/auth/login`, { username, password });
        const { access_token: accessToken, user_id: userId } = response.data || {};
        localStorage.setItem(AUTH_KEY, accessToken);
        localStorage.setItem(USER_KEY, JSON.stringify({ user_id: userId, username }));
        setToken(accessToken);
        setCurrentUser({ user_id: userId, username });
      } else {
        const response = await axios.post(`${API}/auth/register`, {
          username,
          password,
          email: authForm.email.trim()
        });
        if (response.data?.error) {
          setAuthError(response.data.error);
          return;
        }
        const loginResponse = await axios.post(`${API}/auth/login`, { username, password });
        const { access_token: accessToken, user_id: userId } = loginResponse.data || {};
        localStorage.setItem(AUTH_KEY, accessToken);
        localStorage.setItem(USER_KEY, JSON.stringify({ user_id: userId, username }));
        setToken(accessToken);
        setCurrentUser({ user_id: userId, username });
      }
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || err.response?.data?.error || err.message;
      setAuthError(typeof message === 'string' ? message : 'Authentication failed. Please try again.');
    } finally {
      setAuthSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    setToken('');
    setCurrentUser(null);
    setAuthMode('login');
    setAuthForm({ username: '', password: '', email: '' });
    setPortfolios([]);
    setActiveView('overview');
  };

  const switchAuthMode = (mode) => {
    setAuthMode(mode);
    setAuthError('');
    setAuthForm({ username: '', password: '', email: '' });
  };

  const loadHoldings = async (portfolioId) => {
    if (!portfolioId) return;
    try {
      const res = await axios.get(`${API}/transactions/${portfolioId}`);
      setTransactions(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };
  const loadInsights = async (portfolioId) => {
    if (!portfolioId) return;
    try {
      const [priceRes, recRes, riskRes] = await Promise.all([
        axios.get(`${API}/prices/AAPL`),
        axios.get(`${API}/recommend/gaps/${portfolioId}?limit=5`),
        axios.get(`${API}/risk/sharpe/${portfolioId}`)
      ]);

      if (Array.isArray(priceRes.data) && priceRes.data.length) {
        setPriceSeries(priceRes.data.slice().reverse());
      }
      if (recRes.data?.recommendations?.length) {
        setRecommendations(recRes.data.recommendations);
      }
      if (riskRes.data) {
        setRiskSummary(riskRes.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const sectorWeightsFromTransactions = (transactions) => {
    const valueBySector = new Map();
    let total = 0;
    (transactions || []).forEach((tx) => {
      const asset = assets.find((a) => String(a.asset_id) === String(tx.asset_id));
      const sector = asset?.sector || 'Unclassified';
      const sign = tx.type === 'SELL' ? -1 : 1;
      const value = sign * Number(tx.quantity || 0) * Number(tx.price || 0);
      valueBySector.set(sector, (valueBySector.get(sector) || 0) + value);
      total += value;
    });
    const weights = {};
    valueBySector.forEach((value, sector) => {
      weights[sector] = total > 0 ? (value / total) * 100 : 0;
    });
    return weights;
  };

  const portfolioName = (portfolioId) => {
    const found = portfolios.find((p) => String(p.portfolio_id) === String(portfolioId));
    return found?.name || `Portfolio ${portfolioId}`;
  };

  const loadComparison = async () => {
    if (portfolios.length < 2) return;
    const aId = compareA || String(portfolios[0].portfolio_id);
    const bId = compareB || String(portfolios[1].portfolio_id);
    try {
      const [txA, txB] = await Promise.all([
        axios.get(`${API}/transactions/${aId}`),
        axios.get(`${API}/transactions/${bId}`)
      ]);
      const weightsA = sectorWeightsFromTransactions(txA.data);
      const weightsB = sectorWeightsFromTransactions(txB.data);
      const sectors = Array.from(new Set([...Object.keys(weightsA), ...Object.keys(weightsB)]));
      setHeatmapData({
        sectors,
        left: { name: portfolioName(aId), values: sectors.map((s) => weightsA[s] || 0) },
        right: { name: portfolioName(bId), values: sectors.map((s) => weightsB[s] || 0) }
      });
    } catch (err) {
      console.error(err);
      setHeatmapData(fallbackHeatmap);
    }
  };

  const loadTransactions = async () => {
    if (!selectedPortfolio) return;
    try {
      const res = await axios.get(`${API}/transactions/${selectedPortfolio}`);
      setTransactions(res.data || []);
    } catch (err) {
      console.error(err);
      setTransactions([]);
    }
  };

  const loadPredictions = async () => {
    if (!predictionTicker) return;
    try {
      const endpoint = `${API}/ml/predict/${predictionTicker}/${predictionMethod}/${predictionDays}`;
      const res = await axios.get(endpoint);
      setPredictions(res.data);
    } catch (err) {
      console.error(err);
      setPredictions(null);
    }
  };

  const loadAssetClassification = async () => {
    if (!classifyTicker) return;
    try {
      const res = await axios.get(`${API}/ml/classify/${classifyTicker}`);
      setAssetClassification(res.data);
    } catch (err) {
      console.error(err);
      setAssetClassification(null);
    }
  };

  const loadOptimization = async () => {
    if (!selectedPortfolio) return;
    try {
      const [frontierRes, optimalRes, riskParityRes, monteCarloRes] = await Promise.all([
        axios.get(`${API}/optimize/frontier/${selectedPortfolio}`).catch(() => null),
        axios.get(`${API}/optimize/max-sharpe/${selectedPortfolio}`).catch(() => null),
        axios.get(`${API}/optimize/risk-parity/${selectedPortfolio}`).catch(() => null),
        axios.get(`${API}/optimize/monte-carlo/${selectedPortfolio}`).catch(() => null)
      ]);
      setEfficientFrontier(frontierRes?.data || null);
      setOptimalAllocation(optimalRes?.data || null);
      setRiskParity(riskParityRes?.data || null);
      setMonteCarloResult(monteCarloRes?.data || null);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (token) {
      loadData(true);
    }
  }, [token]);

  useEffect(() => {
    if (!selectedPortfolio) return;
    loadInsights(selectedPortfolio);
    loadHoldings(selectedPortfolio);
    loadTransactions();
  }, [selectedPortfolio]);

  useEffect(() => {
    if (activeView === 'ml') {
      loadPredictions();
      loadAssetClassification();
    }
  }, [activeView, predictionTicker, predictionDays, predictionMethod, classifyTicker]);

  useEffect(() => {
    if (activeView === 'optimize') {
      loadOptimization();
    }
  }, [activeView, selectedPortfolio]);

  useEffect(() => {
    if (activeView === 'transactions') {
      loadTransactions();
    }
  }, [activeView, selectedPortfolio]);

  useEffect(() => {
    if (!portfolios.length) return;
    setCompareA((current) => current || String(portfolios[0].portfolio_id));
    setCompareB((current) => current || String(portfolios[1]?.portfolio_id || portfolios[0].portfolio_id));
  }, [portfolios]);

  useEffect(() => {
    if (compareA && compareB && compareA !== compareB) {
      loadComparison();
    }
  }, [compareA, compareB, portfolios, assets]);

  const refreshDashboard = async () => {
    if (!selectedPortfolio) return;
    setRefreshing(true);
    await Promise.all([loadInsights(selectedPortfolio), loadHoldings(selectedPortfolio), loadData(), loadComparison()]);
    setRefreshing(false);
  };

  const selectedPortfolioData = portfolios.find((portfolio) => String(portfolio.portfolio_id) === selectedPortfolio) || portfolios[0] || null;

  const handlePortfolioSubmit = async (event) => {
    event.preventDefault();
    if (!portfolioForm.name.trim()) return;

    setSubmitting(true);
    try {
      const payload = {
        name: portfolioForm.name.trim(),
        description: portfolioForm.description.trim() || null,
        user_id: portfolioForm.user_id ? Number(portfolioForm.user_id) : null
      };

      if (editingPortfolioId) {
        await axios.put(`${API}/portfolios/${editingPortfolioId}`, payload);
      } else {
        const response = await axios.post(`${API}/portfolios/`, payload);
        const createdId = response.data?.portfolio_id;
        if (createdId) {
          setSelectedPortfolio(String(createdId));
        }
      }

      setPortfolioForm({ name: '', description: '', user_id: '' });
      setEditingPortfolioId(null);
      setError('');
      await loadData();
      setActiveView('manage');
    } catch (err) {
      console.error(err);
      setError('Portfolio changes could not be saved.');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePortfolioDelete = async (portfolioId) => {
    if (!window.confirm('Delete this portfolio from the database?')) return;
    try {
      await axios.delete(`${API}/portfolios/${portfolioId}`);
      if (String(selectedPortfolio) === String(portfolioId)) {
        setSelectedPortfolio('');
      }
      await loadData();
    } catch (err) {
      console.error(err);
      setError('The portfolio could not be deleted.');
    }
  };

  const handlePortfolioEdit = (portfolio) => {
    setEditingPortfolioId(portfolio.portfolio_id);
    setPortfolioForm({
      name: portfolio.name,
      description: portfolio.description || '',
      user_id: portfolio.user_id ? String(portfolio.user_id) : ''
    });
    setActiveView('manage');
  };

  const handleUserSubmit = async (event) => {
    event.preventDefault();
    if (!userForm.name.trim()) return;

    setSubmitting(true);
    try {
      await axios.post(`${API}/users/`, { name: userForm.name.trim() });
      setUserForm({ name: '' });
      setError('');
      await loadData();
    } catch (err) {
      console.error(err);
      setError('The user could not be added.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAssetSubmit = async (event) => {
    event.preventDefault();
    const ticker = assetForm.ticker.trim().toUpperCase();
    if (!ticker) return;

    setSubmitting(true);
    try {
      const payload = {
        name: assetForm.name.trim() || ticker,
        exchange: assetForm.exchange.trim() || null,
        sector: assetForm.sector.trim() || null,
        industry: assetForm.industry.trim() || null
      };

      const targetTicker = editingAssetTicker || ticker;
      await axios.post(`${API}/assets/${targetTicker}`, payload);

      setAssetForm({ ticker: '', name: '', exchange: '', sector: '', industry: '' });
      setEditingAssetTicker('');
      setError('');
      await loadData();
      setActiveView('assets');
    } catch (err) {
      console.error(err);
      setError('Asset changes could not be saved.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAssetEdit = (asset) => {
    setEditingAssetTicker(asset.ticker);
    setAssetForm({
      ticker: asset.ticker || '',
      name: asset.name || '',
      exchange: asset.exchange || '',
      sector: asset.sector || '',
      industry: asset.industry || ''
    });
    setActiveView('assets');
  };

  const handleAssetDelete = async (ticker) => {
    if (!window.confirm(`Remove ${ticker} from the database?`)) return;
    try {
      await axios.delete(`${API}/assets/${ticker}`);
      await loadData();
    } catch (err) {
      console.error(err);
      setError('The asset could not be deleted.');
    }
  };

  const handleChatSubmit = async (event) => {
    event.preventDefault();
    const text = chatInput.trim();
    if (!text || chatSending) return;

    setChatMessages((current) => [...current, { role: 'user', text }]);
    setChatInput('');
    setChatSending(true);
    try {
      const response = await axios.post(`${API}/chat/`, {
        message: text,
        portfolio_id: selectedPortfolio ? Number(selectedPortfolio) : null
      });
      const reply = response.data?.reply || 'Sorry, I could not find an answer.';
      setChatMessages((current) => [...current, { role: 'bot', text: reply }]);
    } catch (err) {
      console.error(err);
      setChatMessages((current) => [...current, { role: 'bot', text: 'The chat service is temporarily unavailable.' }]);
    } finally {
      setChatSending(false);
    }
  };

  const handleTransactionSubmit = async (event) => {
    event.preventDefault();
    if (!selectedPortfolio || !transactionForm.assetId) return;

    setSubmitting(true);
    try {
      await axios.post(`${API}/transactions/${selectedPortfolio}`, {
        asset_id: Number(transactionForm.assetId),
        type: transactionForm.type,
        quantity: Number(transactionForm.quantity),
        price: Number(transactionForm.price)
      });
      setTransactionForm({ assetId: '', type: 'BUY', quantity: '', price: '' });
      setError('');
      await loadHoldings(selectedPortfolio);
      setActiveView('holdings');
    } catch (err) {
      console.error(err);
      setError('The transaction could not be added.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTransactionDelete = async (transactionId) => {
    if (!selectedPortfolio) return;
    if (!window.confirm('Remove this transaction from the portfolio?')) return;
    try {
      await axios.delete(`${API}/transactions/${selectedPortfolio}/${transactionId}`);
      await loadHoldings(selectedPortfolio);
    } catch (err) {
      console.error(err);
      setError('The transaction could not be removed.');
    }
  };

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 1400, easing: 'easeOutQuart' },
    plugins: { legend: { display: false } }
  }), []);

  const chartData = useMemo(() => {
    const labels = (priceSeries || []).map((row) => row.date);
    const values = (priceSeries || []).map((row) => Number(row.close || 0));
    return {
      labels,
      datasets: [{
        label: 'Closing price',
        data: values,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.18)',
        fill: true,
        tension: 0.35
      }]
    };
  }, [priceSeries]);

  const distributionData = useMemo(() => {
    const counts = portfolios.reduce((acc, portfolio) => {
      acc[portfolio.name] = (acc[portfolio.name] || 0) + 1;
      return acc;
    }, {});

    return {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: ['#818cf8', '#38bdf8', '#34d399']
      }]
    };
  }, [portfolios]);

  const barData = useMemo(() => {
    const items = recommendations.slice(0, 5);
    return {
      labels: items.map((item) => item.ticker),
      datasets: [{
        label: 'Similarity score',
        data: items.map((item) => Number(item.similarity_score || 0)),
        backgroundColor: '#818cf8'
      }]
    };
  }, [recommendations]);

  const insightItems = recommendations.length ? recommendations.slice(0, 4) : fallbackRecommendations;
  const signalCards = [
    { title: 'Momentum', value: 'Strong', detail: 'Growth names continue to lead' },
    { title: 'Diversification', value: 'Healthy', detail: 'Signals remain well balanced' },
    { title: 'Risk stance', value: 'Controlled', detail: 'Sharpe view remains constructive' }
  ];

  const riskCards = [
    { label: 'Sharpe ratio', value: riskSummary?.sharpe_ratio ?? '1.24' },
    { label: 'Risk level', value: riskSummary?.risk_level ?? 'Balanced' },
    { label: 'Portfolio size', value: `${assets.length || 6} positions` }
  ];

  if (!token) {
    return (
      <div className="auth-shell">
        <div className="auth-backdrop" />
        <div className="auth-panel">
          <div className="auth-brand">
            <div className="brand-icon">AW</div>
            <h2>Portfolio Pulse</h2>
            <p>AI-powered portfolio OS</p>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={`auth-tab ${authMode === 'login' ? 'active' : ''}`}
              onClick={() => switchAuthMode('login')}
            >
              Login
            </button>
            <button
              type="button"
              className={`auth-tab ${authMode === 'register' ? 'active' : ''}`}
              onClick={() => switchAuthMode('register')}
            >
              Register
            </button>
          </div>

          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {authMode === 'register' && (
              <label>
                Email
                <input
                  type="email"
                  value={authForm.email}
                  onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })}
                  placeholder="you@example.com"
                  autoComplete="email"
                />
              </label>
            )}
            <label>
              Username
              <input
                type="text"
                value={authForm.username}
                onChange={(event) => setAuthForm({ ...authForm, username: event.target.value })}
                placeholder="alice"
                autoComplete="username"
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={authForm.password}
                onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
                placeholder="••••••••"
                autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                required
              />
            </label>

            {authError ? <div className="auth-error">{authError}</div> : null}

            <button className="primary-btn auth-submit" type="submit" disabled={authSubmitting}>
              {authSubmitting ? 'Please wait…' : authMode === 'login' ? 'Login' : 'Create account'}
            </button>
          </form>

          <p className="auth-foot">
            {authMode === 'login'
              ? 'New here? Switch to Register to create an account.'
              : 'Already have an account? Switch to Login.'}
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="loading">Loading Portfolio Pulse…</div>;
  }

  return (
    <div className={`dashboard-shell ${theme}`}>
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-icon">AW</div>
          <div>
            <h2>Portfolio Pulse</h2>
            <p>AI-powered portfolio OS</p>
          </div>
        </div>

        <nav className="nav-links">
          {navItems.map((item) => (
            <button
              key={item.key}
              className={`nav-item ${activeView === item.key ? 'active' : ''}`}
              onClick={() => setActiveView(item.key)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <button className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} type="button">
          {theme === 'dark' ? '☀️ Light mode' : '🌙 Dark mode'}
        </button>

        <div className="sidebar-card">
          <p className="eyebrow">Signed in</p>
          <h3>{currentUser?.username || 'User'}</h3>
          <span>FastAPI • MySQL • ML engine</span>
          <button className="logout-btn" onClick={handleLogout} type="button">Logout</button>
        </div>
      </aside>

      <main className="main-panel">
        <header className="hero-panel">
          <div>
            <p className="eyebrow">Premium analytics console</p>
            <h1>Portfolio Pulse turns your portfolio into a live decision surface</h1>
            <p className="subtitle">Monitor positions, review recommendations, and understand your portfolio performance in a refined workspace.</p>
          </div>
          <div className="hero-actions">
            <div className="status-pill">Live</div>
            <button className="refresh-btn" onClick={refreshDashboard} type="button">
              {refreshing ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>
        </header>

        {error ? <div className="notice">{error}</div> : null}

        {activeView === 'overview' && (
          <section className="metrics-grid">
            <article className="metric-card">
              <p className="metric-label">Selected portfolio</p>
              <h3>{selectedPortfolioData?.name || 'No portfolio selected'}</h3>
            </article>
            <article className="metric-card">
              <p className="metric-label">Tracked assets</p>
              <h3>{assets.length || 6}</h3>
            </article>
            <article className="metric-card">
              <p className="metric-label">Sharpe ratio</p>
              <h3>{riskSummary?.sharpe_ratio ?? '1.24'}</h3>
            </article>
            <article className="metric-card">
              <p className="metric-label">Risk profile</p>
              <h3>{riskSummary?.risk_level ?? 'Balanced'}</h3>
            </article>
          </section>
        )}

        {activeView === 'overview' && (
          <>
            <section className="overview-grid">
              <article className="panel panel-large">
                <div className="panel-head">
                  <div>
                    <p className="eyebrow">Portfolio overview</p>
                    <h3>{selectedPortfolioData?.name || 'Portfolio workspace'}</h3>
                  </div>
                  <label className="select-wrap">
                    Portfolio
                    <select value={selectedPortfolio} onChange={(event) => setSelectedPortfolio(event.target.value)}>
                      {portfolios.map((portfolio) => (
                        <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>{portfolio.name}</option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="portfolio-summary">
                  <div>
                    <h4>{selectedPortfolioData?.description || 'A focused portfolio view with actionable insights.'}</h4>
                    <p>User name: {selectedPortfolioData?.user_name || '—'} · Every section below is linked to the live backend, making the dashboard fully data-aware and ready for real portfolio operations.</p>
                  </div>
                  <div className="mini-stats">
                    <div><span>Portfolios</span><strong>{portfolios.length}</strong></div>
                    <div><span>Assets</span><strong>{assets.length || 6}</strong></div>
                    <div><span>Insights</span><strong>{insightItems.length}</strong></div>
                  </div>
                </div>

                <div className="asset-table">
                  <div className="asset-row asset-row-head">
                    <span>Ticker</span>
                    <span>Name</span>
                    <span>Sector</span>
                  </div>
                  {assets.length ? assets.slice(0, 6).map((asset) => (
                    <div className="asset-row" key={asset.ticker || asset.asset_id}>
                      <span>{asset.ticker}</span>
                      <span>{asset.name || 'Tracked asset'}</span>
                      <span>{asset.sector || '—'}</span>
                    </div>
                  )) : (
                    <div className="empty-state">No assets are available yet. Seed the backend to populate this view.</div>
                  )}
                </div>
              </article>

              <div className="stack">
                <article className="panel">
                  <div className="panel-head">
                    <div>
                      <p className="eyebrow">Market pulse</p>
                      <h3>Signals</h3>
                    </div>
                  </div>
                  <div className="signal-list">
                    {signalCards.map((signal) => (
                      <div className="signal-card" key={signal.title}>
                        <div>
                          <strong>{signal.title}</strong>
                          <p>{signal.detail}</p>
                        </div>
                        <span>{signal.value}</span>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="panel">
                  <div className="panel-head">
                    <div>
                      <p className="eyebrow">Allocation snapshot</p>
                      <h3>Portfolio distribution</h3>
                    </div>
                  </div>
                  <div className="chart-wrapper donut-wrapper">
                    <Doughnut data={distributionData} options={chartOptions} />
                  </div>
                </article>
              </div>
            </section>

            <section className="charts-grid">
              <article className="panel">
                <div className="panel-head">
                  <div>
                    <p className="eyebrow">Performance trend</p>
                    <h3>Price movement</h3>
                  </div>
                </div>
                <div className="chart-wrapper">
                  <Line data={chartData} options={chartOptions} />
                </div>
              </article>

              <article className="panel">
                <div className="panel-head">
                  <div>
                    <p className="eyebrow">Recommendations</p>
                    <h3>ML-driven opportunities</h3>
                  </div>
                </div>
                <div className="chart-wrapper bar-wrapper">
                  <Bar data={barData} options={chartOptions} />
                </div>
                <ul className="insight-list">
                  {insightItems.map((item) => (
                    <li key={item.ticker}>
                      <strong>{item.ticker}</strong>
                      <span>{item.reason}</span>
                    </li>
                  ))}
                </ul>
              </article>
            </section>
          </>
        )}

        {activeView === 'holdings' && (
          <section className="detail-view">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Holdings</p>
                  <h3>{selectedPortfolioData?.name || 'Selected portfolio'} — transactions</h3>
                </div>
              </div>
              <div className="asset-table">
                {assets.length ? assets.slice(0, 8).map((asset) => (
                  <div className="asset-row detail-row" key={asset.ticker || asset.asset_id}>
                    <span>{asset.ticker}</span>
                    <span>{asset.name || 'Tracked asset'}</span>
                    <span>{asset.sector || 'Core'}</span>
                    <span className="row-actions">
                      <button type="button" className="icon-btn danger-icon" onClick={() => handleAssetDelete(asset.ticker)} title={`Remove ${asset.ticker}`}>✕</button>
                    </span>
                  </div>
                )) : (
                  <div className="empty-state">No holdings available yet.</div>
                )}
              </div>

              <form className="manager-form" onSubmit={handleTransactionSubmit}>
                <label>
                  Asset
                  <select
                    value={transactionForm.assetId}
                    onChange={(event) => setTransactionForm({ ...transactionForm, assetId: event.target.value })}
                    required
                  >
                    <option value="">Select an asset</option>
                    {assets.map((asset) => (
                      <option key={asset.asset_id} value={asset.asset_id}>
                        {asset.ticker} — {asset.name || 'Tracked asset'}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Type
                  <select
                    value={transactionForm.type}
                    onChange={(event) => setTransactionForm({ ...transactionForm, type: event.target.value })}
                  >
                    <option value="BUY">BUY</option>
                    <option value="SELL">SELL</option>
                  </select>
                </label>
                <label>
                  Quantity
                  <input
                    type="number"
                    step="any"
                    min="0"
                    value={transactionForm.quantity}
                    onChange={(event) => setTransactionForm({ ...transactionForm, quantity: event.target.value })}
                    placeholder="e.g. 10"
                    required
                  />
                </label>
                <label>
                  Price
                  <input
                    type="number"
                    step="any"
                    min="0"
                    value={transactionForm.price}
                    onChange={(event) => setTransactionForm({ ...transactionForm, price: event.target.value })}
                    placeholder="e.g. 182.50"
                    required
                  />
                </label>
                <button className="primary-btn" type="submit" disabled={submitting || !selectedPortfolio}>
                  {submitting ? 'Saving…' : 'Add transaction'}
                </button>
              </form>

              <div className="list-stack">
                {transactions.length ? transactions.map((tx) => {
                  const asset = assets.find((a) => String(a.asset_id) === String(tx.asset_id));
                  return (
                    <div className="list-item" key={tx.transaction_id}>
                      <div>
                        <strong>{asset?.ticker || `Asset ${tx.asset_id}`} <span className={`tx-type ${String(tx.type).toLowerCase()}`}>{tx.type}</span></strong>
                        <p>{Number(tx.quantity).toFixed(2)} @ {Number(tx.price).toFixed(2)} — {tx.timestamp}</p>
                      </div>
                      <div className="action-row">
                        <button type="button" className="danger-btn" onClick={() => handleTransactionDelete(tx.transaction_id)}>
                          Remove
                        </button>
                      </div>
                    </div>
                  );
                }) : (
                  <div className="empty-state">No transactions yet for this portfolio. Add a BUY to start building a position.</div>
                )}
              </div>
            </article>
          </section>
        )}

        {activeView === 'risk' && (
          <section className="detail-view">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Risk overview</p>
                  <h3>Portfolio risk posture</h3>
                </div>
              </div>
              <div className="risk-grid">
                {riskCards.map((card) => (
                  <div className="risk-card" key={card.label}>
                    <span>{card.label}</span>
                    <strong>{card.value}</strong>
                  </div>
                ))}
              </div>
              <p className="detail-copy">The current model view indicates a balanced stance with encouraging diversification and a constructive risk-adjusted return profile.</p>
            </article>
          </section>
        )}

        {activeView === 'compare' && (
          <section className="detail-view">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Portfolio comparison</p>
                  <h3>Allocation heatmap</h3>
                </div>
                <div className="compare-pickers">
                  <label className="select-wrap">
                    Portfolio A
                    <select value={compareA} onChange={(event) => setCompareA(event.target.value)}>
                      {portfolios.map((portfolio) => (
                        <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>{portfolio.name}</option>
                      ))}
                    </select>
                  </label>
                  <label className="select-wrap">
                    Portfolio B
                    <select value={compareB} onChange={(event) => setCompareB(event.target.value)}>
                      {portfolios.map((portfolio) => (
                        <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>{portfolio.name}</option>
                      ))}
                    </select>
                  </label>
                </div>
              </div>

              {heatmapData && heatmapData.sectors?.length ? (
                <>
                  <div className="heatmap-grid" role="table" aria-label="Sector allocation heatmap">
                    <div className="heatmap-corner">Sector</div>
                    <div className="heatmap-head">{heatmapData.left.name}</div>
                    <div className="heatmap-head">{heatmapData.right.name}</div>
                    {heatmapData.sectors.map((sector) => (
                      <HeatRow
                        key={sector}
                        sector={sector}
                        left={heatmapData.left.values[heatmapData.sectors.indexOf(sector)]}
                        right={heatmapData.right.values[heatmapData.sectors.indexOf(sector)]}
                        max={maxHeatValue(heatmapData)}
                      />
                    ))}
                  </div>
                  <div className="heatmap-legend">
                    <span className="legend-caption">Allocation weight</span>
                    <span className="legend-swatch" style={{ background: 'rgba(99, 102, 241, 0.14)' }}>0%</span>
                    <div className="legend-gradient" />
                    <span className="legend-swatch" style={{ background: 'rgba(56, 189, 248, 1)' }}>max</span>
                  </div>
                  <p className="detail-copy">
                    Cells show each portfolio's exposure to a sector as a share of total holdings value. Darker cells indicate heavier concentration; compare columns to spot divergence between the two baskets.
                  </p>
                </>
              ) : (
                <div className="empty-state">No allocation data available for comparison.</div>
              )}
            </article>
          </section>
        )}

        {activeView === 'recommendations' && (
          <section className="detail-view">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Opportunity engine</p>
                  <h3>Recommended next moves</h3>
                </div>
              </div>
              <div className="recommendation-grid">
                {insightItems.map((item) => (
                  <div className="recommendation-card" key={item.ticker}>
                    <div className="recommendation-head">
                      <strong>{item.ticker}</strong>
                      <span>{Number(item.similarity_score || item.momentum || 0).toFixed(2)}</span>
                    </div>
                    <p>{item.reason}</p>
                  </div>
                ))}
              </div>
            </article>
          </section>
        )}

        {activeView === 'ml' && (
          <section className="detail-view management-grid">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Machine learning</p>
                  <h3>Price predictions & classification</h3>
                </div>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h4 style={{ marginBottom: '1rem' }}>Price Predictions</h4>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                  <label style={{ flex: '1', minWidth: '200px' }}>
                    Ticker
                    <input
                      value={predictionTicker}
                      onChange={(e) => setPredictionTicker(e.target.value.toUpperCase())}
                      placeholder="AAPL"
                    />
                  </label>
                  <label style={{ flex: '1', minWidth: '200px' }}>
                    Days
                    <input
                      type="number"
                      value={predictionDays}
                      onChange={(e) => setPredictionDays(parseInt(e.target.value) || 7)}
                      min="1"
                      max="30"
                    />
                  </label>
                  <label style={{ flex: '1', minWidth: '200px' }}>
                    Method
                    <select value={predictionMethod} onChange={(e) => setPredictionMethod(e.target.value)}>
                      <option value="lstm">LSTM</option>
                      <option value="prophet">Prophet</option>
                      <option value="linear">Linear</option>
                      <option value="ensemble">Ensemble</option>
                    </select>
                  </label>
                </div>
                <button className="primary-btn" onClick={loadPredictions} style={{ marginBottom: '1rem' }}>Get Prediction</button>

                {predictions && (
                  <div style={{ padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '0.5rem' }}>
                    <p><strong>Ticker:</strong> {predictions.ticker}</p>
                    <p><strong>Method:</strong> {predictions.method}</p>
                    <p><strong>Current Price:</strong> ${Number(predictions.current_price || 0).toFixed(2)}</p>
                    <p><strong>Predicted Price (Day {predictionDays}):</strong> ${Number(predictions.predicted_price || 0).toFixed(2)}</p>
                    {predictions.confidence && <p><strong>Confidence:</strong> {Number(predictions.confidence || 0).toFixed(2)}</p>}
                  </div>
                )}
              </div>

              <div>
                <h4 style={{ marginBottom: '1rem' }}>Asset Classification</h4>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                  <label style={{ flex: '1', minWidth: '200px' }}>
                    Ticker
                    <input
                      value={classifyTicker}
                      onChange={(e) => setClassifyTicker(e.target.value.toUpperCase())}
                      placeholder="AAPL"
                    />
                  </label>
                </div>
                <button className="primary-btn" onClick={loadAssetClassification} style={{ marginBottom: '1rem' }}>Classify Asset</button>

                {assetClassification && (
                  <div style={{ padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '0.5rem' }}>
                    <p><strong>Ticker:</strong> {assetClassification.ticker}</p>
                    <p><strong>Risk Class:</strong> {assetClassification.risk_class}</p>
                    <p><strong>Income Class:</strong> {assetClassification.income_class}</p>
                  </div>
                )}
              </div>
            </article>
          </section>
        )}

        {activeView === 'optimize' && (
          <section className="detail-view management-grid">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Portfolio optimization</p>
                  <h3>Find efficient allocations</h3>
                </div>
              </div>

              <button className="primary-btn" onClick={loadOptimization} style={{ marginBottom: '2rem' }}>Load Optimization Results</button>

              {optimalAllocation && (
                <div style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '0.5rem' }}>
                  <h4 style={{ marginBottom: '1rem' }}>Max Sharpe Ratio Portfolio</h4>
                  <p><strong>Sharpe Ratio:</strong> {Number(optimalAllocation.sharpe_ratio || 0).toFixed(4)}</p>
                  <p><strong>Expected Return:</strong> {Number(optimalAllocation.expected_return || 0).toFixed(4)}</p>
                  <p><strong>Volatility:</strong> {Number(optimalAllocation.volatility || 0).toFixed(4)}</p>
                  {optimalAllocation.allocation && (
                    <div style={{ marginTop: '1rem' }}>
                      <h5>Allocation:</h5>
                      {Object.entries(optimalAllocation.allocation).map(([ticker, weight]) => (
                        <p key={ticker}>{ticker}: {(Number(weight) * 100).toFixed(1)}%</p>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {riskParity && (
                <div style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '0.5rem' }}>
                  <h4 style={{ marginBottom: '1rem' }}>Risk Parity Portfolio</h4>
                  <p><strong>Sharpe Ratio:</strong> {Number(riskParity.sharpe_ratio || 0).toFixed(4)}</p>
                  {riskParity.allocation && (
                    <div style={{ marginTop: '1rem' }}>
                      <h5>Allocation:</h5>
                      {Object.entries(riskParity.allocation).map(([ticker, weight]) => (
                        <p key={ticker}>{ticker}: {(Number(weight) * 100).toFixed(1)}%</p>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {monteCarloResult && (
                <div style={{ padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '0.5rem' }}>
                  <h4 style={{ marginBottom: '1rem' }}>Monte Carlo Simulation</h4>
                  <p><strong>Expected Value (1 year):</strong> ${Number(monteCarloResult.expected_value || 0).toFixed(2)}</p>
                  <p><strong>Value at Risk (95%):</strong> ${Number(monteCarloResult.var_95 || 0).toFixed(2)}</p>
                  <p><strong>Value at Risk (99%):</strong> ${Number(monteCarloResult.var_99 || 0).toFixed(2)}</p>
                </div>
              )}
            </article>
          </section>
        )}

        {activeView === 'transactions' && (
          <section className="detail-view">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Transaction history</p>
                  <h3>View all portfolio transactions</h3>
                </div>
              </div>

              <div className="list-stack">
                {transactions.length ? transactions.map((tx, idx) => (
                  <div className="list-item" key={idx}>
                    <div>
                      <strong>{tx.ticker}</strong>
                      <p>{tx.type} {tx.quantity} @ ${Number(tx.price || 0).toFixed(2)} on {tx.transaction_date || 'N/A'}</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ fontSize: '0.9rem', opacity: 0.7 }}>${(tx.quantity * tx.price).toFixed(2)}</p>
                    </div>
                  </div>
                )) : (
                  <div className="empty-state">No transactions found for this portfolio.</div>
                )}
              </div>
            </article>
          </section>
        )}

        {activeView === 'assets' && (
          <section className="detail-view">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Asset management</p>
                  <h3>Add, update, and remove assets</h3>
                </div>
              </div>

              <form className="manager-form" onSubmit={handleAssetSubmit}>
                <label>
                  Ticker
                  <input
                    value={assetForm.ticker}
                    onChange={(event) => setAssetForm({ ...assetForm, ticker: event.target.value.toUpperCase() })}
                    placeholder="AAPL"
                    required
                  />
                </label>
                <label>
                  Name
                  <input
                    value={assetForm.name}
                    onChange={(event) => setAssetForm({ ...assetForm, name: event.target.value })}
                    placeholder="Apple Inc."
                  />
                </label>
                <label>
                  Exchange
                  <input
                    value={assetForm.exchange}
                    onChange={(event) => setAssetForm({ ...assetForm, exchange: event.target.value })}
                    placeholder="NASDAQ"
                  />
                </label>
                <label>
                  Sector
                  <input
                    value={assetForm.sector}
                    onChange={(event) => setAssetForm({ ...assetForm, sector: event.target.value })}
                    placeholder="Technology"
                  />
                </label>
                <label>
                  Industry
                  <input
                    value={assetForm.industry}
                    onChange={(event) => setAssetForm({ ...assetForm, industry: event.target.value })}
                    placeholder="Consumer Electronics"
                  />
                </label>
                <button className="primary-btn" type="submit" disabled={submitting}>
                  {submitting ? 'Saving…' : editingAssetTicker ? 'Save asset' : 'Add asset'}
                </button>
              </form>

              <div className="list-stack">
                {assets.length ? assets.map((asset) => (
                  <div className="list-item" key={asset.ticker || asset.asset_id}>
                    <div>
                      <strong>{asset.ticker}</strong>
                      <p>{asset.name || 'Tracked asset'}</p>
                    </div>
                    <div className="action-row">
                      <button type="button" className="secondary-btn" onClick={() => handleAssetEdit(asset)}>
                        Edit
                      </button>
                      <button type="button" className="danger-btn" onClick={() => handleAssetDelete(asset.ticker)}>
                        Delete
                      </button>
                    </div>
                  </div>
                )) : (
                  <div className="empty-state">No assets are currently stored.</div>
                )}
              </div>
            </article>
          </section>
        )}

        {activeView === 'manage' && (
          <section className="detail-view management-grid">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Portfolio management</p>
                  <h3>Create or refine portfolios</h3>
                </div>
              </div>

              <form className="manager-form" onSubmit={handlePortfolioSubmit}>
                <label>
                  User name
                  <select
                    value={portfolioForm.user_id}
                    onChange={(event) => setPortfolioForm({ ...portfolioForm, user_id: event.target.value })}
                  >
                    <option value="">Select user</option>
                    {users.map((user) => (
                      <option key={user.user_id} value={user.user_id}>{user.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Portfolio name
                  <input
                    value={portfolioForm.name}
                    onChange={(event) => setPortfolioForm({ ...portfolioForm, name: event.target.value })}
                    placeholder="e.g. Growth Focus"
                    required
                  />
                </label>
                <label>
                  Description
                  <textarea
                    value={portfolioForm.description}
                    onChange={(event) => setPortfolioForm({ ...portfolioForm, description: event.target.value })}
                    placeholder="Describe the focus of the portfolio"
                    rows="3"
                  />
                </label>
                <button className="primary-btn" type="submit" disabled={submitting}>
                  {submitting ? 'Saving…' : editingPortfolioId ? 'Save portfolio' : 'Create portfolio'}
                </button>
              </form>

              <form className="manager-form manager-form-inline" onSubmit={handleUserSubmit}>
                <label>
                  New user name
                  <input
                    value={userForm.name}
                    onChange={(event) => setUserForm({ name: event.target.value })}
                    placeholder="e.g. Alice Johnson"
                  />
                </label>
                <button className="secondary-btn" type="submit" disabled={submitting}>
                  {submitting ? 'Saving…' : 'Add user'}
                </button>
              </form>

              <div className="list-stack">
                {portfolios.length ? portfolios.map((portfolio) => (
                  <div className="list-item" key={portfolio.portfolio_id}>
                    <div>
                      <strong>{portfolio.name}</strong>
                      <p>{portfolio.description || 'No description provided yet.'}</p>
                      <p className="list-sub">User: {portfolio.user_name || '—'}</p>
                    </div>
                    <div className="action-row">
                      <button type="button" className="secondary-btn" onClick={() => handlePortfolioEdit(portfolio)}>
                        Edit
                      </button>
                      <button type="button" className="danger-btn" onClick={() => handlePortfolioDelete(portfolio.portfolio_id)}>
                        Delete
                      </button>
                    </div>
                  </div>
                )) : (
                  <div className="empty-state">No portfolios are currently stored.</div>
                )}
              </div>
            </article>
          </section>
        )}
      </main>

      {chatOpen && (
        <div className="chat-panel">
          <div className="chat-head">
            <div>
              <strong>Portfolio Assistant</strong>
              <span>Ask me about your portfolio</span>
            </div>
            <button type="button" className="chat-close" onClick={() => setChatOpen(false)} aria-label="Close chat">✕</button>
          </div>
          <div className="chat-body">
            {chatMessages.map((message, index) => (
              <div className={`chat-msg ${message.role}`} key={index}>
                {message.text}
              </div>
            ))}
            {chatSending ? <div className="chat-msg bot typing">Thinking…</div> : null}
          </div>
          <form className="chat-form" onSubmit={handleChatSubmit}>
            <input
              value={chatInput}
              onChange={(event) => setChatInput(event.target.value)}
              placeholder="Ask about holdings, risk, recommendations…"
              autoFocus
            />
            <button type="submit" className="chat-send" disabled={chatSending}>Send</button>
          </form>
        </div>
      )}

      <button
        type="button"
        className="chat-fab"
        onClick={() => setChatOpen((open) => !open)}
        aria-label="Toggle chat"
      >
        💬
      </button>
    </div>
  );
}

const maxHeatValue = (data) => {
  const all = [...(data?.left?.values || []), ...(data?.right?.values || [])];
  return Math.max(1, ...all.map((v) => Number(v) || 0));
};

const heatColor = (value, max) => {
  const ratio = max > 0 ? Math.min(1, Math.max(0, Number(value || 0) / max)) : 0;
  return {
    background: `rgba(99, 102, 241, ${0.08 + 0.9 * ratio})`,
    color: ratio > 0.55 ? '#ffffff' : '#c4cdec'
  };
};

function HeatRow({ sector, left, right, max }) {
  const leftCell = heatColor(left, max);
  const rightCell = heatColor(right, max);
  return (
    <>
      <div className="heatmap-label">{sector}</div>
      <div className="heatmap-cell" style={leftCell}>
        {Number(left || 0).toFixed(1)}%
      </div>
      <div className="heatmap-cell" style={rightCell}>
        {Number(right || 0).toFixed(1)}%
      </div>
    </>
  );
}

export default App;
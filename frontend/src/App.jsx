import { useEffect, useState } from "react";
import axios from "axios";
import Dashboard from "./Dashboard";
import MapView from "./MapView";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8100";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("smartdine_token") || "");
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("smartdine_user");
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");

  const [cuisine, setCuisine] = useState("");
  const [budget, setBudget] = useState("");
  const [location, setLocation] = useState("");
  const [nearby, setNearby] = useState(false);
  const [vegOnly, setVegOnly] = useState(false);
  const [wifi, setWifi] = useState(false);
  const [parking, setParking] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [view, setView] = useState("search");
  const [showMap, setShowMap] = useState(false);

  const [selectedIds, setSelectedIds] = useState([]);
  const [compareData, setCompareData] = useState([]);
  const [showCompare, setShowCompare] = useState(false);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common.Authorization = `Bearer ${token}`;
      localStorage.setItem("smartdine_token", token);
    } else {
      delete axios.defaults.headers.common.Authorization;
      localStorage.removeItem("smartdine_token");
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem("smartdine_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("smartdine_user");
    }
  }, [user]);

  const handleAuthChange = (event) => {
    const { name, value } = event.target;
    setAuthForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleAuthSubmit = async (event) => {
    event.preventDefault();
    setAuthError("");
    setAuthLoading(true);

    try {
      const endpoint = authMode === "signup" ? "/auth/signup" : "/auth/login";
      const payload =
        authMode === "signup"
          ? { name: authForm.name, email: authForm.email, password: authForm.password }
          : { email: authForm.email, password: authForm.password };

      const res = await axios.post(`${API_URL}${endpoint}`, payload);
      setToken(res.data.token);
      setUser(res.data.user);
      setAuthForm({ name: "", email: "", password: "" });
    } catch (err) {
      setAuthError(err.response?.data?.detail || "Authentication failed. Please try again.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setToken("");
    setUser(null);
    setError("");
    setNote("");
  };

  const handleSearch = async () => {
    if (nearby && !location) {
      setError("Type a location to use the Nearby option");
      return;
    }
    setLoading(true);
    setError("");
    setNote("");
    setShowCompare(false);
    try {
      const res = await axios.post(`${API_URL}/recommend`, {
        cuisine: cuisine || null,
        budget: budget ? parseFloat(budget) : null,
        location: location || null,
        nearby: nearby || null,
        veg_only: vegOnly || null,
        wifi_available: wifi || null,
        parking_available: parking || null,
        limit: 10,
      });
      setResults(res.data.results);
      setSelectedIds([]);
      if (res.data.note) setNote(res.data.note);
    } catch (err) {
      setError("Something went wrong. Is the backend running?");
    }
    setLoading(false);
  };

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= 3) return prev;
      return [...prev, id];
    });
  };

  const handleCompare = async () => {
    if (selectedIds.length < 2) {
      setError("Select at least 2 restaurants to compare");
      return;
    }
    setError("");
    try {
      const res = await axios.get(`${API_URL}/compare`, {
        params: { ids: selectedIds.join(",") },
      });
      setCompareData(res.data.results);
      setShowCompare(true);
    } catch (err) {
      setError("Could not load comparison");
    }
  };

  if (!token || !user) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h1>SmartDine</h1>
          <p className="subtitle">Sign in to discover restaurants you’ll love</p>

          <div className="auth-toggle">
            <button
              type="button"
              className={authMode === "login" ? "active" : ""}
              onClick={() => setAuthMode("login")}
            >
              Login
            </button>
            <button
              type="button"
              className={authMode === "signup" ? "active" : ""}
              onClick={() => setAuthMode("signup")}
            >
              Sign Up
            </button>
          </div>

          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {authMode === "signup" && (
              <input
                type="text"
                name="name"
                placeholder="Full name"
                value={authForm.name}
                onChange={handleAuthChange}
                required
              />
            )}
            <input
              type="email"
              name="email"
              placeholder="Email address"
              value={authForm.email}
              onChange={handleAuthChange}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={authForm.password}
              onChange={handleAuthChange}
              minLength={6}
              required
            />
            {authError && <p className="error">{authError}</p>}
            <button type="submit" className="primary-button" disabled={authLoading}>
              {authLoading ? "Please wait..." : authMode === "login" ? "Login" : "Create account"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="topbar">
        <div>
          <h1>SmartDine Personalized Restaurant Discovery Platform</h1>
          <p className="subtitle">Welcome back, {user.name}</p>
        </div>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <section className="editorial-banner">
        <div className="editorial-copy">
          <span className="editorial-kicker">Your table is waiting</span>
          <h2>Find a place worth remembering.</h2>
          <p>Curated restaurant recommendations for every mood, meal, and moment.</p>
        </div>
        <div className="editorial-stats" aria-label="SmartDine highlights">
          <div>
            <strong>10k+</strong>
            <span>restaurants</span>
          </div>
          <div>
            <strong>4.5</strong>
            <span>average rating</span>
          </div>
        </div>
      </section>

      <div className="tabs">
        <button
          className={view === "search" ? "active" : ""}
          onClick={() => setView("search")}
        >
          Search
        </button>
        <button
          className={view === "dashboard" ? "active" : ""}
          onClick={() => setView("dashboard")}
        >
          Dashboard
        </button>
      </div>

      {view === "dashboard" && <Dashboard />}

      {view === "search" && (
        <>
          <div className="search-box">
            <input
              type="text"
              placeholder="Cuisine (e.g. North Indian)"
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
            />
            <input
              type="text"
              placeholder="Location (e.g. Koramangala)"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
            <input
              type="number"
              placeholder="Budget for two (₹)"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
            <button onClick={handleSearch} disabled={loading}>
              {loading ? "Searching..." : "Find Restaurants"}
            </button>
          </div>

          <div className="facility-filters">
            <label>
              <input type="checkbox" checked={nearby} onChange={(e) => setNearby(e.target.checked)} />
              <span className="facility-icon" aria-hidden="true">📍</span>
              <span>Nearby (5 km)</span>
            </label>
            <label>
              <input type="checkbox" checked={vegOnly} onChange={(e) => setVegOnly(e.target.checked)} />
              <span className="facility-icon" aria-hidden="true">🥗</span>
              <span>Veg Only</span>
            </label>
            <label>
              <input type="checkbox" checked={wifi} onChange={(e) => setWifi(e.target.checked)} />
              <span className="facility-icon" aria-hidden="true">📶</span>
              <span>Wi-Fi</span>
            </label>
            <label>
              <input type="checkbox" checked={parking} onChange={(e) => setParking(e.target.checked)} />
              <span className="facility-icon" aria-hidden="true">🅿️</span>
              <span>Parking</span>
            </label>
          </div>

          {note && <p className="note">ℹ️ {note}</p>}
          {error && <p className="error">{error}</p>}

          {results.length > 0 && (
            <div className="map-toggle">
              <button onClick={() => setShowMap(!showMap)}>
                {showMap ? "Hide Map" : "Show Map"}
              </button>
            </div>
          )}

          {showMap && results.length > 0 && (
            <div className="map-wrapper">
              <MapView restaurants={results} />
            </div>
          )}

          {results.length > 0 && (
            <div className="compare-bar">
              <span>{selectedIds.length} selected (pick 2-3 to compare)</span>
              <button onClick={handleCompare} disabled={selectedIds.length < 2}>
                Compare Selected
              </button>
            </div>
          )}

          {showCompare && (
            <div className="compare-table">
              <h2>Comparison</h2>
              <div className="compare-grid">
                {compareData.map((r) => (
                  <div key={r.id} className="compare-card">
                    <h3>{r.name}</h3>
                    <p><strong>Location:</strong> {r.location}</p>
                    <p><strong>Rating:</strong> ⭐ {r.rate}</p>
                    <p><strong>Cost for two:</strong> ₹{r.approx_cost}</p>
                    <p><strong>Cuisines:</strong> {r.cuisines}</p>
                    <p><strong>Type:</strong> {r.rest_type}</p>
                    <p><strong>Sentiment:</strong> {r.sentiment_score?.toFixed(2)}</p>
                    <p><strong>Online order:</strong> {r.online_order}</p>
                    <p><strong>Table booking:</strong> {r.book_table}</p>
                    <p>
                      <strong>Wi-Fi:</strong>{" "}
                      {r.has_wifi === null ? "Unknown" : r.has_wifi ? "Yes" : "No"}
                    </p>
                    <p>
                      <strong>Parking:</strong>{" "}
                      {r.has_parking === null ? "Unknown" : r.has_parking ? "Yes" : "No"}
                    </p>
                    <p>
                      <strong>Veg friendly:</strong>{" "}
                      {r.is_veg_friendly === null ? "Unknown" : r.is_veg_friendly ? "Yes" : "No"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="results">
            {results.map((r) => (
              <div
                key={r.id}
                className={`card ${selectedIds.includes(r.id) ? "selected" : ""}`}
              >
                <div className="card-header">
                  <h3>{r.name}</h3>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(r.id)}
                    onChange={() => toggleSelect(r.id)}
                  />
                </div>
                <p className="location">{r.location}</p>
                <p>
                  ⭐ {r.rate} &nbsp; | &nbsp; ₹{r.approx_cost} for two
                  {r.distance_km != null && <> &nbsp; | &nbsp; 📍 {r.distance_km} km</>}
                </p>
                <p className="cuisines">{r.cuisines}</p>
                <div className="badges">
                  {!!r.has_wifi && <span className="badge">📶 Wi-Fi</span>}
                  {!!r.has_parking && <span className="badge">🅿️ Parking</span>}
                  {!!r.is_veg_friendly && <span className="badge">🥗 Veg Friendly</span>}
                  {!!r.has_vegan_options && <span className="badge">🌱 Vegan</span>}
                  {!!r.wheelchair_accessible && <span className="badge">♿ Accessible</span>}
                  {!!r.serves_alcohol && <span className="badge">🍷 Alcohol</span>}
                  {!!r.live_music && <span className="badge">🎵 Live Music</span>}
                  {!!r.outdoor_seating && <span className="badge">🌳 Outdoor Seating</span>}
                  {!!r.is_halal && <span className="badge">☪️ Halal</span>}
                  {!!r.has_gluten_free && <span className="badge">🌾 Gluten Free</span>}
                </div>
                <p className="explanation">Why: {r.explanation}</p>
                <p className="summary">{r.review_summary}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
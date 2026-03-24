import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import apiClient from "@/api/client";

export function LoginPage() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSetup, setIsSetup] = useState(false);
  const [checking, setChecking] = useState(true);
  const [confirmPassword, setConfirmPassword] = useState("");

  const { login, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  // Jei jau prisijungęs, redirect
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Tikrinti ar reikia setup
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const { data } = await apiClient.get("/auth/status");
        setIsSetup(!data.has_admin);
      } catch {
        setIsSetup(false);
      } finally {
        setChecking(false);
      }
    };
    checkStatus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Setup validacija
    if (isSetup) {
      if (password.length < 6) {
        setError("Slaptažodis turi būti bent 6 simbolių");
        setLoading(false);
        return;
      }
      if (password !== confirmPassword) {
        setError("Slaptažodžiai nesutampa");
        setLoading(false);
        return;
      }
    }

    try {
      const endpoint = isSetup ? "/auth/setup" : "/auth/login";
      const { data } = await apiClient.post(endpoint, { username, password });
      login(data.access_token, data.username);
      navigate("/", { replace: true });
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        "Prisijungimo klaida. Bandykite dar kartą.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (checking) {
    return (
      <div className="login-page">
        <div className="login-loading">
          <div className="login-spinner" />
        </div>
        <style>{styles}</style>
      </div>
    );
  }

  return (
    <div className="login-page">
      {/* Background decoration */}
      <div className="login-bg-pattern" />
      <div className="login-bg-glow login-bg-glow-1" />
      <div className="login-bg-glow login-bg-glow-2" />

      <div className="login-container">
        {/* Logo + Header */}
        <div className="login-header">
          <div className="login-logo">
            <div className="login-logo-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path
                  d="M16 2L2 9L16 16L30 9L16 2Z"
                  fill="currentColor"
                  opacity="0.9"
                />
                <path
                  d="M2 23L16 30L30 23"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.5"
                />
                <path
                  d="M2 16L16 23L30 16"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity="0.7"
                />
              </svg>
            </div>
            <span className="login-logo-text">Matematika</span>
          </div>
          <h1 className="login-title">
            {isSetup ? "Sukurti administratorių" : "Sveiki sugrįžę"}
          </h1>
          <p className="login-subtitle">
            {isSetup
              ? "Pirmasis paleidimas — sukurkite admin paskyrą"
              : "Prisijunkite prie mokytojo asistento"}
          </p>
        </div>

        {/* Form */}
        <form className="login-form" onSubmit={handleSubmit}>
          {error && (
            <div className="login-error">
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                style={{ flexShrink: 0 }}
              >
                <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
                <path
                  d="M8 5V9M8 11V11.5"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="login-field">
            <label htmlFor="username">Vartotojo vardas</label>
            <div className="login-input-wrapper">
              <svg
                className="login-input-icon"
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
              >
                <circle cx="9" cy="5.5" r="3" stroke="currentColor" strokeWidth="1.5" />
                <path
                  d="M2.5 16C2.5 13.24 5.41 11 9 11C12.59 11 15.5 13.24 15.5 16"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="admin"
                autoComplete="username"
                required
              />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="password">Slaptažodis</label>
            <div className="login-input-wrapper">
              <svg
                className="login-input-icon"
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
              >
                <rect
                  x="3"
                  y="8"
                  width="12"
                  height="8"
                  rx="2"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
                <path
                  d="M6 8V5.5C6 3.84 7.34 2.5 9 2.5C10.66 2.5 12 3.84 12 5.5V8"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
                <circle cx="9" cy="12.5" r="1" fill="currentColor" />
              </svg>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={isSetup ? "Sukurkite slaptažodį (min. 6 simboliai)" : "Įveskite slaptažodį"}
                autoComplete={isSetup ? "new-password" : "current-password"}
                required
              />
            </div>
          </div>

          {isSetup && (
            <div className="login-field">
              <label htmlFor="confirmPassword">Pakartokite slaptažodį</label>
              <div className="login-input-wrapper">
                <svg
                  className="login-input-icon"
                  width="18"
                  height="18"
                  viewBox="0 0 18 18"
                  fill="none"
                >
                  <path
                    d="M13 6L7.5 12L5 9.5"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.5" />
                </svg>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Pakartokite slaptažodį"
                  autoComplete="new-password"
                  required
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? (
              <div className="login-button-loading">
                <div className="login-spinner-small" />
                <span>Jungiamasi...</span>
              </div>
            ) : isSetup ? (
              "Sukurti paskyrą"
            ) : (
              "Prisijungti"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          <p>Matematikos Mokytojo Asistentas v0.2.0</p>
        </div>
      </div>

      <style>{styles}</style>
    </div>
  );
}

const styles = `
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #0a1628 0%, #0d2137 25%, #0a1a2e 50%, #091520 100%);
    position: relative;
    overflow: hidden;
    padding: 1rem;
  }

  .login-bg-pattern {
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(circle at 25% 25%, rgba(16, 185, 129, 0.03) 0%, transparent 50%),
      radial-gradient(circle at 75% 75%, rgba(59, 130, 246, 0.03) 0%, transparent 50%);
  }

  .login-bg-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);
    pointer-events: none;
  }

  .login-bg-glow-1 {
    width: 600px;
    height: 600px;
    background: rgba(16, 185, 129, 0.08);
    top: -200px;
    right: -100px;
    animation: pulse-glow 8s ease-in-out infinite alternate;
  }

  .login-bg-glow-2 {
    width: 500px;
    height: 500px;
    background: rgba(6, 78, 59, 0.12);
    bottom: -150px;
    left: -100px;
    animation: pulse-glow 10s ease-in-out infinite alternate-reverse;
  }

  @keyframes pulse-glow {
    0% { opacity: 0.5; transform: scale(1); }
    100% { opacity: 1; transform: scale(1.15); }
  }

  .login-container {
    position: relative;
    z-index: 10;
    width: 100%;
    max-width: 420px;
    background: rgba(15, 25, 40, 0.85);
    backdrop-filter: blur(24px) saturate(1.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.03),
      0 24px 80px rgba(0, 0, 0, 0.5),
      0 8px 32px rgba(0, 0, 0, 0.3);
    animation: card-appear 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes card-appear {
    from {
      opacity: 0;
      transform: translateY(20px) scale(0.97);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .login-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .login-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.625rem;
    margin-bottom: 1.5rem;
  }

  .login-logo-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #064e3b, #10b981);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
  }

  .login-logo-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: -0.025em;
  }

  .login-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 0.5rem;
    letter-spacing: -0.025em;
  }

  .login-subtitle {
    font-size: 0.875rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.5;
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .login-error {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 10px;
    color: #fca5a5;
    font-size: 0.8125rem;
    line-height: 1.5;
    animation: shake 0.4s ease-in-out;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-4px); }
    40% { transform: translateX(4px); }
    60% { transform: translateX(-3px); }
    80% { transform: translateX(2px); }
  }

  .login-field {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
  }

  .login-field label {
    font-size: 0.8125rem;
    font-weight: 500;
    color: #cbd5e1;
    padding-left: 0.125rem;
  }

  .login-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .login-input-icon {
    position: absolute;
    left: 0.875rem;
    color: #64748b;
    pointer-events: none;
    transition: color 0.2s;
  }

  .login-input-wrapper:focus-within .login-input-icon {
    color: #10b981;
  }

  .login-field input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.75rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #f1f5f9;
    font-size: 0.9375rem;
    outline: none;
    transition: all 0.2s ease;
  }

  .login-field input::placeholder {
    color: #475569;
  }

  .login-field input:focus {
    border-color: rgba(16, 185, 129, 0.5);
    background: rgba(255, 255, 255, 0.06);
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
  }

  .login-button {
    margin-top: 0.5rem;
    padding: 0.875rem 1.5rem;
    background: linear-gradient(135deg, #064e3b, #10b981);
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
  }

  .login-button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.25);
  }

  .login-button:active:not(:disabled) {
    transform: translateY(0);
  }

  .login-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .login-button-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .login-spinner, .login-spinner-small {
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-top-color: #10b981;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .login-spinner {
    width: 32px;
    height: 32px;
  }

  .login-spinner-small {
    width: 18px;
    height: 18px;
    border-width: 2px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .login-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
  }

  .login-footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 1.25rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }

  .login-footer p {
    font-size: 0.75rem;
    color: #475569;
    margin: 0;
  }

  @media (max-width: 480px) {
    .login-container {
      padding: 2rem 1.5rem;
      border-radius: 16px;
    }

    .login-title {
      font-size: 1.25rem;
    }
  }
`;

import { useState } from "react";

function App() {
  const [market, setMarket] = useState("BIST");
  const [ticker, setTicker] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [accepted, setAccepted] = useState(false);

  const inputStyle = {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    fontSize: "14px",
    boxSizing: "border-box",
  };

  const analyze = async () => {
    if (!accepted) {
      setError("Please accept the disclaimer first");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("https://borsa-ai-production-fc3c.up.railway.app/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          market: market,
          ticker: ticker
        })
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (e) {
      setError("API connection error");
    }

    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 420, margin: "50px auto", fontFamily: "Arial" }}>
      <h2>📈 Stock AI Analyzer</h2>

      {/* MARKET */}
      <label>Market</label>
      <div style={{ marginBottom: 10 }}>
  <label style={{ marginRight: 15 }}>
    <input
      type="radio"
      value="BIST"
      checked={market === "BIST"}
      onChange={(e) => {
        setMarket(e.target.value);
        setTicker("");
        setResult(null);
        setError(null);
        setAccepted(false);
      }}
    />
    {" "}BIST
  </label>

  <label>
    <input
      type="radio"
      value="US"
      checked={market === "US"}
      onChange={(e) => {
        setMarket(e.target.value);
        setTicker("");
        setResult(null);
        setError(null);
        setAccepted(false);
      }}
    />
    {" "}NASDAQ / US
  </label>
</div>

      {/* INPUT */}
      <label>Stock Symbol</label>
      <input
        placeholder={market === "BIST" ? "THYAO" : "AAPL"}
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        style={inputStyle}
      />

      {/* DISCLAIMER BOX */}
      <div style={{
        border: "1px solid #ddd",
        padding: 10,
        marginBottom: 10,
        background: "#111"
      }}>
        <p style={{ fontSize: 12, marginBottom: 8 }}>
        ⚠️ This tool provides AI-generated analysis for informational purposes only and does NOT constitute financial advice.

        No guarantees are made regarding accuracy or outcomes. 
        The developer is not liable for any losses, damages, or claims by users or third parties, including those related to any company or security mentioned.

        Use at your own risk.
        </p>

        <label style={{ fontSize: 12 }}>
          <input
            type="checkbox"
            checked={accepted}
            onChange={() => setAccepted(!accepted)}
          />
          {" "}I understand and accept
        </label>
      </div>

      {/* BUTTON */}
      <button
        onClick={analyze}
        disabled={loading || !ticker || !accepted}
        style={{
          width: "100%",
          padding: 10,
          background: "#2563eb",
          color: "white",
          border: "none",
          cursor: "pointer"
        }}
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {/* ERROR */}
      {error && (
        <p style={{ color: "red", marginTop: 15 }}>
          ❌ {error}
        </p>
      )}

      {/* RESULT */}
      {result && (
  <div style={{ marginTop: 20, padding: 15, border: "1px solid #ddd" }}>
    <h3>{result.ticker}</h3>

    {/* SIGNAL TEXT */}
    <p>
      <b>AI Signal:</b>{" "}
      <span style={{ color: result.up > result.down ? "green" : "red" }}>
        {result.up > result.down ? "🔥 Positive bias" : "🔻 Negative bias"}
      </span>
    </p>

    {/* DOUBLE BAR */}
    <div style={{ marginTop: 15 }}>
      <div
        style={{
          display: "flex",
          height: 12,
          borderRadius: 6,
          overflow: "hidden"
        }}
      >
        {/* DOWN */}
        <div
          style={{
            width: `${result.down}%`,
            background: "#dc2626"
          }}
        />

        {/* UP */}
        <div
          style={{
            width: `${result.up}%`,
            background: "#16a34a"
          }}
        />
      </div>

      {/* LABELS */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        fontSize: 13,
        marginTop: 6
      }}>
        <span>🔻 {result.down}%</span>
        <span>{result.up}% 🔥</span>
      </div>
    </div>

    {/* INFO */}
    <p style={{ fontSize: 12, marginTop: 10, color: "#444" }}>
      This reflects the AI model’s probability distribution between negative and positive outcomes.
    </p>

    {/* DISCLAIMER */}
    <p style={{ fontSize: 11, color: "#666", marginTop: 15 }}>
      ⚠️ This tool provides AI-generated analysis for informational purposes only.
      It does not constitute financial advice or a recommendation to buy or sell any asset.
      Use at your own risk.
    </p>
  </div>
)}
    </div>
  );
}

export default App;
import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8001";

function InsightsIcon({ name, size = "small" }) {
  const symbols = {
    alert: "!",
    check: "✓",
    clock: "◷",
    compare: "⇄",
    file: "▣",
    layers: "▱",
    quote: "“",
    trend: "↗",
    user: "●",
  };

  return (
    <span
      className={`insights-icon insights-icon-${size}`}
      aria-hidden="true"
    >
      {symbols[name]}
    </span>
  );
}

function Insights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE_URL}/insights`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load insights");
        }

        return response.json();
      })
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch((requestError) => {
        console.error(requestError);
        setError("Could not load the cross-expert analysis.");
        setLoading(false);
      });
  }, []);

  const isSupported = data?.status === "supported";

  return (
    <div className="page-container insights-page">
      <div className="page-header">
        <div>
          <div className="breadcrumb">Research / Insights</div>
          <h1>Insights</h1>
          <p>
            Cross-expert analysis of themes, differences, and market outlook
            from the three interviews.
          </p>
        </div>

        <div
          className={`evidence-status ${
            !isSupported ? "insights-status-insufficient" : ""
          }`}
        >
          <InsightsIcon name={isSupported ? "check" : "alert"} />
          <span>
            {isSupported
              ? "Evidence grounded"
              : "Insufficient evidence"}
          </span>
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}

      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          Synthesizing evidence across the expert interviews...
        </div>
      ) : data ? (
        <>
          {isSupported ? (
            <>
              <InsightThemes themes={data.themes || []} />
              <InsightDifferences differences={data.differences || []} />
              <InsightOutlook outlook={data.outlook} />
              <InsightEvidence evidence={data.evidence || []} />
            </>
          ) : (
            <div className="insights-empty-state">
              <InsightsIcon name="alert" />
              <div>
                <strong>Evidence status</strong>
                <p>Insufficient evidence in the provided transcripts.</p>
              </div>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}

function InsightThemes({ themes }) {
  return (
    <section className="insights-section">
      <div className="insights-section-heading">
        <div>
          <h2>Common themes</h2>
          <p>Themes supported across multiple expert interviews.</p>
        </div>
        <InsightsIcon name="layers" size="large" />
      </div>

      <div className="insights-theme-grid">
        {themes.map((theme, index) => (
          <article className="insights-theme-card" key={`${theme.title}-${index}`}>
            <div className="insights-index">{String(index + 1).padStart(2, "0")}</div>
            <h3>{theme.title}</h3>
            <p>{theme.summary}</p>
            <div className="insights-expert-tags">
              {(theme.experts || []).map((country) => (
                <span key={country}>
                  {getCountryFlag(country)} {country}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function InsightDifferences({ differences }) {
  return (
    <section className="insights-section">
      <div className="insights-section-heading">
        <div>
          <h2>Differences in emphasis</h2>
          <p>How the interviewed experts frame the market differently.</p>
        </div>
        <InsightsIcon name="compare" size="large" />
      </div>

      <div className="insights-difference-grid">
        {differences.map((item, index) => (
          <article
            className="insights-difference-card"
            key={`${item.expert}-${item.country}-${index}`}
          >
            <div className="insights-country-label">
              {getCountryFlag(item.country)} {item.country}
            </div>
            <h3>{item.expert}</h3>
            <p>{item.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function InsightOutlook({ outlook }) {
  const summary = typeof outlook === "string"
    ? outlook
    : outlook?.summary;
  const points = typeof outlook === "object"
    ? outlook?.points || []
    : [];

  return (
    <section className="insights-section">
      <div className="insights-section-heading">
        <div>
          <h2>Market outlook</h2>
          <p>Cross-expert synthesis of the forward-looking evidence.</p>
        </div>
        <InsightsIcon name="trend" size="large" />
      </div>

      <div className="insights-outlook-card">
        <div className="insights-outlook-icon">
          <InsightsIcon name="trend" size="large" />
        </div>
          <div className="insights-outlook-content">
            <p>{summary || "Insufficient evidence in the provided transcripts."}</p>

            {points.length > 0 && (
              <div className="insights-outlook-points">
                {points.map((item, index) => (
                  <div
                    className="insights-outlook-point"
                    key={`${item.expert}-${item.country}-${index}`}
                  >
                    <strong>
                      {getCountryFlag(item.country)} {item.country} - {item.expert}
                    </strong>
                    <span>{item.summary}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
      </div>
    </section>
  );
}

function InsightEvidence({ evidence }) {
  return (
    <section className="insights-section">
      <div className="insights-section-heading">
        <div>
          <h2>Evidence trace</h2>
          <p>Exact transcript passages supporting the generated analysis.</p>
        </div>
        <span className="source-count">{evidence.length} passages</span>
      </div>

      <div className="insights-evidence-grid">
        {evidence.map((item, index) => (
          <article
            className="insights-evidence-card"
            key={`${item.source}-${item.timestamp}-${index}`}
          >
            <div className="insights-evidence-header">
              <div className="expert-identity">
                <div className="small-avatar">{getInitials(item.expert)}</div>
                <div>
                  <strong>{item.expert}</strong>
                  <div className="expert-meta">
                    {getCountryFlag(item.country)} {item.country}
                  </div>
                </div>
              </div>
            </div>

            <div className="insights-quote">
              <div className="quote-icon">
                <InsightsIcon name="quote" />
              </div>
              <p>"{item.text}"</p>
            </div>

            <div className="evidence-meta">
              <span>
                <InsightsIcon name="clock" />
                {item.timestamp}
              </span>
              <span>
                <InsightsIcon name="file" />
                {item.source}
              </span>
              <span>
                <InsightsIcon name="user" />
                {item.speaker}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function getInitials(name) {
  if (!name) {
    return "?";
  }

  return name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2);
}

function getCountryFlag(country) {
  if (!country) {
    return "🌍";
  }

  if (country.includes("France")) {
    return "🇫🇷";
  }

  if (country.includes("Germany")) {
    return "🇩🇪";
  }

  if (country.includes("UK") || country.includes("United Kingdom")) {
    return "🇬🇧";
  }

  return "🌍";
}

export default Insights;

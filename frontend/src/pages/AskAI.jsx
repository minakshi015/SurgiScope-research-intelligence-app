import { useState } from "react";


const API_BASE_URL = "http://127.0.0.1:8001";

function AskAIIcon({ name, className = "" }) {
  return (
    <span
      className={`ask-ai-icon ask-ai-icon-${name} ${className}`}
      aria-hidden="true"
    />
  );
}


function AskAI() {

  const [query, setQuery] = useState("");

  const [answer, setAnswer] = useState("");

  const [perspective, setPerspective] = useState([]);

  const [evidence, setEvidence] = useState([]);

  const [evidenceStatus, setEvidenceStatus] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [hasAsked, setHasAsked] = useState(false);


  const askQuestion = async () => {

    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setPerspective([]);
    setEvidence([]);
    setEvidenceStatus("");
    setHasAsked(true);

    try {

      const response = await fetch(
        `${API_BASE_URL}/ask?query=${encodeURIComponent(
          trimmedQuery
        )}&n_results=6`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to get an answer from the research backend."
        );
      }

      const data = await response.json();

      setAnswer(data.answer || "");

      setPerspective(
        Array.isArray(data.perspective)
          ? data.perspective
          : []
      );

      setEvidence(data.evidence || []);

      setEvidenceStatus(
        data.evidence_status ||
        (data.evidence?.length
          ? "Supported"
          : "Insufficient evidence")
      );

    } catch (err) {

      console.error(err);

      setError(
        "Could not generate the answer. Make sure the backend is running."
      );

    } finally {

      setLoading(false);

    }
  };

  const displayedEvidence = getStrongestEvidencePerExpert(evidence);


  const handleKeyDown = (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      askQuestion();

    }
  };


  return (

    <div className="page-container ask-ai-page">

      <div className="page-header">

        <div>

          <div className="breadcrumb">
            Research / Ask AI
          </div>

          <h1>
            Ask AI
          </h1>

          <p>
            Ask questions across the expert interviews.
            Answers are generated only from retrieved transcript evidence.
          </p>

        </div>


        <div
          className={`evidence-status ${
            evidenceStatus === "Insufficient evidence"
              ? "evidence-status-insufficient"
              : ""
          }`}
        >

          {evidenceStatus === "Insufficient evidence" ? (
            <AskAIIcon name="alert" />
          ) : (
            <AskAIIcon name="shield" />
          )}

          <span>
            {evidenceStatus || "Evidence grounded"}
          </span>

        </div>

      </div>


      {/* ------------------------------------------------
          QUESTION INPUT
      ------------------------------------------------ */}

      <section className="ask-panel">

        <div className="ask-label">
          RESEARCH QUESTION
        </div>


        <div className="ask-input-wrapper">

          <AskAIIcon name="search" className="ask-input-icon" />


          <textarea
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the expert interviews..."
            rows={3}
          />


          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={
              loading ||
              !query.trim()
            }
          >

            {loading
              ? "Analyzing..."
              : "Ask AI"}

          </button>

        </div>


        <div className="ask-hint">

          Example:

          {" "}

          <button
            onClick={() => {
              setQuery(
                "What are the main barriers to robotic surgery adoption?"
              );
            }}
          >
            What are the main barriers to robotic surgery adoption?
          </button>

        </div>

      </section>


      {/* ------------------------------------------------
          ERROR
      ------------------------------------------------ */}

      {error && (

        <div className="error-box">

          <AskAIIcon name="alert" />

          {error}

        </div>

      )}


      {/* ------------------------------------------------
          LOADING
      ------------------------------------------------ */}

      {loading && (

        <div className="loading-state">

          <div className="loading-spinner"></div>

          Retrieving relevant evidence and generating a
          grounded answer...

        </div>

      )}


      {/* ------------------------------------------------
          ANSWER
      ------------------------------------------------ */}

      {!loading &&
        hasAsked &&
        answer && (

          <section className="answer-section">

            <div className="section-heading">

              <div>

                <h2>
                  Answer
                </h2>

                <p>
                  {displayedEvidence.length > 0
                    ? "Generated from retrieved transcript evidence."
                      : "No transcript evidence met the relevance threshold."}
                </p>

              </div>

              {displayedEvidence.length > 0 && (
                <span className="evidence-trace">
                  <AskAIIcon name="shield" />
                  {displayedEvidence.length} expert sources used
                </span>
              )}

            </div>


            <div className="answer-card">

              <div className="answer-icon">

                <AskAIIcon name="shield" />

              </div>


              <div className="answer-content">

                <p>
                  {answer}
                </p>

              </div>

            </div>

          </section>

        )}


      {/* ------------------------------------------------
          EXPERT PERSPECTIVES
      ------------------------------------------------ */}

      {!loading &&
        hasAsked &&
        perspective.length > 0 && (

          <section className="answer-section">

            <div className="section-heading">

              <div>

                <h2>
                  Expert perspectives
                </h2>

                <p>
                  How the retrieved expert views compare.
                </p>

              </div>

              <AskAIIcon name="users" />

            </div>


            <div className="perspective-grid">

              {perspective.map((item, index) => (

                <article
                  className="perspective-card"
                  key={`${item.expert}-${item.country}-${index}`}
                >

                  <div className="perspective-identity">

                    <span className="perspective-country">
                      {getCountryFlag(item.country)} {item.country}
                    </span>

                    <strong>
                      {item.expert}
                    </strong>

                  </div>

                  <p>
                    {item.summary}
                  </p>

                </article>

              ))}

            </div>

          </section>

        )}


      {/* ------------------------------------------------
          EVIDENCE
      ------------------------------------------------ */}

      {!loading &&
        hasAsked &&
        evidence.length > 0 && (

          <section className="answer-section">

            <div className="section-heading">

              <div>

                <h2>
                  Supporting evidence
                </h2>

                <p>
                  Retrieved transcript passages used by the
                  RAG pipeline.
                </p>

              </div>


              <span className="source-count">

                {displayedEvidence.length} sources

              </span>

            </div>


            <div className="ask-evidence-grid">

              {displayedEvidence.map(
                (item, index) => (

                  <div
                    className="ask-evidence-card"
                    key={`${item.source}-${item.timestamp}-${index}`}
                  >

                    <div className="ask-evidence-header">

                      <div className="expert-identity">

                        <div className="small-avatar">

                          {getInitials(
                            item.expert
                          )}

                        </div>

                        <div>

                          <strong>
                            {item.expert}
                          </strong>

                          <div className="expert-meta">

                            {getCountryFlag(
                              item.country
                            )}

                            {" "}

                            {item.country}

                          </div>

                        </div>

                      </div>

                    </div>


                    <div className="ask-quote">

                      <div className="quote-icon">

                        <AskAIIcon name="quote" />

                      </div>


                      <p>
                        "{item.text}"
                      </p>

                    </div>


                    <div className="evidence-meta">

                      <span>

                        <AskAIIcon name="clock" />

                        {item.timestamp}

                      </span>


                      <span>

                        <AskAIIcon name="file" />

                        {item.source}

                      </span>


                      <span>

                        <AskAIIcon name="user" />

                        {item.speaker}

                      </span>

                    </div>

                  </div>

                )
              )}

            </div>

          </section>

        )}


      {/* ------------------------------------------------
          NO EVIDENCE
      ------------------------------------------------ */}

      {!loading &&
        hasAsked &&
        evidenceStatus === "Insufficient evidence" &&
        evidence.length === 0 &&
        !error && (

          <div className="insufficient-evidence">

            <AskAIIcon name="alert" />

            <div>
              <strong>Evidence status</strong>
              <p>Insufficient evidence in the provided transcripts.</p>
            </div>

          </div>

        )}


      {!loading &&
        hasAsked &&
        (evidenceStatus === "Supported" ||
          evidenceStatus === "Limited evidence") && (

          <div className="grounded-status">

            <AskAIIcon name="shield" />

            <strong>Evidence status</strong>

            <span>{evidenceStatus}</span>

          </div>

        )}

    </div>

  );

}


/* ------------------------------------------------
   Helpers
------------------------------------------------ */

function getInitials(name) {

  if (!name) {
    return "?";
  }

  return name
    .split(" ")
    .map(
      (word) => word[0]
    )
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

  if (
    country.includes("UK") ||
    country.includes("United Kingdom")
  ) {
    return "🇬🇧";
  }

  return "🌍";

}


function getStrongestEvidencePerExpert(items) {

  const strongestByExpert = new Map();

  items.forEach((item) => {

    const expertKey = item.expert || item.country || item.source;
    const current = strongestByExpert.get(expertKey);

    if (!current || item.distance < current.distance) {
      strongestByExpert.set(expertKey, item);
    }

  });

  return Array.from(strongestByExpert.values());

}


export default AskAI;
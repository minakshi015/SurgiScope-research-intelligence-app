import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8001";

function InterviewGuideIcon({ name, className = "" }) {
  return (
    <span
      className={`interview-guide-icon interview-guide-icon-${name} ${className}`}
      aria-hidden="true"
    />
  );
}

function InterviewGuide() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [openQuestion, setOpenQuestion] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loadingQuestion, setLoadingQuestion] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/interview-guide`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Failed to load interview guide"
          );
        }

        return response.json();
      })
      .then((data) => {
        setQuestions(data.results || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);

        setError(
          "Could not load the interview evidence."
        );

        setLoading(false);
      });
  }, []);

  const toggleQuestion = async (id) => {
    if (openQuestion === id) {
      setOpenQuestion(null);
      return;
    }

    setOpenQuestion(id);

    if (answers[id]) {
      return;
    }

    const selectedQuestion = questions.find(
      (item) => item.question_id === id
    );

    if (!selectedQuestion) {
      return;
    }

    setLoadingQuestion(id);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/interview-guide/${id}`
      );

      if (!response.ok) {
        throw new Error("Failed to load question evidence");
      }

      const data = await response.json();

      setAnswers((currentAnswers) => ({
        ...currentAnswers,
        [id]: data,
      }));
    } catch (err) {
      console.error(err);
      setError("Could not load the answer for this question.");
    } finally {
      setLoadingQuestion(null);
    }
  };

  return (
    <div className="page-container interview-guide-page">

      {/* Header */}

      <div className="page-header">

        <div>

          <div className="breadcrumb">
            Research / Interview Guide
          </div>

          <h1>
            Interview Guide
          </h1>

          <p>
            Evidence retrieved from the three expert
            interviews for each research question.
          </p>

        </div>


        <div className="evidence-status">

          <InterviewGuideIcon name="shield" />

          <span>
            Evidence grounded
          </span>

        </div>

      </div>


      {/* Error */}

      {error && (

        <div className="error-box">
          {error}
        </div>

      )}


      {/* Loading */}

      {loading ? (

        <div className="loading-state">

          <div className="loading-spinner"></div>

          Loading interview evidence...

        </div>

      ) : (

        /* Questions */

        <div className="questions-list">

          {questions.map((item) => {

            const isOpen =
              openQuestion ===
              item.question_id;
            const result = answers[item.question_id];

            return (

              <section
                className="question-card"
                key={item.question_id}
              >

                {/* Question header */}

                <button
                  className="question-header"
                  onClick={() =>
                    toggleQuestion(
                      item.question_id
                    )
                  }
                >

                  <div className="question-number">
                    Q{item.question_id}
                  </div>

                  <div className="question-title">
                    {item.question}
                  </div>

                  <InterviewGuideIcon
                    name="chevron"
                    className={isOpen ? "chevron-open" : ""}
                  />

                </button>


                {/* Evidence */}

                {isOpen && (

                  <div className="question-content">

                    <div className="question-evidence-intro">

                      <div>

                        <strong>
                          Evidence from expert interviews
                        </strong>

                        <p>
                          Retrieved directly from the
                          indexed transcripts. Timestamps
                          and source metadata come from
                          the transcript records.
                        </p>

                      </div>

                      <span className="source-count">

                        {result?.evidence?.length || 0}
                        {" "}
                        sources

                      </span>

                    </div>


                    {loadingQuestion === item.question_id ? (
                      <div className="loading-state">
                        <div className="loading-spinner"></div>
                        Retrieving evidence and generating an answer...
                      </div>
                    ) : result ? (
                      <>
                        <div className="guide-answer-heading">
                          <div>
                            <h2>Answer</h2>
                            <p>
                              Concise synthesis from the selected expert evidence.
                            </p>
                          </div>
                          <span className="evidence-supported">
                            <InterviewGuideIcon name="shield" />
                            {result.evidence_status || "Supported"}
                          </span>
                        </div>

                        <div className="answer-card guide-answer-card">
                          <div className="answer-content">
                            <p>{result.answer}</p>
                          </div>
                        </div>

                        {result.evidence?.map((evidence, index) => (
                          <ExpertEvidence
                            key={`${item.question_id}-${evidence.source}-${evidence.timestamp}-${index}`}
                            expert={{
                              expert: evidence.expert,
                              country: evidence.country,
                              evidence: [evidence],
                            }}
                          />
                        ))}

                        {result.evidence?.length === 0 && (
                          <div className="no-evidence">
                            Insufficient evidence in the provided transcripts.
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="no-evidence">
                        Open this question to retrieve a grounded answer.
                      </div>
                    )}

                  </div>

                )}

              </section>

            );
          })}

        </div>

      )}

    </div>
  );
}


/* ============================================================
   EXPERT EVIDENCE
============================================================ */

function ExpertEvidence({ expert }) {

  const evidence =
    expert.evidence || [];

  const topEvidence =
    evidence.slice(0, 2);

  return (

    <div className="expert-evidence">

      {/* Expert header */}

      <div className="evidence-expert-header">

        <div className="expert-identity">

          <div className="small-avatar">

            {getInitials(
              expert.expert
            )}

          </div>


          <div>

            <strong>
              {expert.expert}
            </strong>

            <div className="expert-meta">

              <span>
                {getCountryFlag(
                  expert.country
                )}

                {" "}

                {expert.country}
              </span>

            </div>

          </div>

        </div>


        <div className="evidence-supported">

          <InterviewGuideIcon name="shield" />

          Evidence retrieved

        </div>

      </div>


      {/* Evidence */}

      <div className="evidence-list">

        {topEvidence.map(
          (item, index) => (

            <div
              className="evidence-item"
              key={`${item.source}-${item.timestamp}-${index}`}
            >

              <div className="quote-icon">

                <InterviewGuideIcon name="quote" />

              </div>


              <div className="evidence-body">

                <p className="quote-text">

                  "{item.text}"

                </p>


                <div className="evidence-meta">

                  <span>

                    <InterviewGuideIcon name="clock" />

                    {item.timestamp}

                  </span>


                  <span>

                    <InterviewGuideIcon name="file" />

                    {item.source}

                  </span>


                  <span>

                    <InterviewGuideIcon name="user" />

                    {item.speaker}

                  </span>

                </div>

              </div>

            </div>

          )
        )}

      </div>


      {/* Empty state */}

      {evidence.length === 0 && (

        <div className="no-evidence">

          No matching evidence was retrieved
          for this expert and question.

        </div>

      )}

    </div>

  );
}


/* ============================================================
   HELPERS
============================================================ */

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


export default InterviewGuide;
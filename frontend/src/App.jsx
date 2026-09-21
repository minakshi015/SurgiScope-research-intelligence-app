import { useEffect, useState } from "react";

import InterviewGuide from "./pages/InterviewGuide";
import AskAI from "./pages/AskAI";
import Insights from "./pages/Insights";

import {
  LayoutDashboard,
  ClipboardList,
  Lightbulb,
  MessageSquare,
  Search,
  ChevronRight,
} from "lucide-react";


const API_BASE_URL = "http://127.0.0.1:8001";


function App() {

  const [activePage, setActivePage] = useState("overview");

  const [transcripts, setTranscripts] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");


  useEffect(() => {

    fetch(`${API_BASE_URL}/transcripts`)

      .then((response) => {

        if (!response.ok) {
          throw new Error("Failed to load transcripts");
        }

        return response.json();

      })

      .then((data) => {

        setTranscripts(data.transcripts || []);

        setLoading(false);

      })

      .catch((err) => {

        console.error("Backend connection error:", err);

        setError(
          "Could not connect to the research backend."
        );

        setLoading(false);

      });

  }, []);


  return (

    <div className="app-shell">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            H
          </div>

          <div>

            <div className="brand-name">
              SurgiScope
            </div>

            

          </div>

        </div>


        <nav className="navigation">

          <div className="nav-label">
            WORKSPACE
          </div>


          {/* OVERVIEW */}

          <button
            type="button"
            className={`nav-item ${
              activePage === "overview"
                ? "active"
                : ""
            }`}
            onClick={() => {
              console.log("Overview clicked");
              setActivePage("overview");
            }}
          >

            <LayoutDashboard size={18} />

            <span>
              Overview
            </span>

          </button>


          {/* INTERVIEW GUIDE */}

          <button
            type="button"
            className={`nav-item ${
              activePage === "interview"
                ? "active"
                : ""
            }`}
            onClick={() => {
              console.log("Interview Guide clicked");
              setActivePage("interview");
            }}
          >

            <ClipboardList size={18} />

            <span>
              Interview Guide
            </span>

          </button>


          {/* INSIGHTS */}

          <button
            type="button"
            className={`nav-item ${
              activePage === "insights"
                ? "active"
                : ""
            }`}
            onClick={() => {
              setActivePage("insights");
            }}
          >

            <Lightbulb size={18} />

            <span>
              Insights
            </span>

          </button>


          {/* ASK AI */}

          <button
            type="button"
            className={`nav-item ${
              activePage === "ask"
                ? "active"
                : ""
            }`}
            onClick={() => {
              console.log("ASK AI CLICKED");
              setActivePage("ask");
            }}
          >

            <MessageSquare size={18} />

            <span>
              Ask AI
            </span>

          </button>


        </nav>


        {/* SIDEBAR STATUS */}

        <div className="sidebar-footer">

          <div
            className={`status-dot ${
              error
                ? "status-error"
                : ""
            }`}
          />

          <span>

            {loading
              ? "Loading transcripts..."
              : error
              ? "Backend unavailable"
              : `${transcripts.length} transcripts indexed`}

          </span>

        </div>

      </aside>


      {/* ================= MAIN CONTENT ================= */}

      <main className="main-content">


        {/* ASK AI PAGE */}

        {activePage === "ask" && (

          <AskAI />

        )}


        {/* INTERVIEW GUIDE PAGE */}

        {activePage === "interview" && (

          <InterviewGuide />

        )}


        {/* INSIGHTS PAGE */}

        {activePage === "insights" && (

          <Insights />

        )}


        {/* OVERVIEW PAGE */}

        {activePage === "overview" && (

          <Overview
            transcripts={transcripts}
            loading={loading}
            error={error}
            setActivePage={setActivePage}
          />

        )}

      </main>

    </div>

  );

}


/* =========================================================
   OVERVIEW
========================================================= */

function Overview({
  transcripts,
  loading,
  error,
  setActivePage,
}) {

  return (

    <>

      <header className="topbar">

        <div>

          <div className="breadcrumb">
            Research / Market Intelligence
          </div>

          <h1>
            European Robotic Surgery Market
          </h1>

          <p>
            AI-powered analysis of expert interviews
            across France, Germany and the United Kingdom.
          </p>

        </div>


        <div className="topbar-actions">

          <div className="search-box">

            <Search size={17} />

            <span>
              Search evidence...
            </span>

            <kbd>
              ⌘ K
            </kbd>

          </div>

        </div>

      </header>


      {error && (

        <div className="error-box">
          {error}
        </div>

      )}


      {/* METRICS */}

      <section className="metrics-grid">

        <div className="metric-card">

          <div className="metric-label">
            EXPERT INTERVIEWS
          </div>

          <div className="metric-value">

            {loading
              ? "—"
              : transcripts.length}

          </div>

          <div className="metric-description">
            Primary expert sources
          </div>

        </div>


        <div className="metric-card">

          <div className="metric-label">
            MARKETS COVERED
          </div>

          <div className="metric-value">

            {loading
              ? "—"
              : new Set(
                  transcripts.map(
                    (item) => item.country
                  )
                ).size}

          </div>

          <div className="metric-description">
            France · Germany · UK
          </div>

        </div>


        <div className="metric-card">

          <div className="metric-label">
            INTERVIEW QUESTIONS
          </div>

          <div className="metric-value">
            6
          </div>

          <div className="metric-description">
            Structured research guide
          </div>

        </div>


        <div className="metric-card">

          <div className="metric-label">
            EVIDENCE MODE
          </div>

          <div className="metric-value evidence-value">

            <span className="live-dot"></span>

            Grounded

          </div>

          <div className="metric-description">
            Source-linked responses
          </div>

        </div>

      </section>


      {/* EXPERT PERSPECTIVES */}

      <section className="section">

        <div className="section-heading">

          <div>

            <h2>
              Expert perspectives
            </h2>

            <p>
              Interview participants contributing
              to the market analysis.
            </p>

          </div>


          <button
            type="button"
            className="view-button"
            onClick={() =>
              setActivePage("interview")
            }
          >

            View evidence

            <ChevronRight size={16} />

          </button>

        </div>


        {loading ? (

          <div className="experts-grid">

            {[1, 2, 3].map((item) => (

              <div
                className="expert-card"
                key={item}
              >
                Loading expert...
              </div>

            ))}

          </div>

        ) : transcripts.length === 0 ? (

          <div className="loading-state">
            No transcripts found.
          </div>

        ) : (

          <div className="experts-grid">

            {transcripts.map((expert) => (

              <div
                className="expert-card"
                key={expert.source}
              >

                <div className="expert-top">

                  <div className="avatar">

                    {expert.expert
                      ?.split(" ")
                      .map(
                        (word) => word[0]
                      )
                      .join("")
                      .slice(0, 2)}

                  </div>


                  <div className="country-badge">

                    {getCountryFlag(
                      expert.country
                    )}

                    {" "}

                    {expert.country}

                  </div>

                </div>


                <h3>
                  {expert.expert}
                </h3>


                <p className="expert-role">
                  {expert.role}
                </p>


                <div className="expert-focus">

                  <span>
                    Source
                  </span>

                  <strong>
                    {expert.source}
                  </strong>

                </div>


                <button
                  type="button"
                  className="evidence-link"
                  onClick={() =>
                    setActivePage("interview")
                  }
                >

                  Explore evidence

                  <ChevronRight size={15} />

                </button>

              </div>

            ))}

          </div>

        )}

      </section>


      {/* THEMES */}

      <section className="section">

        <div className="section-heading">

          <div>

            <h2>
              Research themes
            </h2>

            <p>
              Topics appearing across the provided
              expert interviews.
            </p>

          </div>

        </div>


        <div className="themes-grid">

          <div className="theme-card">

            <div className="theme-number">
              01
            </div>

            <h3>
              Capital & economics
            </h3>

            <p>
              Hospital budgets, ROI, utilisation
              and total cost are recurring
              considerations.
            </p>

            <span>
              3 / 3 experts
            </span>

          </div>


          <div className="theme-card">

            <div className="theme-number">
              02
            </div>

            <h3>
              Surgeon training
            </h3>

            <p>
              Training capacity and the number
              of trained surgeons affect utilisation
              and adoption.
            </p>

            <span>
              3 / 3 experts
            </span>

          </div>


          <div className="theme-card">

            <div className="theme-number">
              03
            </div>

            <h3>
              Uneven adoption
            </h3>

            <p>
              Larger or university hospitals are
              described as further ahead than
              smaller hospitals.
            </p>

            <span>
              3 / 3 experts
            </span>

          </div>

        </div>

      </section>

    </>

  );

}


/* =========================================================
   COUNTRY FLAG
========================================================= */

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


export default App;
import { useState, useCallback } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://social-media-content-analyzer-api-7onz.onrender.com';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/webp',
];

function App() {
  const [file, setFile] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // LLM states
  const [improving, setImproving] = useState(false);
  const [improvedCaption, setImprovedCaption] = useState(null);
  const [llmError, setLlmError] = useState(null);

  // Methodology
  const [showMethodology, setShowMethodology] = useState(false);

  // -----------------------------------------
  // File handling + validation + analysis
  // -----------------------------------------

  const handleFile = useCallback(async (selectedFile) => {
    if (!selectedFile) return;

    // Reset previous state
    setError(null);
    setResult(null);
    setImprovedCaption(null);
    setLlmError(null);
    setShowMethodology(false);

    // File type validation
    if (!ALLOWED_FILE_TYPES.includes(selectedFile.type)) {
      setFile(null);
      setError(
        'Unsupported file type. Please upload a PDF, PNG, JPG, JPEG, or WEBP image.'
      );
      return;
    }

    // File size validation
    if (selectedFile.size > MAX_FILE_SIZE) {
      setFile(null);
      setError(
        'File is too large. Please upload a file smaller than 10 MB.'
      );
      return;
    }

    setFile(selectedFile);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await axios.post(
        `${API_URL}/analyze`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(res.data);

    } catch (err) {
      const message =
        err.response?.data?.detail ||
        'Something went wrong while analyzing the file. Please try again.';

      setError(message);

    } finally {
      setLoading(false);
    }
  }, []);

  // -----------------------------------------
  // Reset / Analyze another
  // -----------------------------------------

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setImproving(false);
    setImprovedCaption(null);
    setLlmError(null);
    setShowMethodology(false);
    setIsDragActive(false);
  };

  // -----------------------------------------
  // Drag & Drop
  // -----------------------------------------

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);

    const droppedFile = e.dataTransfer.files[0];

    if (droppedFile) {
      handleFile(droppedFile);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const onDragLeave = () => {
    setIsDragActive(false);
  };

  const onFileSelect = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      handleFile(selectedFile);
    }

    // Allows selecting the same file again
    e.target.value = '';
  };

  // -----------------------------------------
  // LLM Caption Improvement
  // -----------------------------------------

  const handleImproveCaption = async () => {
    if (!result?.extracted_text) return;

    setImproving(true);
    setImprovedCaption(null);
    setLlmError(null);

    try {
      const res = await axios.post(
        `${API_URL}/improve-caption`,
        {
          text: result.extracted_text,
        }
      );

      setImprovedCaption(res.data.improved_caption);

    } catch (err) {
      const message =
        err.response?.data?.detail ||
        'Unable to improve the caption. Please try again.';

      setLlmError(message);

    } finally {
      setImproving(false);
    }
  };

  // -----------------------------------------
  // UI
  // -----------------------------------------

  return (
    <div className="container">

      {/* =====================================
          COMPANY BRANDING
      ====================================== */}

      <div className="company-brand">

        <div className="company-name">
          UNTHINKABLE SOLUTIONS
        </div>

        <div className="company-location">
          GURUGRAM · SOFTWARE ENGINEERING ASSESSMENT
        </div>

      </div>


      {/* =====================================
          PAGE HEADER
      ====================================== */}

      <div className="eyebrow">
        Document Intelligence
      </div>

      <h1 className="title">
        Social Media Content Analyzer
      </h1>

      <p className="subtitle">
        Upload a PDF or scanned image. Text is extracted and analyzed
        for engagement improvements.
      </p>


      {/* =====================================
          UPLOAD AREA
      ====================================== */}

      <label
        className={`dropzone ${isDragActive ? 'active' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >

        <div className="scan-line"></div>

        <input
          type="file"
          accept=".pdf,image/png,image/jpeg,image/jpg,image/webp"
          onChange={onFileSelect}
        />

        <div className="dropzone-icon">
          [ + ]
        </div>

        <p className="primary">
          <strong>Drag & drop</strong> a file, or click to browse
        </p>

        <p className="secondary">
          PDF · PNG · JPG · WEBP · MAX 10 MB
        </p>

      </label>


      {/* =====================================
          SELECTED FILE
      ====================================== */}

      {file && !loading && (
        <div className="file-info">

          <span>
            {file.name}
          </span>

          <span>
            {(file.size / 1024).toFixed(1)} KB
          </span>

        </div>
      )}


      {/* =====================================
          EXTRACTION LOADING
      ====================================== */}

      {loading && (
        <div className="loading-box">

          <div className="spinner"></div>

          <p>
            extracting_text( ) — please wait
          </p>

        </div>
      )}


      {/* =====================================
          GENERAL ERROR
      ====================================== */}

      {error && (
        <div className="error-box">
          Error — {error}
        </div>
      )}


      {/* =====================================
          RESULTS
      ====================================== */}

      {result && (
        <>

          {/* ---------------------------------
              EXTRACTED TEXT
          ---------------------------------- */}

          <div className="results">

            <div className="results-header">

              <h3>
                Extracted Text
              </h3>

              <span className="word-count">
                {result.word_count} words · {result.source_type}
              </span>

            </div>

            <div className="extracted-text">
              {result.extracted_text}
            </div>

          </div>


          {/* ---------------------------------
              ENGAGEMENT ANALYSIS
          ---------------------------------- */}

          {result.engagement_analysis && (
            <div className="analysis-results">

              {/* Analysis Header */}

              <div className="analysis-header">

                <div>

                  <div className="analysis-label">
                    ENGAGEMENT ANALYSIS
                  </div>

                  <h3>
                    Content Performance
                  </h3>

                </div>

                <div className="score">

                  {result.engagement_analysis.score}

                  <span>
                    /100
                  </span>

                </div>

              </div>


              {/* Analysis Content */}

              <div className="analysis-body">

                {/* =========================
                    STRENGTHS
                ========================== */}

                <div className="analysis-section">

                  <h4>
                    Strengths
                  </h4>

                  {result.engagement_analysis.strengths?.length > 0 ? (

                    <ul>

                      {result.engagement_analysis.strengths.map(
                        (strength, index) => (

                          <li key={index}>

                            <span className="check">
                              ✓
                            </span>

                            <span>
                              {strength}
                            </span>

                          </li>

                        )
                      )}

                    </ul>

                  ) : (

                    <p className="muted">
                      No major strengths detected yet.
                    </p>

                  )}

                </div>


                {/* =========================
                    SUGGESTIONS
                ========================== */}

                <div className="analysis-section">

                  <h4>
                    Suggestions
                  </h4>

                  {result.engagement_analysis.suggestions?.length > 0 ? (

                    <ul>

                      {result.engagement_analysis.suggestions.map(
                        (suggestion, index) => (

                          <li key={index}>

                            <span className="bullet">
                              →
                            </span>

                            <span>
                              {suggestion}
                            </span>

                          </li>

                        )
                      )}

                    </ul>

                  ) : (

                    <p className="muted">
                      Your content already follows the main
                      engagement guidelines.
                    </p>

                  )}


                  {/* =========================
                      LLM ACTION
                  ========================== */}

                  <div className="llm-action">

                    <button
                      className="improve-button"
                      onClick={handleImproveCaption}
                      disabled={improving}
                    >

                      {improving
                        ? 'Improving caption...'
                        : '✦ Improve Caption'}

                    </button>

                    <span className="llm-note">
                      Powered by local AI
                    </span>

                  </div>

                </div>

              </div>


              {/* =================================
                  SCORE METHODOLOGY
              ================================== */}

              <div className="methodology">

                <button
                  className="methodology-toggle"
                  onClick={() =>
                    setShowMethodology(!showMethodology)
                  }
                >

                  <span>
                    HOW IS THIS SCORE CALCULATED?
                  </span>

                  <span>
                    {showMethodology ? '−' : '+'}
                  </span>

                </button>


                {showMethodology && (
                  <div className="methodology-content">

                    <p className="methodology-description">
                      The engagement score is generated using
                      deterministic content-analysis rules. The
                      optional AI rewrite does not affect the score.
                    </p>

                    <div className="score-breakdown">

                      <div className="score-row">
                        <span>Concise content length</span>
                        <strong>20 pts</strong>
                      </div>

                      <div className="score-row">
                        <span>Call-to-action</span>
                        <strong>20 pts</strong>
                      </div>

                      <div className="score-row">
                        <span>Audience interaction</span>
                        <strong>20 pts</strong>
                      </div>

                      <div className="score-row">
                        <span>Relevant hashtags</span>
                        <strong>15 pts</strong>
                      </div>

                      <div className="score-row">
                        <span>Opening hook</span>
                        <strong>15 pts</strong>
                      </div>

                      <div className="score-row">
                        <span>Emoji usage</span>
                        <strong>10 pts</strong>
                      </div>

                      <div className="score-total">
                        <span>Total</span>
                        <strong>100 pts</strong>
                      </div>

                    </div>

                  </div>
                )}

              </div>


              {/* =================================
                  LLM ERROR
              ================================== */}

              {llmError && (
                <div className="llm-error">
                  Error — {llmError}
                </div>
              )}


              {/* =================================
                  IMPROVED CAPTION
              ================================== */}

              {improvedCaption && (
                <div className="improved-caption">

                  <div className="improved-caption-header">

                    <div className="analysis-label">
                      AI REWRITE
                    </div>

                    <h3>
                      Improved Caption
                    </h3>

                  </div>

                  <div className="improved-caption-body">
                    {improvedCaption}
                  </div>

                </div>
              )}

            </div>
          )}


          {/* =====================================
              ANALYZE ANOTHER FILE
          ====================================== */}

          <button
            className="reset-button"
            onClick={handleReset}
          >
            ↻ Analyze Another File
          </button>

        </>
      )}


      {/* =====================================
          FOOTER
      ====================================== */}

      <div className="footer">

        <div className="footer-name">
          Developed by <strong>Swakatha Bandyopadhyay</strong>
        </div>

        <div className="footer-meta">
          <span>
            Reg. No. 23BCE0087
          </span>

          <span className="footer-divider">
            ·
          </span>

          <span>
            Software Engineering Assessment
          </span>

        </div>

      </div>

    </div>
  );
}

export default App;
import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { submitBatch, getBatchStatus, getBatchResult } from '../utils/api';
import './BatchUpload.css';

function BatchUpload() {
  const [batchId, setBatchId] = useState('');
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jsonData, setJsonData] = useState('');
  const [polling, setPolling] = useState(false);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setJsonData(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
    },
    multiple: false,
  });

  const handleSubmit = async () => {
    if (!jsonData.trim()) {
      setError('Please provide JSON data or upload a file');
      return;
    }

    setLoading(true);
    setError(null);
    setStatus(null);
    setResult(null);

    try {
      const payload = JSON.parse(jsonData);
      const response = await submitBatch(payload);
      setBatchId(response.batch_id);
      setStatus(response);
      setPolling(true);
    } catch (err) {
      setError(err.message || 'Failed to submit batch');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!polling || !batchId) return;

    const interval = setInterval(async () => {
      try {
        const statusData = await getBatchStatus(batchId);
        setStatus(statusData);

        if (statusData.status === 'completed') {
          setPolling(false);
          const resultData = await getBatchResult(batchId);
          setResult(resultData);
        } else if (statusData.status === 'failed') {
          setPolling(false);
          setError(statusData.error || 'Batch processing failed');
        }
      } catch (err) {
        setPolling(false);
        setError(err.message);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [polling, batchId]);

  const getProgress = () => {
    if (!status || !status.total) return 0;
    return Math.round((status.processed / status.total) * 100);
  };

  return (
    <div className="batch-container">
      <div className="batch-card">
        <h2>Batch Evaluation</h2>
        <p className="subtitle">Upload and evaluate 100s of agent responses in batch mode</p>

        <div className="batch-section">
          <h3>Upload JSON File</h3>
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''}`}
          >
            <input {...getInputProps()} />
            <div className="dropzone-content">
              <span className="dropzone-icon">📁</span>
              {isDragActive ? (
                <p>Drop the JSON file here...</p>
              ) : (
                <>
                  <p>Drag & drop a JSON file here, or click to select</p>
                  <p className="dropzone-hint">Supports .json files</p>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="batch-section">
          <h3>Or Paste JSON Data</h3>
          <textarea
            value={jsonData}
            onChange={(e) => setJsonData(e.target.value)}
            placeholder={`{\n  "id": "batch-001",\n  "model_name": "gpt-4",\n  "inputs": [\n    {\n      "prompt": "What is AI?",\n      "agent_response": "AI is artificial intelligence...",\n      "reference": "Expected answer (optional)"\n    }\n  ]\n}`}
            rows="15"
            className="json-input"
          />
        </div>

        <button
          onClick={handleSubmit}
          className="submit-btn"
          disabled={loading || !jsonData.trim()}
        >
          {loading ? 'Submitting...' : 'Submit Batch'}
        </button>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {status && (
          <div className="status-card">
            <h3>Batch Status</h3>
            <div className="status-info">
              <div className="status-item">
                <span className="status-label">Batch ID:</span>
                <span className="status-value">{status.batch_id}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Status:</span>
                <span className={`status-badge ${status.status}`}>
                  {status.status}
                </span>
              </div>
              {status.total && (
                <>
                  <div className="status-item">
                    <span className="status-label">Progress:</span>
                    <span className="status-value">
                      {status.processed} / {status.total}
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${getProgress()}%` }}
                    />
                  </div>
                  <div className="progress-text">{getProgress()}%</div>
                </>
              )}
            </div>
          </div>
        )}

        {result && (
          <div className="result-card">
            <h3>Batch Results</h3>
            <div className="batch-summary">
              <div className="summary-item">
                <span className="summary-label">Total Evaluated:</span>
                <span className="summary-value">{result.total_evaluated}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Average Score:</span>
                <span className="summary-value highlight">
                  {(result.average_score * 100).toFixed(2)}%
                </span>
              </div>
            </div>

            {result.dimension_averages && (
              <div className="dimension-averages">
                <h4>Dimension Averages</h4>
                <div className="dimensions-grid">
                  {Object.entries(result.dimension_averages).map(([dim, score]) => (
                    <div key={dim} className="dimension-item">
                      <span className="dimension-name">
                        {dim.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className="dimension-score">
                        {(score * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.score_distribution && (
              <div className="score-distribution">
                <h4>Score Distribution</h4>
                <div className="distribution-grid">
                  <div className="dist-item excellent">
                    <span className="dist-label">Excellent (≥90%)</span>
                    <span className="dist-count">{result.score_distribution.excellent}</span>
                  </div>
                  <div className="dist-item good">
                    <span className="dist-label">Good (70-89%)</span>
                    <span className="dist-count">{result.score_distribution.good}</span>
                  </div>
                  <div className="dist-item fair">
                    <span className="dist-label">Fair (50-69%)</span>
                    <span className="dist-count">{result.score_distribution.fair}</span>
                  </div>
                  <div className="dist-item poor">
                    <span className="dist-label">Poor (&lt;50%)</span>
                    <span className="dist-count">{result.score_distribution.poor}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default BatchUpload;


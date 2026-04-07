import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  createPatient,
  getPatientAnalysis,
  getPatientReports,
  getPatients,
  getReportDetail,
} from '../services/api';
import './PatientDashboard.css';

const PatientDashboard = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddPatient, setShowAddPatient] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [reports, setReports] = useState([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [activePanel, setActivePanel] = useState('history');
  const [patientSearch, setPatientSearch] = useState('');
  const [reportFilterType, setReportFilterType] = useState('all');
  const [reportFilterEmotion, setReportFilterEmotion] = useState('all');
  const [reportDetail, setReportDetail] = useState(null);
  const [reportDetailLoading, setReportDetailLoading] = useState(false);
  const [newPatient, setNewPatient] = useState({
    name: '',
    age: '',
    gender: '',
    phone: '',
    email: '',
    medical_history: ''
  });

  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    loadPatients();
  }, [token, navigate]);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const response = await getPatients();

      if (response.data.success) {
        setPatients(response.data.patients);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load patients');
      console.error('Error loading patients:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPatient = async (e) => {
    e.preventDefault();

    if (!newPatient.name.trim()) {
      setError('Patient name is required');
      return;
    }

    try {
      const response = await createPatient(newPatient);

      if (response.data.success) {
        setPatients([...patients, response.data.patient]);
        setNewPatient({
          name: '',
          age: '',
          gender: '',
          phone: '',
          email: '',
          medical_history: ''
        });
        setShowAddPatient(false);
        setError('');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create patient');
    }
  };

  const normalizeReportSummary = (report) => {
    if (!report || !report.report_summary) {
      return null;
    }

    if (typeof report.report_summary === 'object') {
      return report.report_summary;
    }

    try {
      return JSON.parse(report.report_summary);
    } catch {
      return null;
    }
  };

  const selectPatient = async (patient) => {
    setSelectedPatient(patient);
    localStorage.setItem('selectedPatient', JSON.stringify(patient));

    try {
      setReportsLoading(true);
      const [analysisResponse, reportResponse] = await Promise.allSettled([
        getPatientAnalysis(patient.patient_id),
        getPatientReports(patient.patient_id),
      ]);

      if (
        analysisResponse.status === 'fulfilled' &&
        analysisResponse.value?.data?.success
      ) {
        setAnalysisHistory(analysisResponse.value.data.analysis_results || []);
      } else {
        setAnalysisHistory([]);
      }

      if (reportResponse.status === 'fulfilled' && reportResponse.value?.data?.success) {
        setReports(reportResponse.value.data.reports || []);
      } else {
        setReports([]);
      }
    } catch (err) {
      console.error('Error loading patient intelligence data:', err);
      setAnalysisHistory([]);
      setReports([]);
    } finally {
      setReportsLoading(false);
    }
  };

  const handleAnalyzeAudio = () => {
    localStorage.setItem('selectedPatient', JSON.stringify(selectedPatient));
    navigate('/audio');
  };

  const handleAnalyzeVideo = () => {
    localStorage.setItem('selectedPatient', JSON.stringify(selectedPatient));
    navigate('/video');
  };

  const handleAnalyzeMultimodal = () => {
    localStorage.setItem('selectedPatient', JSON.stringify(selectedPatient));
    navigate('/multimodal');
  };

  const openReportDetail = async (reportId) => {
    try {
      setReportDetailLoading(true);
      setReportDetail({ report_title: 'Loading Report...' });
      const response = await getReportDetail(reportId);
      if (response.data.success) {
        setReportDetail(response.data.report);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to load report details');
    } finally {
      setReportDetailLoading(false);
    }
  };

  const exportReportJson = () => {
    if (!reportDetail) {
      return;
    }

    const blob = new Blob([JSON.stringify(reportDetail, null, 2)], {
      type: 'application/json;charset=utf-8',
    });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${reportDetail.report_id || 'report'}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const filteredPatients = patients.filter((patient) => {
    const query = patientSearch.toLowerCase().trim();
    if (!query) {
      return true;
    }

    return (
      patient.name?.toLowerCase().includes(query) ||
      patient.patient_id?.toLowerCase().includes(query) ||
      patient.email?.toLowerCase().includes(query)
    );
  });

  const emotionOptions = [...new Set(reports.map((report) => report.emotion_detected).filter(Boolean))];

  const filteredReports = reports.filter((report) => {
    const typeMatch =
      reportFilterType === 'all' ||
      report.analysis_type?.toLowerCase() === reportFilterType;

    const emotionMatch =
      reportFilterEmotion === 'all' || report.emotion_detected === reportFilterEmotion;

    return typeMatch && emotionMatch;
  });

  const averageConfidence = reports.length
    ? (
        reports.reduce((sum, report) => sum + Number(report.confidence_score || 0), 0) /
        reports.length
      ) *
      100
    : 0;

  const dominantEmotion = (() => {
    const buckets = reports.reduce((accumulator, report) => {
      if (!report.emotion_detected) {
        return accumulator;
      }
      accumulator[report.emotion_detected] = (accumulator[report.emotion_detected] || 0) + 1;
      return accumulator;
    }, {});

    const sorted = Object.entries(buckets).sort((first, second) => second[1] - first[1]);
    return sorted[0]?.[0] || 'N/A';
  })();

  const summary = normalizeReportSummary(reportDetail);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading patients...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Patient Intelligence Hub</h1>
          <p>Centralized care insights, report tracking, and multimodal workflows.</p>
        </div>
        <div className="header-actions">
          <button className="secondary-action-btn" onClick={loadPatients}>
            Refresh Data
          </button>
          <button
            className="add-patient-btn"
            onClick={() => setShowAddPatient(!showAddPatient)}
          >
            {showAddPatient ? 'Cancel' : 'Add Patient'}
          </button>
        </div>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <p>Total Patients</p>
          <h3>{patients.length}</h3>
          <span>Registered records</span>
        </div>
        <div className="kpi-card">
          <p>Analyses</p>
          <h3>{analysisHistory.length}</h3>
          <span>For selected patient</span>
        </div>
        <div className="kpi-card">
          <p>Reports</p>
          <h3>{reports.length}</h3>
          <span>Generated summaries</span>
        </div>
        <div className="kpi-card">
          <p>Avg Confidence</p>
          <h3>{averageConfidence.toFixed(1)}%</h3>
          <span>Dominant emotion: {dominantEmotion}</span>
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}

      {showAddPatient && (
        <div className="add-patient-card">
          <h3>Add New Patient</h3>
          <form onSubmit={handleAddPatient} className="add-patient-form">
            <input
              type="text"
              placeholder="Patient Name *"
              value={newPatient.name}
              onChange={(e) => setNewPatient({...newPatient, name: e.target.value})}
              required
            />
            <input
              type="number"
              placeholder="Age"
              value={newPatient.age}
              onChange={(e) => setNewPatient({...newPatient, age: e.target.value})}
            />
            <select
              value={newPatient.gender}
              onChange={(e) => setNewPatient({...newPatient, gender: e.target.value})}
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            <input
              type="tel"
              placeholder="Phone"
              value={newPatient.phone}
              onChange={(e) => setNewPatient({...newPatient, phone: e.target.value})}
            />
            <input
              type="email"
              placeholder="Email"
              value={newPatient.email}
              onChange={(e) => setNewPatient({...newPatient, email: e.target.value})}
            />
            <textarea
              placeholder="Medical History"
              value={newPatient.medical_history}
              onChange={(e) => setNewPatient({...newPatient, medical_history: e.target.value})}
              rows="3"
            ></textarea>
            <button type="submit" className="submit-btn">Create Patient</button>
          </form>
        </div>
      )}

      <div className="dashboard-content">
        <div className="patients-section">
          <div className="section-heading">
            <h2>Patient Directory</h2>
            <span>{filteredPatients.length} visible</span>
          </div>

          <div className="patient-search-row">
            <input
              type="text"
              value={patientSearch}
              onChange={(event) => setPatientSearch(event.target.value)}
              placeholder="Search by name, ID, or email"
            />
          </div>

          <div className="patients-list">
            {filteredPatients.length > 0 ? (
              filteredPatients.map((patient) => (
                <div
                  key={patient.patient_id}
                  className={`patient-card ${selectedPatient?.patient_id === patient.patient_id ? 'active' : ''}`}
                  onClick={() => selectPatient(patient)}
                >
                  <div className="patient-id">{patient.patient_id}</div>
                  <div className="patient-info">
                    <h3>{patient.name}</h3>
                    <p>Age: {patient.age || 'N/A'} | Gender: {patient.gender || 'N/A'}</p>
                    {patient.phone && <p>📞 {patient.phone}</p>}
                    {patient.email && <p>📧 {patient.email}</p>}
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>No patients yet. Add your first patient to get started.</p>
              </div>
            )}
          </div>
        </div>

        {selectedPatient && (
          <div className="analysis-section">
            <h2>Analysis for {selectedPatient.name}</h2>
            
            <div className="analysis-actions">
              <button className="analysis-btn audio" onClick={handleAnalyzeAudio}>
                🎵 Analyze Audio
              </button>
              <button className="analysis-btn video" onClick={handleAnalyzeVideo}>
                🎬 Analyze Video
              </button>
              <button className="analysis-btn multimodal" onClick={handleAnalyzeMultimodal}>
                🎯 Multimodal Analysis
              </button>
            </div>

            <div className="panel-tabs">
              <button
                className={activePanel === 'history' ? 'active' : ''}
                onClick={() => setActivePanel('history')}
              >
                Analysis History
              </button>
              <button
                className={activePanel === 'reports' ? 'active' : ''}
                onClick={() => setActivePanel('reports')}
              >
                Report Center
              </button>
            </div>

            {activePanel === 'history' && (
              <div className="analysis-history">
                {analysisHistory.length > 0 ? (
                  <div className="history-list">
                    {analysisHistory.map((result, idx) => (
                      <div key={idx} className="history-item">
                        <div className="result-type">{result.analysis_type?.toUpperCase()}</div>
                        <div className="result-info">
                          <p><strong>File:</strong> {result.file_name}</p>
                          <p><strong>Date:</strong> {new Date(result.created_at).toLocaleString()}</p>
                          {result.notes && <p><strong>Notes:</strong> {result.notes}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-history">No analysis results yet for this patient.</p>
                )}
              </div>
            )}

            {activePanel === 'reports' && (
              <div className="reports-center">
                <div className="reports-toolbar">
                  <select
                    value={reportFilterType}
                    onChange={(event) => setReportFilterType(event.target.value)}
                  >
                    <option value="all">All Types</option>
                    <option value="audio">Audio</option>
                    <option value="video">Video</option>
                    <option value="multimodal">Multimodal</option>
                  </select>

                  <select
                    value={reportFilterEmotion}
                    onChange={(event) => setReportFilterEmotion(event.target.value)}
                  >
                    <option value="all">All Emotions</option>
                    {emotionOptions.map((emotion) => (
                      <option key={emotion} value={emotion}>
                        {emotion}
                      </option>
                    ))}
                  </select>
                </div>

                {reportsLoading ? (
                  <p className="no-history">Loading reports...</p>
                ) : filteredReports.length > 0 ? (
                  <div className="reports-list">
                    {filteredReports.map((report) => (
                      <article key={report.report_id} className="report-card">
                        <div className="report-head">
                          <h4>{report.report_title || 'Untitled Report'}</h4>
                          <span className="report-type-chip">{report.analysis_type}</span>
                        </div>
                        <p>
                          Emotion: <strong>{report.emotion_detected || 'Unknown'}</strong>
                        </p>
                        <p>
                          Confidence:{' '}
                          <strong>{(Number(report.confidence_score || 0) * 100).toFixed(1)}%</strong>
                        </p>
                        <p>Generated: {new Date(report.generated_at).toLocaleString()}</p>
                        <button
                          className="secondary-action-btn"
                          onClick={() => openReportDetail(report.report_id)}
                        >
                          View Full Report
                        </button>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="no-history">No reports match the current filters.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {reportDetail && (
        <div className="report-modal-overlay" onClick={() => setReportDetail(null)}>
          <div className="report-modal" onClick={(event) => event.stopPropagation()}>
            <div className="report-modal-head">
              <h3>{reportDetail.report_title}</h3>
              <button onClick={() => setReportDetail(null)} aria-label="Close report detail">
                ✕
              </button>
            </div>

            {reportDetailLoading ? (
              <p>Loading report details...</p>
            ) : (
              <>
                <div className="report-meta-grid">
                  <div>
                    <span>Analysis Type</span>
                    <strong>{reportDetail.analysis_type}</strong>
                  </div>
                  <div>
                    <span>Emotion</span>
                    <strong>{reportDetail.emotion_detected || 'Unknown'}</strong>
                  </div>
                  <div>
                    <span>Confidence</span>
                    <strong>{(Number(reportDetail.confidence_score || 0) * 100).toFixed(1)}%</strong>
                  </div>
                  <div>
                    <span>Generated At</span>
                    <strong>{new Date(reportDetail.generated_at).toLocaleString()}</strong>
                  </div>
                </div>

                {summary?.emotion_analysis && (
                  <section className="modal-section">
                    <h4>Emotion Analysis</h4>
                    <p>{summary.emotion_analysis.description}</p>
                  </section>
                )}

                {Array.isArray(reportDetail.recommendations) && reportDetail.recommendations.length > 0 && (
                  <section className="modal-section">
                    <h4>Recommendations</h4>
                    <ul>
                      {reportDetail.recommendations.map((item, index) => (
                        <li key={`${reportDetail.report_id}-${index}`}>{item}</li>
                      ))}
                    </ul>
                  </section>
                )}

                <div className="modal-actions">
                  <button className="secondary-action-btn" onClick={exportReportJson}>
                    Export JSON
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDashboard;

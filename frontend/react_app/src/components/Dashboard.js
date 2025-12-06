import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import api from '../utils/api';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState({
    totalEvaluations: 0,
    averageScore: 0,
    modelsEvaluated: 0,
    excellentResponses: 0,
    dimensionStats: [],
    modelComparison: [],
    scoreDistribution: [],
    trendData: [],
    recentEvaluations: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsData, dimensionData, modelData, distributionData, trendData, recentData] = await Promise.all([
        api.get('/api/dashboard/stats'),
        api.get('/api/dashboard/dimension-stats'),
        api.get('/api/dashboard/model-comparison'),
        api.get('/api/dashboard/score-distribution'),
        api.get('/api/dashboard/trend?days=7'),
        api.get('/api/dashboard/recent?limit=10'),
      ]);

      const distribution = [
        { name: 'Excellent (≥90%)', value: distributionData.data.excellent || 0, color: '#10b981' },
        { name: 'Good (70-89%)', value: distributionData.data.good || 0, color: '#f59e0b' },
        { name: 'Fair (50-69%)', value: distributionData.data.fair || 0, color: '#f97316' },
        { name: 'Poor (<50%)', value: distributionData.data.poor || 0, color: '#ef4444' },
      ];

      setStats({
        totalEvaluations: statsData.data.total_evaluations || 0,
        averageScore: statsData.data.average_score || 0,
        modelsEvaluated: statsData.data.models_evaluated || 0,
        excellentResponses: statsData.data.excellent_responses || 0,
        dimensionStats: dimensionData.data || [],
        modelComparison: modelData.data || [],
        scoreDistribution: distribution,
        trendData: trendData.data || [],
        recentEvaluations: recentData.data || [],
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      // Keep default/empty state on error
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#10b981';
    if (score >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <p className="dashboard-subtitle">Comprehensive evaluation metrics and insights</p>
      </div>

      {loading ? (
        <div className="loading-state">Loading dashboard data...</div>
      ) : stats.totalEvaluations === 0 ? (
        <div className="empty-state">
          <h3>No evaluations yet</h3>
          <p>Start evaluating agent responses to see analytics here.</p>
        </div>
      ) : (
        <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">Total Evaluations</div>
            <div className="stat-value">{stats.totalEvaluations}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <div className="stat-label">Average Score</div>
            <div className="stat-value">{(stats.averageScore * 100).toFixed(1)}%</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <div className="stat-label">Models Evaluated</div>
            <div className="stat-value">{stats.modelsEvaluated}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">Excellent Responses</div>
            <div className="stat-value">{stats.excellentResponses}</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Score Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 1]} />
              <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
              <Legend />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#667eea"
                strokeWidth={3}
                dot={{ fill: '#667eea', r: 5 }}
                name="Average Score"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Dimension Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.dimensionStats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis domain={[0, 1]} />
              <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
              <Bar dataKey="score" fill="#667eea" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Model Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.modelComparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis domain={[0, 1]} />
              <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
              <Legend />
              <Bar dataKey="score" fill="#764ba2" radius={[8, 8, 0, 0]} name="Average Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Score Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats.scoreDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {stats.scoreDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="leaderboard-section">
        <h2>Model Leaderboard</h2>
        <div className="leaderboard-card">
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Model</th>
                <th>Average Score</th>
                <th>Evaluations</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {stats.modelComparison
                .sort((a, b) => b.score - a.score)
                .map((model, index) => (
                  <tr key={model.model}>
                    <td className="rank-cell">
                      <span className={`rank-badge rank-${index + 1}`}>
                        {index + 1}
                      </span>
                    </td>
                    <td className="model-cell">
                      <strong>{model.model}</strong>
                    </td>
                    <td>
                      <div className="score-bar-container">
                        <div
                          className="score-bar"
                          style={{
                            width: `${model.score * 100}%`,
                            backgroundColor: getScoreColor(model.score),
                          }}
                        />
                        <span className="score-text">
                          {(model.score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td>{model.count}</td>
                    <td>
                      <span className="status-badge active">Active</span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="recent-section">
        <h2>Recent Evaluations</h2>
        <div className="recent-card">
          <div className="recent-list">
            {stats.recentEvaluations.map((evaluation) => (
              <div key={evaluation.id} className="recent-item">
                <div className="recent-info">
                  <span className="recent-id">{evaluation.id}</span>
                  <span className="recent-model">{evaluation.model}</span>
                  <span className="recent-date">{evaluation.date}</span>
                </div>
                <div className="recent-score">
                  <span
                    className="score-badge"
                    style={{ backgroundColor: getScoreColor(evaluation.score) }}
                  >
                    {(evaluation.score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;


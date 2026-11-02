import { useEffect, useState } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8100";

function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get(`${API_URL}/dashboard`)
      .then((res) => setData(res.data))
      .catch(() => setError("Could not load dashboard data. Is the backend running?"));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading dashboard...</p>;

  const locationChart = {
    labels: data.by_location.map((d) => d.location),
    datasets: [
      {
        label: "Restaurant Count",
        data: data.by_location.map((d) => d.count),
        backgroundColor: "#d64545",
      },
    ],
  };
  const chartOptions = {
    responsive: true,
    scales: {
      x: {
        title: {
          display: true,
          text: "Location",
        },
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Restaurant Count",
        },
      },
    },
  };

  const typeChart = {
    labels: data.by_rest_type.map((d) => d.rest_type),
    datasets: [
      {
        label: "Restaurant Count",
        data: data.by_rest_type.map((d) => d.count),
        backgroundColor: "#1a7a3a",
      },
    ],
  };

  return (
    <div className="dashboard">
      <div className="stats-summary">
        <div className="stat-box">
          <span className="stat-value">{data.overall.avg_rating?.toFixed(2)}</span>
          <span className="stat-label">Avg Rating</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{data.overall.avg_sentiment?.toFixed(2)}</span>
          <span className="stat-label">Avg Sentiment</span>
        </div>
      </div>

      <div className="chart-box">
        <h3>Top 10 Locations by Restaurant Count</h3>
        <Bar data={locationChart} options={chartOptions} />
      </div>

      <div className="chart-box">
        <h3>Top 10 Restaurant Types</h3>
        <Bar
          data={typeChart}
          options={{
            ...chartOptions,
            scales: {
              ...chartOptions.scales,
              x: {
                ...chartOptions.scales.x,
                title: { display: true, text: "Restaurant Type" },
              },
            },
          }}
        />
      </div>
    </div>
  );
}

export default Dashboard;
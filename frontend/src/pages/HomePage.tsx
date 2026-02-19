import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Card from "../components/Card";
import Button from "../components/Button";
import MainLayout from "../components/layout/MainLayout";
import { getHomeStats, type HomeStats } from "../services/statsService";
import { apiClient } from "../services/apiClient";

export default function HomePage() {
  const [stats, setStats] = useState<HomeStats | null>(null);
  const [loading, setLoading] = useState(true);

  const [apiTestLoading, setApiTestLoading] = useState(false);
  const [apiTestResult, setApiTestResult] = useState<string>("");

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        setLoading(true);
        const data = await getHomeStats();
        if (mounted) setStats(data);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  const testApi = async () => {
    try {
      setApiTestLoading(true);
      setApiTestResult("");
      const res = await apiClient.get("/stats/");
      setApiTestResult(JSON.stringify(res.data, null, 2));
    } catch (e) {
      setApiTestResult("ERROR");
    } finally {
      setApiTestLoading(false);
    }
  };

  return (
    <MainLayout>
      <Hero />

      <section style={{ marginBottom: 18 }}>
        <Card title="API Test (stats)">
          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <Button type="button" onClick={testApi} disabled={apiTestLoading}>
              {apiTestLoading ? "Testing..." : "Test /api/stats/"}
            </Button>
            <div style={{ fontSize: 13, color: "var(--muted)" }}>
              After login, this should hit 127.0.0.1:8000 and include Authorization header.
            </div>
          </div>
          <pre
            style={{
              marginTop: 12,
              padding: 12,
              borderRadius: 12,
              border: "1px solid var(--border)",
              background: "white",
              overflow: "auto",
              maxHeight: 240,
              fontSize: 12,
            }}
          >
            {apiTestResult || "Click the button to test."}
          </pre>
        </Card>
      </section>

      <StatsSection stats={stats} loading={loading} />
      <FeaturesSection />
    </MainLayout>
  );
}

function Hero() {
  return (
    <section style={{ marginBottom: 18 }}>
      <h1 style={{ marginTop: 0, fontSize: 34, lineHeight: 1.2 }}>
        Police Case Management System
      </h1>
      <p style={{ marginTop: 8, color: "var(--muted)", maxWidth: 760 }}>
        A centralized platform for managing complaints, cases, evidence, and reporting—designed for
        role-based workflows and investigative collaboration.
      </p>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
        <Link to="/auth">
          <Button>Get started</Button>
        </Link>
        <Link to="/most-wanted">
          <Button variant="secondary">View Most Wanted</Button>
        </Link>
      </div>
    </section>
  );
}

function StatsSection({ stats, loading }: { stats: HomeStats | null; loading: boolean }) {
  const items = [
    { label: "Solved cases", value: stats?.solvedCases ?? 0 },
    { label: "Total staff", value: stats?.totalStaff ?? 0 },
    { label: "Active cases", value: stats?.activeCases ?? 0 },
  ];

  return (
    <section style={{ marginBottom: 18 }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 14,
        }}
      >
        {items.map((it) => (
          <Card key={it.label} title={it.label}>
            <div style={{ fontSize: 32, fontWeight: 900, letterSpacing: -0.5 }}>
              {loading ? "—" : it.value.toLocaleString()}
            </div>
            <div style={{ marginTop: 6, fontSize: 13, color: "var(--muted)" }}>
              {loading ? "Loading..." : "Updated recently"}
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
}

function FeaturesSection() {
  const features = [
    {
      title: "Modular dashboard",
      desc: "Modules are shown based on your role and responsibilities.",
    },
    {
      title: "Evidence handling",
      desc: "Register, review, and track evidence across cases.",
    },
    {
      title: "Detective board",
      desc: "Connect clues visually and organize investigative links.",
    },
    {
      title: "Global reporting",
      desc: "Generate case summaries and decision-ready reports.",
    },
  ];

  return (
    <section>
      <h2 style={{ marginTop: 0 }}>What you can do</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: 14,
        }}
      >
        {features.map((f) => (
          <Card key={f.title} title={f.title}>
            <p style={{ marginTop: 0, color: "var(--muted)" }}>{f.desc}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}

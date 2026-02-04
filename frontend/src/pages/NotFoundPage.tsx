import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <main className="container">
      <h1 style={{ marginTop: 0 }}>Page not found</h1>
      <p style={{ color: "var(--muted)" }}>The page you are looking for does not exist.</p>
      <Link to="/" style={{ fontWeight: 700 }}>
        Go to Home
      </Link>
    </main>
  );
}

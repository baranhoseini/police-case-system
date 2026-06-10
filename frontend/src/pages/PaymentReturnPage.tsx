import { Link, useSearchParams } from "react-router-dom";
import MainLayout from "../components/layout/MainLayout";
import Card from "../components/Card";
import Button from "../components/Button";

export default function PaymentReturnPage() {
  const [params] = useSearchParams();

  const paymentId = params.get("payment_id") || "";
  const okParam = (params.get("ok") || "").toLowerCase();
  const ok = okParam === "1" || okParam === "true";
  const status = params.get("status") || params.get("Status") || "";
  const refId = params.get("ref_id") || params.get("RefID") || "";
  const authority = params.get("authority") || params.get("Authority") || "";
  const code = params.get("code") || "";
  const message = params.get("message") || "";

  return (
    <MainLayout title="Payment result">
      <Card title={ok ? "✅ Payment successful" : "❌ Payment failed / canceled"}>
        {!paymentId ? (
          <p style={{ marginTop: 0, color: "var(--muted)" }}>
            Missing payment_id in the callback URL.
          </p>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            <div>
              <div style={{ color: "var(--muted)", fontSize: 13 }}>Payment ID</div>
              <div style={{ fontWeight: 800 }}>{paymentId}</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <div style={{ color: "var(--muted)", fontSize: 13 }}>Status</div>
                <div style={{ fontWeight: 700 }}>{status || (ok ? "OK" : "NOK")}</div>
              </div>
              <div>
                <div style={{ color: "var(--muted)", fontSize: 13 }}>Ref ID</div>
                <div style={{ fontWeight: 700 }}>{refId || "-"}</div>
              </div>
            </div>

            <div>
              <div style={{ color: "var(--muted)", fontSize: 13 }}>Authority</div>
              <div style={{ fontWeight: 700, wordBreak: "break-all" }}>{authority || "-"}</div>
            </div>

            {(code || message) && (
              <div style={{ display: "grid", gap: 6 }}>
                {code && (
                  <div>
                    <div style={{ color: "var(--muted)", fontSize: 13 }}>Verify code</div>
                    <div style={{ fontWeight: 700 }}>{code}</div>
                  </div>
                )}
                {message && (
                  <div>
                    <div style={{ color: "var(--muted)", fontSize: 13 }}>Verify message</div>
                    <div style={{ fontWeight: 700 }}>{message}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 16 }}>
          <Link to="/dashboard">
            <Button>Go to dashboard</Button>
          </Link>
          <Link to="/">
            <Button variant="secondary">Go to home</Button>
          </Link>
        </div>
      </Card>
    </MainLayout>
  );
}
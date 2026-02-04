import AuthLayout from "../components/layout/AuthLayout";
import Button from "../components/Button";
import Input from "../components/Input";
import Card from "../components/Card";

export default function AuthPage() {
  return (
    <AuthLayout title="Sign in">
      <Card title="Welcome back">
        <div style={{ display: "grid", gap: 12 }}>
          <Input label="Email" placeholder="you@example.com" />
          <Input label="Password" placeholder="••••••••" type="password" />
          <Button>Sign in</Button>
        </div>
      </Card>
    </AuthLayout>
  );
}

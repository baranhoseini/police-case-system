import { useMemo, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../components/layout/AuthLayout";
import Card from "../components/Card";
import Button from "../components/Button";
import Input from "../components/Input";
import { useAuth } from "../features/auth/useAuth";
import { login, register as registerUser } from "../services/authService";
import { getApiErrorMessage } from "../services/apiErrors";
import { setRefreshToken } from "../features/auth/authStorage";

import {
  loginSchema,
  signupSchema,
  type LoginFormValues,
  type SignupFormValues,
} from "../features/auth/authSchemas";

type Mode = "signin" | "signup";

export default function AuthPage() {
  const [mode, setMode] = useState<Mode>("signin");

  return (
    <AuthLayout title={mode === "signin" ? "Sign in" : "Create account"}>
      <AuthTabs mode={mode} setMode={setMode} />
      {mode === "signin" ? <SignInForm /> : <SignUpForm />}
    </AuthLayout>
  );
}

function AuthTabs({ mode, setMode }: { mode: Mode; setMode: (m: Mode) => void }) {
  const tabBase: React.CSSProperties = {
    flex: 1,
    padding: "10px 12px",
    borderRadius: 12,
    border: "1px solid var(--border)",
    background: "white",
    cursor: "pointer",
    fontWeight: 700,
  };

  return (
    <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
      <button
        type="button"
        onClick={() => setMode("signin")}
        style={{
          ...tabBase,
          background: mode === "signin" ? "var(--primary)" : "white",
          color: mode === "signin" ? "white" : "var(--primary)",
          borderColor: mode === "signin" ? "var(--primary)" : "var(--border)",
        }}
      >
        Sign in
      </button>

      <button
        type="button"
        onClick={() => setMode("signup")}
        style={{
          ...tabBase,
          background: mode === "signup" ? "var(--primary)" : "white",
          color: mode === "signup" ? "white" : "var(--primary)",
          borderColor: mode === "signup" ? "var(--primary)" : "var(--border)",
        }}
      >
        Create account
      </button>
    </div>
  );
}

function SignInForm() {
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: LoginFormValues) => {
    try {
      // loginSchema uses "email" field name, but it is actually the "identifier"
      const res = await login(values);
      setRefreshToken(res.refresh);
      signIn(res.access);
      navigate("/dashboard");
    } catch (err) {
      const msg = getApiErrorMessage(err);
      setError("email", { type: "server", message: msg });
    }
  };

  return (
    <Card title="Welcome back">
      <form onSubmit={handleSubmit(onSubmit)} style={{ display: "grid", gap: 12 }}>
        <Input
          label="Identifier"
          placeholder="username / email / phone / national id"
          autoComplete="username"
          {...register("email")}
          error={errors.email?.message}
        />

        <Input
          label="Password"
          placeholder="••••••••"
          type="password"
          autoComplete="current-password"
          {...register("password")}
          error={errors.password?.message}
        />

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>

        <p style={{ margin: 0, fontSize: 13, color: "var(--muted)" }}>
          By continuing, you agree to the terms and privacy policy.
        </p>
      </form>
    </Card>
  );
}

function SignUpForm() {
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      username: "",
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      nationalId: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (values: SignupFormValues) => {
    try {
      await registerUser({
        username: values.username,
        firstName: values.firstName,
        lastName: values.lastName,
        email: values.email,
        phone: values.phone,
        nationalId: values.nationalId,
        password: values.password,
      });

      // Auto sign-in after registration:
      // login() expects the identifier field named "email" in LoginFormValues.
      // Your login service sends identifier to backend (username/email/phone/national_id).
      const res = await login({ email: values.email, password: values.password });
      setRefreshToken(res.refresh);
      signIn(res.access);
      navigate("/dashboard");
    } catch (err) {
      const msg = getApiErrorMessage(err);
      // Show error on email field (usually best common place)
      setError("email", { type: "server", message: msg });
    }
  };

  const passwordHint = useMemo(() => "Use at least 8 characters. Avoid common passwords.", []);

  return (
    <Card title="Create your account">
      <form onSubmit={handleSubmit(onSubmit)} style={{ display: "grid", gap: 12 }}>
        <Input
          label="Username"
          placeholder="your username"
          autoComplete="username"
          {...register("username")}
          error={errors.username?.message}
        />

        <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr" }}>
          <Input
            label="First name"
            placeholder="John"
            autoComplete="given-name"
            {...register("firstName")}
            error={errors.firstName?.message}
          />
          <Input
            label="Last name"
            placeholder="Doe"
            autoComplete="family-name"
            {...register("lastName")}
            error={errors.lastName?.message}
          />
        </div>

        <Input
          label="Email"
          placeholder="you@example.com"
          autoComplete="email"
          {...register("email")}
          error={errors.email?.message}
        />

        <Input
          label="Phone"
          placeholder="+49..."
          autoComplete="tel"
          {...register("phone")}
          error={errors.phone?.message}
        />

        <Input
          label="National ID"
          placeholder="National ID"
          autoComplete="off"
          {...register("nationalId")}
          error={errors.nationalId?.message}
        />

        <div style={{ display: "grid", gap: 10 }}>
          <Input
            label="Password"
            placeholder="••••••••"
            type="password"
            autoComplete="new-password"
            {...register("password")}
            error={errors.password?.message}
          />
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: -6 }}>{passwordHint}</div>
        </div>

        <Input
          label="Confirm password"
          placeholder="••••••••"
          type="password"
          autoComplete="new-password"
          {...register("confirmPassword")}
          error={errors.confirmPassword?.message}
        />

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </Button>
      </form>
    </Card>
  );
}
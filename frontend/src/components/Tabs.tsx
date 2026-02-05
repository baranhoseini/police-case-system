import type { PropsWithChildren } from "react";

export type TabKey = string;

export type TabItem = {
  key: TabKey;
  label: string;
};

type Props = PropsWithChildren<{
  tabs: TabItem[];
  activeKey: TabKey;
  onChange: (key: TabKey) => void;
}>;

export default function Tabs({ tabs, activeKey, onChange }: Props) {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        {tabs.map((t) => {
          const active = t.key === activeKey;
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => onChange(t.key)}
              style={{
                border: "1px solid var(--border)",
                padding: "8px 12px",
                borderRadius: 12,
                cursor: "pointer",
                fontWeight: 800,
                background: active ? "var(--primary)" : "white",
                color: active ? "white" : "var(--primary)",
                borderColor: active ? "var(--primary)" : "var(--border)",
              }}
            >
              {t.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

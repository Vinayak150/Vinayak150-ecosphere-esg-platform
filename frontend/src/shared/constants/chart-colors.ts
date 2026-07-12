export const CHART_COLORS = {
  environmental: ["#16a34a", "#22c55e", "#4ade80", "#86efac", "#15803d", "#166534"],
  social: ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#1d4ed8", "#1e40af"],
  governance: ["#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#6d28d9", "#5b21b6"],
  gamification: ["#2563eb", "#3b82f6", "#60a5fa", "#7c3aed", "#16a34a"],
  primary: "#16a34a",
  socialPillar: "#2563eb",
  governancePillar: "#7c3aed",
  muted: "hsl(var(--muted))",
} as const;

export const CHART_TOOLTIP_STYLE = {
  backgroundColor: "hsl(var(--card))",
  border: "1px solid hsl(var(--border))",
  borderRadius: "var(--radius)",
  fontSize: 12,
} as const;

export const CHART_AXIS_STYLE = { fontSize: 11, fill: "hsl(var(--muted-foreground))" };

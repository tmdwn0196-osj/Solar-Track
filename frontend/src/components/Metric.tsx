type MetricProps = {
  label: string;
  value: string;
  tone?: "default" | "good" | "warn" | "danger";
};

export function Metric({ label, value, tone = "default" }: MetricProps) {
  return (
    <div className={`metric metric-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

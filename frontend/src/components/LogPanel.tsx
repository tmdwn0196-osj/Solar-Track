import { ListChecks } from "lucide-react";

export function LogPanel({ logs }: { logs: string[] }) {
  return (
    <section className="panel log-panel">
      <div className="panel-heading">
        <ListChecks size={18} />
        <h2>로그</h2>
      </div>
      <ol>
        {logs.slice(-8).map((log, index) => (
          <li key={`${log}-${index}`}>{log}</li>
        ))}
      </ol>
    </section>
  );
}

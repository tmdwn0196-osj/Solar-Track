import { FileText } from "lucide-react";
import type { SolarState } from "../types/solar";
import { buildDemoReport } from "../logic/reportModel";

export function DemoReportPanel({ state }: { state: SolarState }) {
  const report = buildDemoReport(state);

  return (
    <section className="panel">
      <div className="panel-heading">
        <FileText size={18} />
        <h2>시연 리포트</h2>
      </div>
      <p className="panel-note">{report.summary}</p>
      <dl className="agent-list">
        <div>
          <dt>시연 포인트</dt>
          <dd>{report.talkingPoint}</dd>
        </div>
        <div>
          <dt>발표 문장</dt>
          <dd>
            <ol className="script-list">
              {report.script.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ol>
          </dd>
        </div>
      </dl>
    </section>
  );
}

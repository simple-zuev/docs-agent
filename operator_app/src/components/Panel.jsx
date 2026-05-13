export default function Panel({ title, children, tone = "default" }) {
  return (
    <section className={`panel panel-${tone}`}>
      <div className="panel-header">{title}</div>
      <div className="panel-body">{children}</div>
    </section>
  );
}

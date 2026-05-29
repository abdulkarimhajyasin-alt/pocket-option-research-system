document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!form.matches(".action-card")) {
    return;
  }
  const button = form.querySelector("button");
  if (button) {
    button.disabled = true;
    button.textContent = "قيد التشغيل";
  }
});

function renderChart(element) {
  const payload = JSON.parse(element.dataset.chart || "{}");
  const labels = payload.labels || [];
  const series = payload.series || [];
  if (!labels.length || !series.length) {
    element.innerHTML = '<div class="chart-empty">لا توجد بيانات للرسم</div>';
    return;
  }
  const width = 720;
  const height = element.classList.contains("small-chart") ? 220 : 300;
  const padding = { top: 24, right: 38, bottom: 42, left: 52 };
  const values = series.flatMap((item) => item.values || []);
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);
  const span = max - min || 1;
  const xFor = (index) => padding.left + (index * (width - padding.left - padding.right)) / Math.max(labels.length - 1, 1);
  const yFor = (value) => padding.top + ((max - value) * (height - padding.top - padding.bottom)) / span;
  const colorFor = (name) => {
    const colors = { accent: "#39c6a3", blue: "#6ca8ff", green: "#7bd88f", warning: "#ffbf69" };
    return colors[name] || colors.accent;
  };
  const axis = `<line x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" class="axis" />
    <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" class="axis" />`;
  let body = "";
  if (payload.chart_type === "bar") {
    const barWidth = Math.max(8, (width - padding.left - padding.right) / labels.length - 12);
    const baseline = yFor(0);
    const item = series[0];
    body = (item.values || []).map((value, index) => {
      const x = xFor(index) - barWidth / 2;
      const y = Math.min(yFor(value), baseline);
      const h = Math.abs(baseline - yFor(value));
      return `<rect x="${x}" y="${y}" width="${barWidth}" height="${Math.max(h, 2)}" rx="3" class="bar ${item.color || "accent"}" />`;
    }).join("");
  } else {
    body = series.map((item) => {
      const points = (item.values || []).map((value, index) => `${xFor(index)},${yFor(value)}`).join(" ");
      return `<polyline points="${points}" class="line ${item.color || "accent"}" />`;
    }).join("");
  }
  const labelStep = Math.max(1, Math.ceil(labels.length / 6));
  const labelMarkup = labels
    .map((label, index) => index % labelStep === 0
      ? `<text x="${xFor(index)}" y="${height - 14}" class="chart-label">${label}</text>`
      : "")
    .join("");
  const ticks = `<text x="${padding.left - 8}" y="${padding.top + 4}" class="chart-tick">${max.toFixed(1)}</text>
    <text x="${padding.left - 8}" y="${height - padding.bottom}" class="chart-tick">${min.toFixed(1)}</text>`;
  element.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${payload.title || "chart"}">${axis}${body}${ticks}${labelMarkup}</svg>`;
}

document.querySelectorAll("[data-chart]").forEach(renderChart);

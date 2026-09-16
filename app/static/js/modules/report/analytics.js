(() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";

  function readSource(container) {
    const sourceId = container.dataset.chartSource;
    const source = document.getElementById(sourceId);
    if (!source) return null;
    try {
      return JSON.parse(source.textContent || "null");
    } catch (error) {
      console.error("WorkFlow analytics: dados de gráfico inválidos", error);
      return null;
    }
  }

  function emptyState(container, message = "Sem dados para exibir neste período.") {
    container.innerHTML = "";
    const empty = document.createElement("div");
    empty.className = "chart-empty-state";
    empty.textContent = message;
    container.appendChild(empty);
  }

  function svgElement(name, attrs = {}) {
    const el = document.createElementNS(SVG_NS, name);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, String(value)));
    return el;
  }

  function compactNumber(value) {
    return new Intl.NumberFormat("pt-BR", {
      notation: Math.abs(value) >= 1000 ? "compact" : "standard",
      maximumFractionDigits: 1,
    }).format(value);
  }

  function formatMetric(value, label = "", prefix = "") {
    const number = compactNumber(value);
    if (prefix) return `${prefix} ${number}`;
    return `${number}${label ? ` ${label}` : ""}`;
  }

  function renderLine(container) {
    const payload = readSource(container);
    const items = payload && Array.isArray(payload.items) ? payload.items : [];
    const valueKey = container.dataset.valueKey || "value";
    const valueLabel = container.dataset.valueLabel || "";
    const valuePrefix = container.dataset.valuePrefix || "";

    if (!items.length) {
      emptyState(container);
      return;
    }

    const values = items.map((item) => Number(item[valueKey]) || 0);
    const width = 920;
    const height = 300;
    const pad = { top: 24, right: 24, bottom: 48, left: 64 };
    const plotW = width - pad.left - pad.right;
    const plotH = height - pad.top - pad.bottom;
    const rawMax = Math.max(...values, 0);
    const maxValue = rawMax > 0 ? rawMax : 1;

    container.innerHTML = "";
    const svg = svgElement("svg", {
      viewBox: `0 0 ${width} ${height}`,
      role: "img",
      "aria-label": `Gráfico de ${valueLabel || "produção"}`,
      preserveAspectRatio: "xMidYMid meet",
    });
    svg.classList.add("workflow-line-svg");

    for (let i = 0; i <= 4; i += 1) {
      const y = pad.top + (plotH * i) / 4;
      const grid = svgElement("line", {
        x1: pad.left,
        y1: y,
        x2: width - pad.right,
        y2: y,
        class: "chart-grid-line",
      });
      svg.appendChild(grid);

      const tickValue = maxValue * (1 - i / 4);
      const tick = svgElement("text", {
        x: pad.left - 12,
        y: y + 4,
        "text-anchor": "end",
        class: "chart-axis-label",
      });
      tick.textContent = formatMetric(tickValue, "", valuePrefix);
      svg.appendChild(tick);
    }

    const denominator = Math.max(items.length - 1, 1);
    const points = items.map((item, index) => {
      const x = pad.left + (plotW * index) / denominator;
      const value = Number(item[valueKey]) || 0;
      const y = pad.top + plotH - (value / maxValue) * plotH;
      return { x, y, value, label: item.label };
    });

    if (points.length === 1) {
      points[0].x = pad.left + plotW / 2;
    }

    const polyline = svgElement("polyline", {
      points: points.map((point) => `${point.x},${point.y}`).join(" "),
      class: "chart-line-path",
      fill: "none",
    });
    svg.appendChild(polyline);

    const desiredLabels = Math.min(6, items.length);
    const labelIndexes = new Set();
    for (let i = 0; i < desiredLabels; i += 1) {
      const index = desiredLabels === 1 ? 0 : Math.round((i * (items.length - 1)) / (desiredLabels - 1));
      labelIndexes.add(index);
    }

    points.forEach((point, index) => {
      const dot = svgElement("circle", {
        cx: point.x,
        cy: point.y,
        r: 4.5,
        class: "chart-line-dot",
        tabindex: "0",
      });
      const title = svgElement("title");
      title.textContent = `${point.label}: ${formatMetric(point.value, valueLabel, valuePrefix)}`;
      dot.appendChild(title);
      svg.appendChild(dot);

      if (labelIndexes.has(index)) {
        const label = svgElement("text", {
          x: point.x,
          y: height - 18,
          "text-anchor": "middle",
          class: "chart-axis-label chart-x-label",
        });
        label.textContent = point.label;
        svg.appendChild(label);
      }
    });

    container.appendChild(svg);
  }

  function renderBars(container) {
    const data = readSource(container);
    const items = Array.isArray(data) ? data : [];
    const valueLabel = container.dataset.valueLabel || "";

    if (!items.length) {
      emptyState(container);
      return;
    }

    const maxValue = Math.max(...items.map((item) => Number(item.value) || 0), 1);
    container.innerHTML = "";

    const list = document.createElement("div");
    list.className = "workflow-bars";

    items.forEach((item, index) => {
      const value = Number(item.value) || 0;
      const row = document.createElement("div");
      row.className = "workflow-bar-row";

      const header = document.createElement("div");
      header.className = "workflow-bar-header";

      const label = document.createElement("span");
      label.className = "workflow-bar-label";
      label.textContent = item.label;

      const number = document.createElement("strong");
      number.className = "workflow-bar-value";
      number.textContent = `${compactNumber(value)} ${valueLabel}`.trim();

      header.append(label, number);

      const track = document.createElement("div");
      track.className = "workflow-bar-track";
      track.setAttribute("role", "progressbar");
      track.setAttribute("aria-label", item.label);
      track.setAttribute("aria-valuenow", String(value));
      track.setAttribute("aria-valuemin", "0");
      track.setAttribute("aria-valuemax", String(maxValue));

      const fill = document.createElement("div");
      fill.className = "workflow-bar-fill";
      fill.style.width = `${Math.max((value / maxValue) * 100, value > 0 ? 2 : 0)}%`;
      fill.style.setProperty("--bar-order", index);
      track.appendChild(fill);

      row.append(header, track);
      list.appendChild(row);
    });

    container.appendChild(list);
  }

  document.querySelectorAll(".wf-line-chart").forEach(renderLine);
  document.querySelectorAll(".wf-bar-chart").forEach(renderBars);

  document.querySelectorAll(".chart-metric-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const chart = document.getElementById(button.dataset.chartTarget);
      if (!chart) return;

      const group = button.closest(".chart-metric-switch");
      group?.querySelectorAll(".chart-metric-toggle").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");

      chart.dataset.valueKey = button.dataset.valueKey || "value";
      chart.dataset.valueLabel = button.dataset.valueLabel || "";
      chart.dataset.valuePrefix = button.dataset.valuePrefix || "";
      renderLine(chart);
    });
  });
})();

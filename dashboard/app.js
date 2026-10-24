
const files = {
  cases: "data/cases.json",
  alerts: "data/alerts.json",
  forecasts: "data/forecasts.json",
  resources: "data/resources.json",
  calendar: "data/calendar.json"
};

const tooltip = d3.select("#tooltip");
const districtFilter = d3.select("#district-filter");
const diseaseFilter = d3.select("#disease-filter");
const budgetSlider = d3.select("#budget-slider");
const thresholdSlider = d3.select("#threshold-slider");
const equitySlider = d3.select("#equity-slider");

let data = {};

async function loadData() {
  const entries = await Promise.all(
    Object.entries(files).map(async ([key, url]) => {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Failed to load ${url}`);
      return [key, await response.json()];
    })
  );

  data = Object.fromEntries(entries);

  const districts = new Set();
  const diseases = new Set();

  for (const row of data.cases) {
    if (row.district) districts.add(row.district);
    if (row.disease) diseases.add(row.disease);
  }

  for (const row of data.forecasts) {
    if (row.district) districts.add(row.district);
    if (row.disease) diseases.add(row.disease);
  }

  for (const district of [...districts].sort()) {
    districtFilter.append("option").attr("value", district).text(district);
  }

  for (const disease of [...diseases].sort()) {
    diseaseFilter.append("option").attr("value", disease).text(disease);
  }

  districtFilter.on("change", render);
  diseaseFilter.on("change", render);
  budgetSlider.on("input", render);
  thresholdSlider.on("input", render);
  equitySlider.on("input", render);

  d3.select("#status").text(
    `Loaded ${data.cases.length.toLocaleString()} public weekly records.`
  );

  render();
}

function filtered(rows) {
  const district = districtFilter.property("value");
  const disease = diseaseFilter.property("value");

  return rows.filter(row =>
    (district === "ALL" || row.district === district) &&
    (disease === "ALL" || row.disease === disease)
  );
}

function numeric(value) {
  return value !== null && value !== undefined && Number.isFinite(+value)
    ? +value
    : null;
}

function clear(id) {
  d3.select(id).selectAll("*").remove();
}

function showTooltip(event, text) {
  tooltip.style("display", "block")
    .style("left", `${event.clientX + 12}px`)
    .style("top", `${event.clientY + 12}px`)
    .text(text);
}

function hideTooltip() {
  tooltip.style("display", "none");
}

function drawLineChart(container, rows, dateKey, valueKey, label) {
  clear(container);

  const parsed = rows
    .map(d => ({
      date: new Date(d[dateKey]),
      value: numeric(d[valueKey]),
      lower: numeric(d.lower_80),
      upper: numeric(d.upper_80)
    }))
    .filter(d => !Number.isNaN(+d.date) && d.value !== null)
    .sort((a, b) => a.date - b.date);

  if (!parsed.length) {
    d3.select(container).text("No publishable data for this selection.");
    return;
  }

  const width = 540;
  const height = 270;
  const margin = { top: 12, right: 20, bottom: 42, left: 52 };

  const svg = d3.select(container).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`);

  const x = d3.scaleTime()
    .domain(d3.extent(parsed, d => d.date))
    .range([margin.left, width - margin.right]);

  const maxValue = d3.max(parsed, d => d.value) || 1;
  const y = d3.scaleLinear()
    .domain([0, maxValue * 1.1])
    .nice()
    .range([height - margin.bottom, margin.top]);

  svg.append("g")
    .attr("class", "grid")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5).tickSize(-(width - margin.left - margin.right)).tickFormat(""));

  svg.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5));

  svg.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5));

  svg.append("path")
    .datum(parsed)
    .attr("fill", "none")
    .attr("stroke", "#2463a6")
    .attr("stroke-width", 2)
    .attr("d", d3.line()
      .x(d => x(d.date))
      .y(d => y(d.value)));

  const intervalRows = parsed.filter(d => d.lower !== null && d.upper !== null);
  if (intervalRows.length) {
    svg.append("path")
      .datum(intervalRows)
      .attr("fill", "none")
      .attr("stroke", "#c45a3c")
      .attr("stroke-dasharray", "5 4")
      .attr("d", d3.line().x(d => x(d.date)).y(d => y(d.lower)));
    svg.append("path")
      .datum(intervalRows)
      .attr("fill", "none")
      .attr("stroke", "#c45a3c")
      .attr("stroke-dasharray", "5 4")
      .attr("d", d3.line().x(d => x(d.date)).y(d => y(d.upper)));
  }

  svg.selectAll("circle")
    .data(parsed)
    .join("circle")
    .attr("cx", d => x(d.date))
    .attr("cy", d => y(d.value))
    .attr("r", 2.5)
    .attr("fill", "#2463a6")
    .on("mousemove", (event, d) =>
      showTooltip(event, `${d.date.toLocaleDateString()}: ${d.value} ${label}`))
    .on("mouseleave", hideTooltip);
}

function drawDistrictChart(rows) {
  clear("#district-chart");

  const totals = d3.rollups(
    rows.filter(d => numeric(d.published_case_count) !== null),
    values => d3.sum(values, d => numeric(d.published_case_count)),
    d => d.district
  )
    .map(([district, cases]) => ({ district, cases }))
    .sort((a, b) => b.cases - a.cases)
    .slice(0, 15);

  if (!totals.length) {
    d3.select("#district-chart").text("No publishable district totals.");
    return;
  }

  const width = 540;
  const rowHeight = 25;
  const height = Math.max(150, totals.length * rowHeight + 20);
  const margin = { top: 10, right: 40, bottom: 10, left: 135 };

  const svg = d3.select("#district-chart").append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`);

  const x = d3.scaleLinear()
    .domain([0, d3.max(totals, d => d.cases) || 1])
    .nice()
    .range([margin.left, width - margin.right]);

  const y = d3.scaleBand()
    .domain(totals.map(d => d.district))
    .range([margin.top, height - 10])
    .padding(0.2);

  svg.selectAll("text.district")
    .data(totals)
    .join("text")
    .attr("class", "district")
    .attr("x", margin.left - 8)
    .attr("y", d => y(d.district) + y.bandwidth() / 2)
    .attr("text-anchor", "end")
    .attr("dominant-baseline", "middle")
    .attr("font-size", 11)
    .text(d => d.district);

  svg.selectAll("rect")
    .data(totals)
    .join("rect")
    .attr("x", margin.left)
    .attr("y", d => y(d.district))
    .attr("width", d => x(d.cases) - margin.left)
    .attr("height", y.bandwidth())
    .attr("fill", "#39816c")
    .on("mousemove", (event, d) =>
      showTooltip(event, `${d.district}: ${d.cases} published cases`))
    .on("mouseleave", hideTooltip);

  svg.selectAll("text.value")
    .data(totals)
    .join("text")
    .attr("class", "value")
    .attr("x", d => x(d.cases) + 5)
    .attr("y", d => y(d.district) + y.bandwidth() / 2)
    .attr("dominant-baseline", "middle")
    .attr("font-size", 10)
    .text(d => d.cases);
}

function drawAlerts(rows) {
  clear("#alerts-table");

  const threshold = +thresholdSlider.property("value");
  const candidates = rows.filter(d =>
    d.is_outbreak_alert === true ||
    d.is_outbreak_alert === 1 ||
    d.is_outbreak_alert === "true"
  ).filter(d => {
    const score = numeric(d.alert_score);
    return score === null || score >= threshold;
  });

  const table = d3.select("#alerts-table").append("table");
  const columns = ["encounter_date", "district", "disease", "case_count", "baseline_mean"];

  table.append("thead").append("tr")
    .selectAll("th")
    .data(columns)
    .join("th")
    .text(d => d.replaceAll("_", " "));

  table.append("tbody")
    .selectAll("tr")
    .data(candidates.slice(0, 100))
    .join("tr")
    .selectAll("td")
    .data(row => columns.map(c => row[c] ?? "N/A"))
    .join("td")
    .text(d => d);

  if (!candidates.length) {
    d3.select("#alerts-table").text("No alerts for the current selection.");
  }
}

function drawResources(rows) {
  clear("#resource-chart");

  if (!rows.length) {
    d3.select("#resource-chart").text("No allocation data available.");
    return;
  }

  const keys = Object.keys(rows[0]);
  const districtKey = keys.find(k => k.toLowerCase() === "district");
  const valueKey = keys.find(k =>
    /allocation|resource|units/i.test(k) &&
    !/score|demand/i.test(k)
  );

  if (!districtKey || !valueKey) {
    d3.select("#resource-chart").text(
      `Allocation data loaded. Check the output schema: ${keys.join(", ")}`
    );
    return;
  }

  const budget = +budgetSlider.property("value");
  const equityFloor = +equitySlider.property("value");
  d3.select("#budget-value").text(budget);
  d3.select("#threshold-value").text(thresholdSlider.property("value"));
  d3.select("#equity-value").text(equityFloor.toFixed(2));
  const totalDemand = d3.sum(rows, d => numeric(d.forecast_case_demand) || 0) || 1;
  const filteredRows = rows.map(d => ({
    ...d,
    allocated_units: Math.max(
      equityFloor * budget / Math.max(rows.length, 1),
      budget * (numeric(d.forecast_case_demand) || 0) / totalDemand,
    ),
  })).filter(d =>
    districtFilter.property("value") === "ALL" ||
    d[districtKey] === districtFilter.property("value")
  );

  const top = filteredRows
    .map(d => ({ district: d[districtKey], value: numeric(d.allocated_units) || numeric(d[valueKey]) }))
    .filter(d => d.value !== null)
    .sort((a, b) => b.value - a.value)
    .slice(0, 20);

  const width = 900;
  const height = Math.max(100, top.length * 24 + 20);
  const margin = { top: 10, right: 40, bottom: 10, left: 140 };

  const svg = d3.select("#resource-chart").append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`);

  const x = d3.scaleLinear()
    .domain([0, d3.max(top, d => d.value) || 1])
    .nice()
    .range([margin.left, width - margin.right]);

  const y = d3.scaleBand()
    .domain(top.map(d => d.district))
    .range([margin.top, height - 10])
    .padding(0.2);

  svg.selectAll("text")
    .data(top)
    .join("text")
    .attr("x", margin.left - 8)
    .attr("y", d => y(d.district) + y.bandwidth() / 2)
    .attr("text-anchor", "end")
    .attr("dominant-baseline", "middle")
    .attr("font-size", 11)
    .text(d => d.district);

  svg.selectAll("rect")
    .data(top)
    .join("rect")
    .attr("x", margin.left)
    .attr("y", d => y(d.district))
    .attr("width", d => x(d.value) - margin.left)
    .attr("height", y.bandwidth())
    .attr("fill", "#b7792b")
    .on("mousemove", (event, d) =>
      showTooltip(event, `${d.district}: ${d.value} allocated`))
    .on("mouseleave", hideTooltip);
}

function drawCalendar(rows) {
  clear("#calendar-table");

  if (!rows.length) {
    d3.select("#calendar-table").text("No preparedness calendar available.");
    return;
  }

  const columns = Object.keys(rows[0]);
  const table = d3.select("#calendar-table").append("table");

  table.append("thead").append("tr")
    .selectAll("th")
    .data(columns)
    .join("th")
    .text(d => d.replaceAll("_", " "));

  table.append("tbody")
    .selectAll("tr")
    .data(rows.filter(d =>
      districtFilter.property("value") === "ALL" ||
      d.district === districtFilter.property("value")
    ).slice(0, 100))
    .join("tr")
    .selectAll("td")
    .data(row => columns.map(c => row[c] ?? "N/A"))
    .join("td")
    .text(d => d);
}

function render() {
  const caseRows = filtered(data.cases);
  const forecastRows = filtered(data.forecasts);
  const alertRows = filtered(data.alerts);

  const daily = d3.rollups(
    caseRows.filter(d => numeric(d.published_case_count) !== null),
    values => d3.sum(values, d => numeric(d.published_case_count)),
    d => d.date
  )
    .map(([date, cases]) => ({ date, cases }))
    .sort((a, b) => d3.ascending(a.date, b.date));

  drawLineChart("#trend-chart", daily, "date", "cases", "cases");
  drawDistrictChart(caseRows);
  drawAlerts(alertRows);
  drawLineChart(
    "#forecast-chart",
    forecastRows,
    "date",
    "forecast_cases",
    "predicted cases"
  );

  drawResources(data.resources);
  drawCalendar(data.calendar);
}

loadData().catch(error => {
  console.error(error);
  d3.select("#status").text(
    `Dashboard failed to load: ${error.message}. Check that the export files exist.`
  );
});

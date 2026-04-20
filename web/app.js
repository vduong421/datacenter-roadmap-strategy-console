const runButton = document.getElementById("runButton");
const runStatus = document.getElementById("runStatus");
const topPriority = document.getElementById("topPriority");
const programPosture = document.getElementById("programPosture");
const reviewMessage = document.getElementById("reviewMessage");
const initiativeList = document.getElementById("initiativeList");
const decisionNotes = document.getElementById("decisionNotes");
const initiativeTableBody = document.getElementById("initiativeTableBody");

function setStatus(text, mode) {
  runStatus.textContent = text;
  runStatus.className = `status-badge ${mode}`;
}

function bar(label, value, gradient = "background: linear-gradient(90deg, #0f5bd8, #4fc3c8);") {
  const width = Math.max(4, Math.min(100, value * 100));
  return `
    <div class="bar-row">
      <div class="mini">${label}: ${value}</div>
      <div class="bar"><span style="width:${width}%; ${gradient}"></span></div>
    </div>
  `;
}

function initiativeCard(item) {
  return `
    <article class="initiative">
      <div class="initiative-head">
        <div>
          <h3>${item.name}</h3>
          <div class="mini">Competitive pressure ${item.competitor_pressure} | Execution risk ${item.execution_risk}</div>
        </div>
        <div class="priority">${item.priority_score}</div>
      </div>
      ${bar("Demand", item.demand_score)}
      ${bar("Readiness", item.standards_readiness)}
      ${bar("Competitive Gap", item.competitive_gap, "background: linear-gradient(90deg, #d97706, #d14343);")}
      <div class="action">${item.action}</div>
    </article>
  `;
}

function noteCard(title, value, detail) {
  return `
    <article class="note-card">
      <div class="mini">${title}</div>
      <h3>${value}</h3>
      <div class="mini">${detail}</div>
    </article>
  `;
}

function buildNotes(initiatives) {
  const highestDemand = initiatives.reduce((best, item) => (item.demand_score > best.demand_score ? item : best), initiatives[0]);
  const highestRisk = initiatives.reduce((best, item) => (item.execution_risk > best.execution_risk ? item : best), initiatives[0]);
  const bestGap = initiatives.reduce((best, item) => (item.competitive_gap > best.competitive_gap ? item : best), initiatives[0]);

  decisionNotes.innerHTML = [
    noteCard("Strongest Demand Signal", highestDemand.name, `Demand score ${highestDemand.demand_score}`),
    noteCard("Highest Execution Risk", highestRisk.name, `Risk level ${highestRisk.execution_risk}`),
    noteCard("Largest Competitive Gap", bestGap.name, `Gap score ${bestGap.competitive_gap}`),
  ].join("");
}

function buildTable(initiatives) {
  initiativeTableBody.innerHTML = initiatives
    .map(
      (item) => `
        <tr>
          <td>${item.name}</td>
          <td>${item.priority_score}</td>
          <td>${item.demand_score}</td>
          <td>${item.standards_readiness}</td>
          <td>${item.execution_risk}</td>
          <td>${item.competitive_gap}</td>
          <td>${item.competitor_pressure}</td>
        </tr>
      `,
    )
    .join("");
}

async function refreshRoadmap() {
  setStatus("Running", "running");
  runButton.disabled = true;

  try {
    const response = await fetch("/api/run");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();

    topPriority.textContent = data.top_priority;
    programPosture.textContent = data.initiatives[0].priority_score >= 0.72 ? "Commit-ready portfolio" : "Prototype and validate";
    reviewMessage.textContent = data.quarterly_review_message;
    initiativeList.innerHTML = data.initiatives.map(initiativeCard).join("");
    buildNotes(data.initiatives);
    buildTable(data.initiatives);

    setStatus("Completed", "success");
  } catch (error) {
    setStatus(`Error: ${error.message}`, "error");
  } finally {
    runButton.disabled = false;
  }
}

runButton.addEventListener("click", refreshRoadmap);
refreshRoadmap();

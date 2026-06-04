const events = document.querySelector("#events");
const decision = document.querySelector("#decision");
const history = document.querySelector("#history");
const runDemo = document.querySelector("#runDemo");

const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/releases`);

ws.onmessage = (message) => {
  const payload = JSON.parse(message.data);
  const item = document.createElement("li");
  item.textContent = `${payload.event}: ${payload.data.name || payload.data.releaseId || "update"}`;
  events.prepend(item);
  if (payload.event === "assessment.completed") {
    decision.textContent = JSON.stringify(payload.data, null, 2);
    loadHistory();
  }
};

async function loadHistory() {
  const response = await fetch("/api/releases");
  const releases = await response.json();
  history.innerHTML = releases.map((release) => `
    <article class="release">
      <strong>${release.repository}</strong>
      <span>${release.targetEnvironment}</span>
      <span class="risk">${release.riskLevel} / ${release.riskScore}</span>
      <span>${release.decision}</span>
    </article>
  `).join("");
}

runDemo.addEventListener("click", async () => {
  const payload = {
    organization: "horizon-relevance",
    repository: "claims-api",
    branch: "main",
    commitSha: Math.random().toString(16).slice(2, 14),
    releaseVersion: "1.8.0",
    targetEnvironment: "PROD",
    requester: "rishi.sharma@horizonrelevance.com",
    artifact: {
      image: "426946630837.dkr.ecr.us-east-1.amazonaws.com/horizon/claims-api:1.8.0",
      digest: "sha256:demo",
      signatureStatus: "missing",
      provenanceStatus: "missing",
      sbomFormat: "CycloneDX"
    },
    dependencies: [
      { "name": "fastapi", "version": "0.95.0", "license": "MIT", "registry": "pypi", "maintainer": "tiangolo", "runtime": true },
      { "name": "requests", "version": "2.28.1", "license": "Apache-2.0", "registry": "pypi", "maintainer": "psf", "previousVersion": "2.31.0", "runtime": true },
      { "name": "lodash", "version": "4.17.15", "license": "MIT", "registry": "npm", "maintainer": "unknown", "previousVersion": "4.17.21", "runtime": true },
      { "name": "left-pad", "version": "1.3.0", "license": "UNKNOWN", "registry": "npm", "maintainer": "unknown", "runtime": false }
    ],
    changedFiles: ["Dockerfile", "requirements.txt", "k8s/deployment.yaml"]
  };
  const response = await fetch("/api/releases/assess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  decision.textContent = JSON.stringify(await response.json(), null, 2);
  loadHistory();
});

loadHistory();

const content = {
  strategy: {
    kicker: "Strategy / Prosecution",
    title: "Build protection around the invention—not merely a description of it.",
    body: "Invention intake, technical decomposition, claim architecture, drafting support, and prosecution strategy organized around business objectives and a durable evidentiary record.",
    items: ["High-tech hardware & software", "AI, computational, and data systems", "Pharmaceutical and life-science technologies"]
  },
  analysis: {
    kicker: "Prior art / Claims",
    title: "Make the decisive relationship between evidence and claim language visible.",
    body: "Structured prior-art research, limitation-level mapping, claim comparison, and source-supported analysis designed for efficient review and defensible decisions.",
    items: ["Novelty and obviousness analysis", "Claim charts and evidence matrices", "Competitive and portfolio landscapes"]
  },
  systems: {
    kicker: "Evidence / Workflow",
    title: "Turn repeatable legal and scientific work into inspectable systems.",
    body: "Purpose-built workflows preserve provenance, standardize review, and help teams move from raw material to a controlled, auditable work product.",
    items: ["Reproducible research pipelines", "Versioned claim and document workflows", "Human-reviewed AI assistance"]
  }
};

const header = document.querySelector("[data-header]");
const menu = document.querySelector(".menu-toggle");
menu?.addEventListener("click", () => {
  const open = menu.getAttribute("aria-expanded") === "true";
  menu.setAttribute("aria-expanded", String(!open));
  header.classList.toggle("menu-open", !open);
});

const tabs = [...document.querySelectorAll("[data-tab]")];
const panel = document.querySelector("#capability-panel");
tabs.forEach((tab) => tab.addEventListener("click", () => {
  tabs.forEach((item) => { item.classList.toggle("active", item === tab); item.setAttribute("aria-selected", String(item === tab)); });
  const selected = content[tab.dataset.tab];
  panel.animate([{opacity: .2, transform: "translateY(8px)"}, {opacity: 1, transform: "translateY(0)"}], {duration: 320, easing: "ease-out"});
  panel.innerHTML = `<p class="panel-kicker">${selected.kicker}</p><h3>${selected.title}</h3><p>${selected.body}</p><ul>${selected.items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}));

const dialog = document.querySelector("[data-dialog]");
document.querySelectorAll("[data-consultation]").forEach((button) => button.addEventListener("click", () => dialog?.showModal()));
document.querySelector("[data-dialog-close]")?.addEventListener("click", () => dialog.close());
dialog?.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });

document.querySelector("[data-copy-brief]")?.addEventListener("click", async () => {
  const brief = "LAYNE INTELLECTUAL PROPERTY — CONSULTATION BRIEF\n\nName / organization:\nPreferred contact:\nTechnology area:\nObjective:\nKnown deadlines:\nPublic, non-confidential summary:\n\nPlease do not include confidential information before an engagement is confirmed.";
  const status = document.querySelector("[data-copy-status]");
  try { await navigator.clipboard.writeText(brief); status.textContent = "Consultation brief copied to clipboard."; }
  catch { status.textContent = "Copy unavailable in this browser. Please copy the headings manually."; }
});

document.querySelector("[data-profile-toggle]")?.addEventListener("click", (event) => {
  const detail = document.querySelector("[data-profile-detail]");
  const expanded = event.currentTarget.getAttribute("aria-expanded") === "true";
  event.currentTarget.setAttribute("aria-expanded", String(!expanded));
  event.currentTarget.firstChild.textContent = expanded ? "View profile " : "Hide profile ";
  detail.hidden = expanded;
});

const search = document.querySelector("[data-professional-search]");
const filter = document.querySelector("[data-professional-filter]");
const cards = [...document.querySelectorAll(".professional-card")];
function filterProfessionals() {
  const query = search?.value.trim().toLowerCase() ?? "";
  const discipline = filter?.value ?? "all";
  let visible = 0;
  cards.forEach((card) => {
    const haystack = `${card.dataset.name} ${card.dataset.tags}`;
    const show = haystack.includes(query) && (discipline === "all" || card.dataset.tags.includes(discipline));
    card.hidden = !show;
    if (show) visible += 1;
  });
  const count = document.querySelector("[data-result-count]");
  const empty = document.querySelector("[data-empty-state]");
  if (count) count.textContent = String(visible);
  if (empty) empty.hidden = visible !== 0;
}
search?.addEventListener("input", filterProfessionals);
filter?.addEventListener("change", filterProfessionals);

const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
  if (entry.isIntersecting) { entry.target.classList.add("visible"); observer.unobserve(entry.target); }
}), {threshold: .12});
document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));

document.querySelectorAll("[data-year]").forEach((element) => { element.textContent = new Date().getFullYear(); });
window.addEventListener("scroll", () => header?.classList.toggle("scrolled", window.scrollY > 20), {passive: true});

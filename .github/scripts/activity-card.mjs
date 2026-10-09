#!/usr/bin/env node
// Generates the "Atividade no GitHub" cards (dark/light, wide/mobile) from the
// public contribution calendar. No dependencies: Node 20+ (global fetch).
//
//   GITHUB_TOKEN=... node activity-card.mjs --user LucasBatista37 --out ./out
//   node activity-card.mjs --from-json calendar.json --out ./out   (offline)
//
// The calendar is the same one GitHub shows on the profile (it includes
// private contributions only when the owner enables that profile setting).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith("--")) acc.push([cur.slice(2), arr[i + 1]?.startsWith("--") ? "true" : arr[i + 1] ?? "true"]);
    return acc;
  }, []),
);
const USER = args.user || process.env.GITHUB_REPOSITORY_OWNER;
const OUT = args.out || "out";
if (!/^[A-Za-z0-9-]{1,39}$/.test(USER || "") && !args["from-json"]) {
  console.error("invalid or missing --user");
  process.exit(1);
}

async function fetchCalendar() {
  if (args["from-json"]) return JSON.parse(readFileSync(args["from-json"], "utf8"));
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error("GITHUB_TOKEN is required");
  const query = `query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}`;
  for (let attempt = 1; attempt <= 3; attempt++) {
    const res = await fetch("https://api.github.com/graphql", {
      method: "POST",
      headers: { Authorization: `bearer ${token}`, "Content-Type": "application/json", "User-Agent": "profile-activity-card" },
      body: JSON.stringify({ query, variables: { login: USER } }),
      signal: AbortSignal.timeout(20000),
    }).catch((e) => ({ ok: false, status: 0, statusText: String(e) }));
    if (res.ok) {
      const body = await res.json();
      const weeks = body?.data?.user?.contributionsCollection?.contributionCalendar?.weeks;
      if (!Array.isArray(weeks)) throw new Error("unexpected GraphQL response: " + JSON.stringify(body.errors ?? body).slice(0, 300));
      return weeks.flatMap((w) => w.contributionDays).map((d) => ({ date: d.date, count: d.contributionCount }));
    }
    console.warn(`attempt ${attempt} failed: ${res.status} ${res.statusText}`);
    await new Promise((r) => setTimeout(r, 3000 * attempt));
  }
  throw new Error("GitHub API unavailable");
}

function stats(days) {
  days = days.filter((d) => /^\d{4}-\d{2}-\d{2}$/.test(d.date) && Number.isInteger(d.count) && d.count >= 0)
    .sort((a, b) => a.date.localeCompare(b.date));
  if (days.length < 7) throw new Error("calendar too short");
  const total = days.reduce((s, d) => s + d.count, 0);
  const active = days.filter((d) => d.count > 0).length;
  let longest = 0, run = 0;
  for (const d of days) { run = d.count > 0 ? run + 1 : 0; longest = Math.max(longest, run); }
  // current streak: today may still be empty, so start from yesterday in that case
  let i = days.length - 1;
  if (days[i].count === 0) i--;
  let current = 0;
  while (i >= 0 && days[i].count > 0) { current++; i--; }
  const weeks = [];
  for (let k = 0; k < days.length; k += 7) weeks.push({ start: days[k].date, sum: days.slice(k, k + 7).reduce((s, d) => s + d.count, 0) });
  const best = Math.max(...weeks.map((w) => w.sum));
  return { total, active, span: days.length, longest, current, best, weeks, last: days[days.length - 1].date };
}

const PAL = {
  dark: { bg0: "#070B1A", bg1: "#0D1330", surface: "#111936", border: "#27315E", text: "#EEF2FF", muted: "#A3AED0", faint: "#8691B8", violet: "#9B7BFF", cyan: "#2EE6F6", blue: "#4F8BFF", green: "#3DDC97", track: "#1A2350" },
  light: { bg0: "#FFFFFF", bg1: "#F2F4FF", surface: "#FFFFFF", border: "#D8DDF0", text: "#0B1230", muted: "#47517A", faint: "#5E6890", violet: "#5B32E0", cyan: "#0B7A8F", blue: "#2357D9", green: "#0B7A55", track: "#E6E9F7" },
};
const MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const fmt = (n) => n.toLocaleString("pt-BR");
const font = (f) => readFileSync(join(here, "fonts", f)).toString("base64");
const FONTS = `@font-face{font-family:'SG';font-weight:700;src:url(data:font/woff2;base64,${font("sg700.woff2")}) format('woff2')}`
  + `@font-face{font-family:'SG';font-weight:500;src:url(data:font/woff2;base64,${font("sg500.woff2")}) format('woff2')}`
  + `@font-face{font-family:'JBM';font-weight:500;src:url(data:font/woff2;base64,${font("jbm500.woff2")}) format('woff2')}`;

function render(s, theme, compact) {
  const p = PAL[theme];
  const W = compact ? 720 : 1200;
  const pad = compact ? 40 : 48;
  const [yy, mm, dd] = s.last.split("-");
  const kpis = [
    [fmt(s.total), "contribuições em 12 meses", p.violet],
    [`${fmt(s.current)} dias`, s.current > 0 && s.current >= s.longest ? "sequência atual · recorde" : `sequência atual · recorde ${s.longest}`, p.green],
    [`${fmt(s.active)} dias`, "com atividade no período", p.cyan],
    [fmt(s.best), "na semana mais ativa", p.blue],
  ];
  const cols = compact ? 2 : 4;
  const gap = 16;
  const kw = (W - pad * 2 - gap * (cols - 1)) / cols;
  const kh = compact ? 118 : 104;
  const top = pad + (compact ? 92 : 64);
  let out = "";
  kpis.forEach(([v, l, c], i) => {
    const x = pad + (i % cols) * (kw + gap);
    const y = top + Math.floor(i / cols) * (kh + gap);
    out += `<rect x="${x}" y="${y}" width="${kw}" height="${kh}" rx="14" fill="${p.surface}" stroke="${p.border}"/>`
      + `<rect x="${x}" y="${y + 18}" width="3" height="${kh - 36}" rx="1.5" fill="${c}"/>`
      + `<text x="${x + 22}" y="${y + (compact ? 58 : 50)}" class="sg" font-weight="700" font-size="${compact ? 40 : 34}" fill="${p.text}">${v}</text>`
      + `<text x="${x + 22}" y="${y + (compact ? 92 : 80)}" class="jbm" font-size="${compact ? 18 : 14}" fill="${p.muted}">${l}</text>`;
  });
  const rows = Math.ceil(kpis.length / cols);
  const chartTop = top + rows * (kh + gap) + 18;
  const chartH = compact ? 170 : 130;
  const n = s.weeks.length;
  const bw = (W - pad * 2) / n;
  const max = Math.max(...s.weeks.map((w) => w.sum), 1);
  let bars = "", labels = "", lastMonth = -1;
  s.weeks.forEach((w, i) => {
    const h = Math.max(2, (w.sum / max) * chartH);
    const x = pad + i * bw + bw * 0.15;
    bars += `<rect x="${x.toFixed(1)}" y="${(chartTop + chartH - h).toFixed(1)}" width="${(bw * 0.7).toFixed(1)}" height="${h.toFixed(1)}" rx="${Math.min(3, bw * 0.3).toFixed(1)}" fill="url(#bar)" class="b" style="animation-delay:${(i * 0.012).toFixed(3)}s"><title>semana de ${w.start}: ${w.sum}</title></rect>`;
    const m = Number(w.start.slice(5, 7)) - 1;
    if (m !== lastMonth && i < n - 2) {
      if (lastMonth !== -1 && (!compact || m % 2 === 0)) labels += `<text x="${(pad + i * bw).toFixed(1)}" y="${chartTop + chartH + (compact ? 30 : 24)}" class="jbm" font-size="${compact ? 16 : 13}" fill="${p.faint}">${MONTHS[m]}</text>`;
      lastMonth = m;
    }
  });
  const H = chartTop + chartH + (compact ? 44 : 38) + pad - 12;
  const title = "Atividade no GitHub";
  const sub = `${compact ? "" : "contribuições por semana · "}atualizado em ${dd}/${mm}/${yy}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="t d">
<title id="t">${title}</title>
<desc id="d">Nos últimos 12 meses: ${fmt(s.total)} contribuições, sequência atual de ${s.current} dias (recorde do período: ${s.longest}), ${s.active} de ${s.span} dias com atividade e ${s.best} contribuições na semana mais ativa. Dados do calendário público de contribuições, atualizado em ${dd}/${mm}/${yy}.</desc>
<defs><style>${FONTS}
.sg{font-family:'SG',ui-sans-serif,system-ui,sans-serif}.jbm{font-family:'JBM',ui-monospace,Menlo,monospace;font-weight:500}
.b{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@media (prefers-reduced-motion:reduce){.b{animation:none}}
</style>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${p.bg0}"/><stop offset="1" stop-color="${p.bg1}"/></linearGradient>
<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="${p.blue}"/><stop offset="1" stop-color="${p.violet}"/></linearGradient></defs>
<rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="24" fill="url(#bg)" stroke="${p.border}" stroke-width="1.5"/>
<text x="${pad}" y="${pad + (compact ? 36 : 30)}" class="sg" font-weight="700" font-size="${compact ? 38 : 30}" fill="${p.text}">${title}</text>
<text x="${compact ? pad : W - pad}" y="${pad + (compact ? 70 : 30)}" class="jbm" font-size="${compact ? 17 : 14}" text-anchor="${compact ? "start" : "end"}" fill="${p.faint}">${sub}</text>
${out}
<line x1="${pad}" x2="${W - pad}" y1="${chartTop + chartH + 0.5}" y2="${chartTop + chartH + 0.5}" stroke="${p.border}"/>
${bars}${labels}
</svg>`;
}

const days = await fetchCalendar();
const s = stats(days);
mkdirSync(OUT, { recursive: true });
for (const theme of ["dark", "light"]) {
  writeFileSync(join(OUT, `activity-${theme}.svg`), render(s, theme, false));
  writeFileSync(join(OUT, `activity-mobile-${theme}.svg`), render(s, theme, true));
}
console.log(JSON.stringify({ total: s.total, current: s.current, longest: s.longest, active: s.active, last: s.last }));

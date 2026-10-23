// Generates a turbo Pac-Man game from the contribution graph.
// usage: node scripts/pacman.mjs <username> <out.svg> <theme> [platform]
import fs from 'fs';
import { ArcadeRenderer } from 'pacman-contribution-graph';

const [user, out, theme = 'github-dark', platform = 'github'] = process.argv.slice(2);
const SPEED = 4; // >1 = faster

const crazy = (svg) => {
  // turbo: speed up every timeline
  svg = svg.replace(/dur="(\d+(?:\.\d+)?)ms"/g, (_, d) => `dur="${Math.round(d / SPEED)}ms"`);
  const m = svg.match(/<svg[^>]*width="(\d+)"[^>]*height="(\d+)"/);
  const W = m ? +m[1] : 1166, H = m ? +m[2] : 184;
  const fx = `<defs>
<filter id="neon" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity="0.35"/></pattern>
<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>
@keyframes hue{0%{filter:url(#neon) hue-rotate(0deg) saturate(2) brightness(1.1)}50%{filter:url(#neon) hue-rotate(180deg) saturate(2.6) brightness(1.4)}100%{filter:url(#neon) hue-rotate(360deg) saturate(2) brightness(1.1)}}
@keyframes shake{0%,100%{transform:translate(0,0)}10%{transform:translate(-2px,1px)}20%{transform:translate(2px,-1px)}30%{transform:translate(-1px,2px)}40%{transform:translate(1px,-2px)}50%{transform:translate(-2px,0)}60%{transform:translate(2px,1px)}70%{transform:translate(0,-1px)}80%{transform:translate(-1px,1px)}90%{transform:translate(1px,0)}}
@keyframes flick{0%,100%{opacity:.25}7%{opacity:.6}9%{opacity:.15}50%{opacity:.3}52%{opacity:.7}54%{opacity:.2}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
.crazy{animation:hue 2.2s linear infinite}
.shake{animation:shake .35s steps(2) infinite}
.scan{animation:flick 1.3s steps(6) infinite}
.blink{animation:blink .6s steps(1) infinite}
</style>`;
  const overlay = `<rect width="${W}" height="${H}" fill="url(#scan)" class="scan" pointer-events="none"/>
<rect x="-300" y="0" width="300" height="${H}" fill="url(#sweep)" pointer-events="none"><animate attributeName="x" values="-300;${W}" dur="1.6s" repeatCount="indefinite"/></rect>
<text x="${W - 8}" y="${H - 6}" text-anchor="end" font-family="monospace" font-size="11" font-weight="700" fill="#FBBF24" class="blink">TURBO x${SPEED} · INSERT COIN</text>`;
  svg = svg.replace(/(<svg[^>]*>)/, `$1${fx}<g class="shake"><g class="crazy">`)
           .replace(/<\/svg>\s*$/, `</g></g>${overlay}</svg>`);
  return svg;
};

const r = new ArcadeRenderer({
  game: 'pacman',
  platform,
  username: user,
  gameTheme: theme,
  scenario: 'random',
  playerStyle: 'aggressive',
  githubSettings: { accessToken: process.env.GITHUB_TOKEN || '' },
  svgCallback: (svg) => { fs.writeFileSync(out, crazy(svg)); console.log('wrote', out); },
});
await r.start();

// Generates a turbo Pac-Man game from the contribution graph.
// usage: node scripts/pacman.mjs <username> <out.svg> <theme> [platform]
import fs from 'fs';
import { ArcadeRenderer } from 'pacman-contribution-graph';

const [user, out, theme = 'github-dark', platform = 'github'] = process.argv.slice(2);
const SPEED = 2.5; // >1 = faster

const crazy = (svg) => {
  // speed up every timeline
  svg = svg.replace(/dur="(\d+(?:\.\d+)?)ms"/g, (_, d) => `dur="${Math.round(d / SPEED)}ms"`);
  // neon glow + colour cycling
  const style = `<defs><filter id="neon" x="-20%" y="-20%" width="140%" height="140%">
<feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>@keyframes hue{from{filter:url(#neon) hue-rotate(0deg) saturate(1.6)}to{filter:url(#neon) hue-rotate(360deg) saturate(1.6)}}
.crazy{animation:hue 5s linear infinite}</style>`;
  svg = svg.replace(/(<svg[^>]*>)/, `$1${style}<g class="crazy">`).replace(/<\/svg>\s*$/, '</g></svg>');
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

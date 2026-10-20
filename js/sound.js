/* «Мари филворд» sounds: tiny WebAudio synth (no audio files, no licensing issues).
 * Muted: by the 🔊 toggle (S.sound), during ads / Yandex game_api_pause / Android onPause (Platform.audio), and while the tab is hidden. */
(function () {
  let ctx = null, on = true; const block = new Set();
  const muted = () => !on || block.size > 0;
  function ac() {
    if (!ctx) { try { ctx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} }
    if (ctx && ctx.state === 'suspended' && !block.size) { try { ctx.resume(); } catch (e) {} }
    return ctx;
  }
  function tone(f, d, type, vol, delay, f2) {
    if (muted()) return; const c = ac(); if (!c || c.state !== 'running' && c.state !== 'suspended') return;
    const t = c.currentTime + (delay || 0), o = c.createOscillator(), g = c.createGain();
    o.type = type || 'sine'; o.frequency.setValueAtTime(f, t); if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + d);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol || .1, t + .012); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    o.connect(g); g.connect(c.destination); o.start(t); o.stop(t + d + .05);
  }
  const PENTA = [392, 440, 523, 587, 659, 784, 880, 1047, 1175, 1319];   // pentatonic, like the kusle
  function apply() { if (!ctx) return; try { block.size ? ctx.suspend() : ctx.resume(); } catch (e) {} }
  window.Sound = {
    set enabled(v) { on = !!v; }, get enabled() { return on; }, get muted() { return muted(); },
    unlock: ac,
    letter(i) { tone(PENTA[Math.min(i, PENTA.length - 1)], .09, 'triangle', .07); },               // each selected letter, rising
    word() { [659, 784, 1047].forEach((f, i) => tone(f, .22, 'triangle', .09, i * .07)); },         // planned word found
    bonus() { [1319, 1568, 2093].forEach((f, i) => tone(f, .16, 'sine', .06, i * .06)); },          // bonus word sparkle
    wrong() { tone(220, .2, 'sawtooth', .04, 0, 150); },                                          // not a word
    coin() { tone(1568, .08, 'square', .035); tone(2093, .14, 'square', .035, .07); },
    win() { [523, 659, 784, 1047, 1319].forEach((f, i) => tone(f, .32, 'triangle', .1, i * .1)); tone(784, .6, 'sine', .05, .5); },
    hint() { tone(880, .1, 'sine', .06); tone(1175, .16, 'sine', .06, .08); },
    click() { tone(660, .04, 'square', .025); },
    _blocked: block,
  };
  if (window.Platform && Platform.audio) Platform.audio.on((ok, why) => { ok ? block.delete(why) : block.add(why); apply(); });
  document.addEventListener('visibilitychange', () => { document.hidden ? block.add('hidden') : block.delete('hidden'); apply(); });
  window.addEventListener('pagehide', () => { block.add('hidden'); apply(); });
  window.addEventListener('pageshow', () => { if (!document.hidden) { block.delete('hidden'); apply(); } });
})();

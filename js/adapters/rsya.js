/* Web ads via Рекламная сеть Яндекса (Yandex.RTB web blocks). Loaded ONLY in the public web build (tools/build_release.py web),
 * never in the Yandex Games zip or Android (they use their own SDKs). IDs: window.FW_CONFIG.rsya (js/config.js); empty ID = off.
 * - banner: floorAd (touch / desktop), rendered once after the tutorial
 * - interstitial: fullscreen block; same cadence as the apps (every 3rd win, ≥150 s, decided in app.js)
 * - «rewarded»: RSYA web has no rewarded format → the fullscreen block; the hint is given after the ad is CLOSED
 * Graceful fallback: no IDs / ad blocker / no fill / error / 8 s timeout → available() false or the promise resolves without a reward;
 * the game never waits forever. Sound is muted while a fullscreen ad is on screen (Platform.audio.suspend('ad')). */
(function () {
  const C = (window.FW_CONFIG && window.FW_CONFIG.rsya) || {};
  const touch = (() => { try { return matchMedia('(pointer:coarse)').matches || /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent); } catch (e) { return false; } })();
  const plat = touch ? 'touch' : 'desktop';
  const floorId = touch ? C.floorTouch : C.floorDesktop, fullId = touch ? C.fullscreenTouch : C.fullscreenDesktop;
  if (!floorId && !fullId) return;                       // nothing configured → plain web, no loader request at all
  let loaded = false, failed = false;
  window.yaContextCb = window.yaContextCb || [];
  const s = document.createElement('script'); s.src = 'https://yandex.ru/ads/system/context.js'; s.async = true;
  s.onload = () => { loaded = true; }; s.onerror = () => { failed = true; };   // blocked by an ad blocker → failed
  document.head.appendChild(s);
  const ready = () => loaded && !failed && window.Ya && Ya.Context && Ya.Context.AdvManager;
  let bannerDone = false, busy = false;
  function fullscreen() {   // → Promise<boolean shownAndClosed>
    return new Promise(res => {
      if (!fullId || busy || !ready()) return res(false);
      busy = true; let shown = false, done = false;
      const fin = ok => { if (done) return; done = true; busy = false; clearTimeout(t); Platform.audio.resume('ad'); res(ok); };
      const t = setTimeout(() => fin(false), 8000);      // never rendered (no fill, blocked inside)
      Platform.audio.suspend('ad');
      try {
        Ya.Context.AdvManager.render({ blockId: fullId, type: 'fullscreen', platform: plat,
          onRender: () => { shown = true; clearTimeout(t); },
          onClose: () => fin(true),
          onError: () => fin(false) });
      } catch (e) { fin(false); }
    });
  }
  Platform.use({
    name: 'web-rsya',
    ads: {
      rewardedAvailable() { return !!fullId && ready() && !busy; },
      showRewarded() { return fullscreen(); },            // reward only after the ad was shown and closed
      interstitialAvailable() { return !!fullId && ready() && !busy; },
      async showInterstitial() { await fullscreen(); },
      bannerAvailable() { return !!floorId && !failed; },
      showBanner() {
        if (bannerDone || !floorId) return; bannerDone = true;
        window.yaContextCb.push(() => { try { Ya.Context.AdvManager.render({ blockId: floorId, type: 'floorAd', platform: plat }); } catch (e) {} });
      },
      hideBanner() {},                                    // floorAd has its own close button
    },
  });
})();

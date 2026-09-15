/* ==========================================================================
   Endüstri Yatırım Gündemi — Öne çıkan (pop-up) reklam
   Tek dosya: hem CSS'i hem modalı kendisi oluşturur.
   Kullanım: her sayfada </body>'den önce tek satır:
     <script src="/reklam-popup.js" defer></script>
   Reklamı değiştirmek: /images/reklam-popup.png dosyasını değiştir (yeni reklam
   gelince aynı ölçüde bir görsel koyman yeterli). Ayarlar aşağıda CFG'de.
   ========================================================================== */
(function () {
  var CFG = {
    img: "/images/reklam-popup.png",                 // reklam görseli (site kökünden)
    mail: "info@endustriyatirim.com.tr",
    subject: "Reklam Talebi - Endüstri Yatırım Gündemi",
    delay: 800,                                       // açılma gecikmesi (ms)
    once: "session"                                   // "session" | "always" | "daily"
  };

  // --- aynı oturumda/günde tekrar açmama kontrolü ---
  var KEY = "ey_ad_popup_seen";
  function alreadySeen() {
    try {
      if (CFG.once === "always") return false;
      if (CFG.once === "session") return sessionStorage.getItem(KEY) === "1";
      if (CFG.once === "daily")   return localStorage.getItem(KEY) === new Date().toDateString();
    } catch (e) {}
    return false;
  }
  function markSeen() {
    try {
      if (CFG.once === "session") sessionStorage.setItem(KEY, "1");
      if (CFG.once === "daily")   localStorage.setItem(KEY, new Date().toDateString());
    } catch (e) {}
  }

  // --- CSS enjeksiyonu ---
  var css = ''
    + '.adm-overlay{position:fixed;inset:0;z-index:99999;background:rgba(8,16,28,.62);'
    + '-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px);display:flex;align-items:center;'
    + 'justify-content:center;padding:20px;opacity:0;visibility:hidden;transition:opacity .25s,visibility .25s}'
    + '.adm-overlay.open{opacity:1;visibility:visible}'
    + '.adm-box{position:relative;background:#fff;border-radius:16px;overflow:hidden;width:min(600px,94vw);'
    + 'box-shadow:0 30px 80px rgba(0,0,0,.45);transform:translateY(12px) scale(.98);transition:transform .25s}'
    + '.adm-overlay.open .adm-box{transform:none}'
    + '.adm-media{display:block}.adm-media img{display:block;width:100%;height:auto}'
    + '.adm-bar{display:flex;justify-content:flex-end;align-items:center;gap:10px;padding:12px 16px;'
    + 'border-top:1px solid #eee;background:#fafafa}'
    + '.adm-note{margin-right:auto;font:600 12px/1 system-ui,sans-serif;color:#9aa4ad;letter-spacing:.04em}'
    + '.adm-close{appearance:none;border:0;cursor:pointer;background:#22344e;color:#fff;'
    + 'font:600 15px/1 system-ui,sans-serif;padding:11px 22px;border-radius:8px;transition:background .15s}'
    + '.adm-close:hover{background:#0e2038}'
    + '.adm-x{position:absolute;top:10px;right:12px;z-index:2;width:34px;height:34px;border-radius:50%;'
    + 'border:0;cursor:pointer;background:rgba(255,255,255,.9);color:#22344e;font-size:20px;line-height:34px;'
    + 'box-shadow:0 2px 8px rgba(0,0,0,.15)}.adm-x:hover{background:#fff}';

  function init() {
    if (alreadySeen()) return;

    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    var mailto = "mailto:" + CFG.mail + "?subject=" + encodeURIComponent(CFG.subject);
    var overlay = document.createElement("div");
    overlay.className = "adm-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Reklam");
    overlay.innerHTML =
        '<div class="adm-box">'
      +   '<button class="adm-x" data-adm-close aria-label="Kapat">&times;</button>'
      +   '<a class="adm-media" href="' + mailto + '">'
      +     '<img src="' + CFG.img + '" alt="Bu alana reklam verebilirsiniz — ' + CFG.mail + '"/>'
      +   '</a>'
      +   '<div class="adm-bar"><span class="adm-note">REKLAM</span>'
      +     '<button class="adm-close" data-adm-close>Kapat</button></div>'
      + '</div>';
    document.body.appendChild(overlay);

    function open()  { overlay.classList.add("open");  document.body.style.overflow = "hidden"; }
    function close() { overlay.classList.remove("open"); document.body.style.overflow = ""; markSeen(); }

    setTimeout(open, CFG.delay);

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay || (e.target.closest && e.target.closest("[data-adm-close]"))) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("open")) close();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

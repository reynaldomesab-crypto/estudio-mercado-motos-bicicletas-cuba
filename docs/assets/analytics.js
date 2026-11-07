/* Carga GoatCounter solo si hay código configurado. Sin cookies, 3 KB. */
(function () {
  var cfg = window.SITE_CONFIG || {};
  if (!cfg.goatcounter) return;
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://gc.zgo.at/count.js";
  s.setAttribute("data-goatcounter", "https://" + cfg.goatcounter + ".goatcounter.com/count");
  document.head.appendChild(s);
})();

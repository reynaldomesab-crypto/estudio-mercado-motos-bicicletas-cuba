/* Calculadora de precio de referencia + compartir. Sin dependencias. */
(function () {
  "use strict";

  function num(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
  function usd(n) { return "$" + num(n); }

  var D = window.PRECIOS || null;
  var state = { mode: "tipos", id: null };
  var trackedUse = false;

  function track(path) {
    try {
      if (window.goatcounter && window.goatcounter.count) {
        window.goatcounter.count({ path: path, title: path, event: true });
      }
    } catch (e) {}
  }

  function list() {
    if (!D) return [];
    if (state.mode === "marcas") return D.marcas;
    if (state.mode === "zonas") return D.zonas;
    return D.tipos;
  }

  function groupById(id) {
    var all = (D ? D.tipos.concat(D.marcas, D.zonas) : []);
    for (var i = 0; i < all.length; i++) if (all[i].id === id) return all[i];
    return null;
  }

  function percentile(g, v) {
    if (v <= 0) return null;
    if (v <= g.p10) return 0.1 * (v / g.p10);
    var qs = [[0.1, g.p10], [0.25, g.p25], [0.5, g.p50], [0.75, g.p75], [0.9, g.p90]];
    for (var i = 0; i < qs.length - 1; i++) {
      if (v <= qs[i + 1][1]) {
        var a = qs[i], b = qs[i + 1];
        var t = (v - a[1]) / Math.max(1, b[1] - a[1]);
        return a[0] + t * (b[0] - a[0]);
      }
    }
    return 0.9 + 0.1 * Math.min(1, (v - g.p90) / Math.max(1, g.p90 * 0.6));
  }

  function verdict(g, v) {
    var p = percentile(g, v);
    if (v <= g.p10) return { cls: "v-low", text: "Está en el 10% más barato del grupo. Revisa estado, papeles y batería antes de asumir que es una ganga." };
    if (v < g.p25) return { cls: "v-low", text: "Por debajo del rango central: está entre el 10% y el 25% más barato de su grupo." };
    if (v <= g.p75) return { cls: "v-mid", text: "Dentro del rango central del mercado para ese grupo." };
    if (v <= g.p90) return { cls: "v-high", text: "Por encima del rango central: está entre el 75% y el 90% más caro." };
    return { cls: "v-high", text: "En el 10% más caro del grupo. Necesita una razón visible que lo justifique (estado, autonomía, garantía)." };
  }

  function render() {
    var sel = document.getElementById("grupo");
    var box = document.getElementById("resultado");
    if (!sel || !box) return;

    var items = list();
    if (!items.length) { box.innerHTML = "<p>No hay datos suficientes.</p>"; return; }
    if (!state.id || !groupById(state.id) || items.indexOf(groupById(state.id)) === -1) {
      state.id = items[0].id;
      sel.value = state.id;
    }
    var g = groupById(state.id);
    var priceInput = document.getElementById("precio");
    var v = priceInput ? parseFloat(priceInput.value) : NaN;

    var html = '<div class="med">' + usd(g.p50) + ' <small>mediana</small></div>' +
      '<div class="range">Rango habitual (p10–p90): <strong>' + usd(g.p10) + ' – ' + usd(g.p90) + '</strong></div>' +
      '<div class="range muted">' + num(g.n) + ' anuncios con precio declarado · ' + g.nombre + '</div>';

    if (!isNaN(v) && v > 0) {
      var p = percentile(g, v);
      var vd = verdict(g, v);
      html += '<div class="verdict show ' + vd.cls + '">Tu precio de ' + usd(v) + ' está en el percentil ' +
        Math.round(Math.min(99, Math.max(1, p * 100))) + '. ' + vd.text + '</div>';
      if (!trackedUse) { trackedUse = true; track("calc-use"); }
    }
    box.innerHTML = html;
  }

  function fillSelect() {
    var sel = document.getElementById("grupo");
    if (!sel) return;
    var items = list();
    sel.innerHTML = items.map(function (g) {
      return '<option value="' + g.id + '">' + g.nombre + " (" + num(g.n) + ")</option>";
    }).join("");
    sel.value = state.id || (items[0] && items[0].id);
  }

  function setMode(mode) {
    state.mode = mode;
    state.id = null;
    document.querySelectorAll(".mode").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.mode === mode ? "true" : "false");
    });
    fillSelect();
    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!D) return;
    var box = document.getElementById("resultado");
    if (box) {
      fillSelect();
      setMode("tipos");
      var sel = document.getElementById("grupo");
      if (sel) sel.addEventListener("change", function () { state.id = sel.value; render(); });
      var price = document.getElementById("precio");
      if (price) price.addEventListener("input", render);
      document.querySelectorAll(".mode").forEach(function (b) {
        b.addEventListener("click", function () { setMode(b.dataset.mode); });
      });
    }
  });

  /* Compartir */
  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return Promise.reject();
  }
  document.addEventListener("click", function (e) {
    var link = e.target.closest("a");
    if (link && link.getAttribute("href")) {
      var href = link.getAttribute("href");
      if (href.indexOf("checklist.pdf") > -1) track("download-checklist");
      else if (link.classList.contains("btn")) track("cta:" + href.split("?")[0]);
    }
    var btn = e.target.closest("[data-share]");
    if (!btn) return;
    track("share-click");
    e.preventDefault();
    var url = btn.dataset.url || location.href;
    var title = btn.dataset.title || document.title;
    if (navigator.share) {
      navigator.share({ title: title, text: btn.dataset.text || title, url: url }).catch(function () {});
      return;
    }
    copy(url).then(function () {
      var old = btn.textContent;
      btn.textContent = "Enlace copiado";
      setTimeout(function () { btn.textContent = old; }, 1800);
    }).catch(function () {
      window.prompt("Copia el enlace:", url);
    });
  });
})();

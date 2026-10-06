/* Arshad Siddique · Independent Bitget Affiliate — site script (no dependencies) */
(function () {
  "use strict";

  /* ---------- Site configuration ----------
     Social links stay hidden until a URL is filled in. Do not add URLs that
     have not been confirmed by Arshad. */
  var CONFIG = {
    social: {
      Instagram: "",
      Facebook: "",
      "X (Twitter)": "",
      YouTube: "",
      Telegram: "",
      LinkedIn: "",
      TikTok: ""
    }
  };

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Analytics hooks ----------
     Events go to window.dataLayer only if an analytics tool has created it
     (after consent). A DOM event is always dispatched for custom listeners. */
  function track(name, detail) {
    var payload = Object.assign({ event: name }, detail || {});
    if (Array.isArray(window.dataLayer)) window.dataLayer.push(payload);
    document.dispatchEvent(new CustomEvent("site:track", { detail: payload }));
  }
  window.siteTrack = track;

  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-track]");
    if (el) track(el.getAttribute("data-track"), { location: el.getAttribute("data-track-loc") || "" });
  });

  /* ---------- Header ---------- */
  var header = document.querySelector(".site-header");
  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 8);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  function closeMenu() {
    if (!toggle || !nav) return;
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
    nav.classList.remove("is-open");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      toggle.setAttribute("aria-label", open ? "Open menu" : "Close menu");
      nav.classList.toggle("is-open", !open);
      if (!open) {
        var first = nav.querySelector("a");
        if (first) first.focus();
      }
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        closeMenu();
        toggle.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1080) closeMenu();
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Feature cards: pointer glow + expandable details ---------- */
  document.querySelectorAll(".feature").forEach(function (card) {
    card.addEventListener("pointermove", function (e) {
      var r = card.getBoundingClientRect();
      card.style.setProperty("--mx", e.clientX - r.left + "px");
      card.style.setProperty("--my", e.clientY - r.top + "px");
    });
  });
  document.querySelectorAll(".feature-detail a").forEach(function (a) { a.tabIndex = -1; });
  document.querySelectorAll(".feature-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      btn.querySelector(".t").textContent = open ? "Show details" : "Hide details";
      if (panel) {
        panel.classList.toggle("is-open", !open);
        panel.setAttribute("aria-hidden", String(open));
        panel.querySelectorAll("a, button").forEach(function (a) { a.tabIndex = open ? -1 : 0; });
      }
    });
  });

  /* ---------- Copy referral code ---------- */
  var toast = document.createElement("div");
  toast.className = "toast";
  toast.setAttribute("role", "status");
  toast.setAttribute("aria-live", "polite");
  document.body.appendChild(toast);
  var toastTimer;
  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove("is-visible"); }, 2200);
  }
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var label = btn.querySelector(".t") || btn;
      var original = label.textContent;
      function done(ok) {
        if (ok) {
          btn.classList.add("is-copied");
          label.textContent = "Copied";
          showToast("Referral code “" + text + "” copied");
          track("referral_code_copy");
        } else {
          showToast("Referral code: " + text);
        }
        setTimeout(function () {
          btn.classList.remove("is-copied");
          label.textContent = original;
        }, 2000);
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallbackCopy(text)); });
      } else {
        done(fallbackCopy(text));
      }
    });
  });

  /* ---------- QR view event ---------- */
  var qrs = document.querySelectorAll("[data-qr]");
  if (qrs.length && "IntersectionObserver" in window) {
    var qio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          track("qr_view", { location: entry.target.getAttribute("data-qr") });
          qio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    qrs.forEach(function (q) { qio.observe(q); });
  }

  /* ---------- Journey selector (tabs) ---------- */
  var tablist = document.querySelector("[data-selector]");
  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        var p = document.getElementById(t.getAttribute("aria-controls"));
        if (p) {
          p.hidden = !on;
          if (on) {
            p.classList.remove("is-entering");
            void p.offsetWidth;
            p.classList.add("is-entering");
          }
        }
      });
      if (focus) tab.focus();
      var ev = tab.getAttribute("data-interest");
      if (ev) track(ev, { location: "journey_selector" });
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowDown" || e.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowUp" || e.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") next = tabs[0];
        if (e.key === "End") next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
  }

  /* ---------- Wallet card tilt ---------- */
  var stage = document.querySelector(".card-stage");
  var wcard = stage && stage.querySelector(".wcard");
  if (stage && wcard && !reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    stage.addEventListener("pointermove", function (e) {
      var r = stage.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5;
      var y = (e.clientY - r.top) / r.height - 0.5;
      wcard.style.setProperty("--ry", x * 22 + "deg");
      wcard.style.setProperty("--rx", -y * 16 + "deg");
      wcard.style.setProperty("--shine", x * 120 + "%");
    });
    stage.addEventListener("pointerleave", function () {
      wcard.style.removeProperty("--ry");
      wcard.style.removeProperty("--rx");
      wcard.style.removeProperty("--shine");
    });
  }

  /* ---------- Subtle hero parallax ---------- */
  var par = document.querySelector("[data-parallax]");
  if (par && !reduceMotion) {
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = Math.min(window.scrollY, 700);
        par.style.transform = "translate3d(0," + y * 0.06 + "px,0)";
        ticking = false;
      });
    }, { passive: true });
  }

  /* ---------- Social links (only those configured) ---------- */
  document.querySelectorAll("[data-socials]").forEach(function (wrap) {
    Object.keys(CONFIG.social).forEach(function (name) {
      var url = CONFIG.social[name];
      if (!/^https:\/\//.test(url)) return;
      var a = document.createElement("a");
      a.href = url;
      a.className = "btn btn--sm ext";
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = name;
      wrap.appendChild(a);
    });
  });

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();

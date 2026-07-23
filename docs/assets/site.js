(() => {
  const root = document.documentElement;
  const header = document.querySelector("[data-site-header]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const navigation = document.querySelector("[data-site-nav]");

  root.classList.add("js");

  const closeNavigation = () => {
    if (!toggle || !navigation) return;
    toggle.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
  };

  if (toggle && navigation) {
    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      navigation.classList.toggle("is-open", !isOpen);
    });

    navigation.addEventListener("click", (event) => {
      if (event.target.closest("a")) closeNavigation();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeNavigation();
        toggle.focus();
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 980) closeNavigation();
    });
  }

  const updateHeader = () => {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 12);
  };

  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });

  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const targetId = button.getAttribute("data-copy-target");
      const target = targetId ? document.getElementById(targetId) : null;
      if (!target) return;

      const originalLabel = button.textContent;
      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        button.textContent = "已复制";
      } catch {
        button.textContent = "复制失败";
      }
      window.setTimeout(() => {
        button.textContent = originalLabel;
      }, 1600);
    });
  });

  document.querySelectorAll("[data-current-year]").forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });
})();

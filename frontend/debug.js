(() => {
  const el = document.elementFromPoint(217, 62);
  const zIndex = window.getComputedStyle(el).zIndex;
  
  let blockingEl = el;
  let allOverlays = document.querySelectorAll('.sidebar-overlay, .modal-overlay, .toast, .app, .main-panel, body');
  
  const report = {
    topElement: {
      tagName: el.tagName,
      id: el.id,
      className: el.className,
      zIndex: zIndex
    },
    overlays: Array.from(allOverlays).map(o => ({
      id: o.id,
      className: o.className,
      display: window.getComputedStyle(o).display,
      pointerEvents: window.getComputedStyle(o).pointerEvents,
      zIndex: window.getComputedStyle(o).zIndex
    }))
  };

  document.body.innerHTML = '<pre id="debug-output">' + JSON.stringify(report, null, 2) + '</pre>';
})();

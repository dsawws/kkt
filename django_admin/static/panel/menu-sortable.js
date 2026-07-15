(function () {
  var root = document.getElementById('menu-sortable-root');
  if (!root || typeof Sortable === 'undefined') return;

  var reorderUrl = root.getAttribute('data-reorder-url');
  var csrfToken = root.getAttribute('data-csrf');
  var statusEl = document.getElementById('menu-reorder-status');
  var saveTimer = null;

  function setStatus(text, kind) {
    if (!statusEl) return;
    statusEl.textContent = text || '';
    statusEl.className = 'menu-reorder-status' + (kind ? ' is-' + kind : '');
  }

  function collectItems() {
    var items = [];
    root.querySelectorAll('.sortable-menu').forEach(function (list) {
      var parentRaw = list.getAttribute('data-parent') || '';
      var parentId = parentRaw ? parseInt(parentRaw, 10) : null;
      Array.prototype.forEach.call(list.children, function (li, index) {
        if (!li.classList.contains('menu-tree-item')) return;
        var id = parseInt(li.getAttribute('data-id'), 10);
        if (!id) return;
        items.push({ id: id, parent_id: parentId, order: index });
      });
    });
    return items;
  }

  function saveOrder() {
    setStatus('Сохранение…', 'saving');
    fetch(reorderUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({ items: collectItems() }),
      credentials: 'same-origin',
    })
      .then(function (r) {
        return r.json().then(function (data) {
          return { ok: r.ok, data: data };
        });
      })
      .then(function (res) {
        if (res.ok && res.data && res.data.ok) {
          setStatus('Порядок сохранён', 'ok');
          setTimeout(function () { setStatus(''); }, 1800);
        } else {
          setStatus((res.data && res.data.error) || 'Ошибка сохранения', 'error');
        }
      })
      .catch(function () {
        setStatus('Ошибка сети', 'error');
      });
  }

  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveOrder, 250);
  }

  root.querySelectorAll('.sortable-menu').forEach(function (list) {
    Sortable.create(list, {
      group: 'menu-tree',
      animation: 150,
      handle: '.drag-handle',
      draggable: '.menu-tree-item',
      fallbackOnBody: true,
      swapThreshold: 0.65,
      emptyInsertThreshold: 24,
      ghostClass: 'menu-sortable-ghost',
      chosenClass: 'menu-sortable-chosen',
      dragClass: 'menu-sortable-drag',
      onEnd: scheduleSave,
    });
  });
})();

(function () {
    function getEditor() {
        if (typeof CKEDITOR === 'undefined') return null;
        const instances = CKEDITOR.instances;
        for (const key in instances) {
            if (instances.hasOwnProperty(key)) return instances[key];
        }
        return null;
    }

    function insertHtml(html) {
        const editor = getEditor();
        if (editor) {
            editor.insertHtml(html);
        } else {
            const ta = document.querySelector('textarea[name="content"]');
            if (ta) ta.value += html;
        }
        document.getElementById('insert-modal').style.display = 'none';
    }

    function showModal(title, items, onPick) {
        const modal = document.getElementById('insert-modal');
        const list = document.getElementById('insert-modal-list');
        document.getElementById('insert-modal-title').textContent = title;
        list.innerHTML = '';
        if (!items.length) {
            list.innerHTML = '<p>Нет элементов. Загрузите документ в разделе «Документы» или создайте таблицу.</p>';
        } else {
            items.forEach(function (item) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-secondary';
                btn.style.cssText = 'display:block;width:100%;margin-bottom:8px;text-align:left;';
                btn.textContent = item.label;
                btn.onclick = function () { onPick(item); };
                list.appendChild(btn);
            });
        }
        modal.style.display = 'flex';
    }

    window.initPageEditorTools = function (opts) {
        let cache = null;

        function loadSnippets(cb) {
            if (cache) return cb(cache);
            fetch(opts.snippetsUrl, { credentials: 'same-origin' })
                .then(function (r) { return r.json(); })
                .then(function (data) { cache = data; cb(data); });
        }

        const btnTable = document.getElementById('btn-insert-table');
        const btnDoc = document.getElementById('btn-insert-doc');

        if (btnTable) {
            btnTable.addEventListener('click', function () {
                loadSnippets(function (data) {
                    showModal('Вставить таблицу', data.tables.map(function (t) {
                        return { id: t.id, label: t.title };
                    }), function (item) {
                        const url = opts.tableUrlTemplate.replace('{id}', item.id);
                        fetch(url, { credentials: 'same-origin' })
                            .then(function (r) { return r.json(); })
                            .then(function (d) { insertHtml(d.html); });
                    });
                });
            });
        }

        if (btnDoc) {
            btnDoc.addEventListener('click', function () {
                loadSnippets(function (data) {
                    showModal('Вставить документ (блок загрузки)', data.documents.map(function (d) {
                        return { id: d.id, label: d.title };
                    }), function (item) {
                        const url = opts.documentUrlTemplate.replace('{id}', item.id);
                        fetch(url, { credentials: 'same-origin' })
                            .then(function (r) { return r.json(); })
                            .then(function (d) { insertHtml(d.html); });
                    });
                });
            });
        }
    };
})();

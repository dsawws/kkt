(function () {
    const map = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'y',
        'к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f',
        'х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    };

    window.slugifyTitle = function (text) {
        return text.toLowerCase().trim().split('').map(function (ch) {
            return map[ch] || ch;
        }).join('')
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .substring(0, 200);
    };

    window.initSlugField = function (titleId, slugId, previewId) {
        const titleEl = document.getElementById(titleId);
        const slugEl = document.getElementById(slugId);
        const previewEl = previewId ? document.getElementById(previewId) : null;
        if (!titleEl || !slugEl) return;

        let slugManual = slugEl.value && slugEl.dataset.auto !== '1';

        slugEl.addEventListener('input', function () {
            slugManual = true;
            if (previewEl) previewEl.textContent = slugEl.value || '...';
        });

        titleEl.addEventListener('input', function () {
            if (slugManual && slugEl.value) return;
            const slug = slugifyTitle(titleEl.value);
            slugEl.value = slug;
            slugEl.dataset.auto = '1';
            if (previewEl) previewEl.textContent = slug || '...';
        });

        if (previewEl && slugEl.value) previewEl.textContent = slugEl.value;
    };
})();

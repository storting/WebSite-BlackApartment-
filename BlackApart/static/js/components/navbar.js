class CustomNavbar extends HTMLElement {
    connectedCallback() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.render());
        } else {
            this.render();
        }
    }

    render() {
        this.attachShadow({ mode: 'open' });

        const userDataElement = document.getElementById('user-data');
        const isAuth = userDataElement?.dataset.isAuthenticated === 'true';
        const username = userDataElement?.dataset.username || '';
        const avatarUrl = userDataElement?.dataset.avatarUrl;
        const profileUrl = userDataElement?.dataset.profileUrl || '/profile/';
        const logoutUrl = userDataElement?.dataset.logoutUrl || '/logout/';
        const csrfToken = userDataElement?.dataset.csrf || '';

        let userHtml = '';
        if (isAuth) {
            const avatarHtml = avatarUrl
                ? `<img src="${avatarUrl}" class="avatar" alt="avatar">`
                : `<i data-feather="user"></i>`;
            userHtml = `
                <li class="user-menu">
                    <a href="${profileUrl}" class="user-info">
                        ${avatarHtml}
                        <span class="user-name">${username}</span>
                    </a>
                </li>
                <li><button id="logout-btn" class="logout-btn">Выйти</button></li>
            `;
        } else {
            userHtml = `<li><a class="loginBut" href="/login">LOGIN</a></li>`;
        }

        // ... весь CSS и структура навбара (как в предыдущих версиях) ...
        // (код CSS и HTML я опускаю для краткости, он у вас уже есть)

        this.shadowRoot.innerHTML = `...`; // вставьте ваш полный код

        if (typeof feather !== 'undefined') {
            feather.replace(this.shadowRoot);
        }

        if (isAuth) {
            const logoutBtn = this.shadowRoot.getElementById('logout-btn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = logoutUrl;
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = csrfToken;
                    form.appendChild(csrfInput);
                    document.body.appendChild(form);
                    form.submit();
                });
            }
        }
    }
}

customElements.define('custom-navbar', CustomNavbar);
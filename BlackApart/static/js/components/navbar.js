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
        const firstName = userDataElement?.dataset.firstName || '';
        const lastName = userDataElement?.dataset.lastName || '';
        const fullName = (firstName || lastName) ? `${firstName} ${lastName}`.trim() : username;
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
                        <span class="user-name">${fullName}</span>
                    </a>
                </li>
                <li><button id="logout-btn" class="logoutBut"><b>OUT</b></button></li>
            `;
        } else {
            userHtml = `<li><a class="loginBut" href="/login">LOGIN</a></li>`;
        }

        this.shadowRoot.innerHTML = `
            <style>
                nav {
                    background: rgba(0, 0, 0, 0.95);
                    backdrop-filter: blur(10px);
                    padding: 1rem 2rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    z-index: 1000;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                .logo { 
                    color: white; 
                    font-weight: bold; 
                    font-size: 1.5rem;
                    letter-spacing: 2px;
                }
                ul { 
                    display: flex; 
                    gap: 2rem; 
                    list-style: none; 
                    margin: 0; 
                    padding: 0; 
                    align-items: center;
                }
                a { 
                    color: white; 
                    text-decoration: none; 
                    font-weight: 500;
                    position: relative;
                    padding: 0.5rem 0;
                }
                a::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 0;
                    height: 2px;
                    background: white;
                    transition: width 0.3s ease;
                }
                a:hover::after {
                    width: 100%;
                }
                .mobile-menu-btn {
                    display: none;
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                }
                .loginBut, .logoutBut {
                    color: black;
                    padding: 10px 20px; 
                    background-color: #ffffff; 
                    border-radius: 4px; 
                    border: none;       
                    cursor: pointer;    
                }
                .loginBut, logoutBut:hover {
                    color: rgb(255, 255, 255);
                    background-color: #000000; 
                }
                .user-menu {
                    display: flex;
                    align-items: center;
                }
                .user-info {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                .avatar, .user-info i {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    object-fit: cover;
                }
                .user-name {
                    color: white;
                    font-weight: 500;
                }
                @media (max-width: 768px) {
                    .mobile-menu-btn {
                        display: block;
                    }
                    ul {
                        display: none;
                        position: absolute;
                        top: 100%;
                        left: 0;
                        right: 0;
                        background: rgba(0, 0, 0, 0.98);
                        flex-direction: column;
                        padding: 1rem;
                        gap: 1rem;
                    }
                    ul.show {
                        display: flex;
                    }
                }
            </style>
            <nav>
                <div class="logo"><a href="/">BlackApartment</a></div>
                <button class="mobile-menu-btn" onclick="this.getRootNode().host.shadowRoot.querySelector('ul').classList.toggle('show')">
                    <i data-feather="menu"></i>
                </button>
                <ul>
                    <li><a href="/">HOME</a></li>
                    <li><a href="/apartments">APARTMENTS</a></li>
                    ${userHtml}
                </ul>
            </nav>
        `;

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
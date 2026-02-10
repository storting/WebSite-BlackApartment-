class CustomNavbar extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: 'open' });
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
        .loginBut{
            color: black;
            padding: 10px 20px; 
            background-color: #ffffff; 
            border-radius: 4px; 
            border: none;       
            cursor: pointer;    
        }
        .loginBut:hover {
            color: rgb(255, 255, 255);
            background-color: #000000; 
        }
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
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
<button class="mobile-menu-btn" onclick="this.shadowRoot.querySelector('ul').classList.toggle('show')">
          <i data-feather="menu"></i>
        </button>
        <ul>
          <li><a href="/">HOME</a></li>
          <li><a href="/apart">APARTMENTS</a></li>
<li id="user-menu-item">
            <a class="loginBut" href="/log">LOGIN</a>
          </li>
        </ul>
</nav>
    `;
  }
}
customElements.define('custom-navbar', CustomNavbar);
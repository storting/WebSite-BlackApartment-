class CustomFooter extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        footer {
          background: #000000;
          color: white;
          padding: 3rem 2rem;
          text-align: center;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 2rem;
          text-align: left;
        }
        .footer-section h3 {
          font-size: 1.125rem;
          font-weight: 600;
          margin-bottom: 1rem;
        }
        .footer-section p, .footer-section a {
          color: rgba(255, 255, 255, 0.7);
          margin-bottom: 0.5rem;
          text-decoration: none;
          transition: color 0.3s ease;
        }
        .required {
          color: #ef4444;
        }
.footer-section a:hover {
          color: white;
        }
        .social-links {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }
        .social-links a {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          transition: all 0.3s ease;
        }
        .social-links a:hover {
          background: white;
          color: black;
          border-color: white;
        }
        .copyright {
          margin-top: 2rem;
          padding-top: 2rem;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          color: rgba(255, 255, 255, 0.5);
          font-size: 0.875rem;
        }
        @media (max-width: 768px) {
          .footer-content {
            grid-template-columns: 1fr;
            text-align: center;
          }
        }
      </style>
      <footer>
        <div class="footer-content">
          <div class="footer-section">
            <h3>BLACKAPARTMENT</h3>
            <p>Premium apartment rentals in Novosibirsk. Experience luxury living in black and white.</p>
</div>
          <div class="footer-section">
            <h3>CONTACT INFO</h3>
            <p><i data-feather="map-pin"></i> Novosibirsk, Russia</p>
            <p><i data-feather="phone"></i> +7(953)8049896</p>
            <p><i data-feather="mail"></i> storting124@mail.ru</p>
          </div>
          <div class="footer-section">
            <h3>QUICK LINKS</h3>
            <p><a href="./apartments.html">Browse Apartments</a></p>
            <p><a href="./login.html">Login</a></p>
            <p><a href="./register.html">Register</a></p>
          </div>
</div>
        <div class="copyright">
          <p>&copy; 2024 NoirNest Novosibirsk. All rights reserved.</p>
        </div>
      </footer>
    `;
  }
}
customElements.define('custom-footer', CustomFooter);
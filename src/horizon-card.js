const template = document.createElement('template');

template.innerHTML = `
  <style>
    :host {
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #f6f8fb;
      color: #1c2636;
      font-family: Arial, sans-serif;
    }
    article {
      width: min(680px, calc(100vw - 48px));
      border: 1px solid #d7dfeb;
      background: #fff;
      padding: 32px;
      box-shadow: 0 16px 38px rgba(28, 38, 54, 0.12);
    }
    span {
      color: #0b6bcb;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 12px;
    }
    h1 {
      margin: 10px 0 12px;
      font-size: 32px;
    }
    p {
      line-height: 1.6;
    }
  </style>
  <article>
    <span>Horizon Relevance</span>
    <h1>WebComponent Demo Application</h1>
    <p>
      This native custom element validates the WebComponent project type in
      the DevOps Pipeline product.
    </p>
  </article>
`;

class HorizonDemoCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }
}

customElements.define('horizon-demo-card', HorizonDemoCard);

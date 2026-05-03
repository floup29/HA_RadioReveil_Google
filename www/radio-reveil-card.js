/**
 * radio-reveil-card.js
 * Custom Lovelace card for Radio Réveil integration.
 * Install: copy to /config/www/radio-reveil-card.js
 * Add to resources: /local/radio-reveil-card.js (module)
 */

const DAYS_FR   = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"];
const DAYS_FULL = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"];

class RadioReveilCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot) this._build();
    this._render();
  }

  setConfig(config) {
    this._config = config;
  }

  _build() {
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { padding: 16px; }
        .title { font-size: 16px; font-weight: 500; margin-bottom: 12px;
                 display: flex; align-items: center; gap: 8px; }
        .title ha-icon { color: var(--primary-color); }
        .row { display: flex; align-items: center; padding: 8px 0;
               border-bottom: 1px solid var(--divider-color); gap: 12px; }
        .row:last-child { border-bottom: none; }
        .label { flex: 1; font-size: 14px; }
        .label small { display: block; font-size: 11px; color: var(--secondary-text-color); }
        .days-grid { display: grid; grid-template-columns: repeat(7,1fr); gap: 6px; margin-top: 12px; }
        .day-tile { text-align: center; padding: 8px 4px;
                    border-radius: 8px; border: 1px solid var(--divider-color);
                    cursor: pointer; transition: .15s; }
        .day-tile.on  { background: var(--primary-color); color: #fff; border-color: var(--primary-color); }
        .day-tile.off { opacity: .5; }
        .day-name { font-size: 11px; font-weight: 500; }
        .day-time { font-size: 12px; margin-top: 2px; font-family: monospace; }
        .section-label { font-size: 12px; font-weight: 500; color: var(--secondary-text-color);
                         text-transform: uppercase; letter-spacing: .05em;
                         margin: 14px 0 6px; }
      </style>
      <ha-card>
        <div class="title">
          <ha-icon icon="mdi:alarm"></ha-icon>
          Radio Réveil
        </div>
        <div id="content"></div>
      </ha-card>`;
  }

  _entity(suffix) {
    // Find entity by unique_id suffix pattern
    const entries = Object.values(this._hass.states);
    return entries.find(e => e.entity_id.includes(`radio_reveil`) && e.entity_id.endsWith(suffix));
  }

  _toggle(entity_id, state) {
    this._hass.callService("homeassistant", state === "on" ? "turn_on" : "turn_off", { entity_id });
  }

  _render() {
    const h = this._hass;
    const content = this.shadowRoot.getElementById("content");
    if (!content) return;

    const globalState = Object.values(h.states)
      .find(e => e.entity_id.includes("radio_reveil") && e.entity_id.includes("global"));
    const radioState = Object.values(h.states)
      .find(e => e.entity_id.includes("radio_reveil") && e.entity_id.includes("radio") && e.entity_id.startsWith("select."));
    const volState = Object.values(h.states)
      .find(e => e.entity_id.includes("radio_reveil") && e.entity_id.startsWith("number."));
    const mpState = Object.values(h.states)
      .find(e => e.entity_id.includes("radio_reveil") && e.entity_id.startsWith("text."));

    const globalOn = globalState?.state === "on";

    // Build day tiles
    const dayTiles = DAYS_FR.map((key, i) => {
      const sw = Object.values(h.states)
        .find(e => e.entity_id.includes("radio_reveil") && e.entity_id.endsWith(`_${key}`) && e.entity_id.startsWith("switch."));
      const tm = Object.values(h.states)
        .find(e => e.entity_id.includes("radio_reveil") && e.entity_id.includes(`time_${key}`));
      const on = sw?.state === "on" && globalOn;
      const time = tm?.state?.substring(0, 5) || "--:--";
      return `<div class="day-tile ${on ? "on" : "off"}"
                   data-sw="${sw?.entity_id || ""}"
                   data-state="${sw?.state || "off"}">
                <div class="day-name">${DAYS_FULL[i].substring(0,3)}</div>
                <div class="day-time">${time}</div>
              </div>`;
    }).join("");

    content.innerHTML = `
      <!-- 1. Global -->
      <div class="row">
        <ha-icon icon="mdi:alarm" style="color:var(--primary-color)"></ha-icon>
        <div class="label">Réveil actif
          <small>${globalState?.entity_id || "switch non trouvé"}</small>
        </div>
        <ha-switch ?checked="${globalOn}"
          data-eid="${globalState?.entity_id || ""}"
          data-state="${globalState?.state || "off"}">
        </ha-switch>
      </div>

      <!-- 2. Jours -->
      <div class="section-label">Programmation</div>
      <div class="days-grid">${dayTiles}</div>

      <!-- 3. Radio -->
      <div class="section-label">Station & diffusion</div>
      <div class="row">
        <ha-icon icon="mdi:radio" style="color:var(--primary-color)"></ha-icon>
        <div class="label">Station
          <small>${radioState?.entity_id || ""}</small>
        </div>
        <span style="font-size:13px;color:var(--secondary-text-color)">${radioState?.state || "—"}</span>
      </div>

      <!-- 4. Volume -->
      <div class="row">
        <ha-icon icon="mdi:volume-high" style="color:var(--primary-color)"></ha-icon>
        <div class="label">Volume
          <small>${volState?.entity_id || ""}</small>
        </div>
        <span style="font-size:13px;color:var(--secondary-text-color)">${volState ? Math.round(parseFloat(volState.state)*100)+"%" : "—"}</span>
      </div>

      <!-- 5. Media player -->
      <div class="row">
        <ha-icon icon="mdi:google-home" style="color:var(--primary-color)"></ha-icon>
        <div class="label">Diffusion
          <small>${mpState?.entity_id || ""}</small>
        </div>
        <span style="font-size:12px;color:var(--secondary-text-color);font-family:monospace">${mpState?.state || "—"}</span>
      </div>`;

    // Bind global toggle
    const sw = content.querySelector("ha-switch");
    if (sw) sw.addEventListener("change", (e) => {
      const eid = e.target.dataset.eid;
      if (eid) this._toggle(eid, e.target.checked ? "on" : "off");
    });

    // Bind day tiles
    content.querySelectorAll(".day-tile").forEach(tile => {
      tile.addEventListener("click", () => {
        const eid = tile.dataset.sw;
        const state = tile.dataset.state;
        if (eid) this._toggle(eid, state === "on" ? "off" : "on");
      });
    });
  }

  static getConfigElement() {
    return document.createElement("radio-reveil-card-editor");
  }

  static getStubConfig() {
    return {};
  }
}

customElements.define("radio-reveil-card", RadioReveilCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "radio-reveil-card",
  name: "Radio Réveil",
  description: "Contrôlez votre réveil radio hebdomadaire.",
  preview: false,
});

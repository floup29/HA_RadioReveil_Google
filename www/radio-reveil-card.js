/**
 * radio-reveil-card.js  v2.0
 * Multi-instance Lovelace card for Radio Réveil.
 * Install: /config/www/radio-reveil-card.js
 *
 * Card YAML:
 *   type: custom:radio-reveil-card
 *   # entry_id: abc123   ← optional: show only one alarm
 */

const DAYS_FR   = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"];
const DAY_SHORT = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"];

const CSS = `
  :host { display: block; }
  ha-card { padding: 0; overflow: hidden; }
  .card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 16px 10px; border-bottom: 1px solid var(--divider-color);
  }
  .card-title { font-size: 16px; font-weight: 500;
    display: flex; align-items: center; gap: 8px; }
  .alarm-block { border-bottom: 1px solid var(--divider-color); }
  .alarm-block:last-child { border-bottom: none; }
  .alarm-header {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px 6px;
  }
  .alarm-name { font-size: 14px; font-weight: 500; flex: 1; }
  .alarm-name.off { color: var(--secondary-text-color); }
  .row {
    display: flex; align-items: center; padding: 7px 16px;
    border-top: 1px solid var(--divider-color); gap: 10px;
  }
  .row ha-icon { color: var(--primary-color); flex-shrink: 0; }
  .label { flex: 1; font-size: 13px; }
  .label small { display: block; font-size: 11px;
    color: var(--secondary-text-color); font-family: monospace; }
  .val { font-size: 13px; color: var(--secondary-text-color); }
  .days-grid {
    display: grid; grid-template-columns: repeat(7,1fr);
    gap: 5px; padding: 8px 16px 10px;
  }
  .day-tile {
    text-align: center; padding: 7px 2px; border-radius: 8px;
    border: 1px solid var(--divider-color); cursor: pointer;
    transition: .15s; user-select: none;
  }
  .day-tile.on { background: var(--primary-color); color:#fff;
    border-color: var(--primary-color); }
  .day-tile.off-global { opacity:.35; pointer-events:none; }
  .day-short { font-size: 10px; font-weight: 600; text-transform: uppercase; }
  .day-time  { font-size: 11px; margin-top: 2px; font-family: monospace; }
  .section-lbl {
    font-size: 11px; font-weight: 500; letter-spacing:.05em;
    text-transform: uppercase; color: var(--secondary-text-color);
    padding: 10px 16px 2px;
  }
  .empty { padding: 20px 16px; text-align: center;
    color: var(--secondary-text-color); font-size: 14px; }
`;

class RadioReveilCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot) this._build();
    this._render();
  }
  setConfig(config) { this._config = config || {}; }

  _build() {
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `<style>${CSS}</style><ha-card><div id="root"></div></ha-card>`;
  }

  _alarms() {
    const states = Object.values(this._hass.states);
    const map = {};
    // Anchor on global switches: switch.*_global where friendly_name contains "Réveil actif"
    states
      .filter(e => e.entity_id.startsWith("switch.") && e.entity_id.endsWith("_global")
                   && e.attributes.friendly_name?.includes("Réveil"))
      .forEach(g => {
        const m = g.entity_id.match(/^switch\.(.+)_global$/);
        if (!m) return;
        const pfx = m[1];
        const find  = (dom, sfx) => states.find(e => e.entity_id === `${dom}.${pfx}_${sfx}`);
        const findT = (day)      => states.find(e => e.entity_id === `time.${pfx}_time_${day}`);
        // Device name from switch friendly_name: "Radio Réveil — Chambre — Réveil actif" → "Chambre"
        const raw = g.attributes.friendly_name || "";
        const name = raw.replace(/^Radio Réveil\s*[—-]\s*/, "").replace(/\s*[—-]?\s*Réveil actif$/, "") || pfx;
        map[pfx] = {
          pfx, name, global: g,
          days:  DAYS_FR.map(d => find("switch", d)),
          times: DAYS_FR.map(d => findT(d)),
          radio: find("select", "radio"),
          vol:   find("number", "volume"),
          mp:    find("text",   "media_player"),
        };
      });
    return Object.values(map);
  }

  _toggle(eid, state) {
    this._hass.callService("homeassistant", state === "on" ? "turn_off" : "turn_on", { entity_id: eid });
  }

  _render() {
    const root = this.shadowRoot.getElementById("root");
    if (!root) return;

    let alarms = this._alarms();
    if (this._config?.entry_id)
      alarms = alarms.filter(a => a.pfx.includes(this._config.entry_id));

    let html = `
      <div class="card-header">
        <div class="card-title">
          <ha-icon icon="mdi:alarm"></ha-icon>Radio Réveil
        </div>
        <span style="font-size:12px;color:var(--secondary-text-color)">${alarms.length} réveil${alarms.length>1?"s":""}</span>
      </div>`;

    if (!alarms.length) {
      html += `<div class="empty">Aucun réveil configuré.<br>
        <small>Paramètres → Intégrations → Radio Réveil → Ajouter</small></div>`;
    } else {
      alarms.forEach(a => {
        const on = a.global?.state === "on";

        const tiles = DAYS_FR.map((d, i) => {
          const sw    = a.days[i];
          const tm    = a.times[i];
          const dayOn = sw?.state === "on" && on;
          return `<div class="day-tile ${dayOn?"on":""} ${!on?"off-global":""}"
                       data-eid="${sw?.entity_id||""}" data-state="${sw?.state||"off"}">
                    <div class="day-short">${DAY_SHORT[i]}</div>
                    <div class="day-time">${tm?.state?.substring(0,5)||"--:--"}</div>
                  </div>`;
        }).join("");

        html += `
          <div class="alarm-block">
            <!-- 1 · Global -->
            <div class="alarm-header">
              <ha-icon icon="mdi:alarm" style="color:var(--primary-color)"></ha-icon>
              <span class="alarm-name ${on?"":"off"}">${a.name}</span>
              <ha-switch ${on?"checked":""} data-eid="${a.global?.entity_id||""}" data-state="${a.global?.state||"off"}"></ha-switch>
            </div>

            <!-- 2 · Jours -->
            <div class="section-lbl">Programmation</div>
            <div class="days-grid">${tiles}</div>

            <!-- 3 · Radio -->
            <div class="row">
              <ha-icon icon="mdi:radio"></ha-icon>
              <div class="label">Station<small>${a.radio?.entity_id||""}</small></div>
              <span class="val">${a.radio?.state||"—"}</span>
            </div>

            <!-- 4 · Volume -->
            <div class="row">
              <ha-icon icon="mdi:volume-high"></ha-icon>
              <div class="label">Volume<small>${a.vol?.entity_id||""}</small></div>
              <span class="val">${a.vol ? Math.round(parseFloat(a.vol.state)*100)+"%" : "—"}</span>
            </div>

            <!-- 5 · Media player -->
            <div class="row">
              <ha-icon icon="mdi:google-home"></ha-icon>
              <div class="label">Diffusion<small>${a.mp?.entity_id||""}</small></div>
              <span class="val" style="font-family:monospace;font-size:12px">${a.mp?.state||"—"}</span>
            </div>
          </div>`;
      });
    }

    root.innerHTML = html;

    root.querySelectorAll("ha-switch").forEach(sw =>
      sw.addEventListener("change", e => {
        const eid = e.target.dataset.eid;
        if (eid) this._toggle(eid, e.target.dataset.state);
      })
    );
    root.querySelectorAll(".day-tile").forEach(t =>
      t.addEventListener("click", () => {
        const eid = t.dataset.eid;
        if (eid) this._toggle(eid, t.dataset.state);
      })
    );
  }

  static getStubConfig() { return {}; }
}

customElements.define("radio-reveil-card", RadioReveilCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "radio-reveil-card",
  name: "Radio Réveil",
  description: "Gérez tous vos réveils radio hebdomadaires.",
});

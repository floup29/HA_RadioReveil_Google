/**
 * radio-reveil-card.js  v2.2
 * Inline time editing — no popup, no extra dependencies.
 */

const DAYS_FR   = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"];
const DAYS_FULL = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"];

const CSS = `
  :host { display: block; }
  ha-card { padding: 0; overflow: hidden; }

  .card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 16px 10px; border-bottom: 1px solid var(--divider-color);
  }
  .card-title { font-size: 16px; font-weight: 500;
    display: flex; align-items: center; gap: 8px; }

  .alarm-block { border-bottom: 2px solid var(--divider-color); }
  .alarm-block:last-child { border-bottom: none; }

  .alarm-header {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px 0;
  }
  .alarm-name { font-size: 14px; font-weight: 600; flex: 1; }
  .alarm-name.off { color: var(--secondary-text-color); }

  .section-lbl {
    font-size: 11px; font-weight: 500; letter-spacing: .05em;
    text-transform: uppercase; color: var(--secondary-text-color);
    padding: 10px 16px 2px;
  }

  /* ── Day row ── */
  .day-row {
    display: flex; align-items: center;
    padding: 6px 16px; gap: 10px; min-height: 44px;
    border-top: 1px solid var(--divider-color);
  }
  .day-row.off-global { opacity: .4; pointer-events: none; }
  .day-icon { color: var(--primary-color); flex-shrink: 0; }
  .day-label { font-size: 14px; flex: 1; }
  .day-label.off { color: var(--secondary-text-color); }

  /* Inline time input — styled to match HA */
  .time-input {
    font-family: var(--primary-font-family, inherit);
    font-size: 14px; font-weight: 500;
    color: var(--primary-text-color);
    background: var(--secondary-background-color, rgba(0,0,0,.04));
    border: 1px solid var(--divider-color);
    border-radius: 6px;
    padding: 4px 8px;
    outline: none;
    cursor: pointer;
    width: 96px;
    transition: border-color .15s;
    -webkit-appearance: none;
  }
  .time-input:focus { border-color: var(--primary-color); }
  .time-input:disabled {
    opacity: .4; cursor: not-allowed;
    background: transparent; border-color: transparent;
  }
  /* Chrome: hide the clock icon inside the input */
  .time-input::-webkit-calendar-picker-indicator {
    opacity: 0; width: 0; padding: 0;
  }

  /* Other rows */
  .row {
    display: flex; align-items: center; padding: 8px 16px;
    border-top: 1px solid var(--divider-color); gap: 10px; min-height: 44px;
  }
  .row ha-icon { color: var(--primary-color); flex-shrink: 0; }
  .label { flex: 1; font-size: 13px; }
  .label small { display: block; font-size: 11px;
    color: var(--secondary-text-color); font-family: monospace; }
  .val { font-size: 13px; color: var(--secondary-text-color); }

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
    states
      .filter(e => e.entity_id.startsWith("switch.") && e.entity_id.endsWith("_global"))
      .forEach(g => {
        const m = g.entity_id.match(/^switch\.(.+)_global$/);
        if (!m) return;
        const pfx = m[1];
        const find  = (dom, sfx) => states.find(e => e.entity_id === `${dom}.${pfx}_${sfx}`);
        const findT = (day)      => states.find(e => e.entity_id === `time.${pfx}_time_${day}`);
        const raw  = g.attributes.friendly_name || "";
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

  _toggleSwitch(eid, state) {
    this._hass.callService("homeassistant", state === "on" ? "turn_off" : "turn_on", { entity_id: eid });
  }

  _setTime(eid, value) {
    // value from <input type="time"> is "HH:MM" — HA expects "HH:MM:SS"
    this._hass.callService("time", "set_value", {
      entity_id: eid,
      time: value + ":00",
    });
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
          <img src="/local/radio_reveil/icon.png" style="width:28px;height:28px;border-radius:6px;margin-right:4px;vertical-align:middle" onerror="this.style.display='none'">Radio Réveil
        </div>
        <span style="font-size:12px;color:var(--secondary-text-color)">
          ${alarms.length} réveil${alarms.length > 1 ? "s" : ""}
        </span>
      </div>`;

    if (!alarms.length) {
      html += `<div class="empty">Aucun réveil configuré.<br>
        <small>Paramètres → Intégrations → Radio Réveil → Ajouter</small></div>`;
    } else {
      alarms.forEach(a => {
        const globalOn = a.global?.state === "on";

        const dayRows = DAYS_FR.map((d, i) => {
          const sw    = a.days[i];
          const tm    = a.times[i];
          const dayOn = sw?.state === "on";
          const active = dayOn && globalOn;
          // HA time entity state: "HH:MM:SS" → strip seconds for <input type="time">
          const timeVal = (tm?.state || "07:00:00").substring(0, 5);

          return `
            <div class="day-row ${!globalOn ? "off-global" : ""}">
              <ha-icon class="day-icon" icon="mdi:calendar-today"></ha-icon>
              <span class="day-label ${active ? "" : "off"}">${DAYS_FULL[i]}</span>
              <input
                class="time-input"
                type="time"
                value="${timeVal}"
                data-eid="${tm?.entity_id || ""}"
                ${!active ? "disabled" : ""}
              >
              <ha-switch
                ${dayOn ? "checked" : ""}
                data-eid="${sw?.entity_id || ""}"
                data-state="${sw?.state || "off"}">
              </ha-switch>
            </div>`;
        }).join("");

        html += `
          <div class="alarm-block">

            <!-- 1 · Global toggle -->
            <div class="alarm-header">
              <img src="/local/radio_reveil/icon.png" style="width:24px;height:24px;border-radius:4px" onerror="this.style.display='none'">
              <span class="alarm-name ${globalOn ? "" : "off"}">${a.name}</span>
              <ha-switch
                ${globalOn ? "checked" : ""}
                data-eid="${a.global?.entity_id || ""}"
                data-state="${a.global?.state || "off"}">
              </ha-switch>
            </div>

            <!-- 2 · Jours — time input inline + toggle -->
            <div class="section-lbl">Programmation</div>
            ${dayRows}

            <!-- 3 · Radio -->
            <div class="row">
              <ha-icon icon="mdi:radio"></ha-icon>
              <div class="label">Station<small>${a.radio?.entity_id || ""}</small></div>
              <span class="val">${a.radio?.state || "—"}</span>
            </div>

            <!-- 4 · Volume -->
            <div class="row">
              <ha-icon icon="mdi:volume-high"></ha-icon>
              <div class="label">Volume<small>${a.vol?.entity_id || ""}</small></div>
              <span class="val">${a.vol ? Math.round(parseFloat(a.vol.state) * 100) + "%" : "—"}</span>
            </div>

            <!-- 5 · Media player -->
            <div class="row">
              <ha-icon icon="mdi:google-home"></ha-icon>
              <div class="label">Diffusion<small>${a.mp?.entity_id || ""}</small></div>
              <span class="val" style="font-family:monospace;font-size:12px">${a.mp?.state || "—"}</span>
            </div>

          </div>`;
      });
    }

    root.innerHTML = html;

    // Bind ha-switch toggles
    root.querySelectorAll("ha-switch").forEach(sw =>
      sw.addEventListener("change", e => {
        const eid = e.target.dataset.eid;
        if (eid) this._toggleSwitch(eid, e.target.dataset.state);
      })
    );

    // Bind time inputs — fire on "change" (after user confirms, no popup)
    root.querySelectorAll(".time-input").forEach(input =>
      input.addEventListener("change", e => {
        const eid = e.target.dataset.eid;
        if (eid && e.target.value) this._setTime(eid, e.target.value);
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

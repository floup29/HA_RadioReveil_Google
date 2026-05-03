# 📻 Radio Réveil pour Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![HA Version](https://img.shields.io/badge/HA-2023.6%2B-blue.svg)](https://www.home-assistant.io)

Réveil radio hebdomadaire sur Google Home / Chromecast.  
Configurez chaque jour indépendamment — horaire, activation, station radio et volume — directement depuis l'interface HA ou la carte Lovelace dédiée.

---

## Fonctionnalités

- ✅ Activation/désactivation globale du réveil
- ✅ Activation/désactivation et horaire **par jour**
- ✅ Sélection de la station radio parmi 13 stations préconfigurées (ou URL personnalisée)
- ✅ Contrôle du volume
- ✅ Sélection du media player (Google Home, Chromecast, etc.)
- ✅ Carte Lovelace personnalisée intégrée
- ✅ Config flow HA complet (pas de YAML requis)
- ✅ Compatible HACS

---

## Installation

### Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant
2. **Intégrations → ⋮ → Dépôts personnalisés**
3. URL : `https://github.com/votre-repo/radio-reveil` — Catégorie : **Intégration**
4. Recherchez **Radio Réveil** → **Télécharger**
5. Redémarrez Home Assistant

### Manuelle

1. Copiez le dossier `custom_components/radio_reveil/` dans `/config/custom_components/`
2. Copiez `www/radio-reveil-card.js` dans `/config/www/`
3. Redémarrez Home Assistant

---

## Configuration

1. **Paramètres → Intégrations → + Ajouter → Radio Réveil**
2. Renseignez votre entité media player, la station radio et le volume par défaut
3. Validez → l'intégration crée automatiquement toutes les entités

### Entités créées

| Entité | Type | Description |
|---|---|---|
| `switch.radio_reveil_global` | Switch | Activation globale |
| `switch.radio_reveil_lundi` … `dimanche` | Switch | Activation par jour |
| `time.radio_reveil_heure_lundi` … `dimanche` | Time | Horaire par jour |
| `select.radio_reveil_radio` | Select | Station radio |
| `number.radio_reveil_volume` | Number | Volume (0.0–1.0) |
| `text.radio_reveil_media_player` | Text | Entity ID media player |

---

## Carte Lovelace

### Ajouter la ressource

Dans `configuration.yaml` :
```yaml
lovelace:
  resources:
    - url: /local/radio-reveil-card.js
      type: module
```
Ou via **Paramètres → Tableau de bord → Ressources → + Ajouter**.

### Ajouter la carte

Dans l'éditeur de tableau de bord : **+ Ajouter une carte → Personnalisée → Radio Réveil**

Ou en YAML manuel :
```yaml
type: custom:radio-reveil-card
```

---

## Stations radio incluses

| Station | Format |
|---|---|
| Mouv' | AAC |
| FIP | MP3 |
| France Inter | MP3 |
| France Info | MP3 |
| France Musique | MP3 |
| Skyrock | MP3 |
| NRJ | MP3 |
| Rire & Chansons | MP3 |
| OUI FM | MP3 |
| Fun Radio | MP3 |
| RFI Monde | MP3 |
| BBC Radio 4 | MP3 |
| BBC World Service | HLS |

Pour une URL personnalisée, sélectionnez **URL personnalisée** dans le config flow et saisissez le lien direct du flux.

---

## Architecture

```
custom_components/radio_reveil/
├── __init__.py          # Setup de l'intégration
├── manifest.json        # Métadonnées HA
├── config_flow.py       # Assistant de configuration UI
├── const.py             # Constantes (radios, jours, défauts)
├── coordinator.py       # Logique de scheduling et lecture
├── switch.py            # Entités switch (global + jours)
├── time.py              # Entités heure par jour
├── select.py            # Entité sélecteur de radio
├── number.py            # Entité volume
├── text.py              # Entité media player entity ID
├── strings.json         # Traductions FR
└── translations/
    ├── fr.json
    └── en.json

www/
└── radio-reveil-card.js  # Carte Lovelace personnalisée
```

---

## Contribution

Les PR sont bienvenues !  
Testez avec [`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component).

---

## Licence

MIT — voir [LICENSE](LICENSE)

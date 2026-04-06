# AVS Alarm per Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://www.hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1.0%2B-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Integrazione custom per collegare una centrale **AVS Alarm** a **Home Assistant** tramite API HTTP in rete locale.

Questo progetto e pensato per utenti hobbisti che vogliono:

- vedere lo stato dell'impianto dentro Home Assistant;
- armare o disarmare i settori dalla dashboard;
- usare lo stato dell'allarme in automazioni, notifiche e scenari domestici.

## Cosa fa

L'integrazione crea entita Home Assistant per ogni settore configurato:

- `sensor` con stato testuale del settore;
- `binary_sensor` che indica se il settore risulta armato;
- `switch` per inviare i comandi di inserimento e disinserimento.

La comunicazione avviene in **locale** con polling periodico. Non e richiesto alcun servizio cloud.

## Requisiti

- Home Assistant `2024.1.0` o superiore;
- una centrale AVS raggiungibile dalla rete locale;
- indirizzo IP della centrale;
- porta HTTP della centrale, di default `80`;
- nome utente AVS;
- `PID` del sistema;
- HACS opzionale ma consigliato.

## Installazione

### Metodo 1: HACS

1. Apri HACS.
2. Vai in `Integrations`.
3. Apri il menu in alto a destra e scegli `Custom repositories`.
4. Aggiungi il repository:

   ```text
   https://github.com/lelenoce/homeassistant-avs-alarm
   ```

5. Seleziona `Integration`.
6. Installa `AVS Alarm`.
7. Riavvia Home Assistant.

### Metodo 2: installazione manuale

1. Scarica il contenuto del repository.
2. Crea la cartella:

   ```text
   <config>/custom_components/avsalarm
   ```

3. Copia dentro quella cartella i file Python, `manifest.json`, `translations/` e le altre risorse del progetto.
4. Riavvia Home Assistant.

## Configurazione

Dopo il riavvio:

1. vai in `Impostazioni > Dispositivi e servizi`;
2. clicca `Aggiungi integrazione`;
3. cerca `AVS Alarm`;
4. inserisci i parametri richiesti.

### Parametri richiesti

- `Host`: IP della centrale AVS.
- `Port`: porta HTTP della centrale.
- `Username`: utente AVS usato per le chiamate API.
- `PID`: identificativo del sistema.
- `Sectors`: numero di settori da esporre in Home Assistant, da `1` a `4`.

## Entita create

Per ogni settore configurato vengono create queste entita:

- `sensor.avs_alarm_sector_X_status`
- `binary_sensor.avs_alarm_sector_X_armed`
- `switch.avs_alarm_sector_X_arm_on`
- `switch.avs_alarm_sector_X_arm_area`
- `switch.avs_alarm_sector_X_arm_home`
- `switch.avs_alarm_sector_X_arm_perimeter`

I nomi finali possono cambiare leggermente in base alle regole di naming di Home Assistant.

## Modalita di inserimento supportate

Gli switch espongono questi comandi:

- `arm-on`
- `arm-area`
- `arm-home`
- `arm-perimeter`
- `disarm` quando uno switch viene spento

## Esempi di automazione

### Notifica quando il settore si inserisce

```yaml
automation:
  - alias: Notifica inserimento allarme
    trigger:
      - platform: state
        entity_id: binary_sensor.avs_alarm_sector_1_armed
        to: "on"
    action:
      - service: notify.mobile_app_telefono
        data:
          message: "Il settore 1 dell'allarme AVS e stato inserito."
```

### Inserimento notturno automatico

```yaml
automation:
  - alias: Inserimento perimetrale notturno
    trigger:
      - platform: time
        at: "23:30:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.avs_alarm_sector_1_arm_perimeter
```

## Come funziona

L'integrazione:

- apre una sessione verso la centrale;
- legge lo stato del settore via endpoint HTTP;
- aggiorna le entita in Home Assistant ogni 30 secondi;
- invia i comandi di arm/disarm tramite chiamate HTTP dedicate.

## Limiti attuali

Questa sezione e importante per evitare aspettative sbagliate.

- Il polling automatico implementato oggi legge esplicitamente lo stato del `settore 1`.
- Se configuri piu settori, le entita vengono create comunque, ma lo stato letto potrebbe non riflettere ancora tutti i settori in modo completo.
- La comunicazione usa HTTP in chiaro sulla rete locale.
- Il progetto non implementa ancora una gestione avanzata di errori, diagnostica o test automatici.

Per un uso hobbistico e domestico puo andare bene, ma conviene fare prove graduali prima di affidarsi all'integrazione per scenari critici.

## Risoluzione problemi

Se l'integrazione non si configura o non aggiorna lo stato:

1. verifica che la centrale risponda all'IP e alla porta configurati;
2. controlla che `Username` e `PID` siano corretti;
3. verifica che Home Assistant e la centrale siano sulla stessa rete o comunque raggiungibili;
4. consulta i log di Home Assistant filtrando per `avsalarm`.

## A chi e adatto

Questo progetto e indicato se:

- ti piace sperimentare con Home Assistant;
- vuoi integrare una centrale AVS senza passare dal cloud;
- accetti qualche limite tipico di un progetto custom/hobbistico.

Se invece ti serve un'integrazione enterprise, con test, supporto strutturato e copertura completa di tutte le funzioni della centrale, il codice attuale richiede ancora evoluzione.

## Sviluppo

Struttura principale del progetto:

- [`manifest.json`](manifest.json): metadati dell'integrazione;
- [`config_flow.py`](config_flow.py): configurazione via UI;
- [`avs_api.py`](avs_api.py): chiamate HTTP e coordinator;
- [`sensor.py`](sensor.py): sensori di stato;
- [`binary_sensor.py`](binary_sensor.py): stato armato/disarmato;
- [`switch.py`](switch.py): comandi di inserimento/disinserimento.

## Supporto

Per bug, idee o miglioramenti:

- apri una issue su [GitHub](https://github.com/lelenoce/homeassistant-avs-alarm/issues);
- descrivi modello della centrale, versione di Home Assistant e log rilevanti.

## Licenza

Progetto rilasciato con licenza [MIT](LICENSE).

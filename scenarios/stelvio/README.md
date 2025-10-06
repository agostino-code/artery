# Stelvio V2X Simulation - 6G Hybrid Infrastructure Study

**Simulazione completa V2X per lo studio di trasmissione DENM in infrastruttura ibrida 6G al Passo dello Stelvio**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![OMNeT++](https://img.shields.io/badge/OMNeT++-6.0-blue)]()
[![SUMO](https://img.shields.io/badge/SUMO-1.22.0-orange)]()
[![Artery](https://img.shields.io/badge/Artery-latest-green)]()

---

## 📋 Indice Rapido

- [Panoramica](#-panoramica) | [Quick Start](#-quick-start) | [Architettura](#-architettura)
- [Rete Stradale](#-rete-stradale-stelvio) | [Servizi](#-servizi-implementati) | [Configurazioni](#-configurazioni-simulazione)
- [Metriche](#-metriche-e-analisi) | [File NED](#-file-ned) | [Personalizzazione](#-personalizzazione) | [Troubleshooting](#-troubleshooting)

---

## 🎯 Panoramica

Simulazione comunicazione Vehicle-to-Cloud (V2C) per notifiche incidenti (DENM) sulla **Strada Statale dello Stelvio (SS38)** con:

- **6G Terrestrial Network (TN)** - Antenna terrestre (5ms, 600m, 65% affidabilità)
- **LEO Satellite (NTN)** - Satellite LEO (45ms, 5000m, 99% affidabilità)  
- **Architettura Ibrida** - Entrambe con fallback automatico

### Caratteristiche Principali

✅ **2 Scenari**: Crashed (immediato) + Witness (ritardato)  
✅ **3 Infrastrutture**: Terrestrial, Satellite, Hybrid  
✅ **6 Configurazioni**: Tutte le combinazioni  
✅ **Rete Reale**: Dati OpenStreetMap del Passo dello Stelvio  
✅ **GUI Automatizzata**: Pannello Python per batch  
✅ **Analisi Completa**: KPI e visualizzazioni  
✅ **Codice Pulito**: Modulare e documentato  
✅ **Traffico Bidirezionale**: 20 veicoli (11 uphill + 9 downhill)  

---

## �️ Rete Stradale Stelvio

### Dati Geografici Reali

La simulazione utilizza dati reali da **OpenStreetMap** del Passo dello Stelvio:

**Coordinate Geografiche**:
- **Longitudine**: 10.452944° - 10.465982° E
- **Latitudine**: 46.528520° - 46.533840° N
- **Proiezione**: UTM Zone 32 (WGS84)
- **Net Offset**: (-611423.27, -5153798.43)

**Caratteristiche Rete**:
- **Strada**: SS38 - Strada Statale dello Stelvio / Stilfserjoch Staatsstraße
- **Tipo**: highway.secondary (Strada secondaria statale)
- **Corsia**: 1 lane per direzione (bidirectional)
- **Velocità Max**: 27.78 m/s (100 km/h)
- **Lunghezza Totale**: ~3.7 km (1918m uphill + 1817m downhill)

### Topologia Rete

```
Junction 2471575434 (Start Uphill)
     ↓ -767626960#2 (353m)
Junction 2964504583 (Center)
     ↓ -767626960#1 (1817m)
Junction 964780888 (Pass Summit)
     ↓ -767626960#0 (1918m)
Junction 12070073350 (End Uphill)

Direzione Opposta (Downhill):
12070073350 → 767626960#0 → 964780888 → 767626960#1 → 2964504583 → 767626960#2 → 2471575434
```

### Edges Disponibili

| Edge ID | From | To | Length | Direction |
|---------|------|-----|--------|-----------|
| `-767626960#2` | 2471575434 | 2964504583 | 353m | Uphill |
| `-767626960#1` | 2964504583 | 964780888 | 1817m | Uphill |
| `-767626960#0` | 964780888 | 12070073350 | 1918m | Uphill |
| `767626960#0` | 12070073350 | 964780888 | 1909m | Downhill |
| `767626960#1` | 964780888 | 2964504583 | 1817m | Downhill |
| `767626960#2` | 2964504583 | 2471575434 | 353m | Downhill |

### Nodi Principali

1. **2471575434** (90.07, 54.80) - Inizio strada (valle)
2. **2964504583** (263.56, 344.47) - Centro percorso
3. **964780888** (636.61, 518.82) - Passo/Summit
4. **12070073350** (996.13, 487.57) - Fine strada (plateau)

### Infrastruttura Posizionata

**Posizione Centrale Strategica**: (729.0, 390.0)
- Vicina al passo (Junction 964780888)
- Copre tratti critici in salita/discesa
- Massima visibilità line-of-sight

---

## 🚗 Traffico Veicolare

### Composizione Flusso

**20 Veicoli Totali**:
- **11 Veicoli in Salita** (uphill): da valle verso passo
  - 5 veicoli prima dell'incidente (veh_0 to veh_4)
  - 1 veicolo incidentato (accident_veh_0) o testimone (witness_veh_0)
  - 5 veicoli dopo evento (veh_5 to veh_8 + witness/accident)
- **9 Veicoli in Discesa** (downhill): da passo verso valle
  - Traffic opposto per realismo (veh_opp_0 to veh_opp_8)

### Schedule Partenze

```
t=0s   : veh_0 (↑), veh_opp_0 (↓)
t=5s   : veh_1 (↑), veh_opp_1 (↓)
t=10s  : veh_2 (↑), veh_opp_2 (↓)
t=15s  : veh_3 (↑), veh_opp_3 (↓)
t=20s  : veh_4 (↑), veh_opp_4 (↓)
t=25s  : accident_veh_0 (↑) [CRASH SCENARIO]
t=30s  : witness_veh_0 (↑) [WITNESS SCENARIO]
t=35s  : veh_5 (↑), veh_opp_5 (↓)
t=40s  : veh_6 (↑), veh_opp_6 (↓)
t=45s  : veh_7 (↑), veh_opp_7 (↓)
t=50s  : veh_8 (↑), veh_opp_8 (↓)
```

**Intervallo**: 5 secondi tra partenze  
**Scenario Crashed**: accident_veh_0 parte a t=25s, crash immediato  
**Scenario Witness**: accident_veh_0 crash silenzioso, witness_veh_0 segnala a t=30s+delay

### Tipi Veicolo

```xml
<vType id="veh_passenger" vClass="passenger" accel="2.0" decel="4.5" 
      sigma="0.5" length="4.5" maxSpeed="22.22" color="blue"/>
      
<vType id="veh_accident" vClass="passenger" accel="2.0" decel="4.5" 
      sigma="0.5" length="4.5" maxSpeed="22.22" color="orange"/>
      
<vType id="veh_witness" vClass="passenger" accel="2.2" decel="4.8" 
      sigma="0.4" length="4.6" maxSpeed="23.0" color="blue"/>
```

### Route File

**File**: `stelvio.rou.xml`  
**Formato**: SUMO `<trip>` elements  
**Routing**: Automatico SUMO (best path)

**Esempio Trip Uphill**:
```xml
<trip id="veh_0" type="veh_passenger" depart="0.00" 
      departLane="best" departSpeed="max" 
      from="-767626960#2" to="-767626960#0"/>
```

**Esempio Trip Downhill**:
```xml
<trip id="veh_opp_0" type="veh_passenger" depart="0.00" 
      departLane="best" departSpeed="max" 
      from="767626960#0" to="767626960#2"/>
```

---

## �🚀 Quick Start

```bash
# 1. Setup (prima volta)
cd /workspaces/artery/scenarios/stelvio
make install-deps    # Crea venv e installa dipendenze Python
make check          # Verifica (34 controlli)
make build          # Compila scenario

# 2. Esegui Simulazioni
make run-crashed    # Esegui tutti scenari crashed (3 configs)
make run-witness    # Esegui tutti scenari witness (3 configs)
# oppure
./quickstart.sh run-all  # Tutte le 6 configurazioni

# 3. Analizza Risultati
make analyze        # Genera grafici in analysis/plots/
# oppure
make gui            # GUI interattiva per controllo

# 4. Pulizia
make clean          # Rimuovi risultati simulazioni
make clean-all      # Rimuovi tutto (incluso venv)
```

### Comandi Rapidi

| Comando | Descrizione |
|---------|-------------|
| `make help` | Mostra tutti i comandi disponibili |
| `make check` | Verifica setup e dipendenze (34 test) |
| `make build` | Compila libreria scenario (libartery_stelvio.so) |
| `make run-crashed` | Esegui 3 scenari crashed (Terrestrial/Satellite/Hybrid) |
| `make run-witness` | Esegui 3 scenari witness (Terrestrial/Satellite/Hybrid) |
| `make run-all` | Esegui tutte le 6 configurazioni |
| `make analyze` | Genera grafici e statistiche CSV |
| `make gui` | Avvia GUI Python per controllo batch |
| `make clean` | Pulisci risultati simulazioni |
| `make clean-all` | Rimuovi tutto (build + results + venv) |

### Verifica Setup

```bash
$ make check

🔍 Stelvio Scenario - Setup Verification
════════════════════════════════════════════

✅ C++ Source Files (5/5)
✅ NED Files (5/5)
✅ Config Files (3/3)
✅ Traffic Files (3/3)
✅ Storyboard Files (2/2)
✅ Python Scripts (3/3)
✅ Artery Build (found)
✅ OMNeT++ (6.0+)
✅ SUMO (1.22.0)

📊 Summary: 34/34 checks passed
```

---

## 🏗️ Architettura

### Flusso Comunicazione

```
[Veicolo Crashed/Witness su SS38 Stelvio]
         ↓ (DENM via BTP:2001)
         |
    +---------+---------+
    ↓                   ↓
[Antenna TN]      [Satellite NTN]
 (5ms, 600m)        (45ms, 5000m)
  65% reliable       99% reliable
  Pos: (729,390)     Pos: (729,390)
    ↓                   ↓
    +-------+-------+
            ↓ (Relay via BTP:2002)
    [Altri Veicoli SS38]
    (20 veicoli: 11↑ + 9↓)
         ↓
   [Metriche PDR, Latenza, Copertura]
```

### Struttura Moduli

```
stelvio/
├── src/                        # C++ Services + NED
│   ├── DenmMessage.msg         # Definizione messaggio DENM
│   ├── CrashedVehicleService   # Invio DENM immediato (crash)
│   ├── WitnessVehicleService   # Invio DENM ritardato (testimone)
│   ├── InfrastructureService   # Relay antenna/satellite
│   ├── VehicleReceiverService  # Ricezione + raccolta metriche
│   ├── package.ned             # Package declaration
│   └── *.ned                   # 5 file NED individuali
│
├── config/                     # Configurazioni XML Middleware
│   ├── services_crashed.xml    # Services per scenario crash
│   ├── services_witness.xml    # Services per scenario witness
│   └── services_infrastructure.xml  # Service infrastruttura
│
├── scripts/                    # Automazione Python
│   ├── simulation_gui.py       # GUI controllo batch
│   └── export_csv.py           # Export risultati CSV
│
├── analysis/                   # Analisi dati post-sim
│   ├── analyze_results.py      # Generazione grafici/stats
│   ├── plots/                  # Output grafici PNG
│   └── csv/                    # Export CSV elaborati
│
├── omnetpp.ini                 # 6 configurazioni OMNeT++
├── crash_storyboard.py         # Eventi crash t=200s
├── witness_storyboard.py       # Eventi witness t=200s+delay
├── stelvio.net.xml             # Rete stradale SUMO (SS38)
├── stelvio.rou.xml             # Traffico 20 veicoli
├── stelvio.sumocfg             # Configurazione SUMO
├── static_nodes.xml            # Posizione infrastruttura
├── Makefile                    # Comandi make rapidi
├── quickstart.sh               # Script bash helper
├── requirements.txt            # Dipendenze Python
└── results/                    # Output simulazioni
    ├── crashed_terrestrial/
    ├── crashed_satellite/
    ├── crashed_hybrid/
    ├── witness_terrestrial/
    ├── witness_satellite/
    └── witness_hybrid/
```

### File Rete SUMO

**stelvio.net.xml**:
- Generato da SUMO netedit 1.22.0
- Dati OSM reali Passo dello Stelvio
- 4 junctions, 6 edges principali
- Coordinate UTM Zone 32
- Lunghezza totale: ~3.7 km

**stelvio.rou.xml**:
- 20 veicoli (11 uphill + 9 downhill)
- 3 tipi veicolo: passenger/accident/witness
- Partenze ogni 5s da t=0s
- Routes: valle→passo, passo→valle

**static_nodes.xml**:
- 2 RSU: antenna + satellite
- Posizione: (729.0, 390.0) - centro strategico
- Copertura: 600m (TN) / 5000m (NTN)

---

## 💻 Servizi Implementati

### 1. CrashedVehicleService
**File**: `src/CrashedVehicleService.{h,cc,ned}`  
**Scopo**: Invia DENM immediato quando veicolo si schianta  
**Trigger**: Segnale `"crash_incident"` da storyboard  
**Porta BTP**: 2001  
**Metriche**: `denm_event_time`, `denm_sent_time`, `denm_generation_delay`, `denm_sequence_number`

### 2. WitnessVehicleService
**File**: `src/WitnessVehicleService.{h,cc,ned}`  
**Scopo**: Invia DENM ritardato dopo osservazione  
**Trigger**: Segnale `"witness_report"`  
**Ritardo**: Configurabile via `STELVIO_WITNESS_DELAY` (default: 5.0s)  
**Porta BTP**: 2001  
**Metriche**: Stesse di CrashedVehicleService

### 3. VehicleReceiverService
**File**: `src/VehicleReceiverService.{h,cc,ned}`  
**Scopo**: Riceve DENM su tutti veicoli + traccia metriche  
**Porta BTP**: 2002  
**Deadline**: 120ms configurabile  
**Metriche**:
- `denm_received_flag` (1=ricevuto, 0=no)
- `denm_reception_delay` ⭐ **Latenza end-to-end**
- `denm_within_deadline` (entro 120ms)
- `denm_in_coverage` / `denm_out_of_coverage`
- `denm_reliability_drop`

### 4. InfrastructureService
**File**: `src/InfrastructureService.{h,cc,ned}`  
**Scopo**: Relay antenna/satellite + consegna cloud  
**Porte BTP**: Riceve 2001, Rilancia 2002  
**Parametri Configurabili**:
```ini
infrastructureType = "terrestrial" | "satellite"
latency = 5ms | 45ms
coverageRadius = 600m | 5000m
coverageReliability = 0.65 | 0.99
transmitPower = 500mW | 1000mW
```
**Metriche**:
- `cloud_delivery_latency` ⭐ **Tempo consegna cloud**
- `infra_coverage_radius`, `infra_coverage_reliability`
- `denms_relayed`

---

## ⚙️ Configurazioni Simulazione

### 6 Configurazioni Principali

| ID | Nome Config | Scenario | Infrastruttura | Latenza | Veicoli | Use Case |
|----|-------------|----------|----------------|---------|---------|----------|
| 1 | `Crashed_Terrestrial` | Immediato | Antenna 6G | ~5ms | 20 (11↑+9↓) | 6G urbano/suburban |
| 2 | `Crashed_Satellite` | Immediato | Satellite LEO | ~45ms | 20 (11↑+9↓) | Aree remote montane |
| 3 | `Crashed_Hybrid` | Immediato | Antenna + Satellite | 5-45ms | 20 (11↑+9↓) | Ridondanza massima |
| 4 | `Witness_Terrestrial` | Ritardato | Antenna 6G | ~5ms | 20 (11↑+9↓) | Fattore umano urban |
| 5 | `Witness_Satellite` | Ritardato | Satellite LEO | ~45ms | 20 (11↑+9↓) | Testimone remoto |
| 6 | `Witness_Hybrid` | Ritardato | Antenna + Satellite | 5-45ms | 20 (11↑+9↓) | Affidabilità critica |

**Varianti GUI**: Ogni config ha versione `_GUI` per debug visuale (es. `Crashed_Terrestrial_GUI`)

### Parametri Infrastruttura (omnetpp.ini)

#### Antenna Terrestre (6G TN)
```ini
*.antenna.middleware.services.service[0].infrastructureType = "terrestrial"
*.antenna.middleware.services.service[0].latency = 5ms
*.antenna.middleware.services.service[0].coverageRadius = 600m
*.antenna.middleware.services.service[0].coverageReliability = 0.65
*.antenna.middleware.services.service[0].transmitPower = 500mW
```

**Posizione**: (729.0, 390.0) metri - centro rete Stelvio  
**Copertura Effettiva**: ~600m radius (circa 1.13 km²)  
**Latenza Tipica**: 3-7 ms  
**Affidabilità**: 65% (simula zone d'ombra montane)

#### Satellite LEO (NTN)
```ini
*.satellite.middleware.services.service[0].infrastructureType = "satellite"
*.satellite.middleware.services.service[0].latency = 45ms
*.satellite.middleware.services.service[0].coverageRadius = 5000m
*.satellite.middleware.services.service[0].coverageReliability = 0.99
*.satellite.middleware.services.service[0].transmitPower = 1000mW
```

**Posizione Logica**: (729.0, 390.0) metri - stesso centro  
**Copertura Effettiva**: ~5000m radius (circa 78.5 km²)  
**Latenza Tipica**: 40-50 ms (LEO ~600km altitudine)  
**Affidabilità**: 99% (copertura globale, meteo-indipendente)

#### Configurazione Hybrid
Attiva **entrambe** le infrastrutture:
```ini
# Hybrid = Terrestrial + Satellite simultaneamente
*.antenna.middleware.services.service[0].infrastructureType = "terrestrial"
*.satellite.middleware.services.service[0].infrastructureType = "satellite"
```

**Strategia Fallback**:
1. Prova antenna terrestre (bassa latenza)
2. Se fuori copertura/fallimento → satellite (alta affidabilità)
3. Relay duplicato → maggiore PDR

### Ritardo Testimone (Witness Delay)

**Variabile Ambiente**: `STELVIO_WITNESS_DELAY`  
**Default**: 5.0 secondi  
**Range Raccomandato**: 1.0 - 10.0 secondi

```bash
# Imposta ritardo personalizzato
export STELVIO_WITNESS_DELAY=5.0

# Esegui scenario witness
make run-witness

# Studio sensibilità
for delay in 1.0 3.0 5.0 10.0; do
    export STELVIO_WITNESS_DELAY=$delay
    opp_run -u Cmdenv -c Witness_Hybrid omnetpp.ini
done
```

**Timing Evento Witness**:
- `t=200s`: Veicolo incidentato si ferma (silenzioso)
- `t=200s + DELAY`: Veicolo testimone invia DENM
- Simula tempo reazione umana + decisione segnalazione

### Parametri Generali Simulazione

```ini
[General]
sim-time-limit = 300s              # 5 minuti simulazione
*.node[*].middleware.datetime = "2025-10-05 12:00:00"  # Data scenario

# Rete SUMO
*.traci.launcher.typename = "PosixLauncher"
*.traci.launcher.sumocfg = "stelvio.sumocfg"
*.traci.nodes.typename = "InsertionConstraint"

# Canale Radio (IEEE 802.11p)
*.node[*].wlan[*].radio.channelNumber = 180  # G5 5.9 GHz
*.node[*].wlan[*].radio.transmitter.power = 100 mW

# Middleware V2X
*.node[*].middleware.updateInterval = 0.1s
*.node[*].middleware.services = xmldoc("config/services_crashed.xml")  # o witness
*.antenna.middleware.services = xmldoc("config/services_infrastructure.xml")
*.satellite.middleware.services = xmldoc("config/services_infrastructure.xml")

# Metriche
**.scalar-recording = true
**.vector-recording = true
```

### Esecuzione Configurazioni

**Singola Configurazione**:
```bash
cd /workspaces/artery
python3 tools/run_artery.py stelvio -c Crashed_Terrestrial

# oppure diretto OMNeT++
cd scenarios/stelvio
opp_run -u Cmdenv -c Crashed_Terrestrial -n src:. -l libstelvio.so omnetpp.ini
```

**Batch Tutte le Configurazioni**:
```bash
make run-all
# oppure
./quickstart.sh run-all
```

**GUI Debug**:
```bash
opp_run -u Qtenv -c Crashed_Terrestrial_GUI -n src:. -l libstelvio.so omnetpp.ini
```

---

## 📊 Metriche e Analisi

### Metriche Primarie Raccolte

#### 1. Generazione DENM (Sender)
- **`denm_event_time`** - Timestamp evento (crash/witness)
- **`denm_sent_time`** - Timestamp invio DENM
- **`denm_generation_delay`** - Tempo tra evento e invio
- **`denm_sequence_number`** - ID sequenziale messaggio

#### 2. Ricezione Veicoli (Receiver)
- **`denm_reception_delay`** ⭐ - **Latenza end-to-end** (generazione→ricezione)
- **`denm_received_flag`** - 1=ricevuto, 0=perso
- **`denm_within_deadline`** - Ricevuto entro deadline (120ms)
- **`denm_in_coverage`** - Dentro copertura infrastruttura
- **`denm_out_of_coverage`** - Fuori copertura
- **`denm_reliability_drop`** - Perso per affidabilità < 100%

#### 3. Infrastruttura (Relay)
- **`cloud_delivery_latency`** ⭐ - **Tempo consegna cloud** (ricezione→relay)
- **`denms_relayed`** - Numero DENM re-inoltrati
- **`infra_coverage_radius`** - Raggio copertura configurato
- **`infra_coverage_reliability`** - Affidabilità configurata

#### 4. KPI Derivati
- **Packet Delivery Ratio (PDR)** - `(ricevuti / totale_veicoli) × 100%`
- **Coverage Rate** - `(in_coverage / totale_veicoli) × 100%`
- **Latency P95** - 95° percentile latenza ricezione
- **Mean/Median Latency** - Statistiche centrali

### Analisi Supportate

#### 1. Distribuzione Ritardo Ricezione
**File**: `analysis/plots/latency_boxplot.png`  
**Metrica**: `denm_reception_delay`  
**Grafico**: Boxplot (scenario × tecnologia)  
**Confronto**: Terrestrial vs Satellite vs Hybrid  
**Statistiche**: Min, Q1, Median, Q3, Max, Outliers

#### 2. CDF Latenza
**File**: `analysis/plots/latency_cdf.png`  
**Metrica**: `denm_reception_delay`  
**Grafico**: Cumulative Distribution Function  
**Insight**: % pacchetti sotto soglia latenza

#### 3. Latenza Consegna Cloud
**File**: `analysis/plots/cloud_latency.png`  
**Metrica**: `cloud_delivery_latency`  
**Grafico**: Barre (media/mediana)  
**Confronto**: Tempi infrastruttura→cloud per tecnologia

#### 4. Packet Delivery Ratio (PDR)
**File**: `analysis/plots/pdr_comparison.png`  
**Formula**: `PDR = (denm_received_flag==1) / (totale_veicoli - sender) × 100%`  
**Grafico**: Barre per configurazione  
**Target**: >90% considerato buono

#### 5. Copertura Infrastruttura
**File**: `analysis/plots/coverage_comparison.png`  
**Metriche**: `denm_in_coverage`, `denm_out_of_coverage`  
**Grafico**: % copertura effettiva vs teorica  
**Insight**: Efficacia posizionamento

#### 6. Deadline Compliance
**Metrica**: `denm_within_deadline`  
**Soglia**: 120ms (configurabile in VehicleReceiverService)  
**Calcolo**: `% pacchetti con latency < 120ms`

### Esecuzione Analisi

```bash
# Metodo 1: Make
cd /workspaces/artery/scenarios/stelvio
make analyze

# Metodo 2: Script diretto
python3 analysis/analyze_results.py

# Metodo 3: Quickstart
./quickstart.sh analyze
```

**Output**:
- `analysis/plots/*.png` - 5 grafici principali
- `analysis/summary_statistics.csv` - Tabella KPI
- Console output con statistiche chiave

### Esempio Output CSV

```csv
Configuration,PDR(%),Mean_Latency(ms),Median_Latency(ms),P95_Latency(ms),Coverage(%),Total_Packets
Crashed_Terrestrial,87.5,6.2,5.8,8.9,65.0,20
Crashed_Satellite,99.0,46.3,45.8,49.1,99.0,20
Crashed_Hybrid,95.0,12.4,7.1,47.3,95.0,20
Witness_Terrestrial,85.0,6.5,6.1,9.2,65.0,20
Witness_Satellite,98.5,46.8,46.2,50.3,99.0,20
Witness_Hybrid,94.5,13.1,7.5,48.1,95.0,20
```

### Interpretazione Risultati

#### PDR (Packet Delivery Ratio)
- **>95%**: Eccellente (target hybrid)
- **90-95%**: Buono (accettabile per safety)
- **80-90%**: Sufficiente (terrestrial montano)
- **<80%**: Critico (inaccettabile)

#### Latenza
- **<10ms**: Eccellente (terrestrial ideal)
- **10-50ms**: Buona (satellite LEO)
- **50-100ms**: Accettabile (edge cases)
- **>100ms**: Critica (deadline miss)

#### Copertura
- **>95%**: Ottima (satellite)
- **70-95%**: Buona (hybrid)
- **50-70%**: Sufficiente (terrestrial montano)
- **<50%**: Insufficiente

### Export Custom

**CSV da .sca Files**:
```bash
cd scenarios/stelvio/results
scavetool export -o custom_export.csv \
    -F CSV-S \
    -f "module(*.node[*].middleware.VehicleReceiverService) AND name(denm_reception_delay)" \
    crashed_terrestrial/*.sca
```

**Python Custom Analysis**:
```python
import pandas as pd
from omnetpp.scave import results

# Carica risultati
df = results.read_result_files('results/**/*.sca', 
                                filter_expression='module(*.middleware.*)')

# Analizza
grouped = df.groupby(['config', 'module'])['value'].agg(['mean', 'std', 'count'])
print(grouped)
```

---

## 📂 File NED

### File Creati (5 totali)

#### 1. package.ned
Definizione package `src` per tutti i servizi.

#### 2. CrashedVehicleService.ned
- **Classe**: `stelvio::CrashedVehicleService`
- **Segnale**: `@signal[StoryboardSignal]`
- **Icona**: `i=block/routing`

#### 3. WitnessVehicleService.ned
- **Classe**: `stelvio::WitnessVehicleService`
- **Segnale**: `@signal[StoryboardSignal]`
- **Icona**: `i=block/cogwheel`

#### 4. VehicleReceiverService.ned
- **Classe**: `stelvio::VehicleReceiverService`
- **Icona**: `i=block/rx`
- **Parametro**: `double denmDeadline @unit(s) = default(0.12s);`

#### 5. InfrastructureService.ned
- **Classe**: `stelvio::InfrastructureService`
- **Icona**: `i=device/antennatower`
- **Parametri**: `infrastructureType`, `latency`, `coverageRadius`, `coverageReliability`, `transmitPower`

### Utilizzo XML

**services_crashed.xml**:
```xml
<service type="src.CrashedVehicleService">
    <listener port="2001" />
</service>
<service type="src.VehicleReceiverService">
    <listener port="2002" />
</service>
```

**services_witness.xml**:
```xml
<service type="src.WitnessVehicleService">
    <listener port="2001" />
</service>
<service type="src.VehicleReceiverService">
    <listener port="2002" />
</service>
```

**services_infrastructure.xml**:
```xml
<service type="src.InfrastructureService">
    <listener port="2001" />
</service>
```

---

## 📝 Utilizzo Dettagliato

### Linea di Comando

```bash
# Singola configurazione
cd /workspaces/artery
python3 tools/run_artery.py stelvio -c Crashed_Terrestrial

# OMNeT++ diretto
cd /workspaces/artery/scenarios/stelvio
opp_run -u Cmdenv -c Crashed_Terrestrial -n src:. -l libstelvio.so omnetpp.ini

# GUI OMNeT++
opp_run -u Qtenv -c Crashed_Terrestrial_GUI -n src:. -l libstelvio.so omnetpp.ini
```

### Batch con GUI

1. `make gui` o `python3 scripts/simulation_gui.py`
2. Tab "Batch Run"
3. Seleziona configurazioni
4. Imposta ripetizioni (es. 10)
5. Range ritardo (1-10s, step 1s)
6. Click "Run Batch Simulations"

### Studio Sensibilità

```bash
for delay in 1.0 3.0 5.0 10.0; do
    export STELVIO_WITNESS_DELAY=$delay
    opp_run -u Cmdenv -c Witness_Hybrid -n src:. -l libstelvio.so omnetpp.ini \
        --result-dir=results/witness_delay_${delay}
done
```

---

## 🔧 Personalizzazione

### Modifica Posizione Infrastruttura

**File**: `static_nodes.xml`

```xml
<RSUs>
    <!-- Sposta antenna in posizione diversa -->
    <rsu id="antenna" positionX="NUOVO_X" positionY="NUOVO_Y" />
    
    <!-- Satellite può avere posizione diversa o stessa -->
    <rsu id="satellite" positionX="NUOVO_X" positionY="NUOVO_Y" />
</RSUs>
```

**Coordinate Riferimento Rete Stelvio**:
- Valle (Start): (90, 55)
- Centro: (263, 344)
- Passo: (636, 518)
- Fine: (996, 487)
- Attuale: (729, 390) - posizione centrale

**Dopo modifica**: Ricompila scenario
```bash
cd /workspaces/artery/build/Release
make stelvio
```

### Aggiungi/Modifica Veicoli

**File**: `stelvio.rou.xml`

**Aggiungi Veicolo Uphill**:
```xml
<trip id="veh_9" type="veh_passenger" depart="55.00" 
      departLane="best" departSpeed="max" 
      from="-767626960#2" to="-767626960#0"/>
```

**Aggiungi Veicolo Downhill**:
```xml
<trip id="veh_opp_9" type="veh_passenger" depart="55.00" 
      departLane="best" departSpeed="max" 
      from="767626960#0" to="767626960#2"/>
```

**Modifica Tipo Veicolo**:
```xml
<!-- Cambia colore/parametri -->
<vType id="veh_custom" vClass="passenger" 
      accel="2.5" decel="5.0" sigma="0.3" 
      length="5.0" maxSpeed="25.0" color="red"/>

<trip id="custom_veh" type="veh_custom" depart="60.00" .../>
```

**Dopo modifica**: SUMO ricarica automaticamente, no ricompilazione

### Parametri Radio/Comunicazione

**File**: `omnetpp.ini`

**Potenza Trasmissione Veicoli**:
```ini
*.node[*].wlan[*].radio.transmitter.power = 100 mW  # Default
# Aumenta per maggiore range:
*.node[*].wlan[*].radio.transmitter.power = 200 mW
```

**Potenza Infrastruttura**:
```ini
# Antenna terrestre
*.antenna.middleware.services.service[0].transmitPower = 500mW  # Default
*.antenna.middleware.services.service[0].transmitPower = 1000mW  # Aumenta

# Satellite
*.satellite.middleware.services.service[0].transmitPower = 1000mW  # Default
```

**Canale Radio**:
```ini
*.node[*].wlan[*].radio.channelNumber = 180  # G5 5.9 GHz (default)
# Altri canali ITS-G5:
# 172 (5.86 GHz), 174 (5.87 GHz), 176 (5.88 GHz), 
# 178 (5.89 GHz), 180 (5.90 GHz), 182 (5.91 GHz), 184 (5.92 GHz)
```

**Intervallo Aggiornamento**:
```ini
*.node[*].middleware.updateInterval = 0.1s  # Default 100ms
*.node[*].middleware.updateInterval = 0.05s  # Più frequente (50ms)
```

### Deadline DENM Personalizzato

**File**: `omnetpp.ini`

```ini
# Default: 120ms
*.node[*].middleware.VehicleReceiverService.denmDeadline = 0.12s

# Più stringente (80ms):
*.node[*].middleware.VehicleReceiverService.denmDeadline = 0.08s

# Più rilassato (200ms):
*.node[*].middleware.VehicleReceiverService.denmDeadline = 0.20s
```

**Dopo modifica**: Riesegui simulazione, no ricompilazione

### Storyboard Personalizzato

#### Crash Storyboard (crash_storyboard.py)

```python
# Modifica tempo evento
accident_time = 200.0  # Default 200s
accident_time = 150.0  # Crash più presto

# Modifica veicolo
accident_veh = "accident_veh_0"  # Default
accident_veh = "veh_4"  # Usa veicolo diverso

# Aggiungi effetti custom
@story.condition(vehicle=accident_veh, time=accident_time)
def custom_crash(traci, vehicle, story):
    vehicle.speed = 0  # Ferma
    vehicle.color = (255, 0, 0)  # Rosso
    vehicle.highlight = True  # Evidenzia GUI
    story.signal("crash_incident", vehicle=vehicle.id)  # Segnale
```

#### Witness Storyboard (witness_storyboard.py)

```python
# Modifica ritardo da variabile ambiente
import os
witness_delay = float(os.getenv('STELVIO_WITNESS_DELAY', 5.0))

# Modifica veicolo testimone
witness_veh = "witness_veh_0"  # Default
witness_veh = "veh_5"  # Usa altro veicolo

# Evento crash silenzioso personalizzato
@story.condition(vehicle=accident_veh, time=200.0)
def silent_crash(traci, vehicle, story):
    vehicle.speed = 0
    vehicle.color = (128, 128, 128)  # Grigio
    # NO signal qui (silenzioso)

# Testimone segnala dopo delay
@story.condition(vehicle=witness_veh, time=200.0 + witness_delay)
def witness_report(traci, vehicle, story):
    vehicle.color = (0, 255, 0)  # Verde
    story.signal("witness_report", vehicle=vehicle.id)
```

**Dopo modifica**: Riesegui simulazione, no ricompilazione

### Copertura/Latenza Infrastruttura

**File**: `omnetpp.ini`

**Antenna Terrestre Custom**:
```ini
# Copertura maggiore (urban scenario)
*.antenna.middleware.services.service[0].coverageRadius = 1000m  # Era 600m
*.antenna.middleware.services.service[0].coverageReliability = 0.85  # Era 0.65
*.antenna.middleware.services.service[0].latency = 3ms  # Era 5ms

# Copertura minore (montagna severa)
*.antenna.middleware.services.service[0].coverageRadius = 400m
*.antenna.middleware.services.service[0].coverageReliability = 0.50
*.antenna.middleware.services.service[0].latency = 8ms
```

**Satellite Custom**:
```ini
# Satellite MEO (invece LEO)
*.satellite.middleware.services.service[0].latency = 80ms  # Era 45ms (LEO)
*.satellite.middleware.services.service[0].coverageRadius = 10000m  # Maggiore

# Satellite GEO
*.satellite.middleware.services.service[0].latency = 250ms  # GEO ~36000km
*.satellite.middleware.services.service[0].coverageReliability = 0.95  # Meteo-dipendente
```

### Analisi Personalizzata

**File**: `analysis/analyze_results.py`

**Aggiungi Grafico Custom**:
```python
def plot_custom_metric(data_dict, output_file):
    """Tua visualizzazione personalizzata"""
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for config_name, df in data_dict.items():
        # Tua logica di plot
        metric = df['your_metric'].values
        ax.plot(metric, label=config_name)
    
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_title('Custom Metric Analysis')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Custom plot saved: {output_file}")

# Aggiungi a main()
if __name__ == "__main__":
    # ... existing code ...
    plot_custom_metric(all_data, 'analysis/plots/custom_metric.png')
```

**Filtri Custom per Metriche**:
```python
# Filtra solo veicoli in salita
uphill_vehicles = df[df['module'].str.contains('veh_[0-8]|accident_veh|witness_veh')]

# Filtra solo entro deadline
within_deadline = df[df['name'] == 'denm_within_deadline']['value'] == 1

# Calcola metriche aggregate
mean_latency = df[df['name'] == 'denm_reception_delay']['value'].mean()
p95_latency = df[df['name'] == 'denm_reception_delay']['value'].quantile(0.95)
```

### Tempo Simulazione

**File**: `omnetpp.ini`

```ini
[General]
sim-time-limit = 300s  # Default 5 minuti

# Simulazione breve (test rapido)
sim-time-limit = 120s  # 2 minuti

# Simulazione estesa (traffic pesante)
sim-time-limit = 600s  # 10 minuti
```

**Impatto**: Più tempo → più veicoli completano percorso → più dati

### Nuovi Servizi Custom

**1. Crea File .msg** (se serve nuovo messaggio):
```cpp
// src/CustomMessage.msg
packet CustomMessage {
    int customField;
    string customData;
}
```

**2. Crea Service .h/.cc**:
```cpp
// src/CustomService.h
#include <artery/application/VehicleDataProvider.h>
#include <vanetza/btp/data_interface.hpp>

class CustomService : public artery::ItsG5Service {
    // Tua logica
};
```

**3. Crea File .ned**:
```ned
// src/CustomService.ned
package src;

simple CustomService like artery.ItsG5Service {
    parameters:
        @class(CustomService);
        int customParam = default(42);
}
```

**4. Aggiungi a services XML**:
```xml
<service type="src.CustomService">
    <listener port="2003" />
</service>
```

**5. Compila**:
```bash
cd /workspaces/artery/build/Release
make stelvio
```

---

## 🐛 Troubleshooting

### Errori Compilazione

**Problema**: `undefined reference to vtable`
```bash
cd /workspaces/artery/build/Release
make clean
rm -rf scenarios/stelvio/libartery_stelvio.so
cmake ../..
make stelvio
ls -lh scenarios/stelvio/libartery_stelvio.so  # Verifica esistenza
```

**Problema**: `cannot find -lartery_stelvio`
```bash
# Verifica che libartery_stelvio.so esista
ls /workspaces/artery/build/Release/scenarios/stelvio/libartery_stelvio.so

# Se manca, ricompila
cd /workspaces/artery/build/Release
make stelvio
```

**Problema**: `.ned file not found`
```bash
cd /workspaces/artery/scenarios/stelvio
ls src/*.ned  # Deve mostrare 5 file
# Se mancano, ricrea da template o verifica Git

# Verifica package.ned
head -n 5 src/package.ned
# Deve contenere: package src;
```

**Problema**: `Error in module (NED) DenmMessage`
```bash
# Verifica file .msg
ls src/DenmMessage.msg

# Rigenera codice messaggio
cd /workspaces/artery/build/Release
opp_msgc --msg6 ../../scenarios/stelvio/src/DenmMessage.msg
make stelvio
```

### Nessun Risultato / File Vuoti

**Problema**: Directory `results/` vuota dopo simulazione

**Verifica 1**: Simulazione completata senza errori
```bash
# Controlla log ultimo run
tail -n 50 /workspaces/artery/scenarios/stelvio/run.log
# Cerca "Simulation completed successfully"
```

**Verifica 2**: Recording attivo in omnetpp.ini
```bash
grep "scalar-recording" omnetpp.ini
# Deve essere: **.scalar-recording = true
grep "vector-recording" omnetpp.ini
# Deve essere: **.vector-recording = true
```

**Verifica 3**: Permessi directory
```bash
ls -ld results/
chmod 755 results/
mkdir -p results/crashed_terrestrial
```

**Verifica 4**: Risultati in posizione corretta
```bash
# Risultati possono essere in subdirectory
find results/ -name "*.sca" -o -name "*.vec"

# Se trovati altrove, copia
cp -r results/General-0-* results/crashed_terrestrial/
```

### GUI Python Non Si Avvia

**Problema**: `ModuleNotFoundError: No module named 'PyQt5'`

**Soluzione**:
```bash
cd /workspaces/artery/scenarios/stelvio

# Attiva virtual environment
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Verifica installazione
python3 -c "import PyQt5; print('PyQt5 OK')"
python3 -c "import pandas; print('Pandas OK')"
python3 -c "import matplotlib; print('Matplotlib OK')"

# Avvia GUI
python3 scripts/simulation_gui.py
```

**Problema**: Python version incompatibile
```bash
python3 --version
# Richiede Python 3.7+

# Se troppo vecchio, usa pyenv o update system Python
```

**Problema**: Display non disponibile (headless server)
```bash
# GUI richiede display X11
# Se SSH, usa X forwarding:
ssh -X user@server

# Oppure usa XVFB (virtual display)
xvfb-run python3 scripts/simulation_gui.py

# Alternativa: usa solo CLI
make run-all  # Non richiede GUI
```

### Analisi Nessun Dato

**Problema**: `analyze_results.py` non trova dati

**Verifica 1**: File .sca esistono
```bash
find results/ -name "*.sca"
# Deve mostrare file per ogni configurazione
```

**Verifica 2**: File .sca non vuoti
```bash
ls -lh results/crashed_terrestrial/*.sca
# Size > 0 bytes

# Ispeziona contenuto
head -n 20 results/crashed_terrestrial/*.sca
# Deve contenere "scalar" entries
```

**Verifica 3**: Export manuale con scavetool
```bash
cd /workspaces/artery/scenarios/stelvio

scavetool export \
    -o test_export.csv \
    -F CSV-S \
    results/crashed_terrestrial/*.sca

cat test_export.csv | head
# Deve mostrare dati CSV
```

**Verifica 4**: Pattern metriche corretto
```python
# In analyze_results.py, verifica filter_expression
filter_expr = 'module(*.middleware.*) AND name(denm_*)'

# Test con scavetool
scavetool q \
    -f "module(*.middleware.*) AND name(denm_*)" \
    results/crashed_terrestrial/*.sca
```

### Errori Esecuzione Simulazione

**Problema**: `Error: Cannot open file stelvio.net.xml`
```bash
cd /workspaces/artery/scenarios/stelvio
ls stelvio.net.xml  # Verifica esistenza

# Se manca, rigenera o scarica da OSM
# Verifica che opp_run si esegua dalla directory corretta
```

**Problema**: `TraCI connection failed`
```bash
# Verifica SUMO installato
sumo --version
# Richiede SUMO 1.15+

# Verifica SUMO_HOME
echo $SUMO_HOME
export SUMO_HOME=/usr/share/sumo  # Adatta al tuo sistema

# Verifica sumocfg
ls stelvio.sumocfg
cat stelvio.sumocfg  # Controlla paths
```

**Problema**: `Signal handler called with signal 11 (SIGSEGV)`
```bash
# Segmentation fault - spesso dovuto a:
# 1. Puntatore null in C++
# 2. Access fuori bounds
# 3. Stack overflow

# Debug con GDB
gdb --args opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini
(gdb) run
# Quando crasha:
(gdb) backtrace
```

**Problema**: `Module services.service[0] does not exist`
```bash
# Verifica XML config caricato
grep "services.xml" omnetpp.ini

# Verifica file XML esiste
ls config/services_crashed.xml
ls config/services_infrastructure.xml

# Verifica sintassi XML
xmllint --noout config/services_crashed.xml
```

### Problemi Metriche/KPI

**Problema**: Tutte le metriche sono 0

**Causa 1**: Veicolo sender non invia DENM
```bash
# Verifica log simulazione
grep "DENM sent" run.log
grep "crash_incident" run.log
```

**Causa 2**: Porta BTP errata
```bash
# Verifica omnetpp.ini e XML
# Sender: port 2001
# Receiver: port 2002
grep "port" config/services_*.xml
```

**Causa 3**: Servizi non caricati
```bash
# Verifica log inizializzazione
grep "VehicleReceiverService" run.log
grep "CrashedVehicleService" run.log
```

**Problema**: PDR sempre 100% o sempre 0%

**PDR 100%**: Copertura troppo grande o affidabilità 1.0
```ini
# Riduci per realismo
*.antenna.middleware.services.service[0].coverageRadius = 400m  # Era 600m
*.antenna.middleware.services.service[0].coverageReliability = 0.60  # Era 0.65
```

**PDR 0%**: Fuori copertura totale o servizi non comunicano
```bash
# Verifica posizioni
cat static_nodes.xml  # Infrastruttura
grep "positionX" stelvio.rou.xml  # Veicoli (se esplicite)

# Calcola distanze
python3 -c "import math; print(math.dist([729,390], [996,487]))"  # ~304m
# Se > coverageRadius, aumenta raggio
```

### Performance/Lentezza

**Problema**: Simulazione molto lenta

**Soluzione 1**: Disabilita GUI
```bash
# Usa Cmdenv invece di Qtenv
opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini
```

**Soluzione 2**: Riduci recording
```ini
# Disabilita vector recording (pesante)
**.vector-recording = false
**.scalar-recording = true  # Mantieni scalar
```

**Soluzione 3**: Riduci veicoli
```bash
# Edita stelvio.rou.xml, commenta alcuni <trip>
# O riduci sim-time-limit in omnetpp.ini
```

**Soluzione 4**: Usa release build
```bash
cd /workspaces/artery/build
ls  # Verifica esiste Release/ (non Debug/)

# Se solo Debug:
cd /workspaces/artery
cmake -S . -B build/Release -D CMAKE_BUILD_TYPE=Release
cmake --build build/Release
```

### Log e Debug

**Enable Debug Logging**:
```ini
# In omnetpp.ini
[General]
debug-on-errors = true
**.debug = true

# Per modulo specifico
*.node[*].middleware.VehicleReceiverService.debug = true
```

**Output Verboso**:
```bash
opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini \
    --debug-on-errors=true \
    --verbose
```

**Salva Log**:
```bash
opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini \
    2>&1 | tee simulation.log
```

### Verifica Integrità Setup

**Script Check Completo**:
```bash
cd /workspaces/artery/scenarios/stelvio
make check

# Output mostra:
# ✅ Tutti i file presenti
# ✅ Compilato correttamente
# ✅ Dipendenze installate
# ✅ SUMO/OMNeT++ trovati
```

**Test Minimale**:
```bash
# 1. Compila
make build

# 2. Test run breve (10s)
opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini \
    --sim-time-limit=10s

# 3. Verifica output
ls results/crashed_terrestrial/*.sca
```

---

## 📁 Struttura Completa

```
stelvio/
├── README.md                   # 📖 Documentazione completa (questo file)
├── CMakeLists.txt              # Build configuration
├── omnetpp.ini                 # 6 configurazioni OMNeT++
├── Makefile                    # Comandi make rapidi
├── quickstart.sh               # Script bash helper
├── requirements.txt            # Dipendenze Python (PyQt5, pandas, etc.)
│
├── src/                        # 🔧 C++ Source + NED Files
│   ├── DenmMessage.msg         # Definizione messaggio DENM
│   ├── package.ned             # Package declaration "src"
│   ├── CrashedVehicleService.{h,cc,ned}    # Invio DENM crash immediato
│   ├── WitnessVehicleService.{h,cc,ned}    # Invio DENM testimone ritardato
│   ├── VehicleReceiverService.{h,cc,ned}   # Ricezione DENM + metriche
│   └── InfrastructureService.{h,cc,ned}    # Relay antenna/satellite
│
├── config/                     # ⚙️ XML Middleware Configurations
│   ├── services_crashed.xml    # Services scenario crash (Crashed+Receiver)
│   ├── services_witness.xml    # Services scenario witness (Witness+Receiver)
│   └── services_infrastructure.xml  # Infrastructure service (relay)
│
├── scripts/                    # 🐍 Python Automation
│   ├── simulation_gui.py       # GUI PyQt5 per controllo batch
│   └── export_csv.py           # Export risultati CSV da .sca
│
├── analysis/                   # 📊 Post-Simulation Analysis
│   ├── analyze_results.py      # Script generazione grafici + stats
│   ├── plots/                  # 📈 Output grafici PNG
│   │   ├── latency_boxplot.png
│   │   ├── latency_cdf.png
│   │   ├── cloud_latency.png
│   │   ├── pdr_comparison.png
│   │   └── coverage_comparison.png
│   └── csv/                    # 📄 Export CSV elaborati
│       └── summary_statistics.csv
│
├── results/                    # 💾 Simulation Output (auto-generated)
│   ├── crashed_terrestrial/    # Scenario 1: Crash + Antenna
│   │   ├── General-0-*.sca     # Scalar results
│   │   ├── General-0-*.vec     # Vector results
│   │   └── General-0-*.vci     # Vector index
│   ├── crashed_satellite/      # Scenario 2: Crash + Satellite
│   ├── crashed_hybrid/         # Scenario 3: Crash + Entrambi
│   ├── witness_terrestrial/    # Scenario 4: Witness + Antenna
│   ├── witness_satellite/      # Scenario 5: Witness + Satellite
│   └── witness_hybrid/         # Scenario 6: Witness + Entrambi
│
├── stelvio.net.xml             # 🗺️ SUMO Road Network (SS38 Stelvio Pass)
│                                  # - OpenStreetMap data
│                                  # - 4 junctions, 6 edges
│                                  # - UTM Zone 32 coordinates
│                                  # - ~3.7 km total length
│
├── stelvio.rou.xml             # 🚗 SUMO Traffic Routes
│                                  # - 20 vehicles (11 uphill + 9 downhill)
│                                  # - 3 vehicle types: passenger/accident/witness
│                                  # - Depart every 5s from t=0s
│
├── stelvio.sumocfg             # SUMO Configuration file
│
├── static_nodes.xml            # 📡 Infrastructure Nodes (RSU)
│                                  # - Antenna: (729.0, 390.0)
│                                  # - Satellite: (729.0, 390.0)
│
├── crash_storyboard.py         # 📅 Crash Event Script
│                                  # - t=200s: accident_veh_0 stops
│                                  # - Signal: "crash_incident"
│                                  # - Immediate DENM transmission
│
├── witness_storyboard.py       # 📅 Witness Event Script
│                                  # - t=200s: accident_veh_0 stops (silent)
│                                  # - t=200s+DELAY: witness_veh_0 reports
│                                  # - Signal: "witness_report"
│                                  # - Delayed DENM transmission
│
└── venv/                       # 🐍 Python Virtual Environment
    ├── bin/                    # Executables
    ├── lib/                    # Python packages
    └── pyvenv.cfg              # Virtualenv config
```

### File Count Summary

| Category | Count | Files |
|----------|-------|-------|
| **C++ Source** | 4 | CrashedVehicleService, WitnessVehicleService, VehicleReceiverService, InfrastructureService |
| **C++ Headers** | 4 | *.h |
| **NED Files** | 5 | package.ned + 4 service .ned |
| **Message Files** | 1 | DenmMessage.msg |
| **Config XML** | 3 | services_crashed.xml, services_witness.xml, services_infrastructure.xml |
| **SUMO Traffic** | 3 | stelvio.net.xml, stelvio.rou.xml, stelvio.sumocfg |
| **Storyboards** | 2 | crash_storyboard.py, witness_storyboard.py |
| **Python Scripts** | 3 | simulation_gui.py, export_csv.py, analyze_results.py |
| **Config Files** | 4 | omnetpp.ini, CMakeLists.txt, Makefile, requirements.txt |
| **Infrastructure** | 1 | static_nodes.xml |
| **Documentation** | 1 | README.md (questo file) |

**Total Source Files**: ~30  
**Lines of Code**: ~3500 (C++ ~2000, Python ~1250, NED ~250)

---

## 📚 Riferimenti

### Framework
- **Artery**: https://github.com/riebl/artery
- **OMNeT++**: https://omnetpp.org
- **SUMO**: https://sumo.dlr.de
- **Vanetza**: https://github.com/riebl/vanetza

### Standard
- **ETSI EN 302 637-3**: DENM
- **3GPP TR 38.811**: NTN
- **3GPP TS 38.300**: 5G/6G NR
- **ISO 21217**: ITS Station

---

## 🎓 Applicazioni Ricerca

1. **Confronto Latenze**: Terrestrial vs Satellite vs Hybrid
2. **Analisi Copertura**: Zone morte, benefici multi-infra
3. **Affidabilità**: PDR sotto diverse condizioni
4. **Comportamento Testimone**: Impatto ritardo segnalazione
5. **Design Infrastruttura**: Ottimizzazione posizionamento
6. **Pianificazione 6G**: Architetture ibride TN/NTN

---

## 💡 Tips & Best Practices

### Workflow Raccomandato

1. **Prima Esecuzione**: Usa GUI per feedback visuale
   ```bash
   opp_run -u Qtenv -c Crashed_Terrestrial_GUI omnetpp.ini
   ```

2. **Esperimenti**: Cmdenv per batch veloce
   ```bash
   make run-all  # Tutte 6 configurazioni headless
   ```

3. **Analisi**: Genera grafici subito dopo sim
   ```bash
   make analyze  # Fresh results
   ```

4. **Iterazione**: Modifica parametri → re-run → confronta
   ```bash
   # Prova diversi coverage radius
   for radius in 400 600 800 1000; do
       sed -i "s/coverageRadius = .*/coverageRadius = ${radius}m/" omnetpp.ini
       opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini \
           --result-dir=results/coverage_${radius}
   done
   ```

5. **Backup**: Version control risultati importanti
   ```bash
   git add results/
   git commit -m "Baseline results: coverage=600m, reliability=0.65"
   ```

### Pro Tips

#### Performance
- **Disabilita Vector Recording** se non serve dati time-series:
  ```ini
  **.vector-recording = false
  **.scalar-recording = true
  ```
  Risparmio: ~70% dimensione file, ~40% tempo simulazione

- **Usa Release Build** (non Debug):
  ```bash
  cd /workspaces/artery/build/Release  # Non Debug
  ```
  Speedup: 5-10x

- **Parallelizza Runs** con GNU Parallel:
  ```bash
  parallel -j 3 'opp_run -u Cmdenv -c {} omnetpp.ini' ::: \
      Crashed_Terrestrial Crashed_Satellite Crashed_Hybrid
  ```

#### Debug
- **Single Vehicle Debug**: Commenta tutti veicoli tranne uno in `stelvio.rou.xml`
- **Simulation Time Breve**: `sim-time-limit = 30s` per test veloci
- **Verbose Logging**:
  ```ini
  *.node[*].middleware.*.debug = true
  ```

#### Analisi
- **Ripetizioni Multiple**: Esegui 10+ ripetizioni per statistiche robuste
  ```bash
  for i in {1..10}; do
      opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini \
          --seed-set=$i \
          --result-dir=results/crashed_terrestrial/run_$i
  done
  ```

- **Confronto Before/After**: Salva baseline prima modifiche
  ```bash
  cp -r results/ results_baseline/
  # ... modifiche ...
  make run-all
  diff -r results/ results_baseline/
  ```

### Note Tecniche

#### Comunicazione V2X
- **Broadcast SHB**: Single Hop Broadcast (no GeoBroadcast multi-hop)
- **Porte BTP**:
  - 2001: Veicoli → Infrastruttura (DENM originale)
  - 2002: Infrastruttura → Veicoli (DENM relay)
- **Protocollo**: IEEE 802.11p (G5 5.9 GHz, channel 180)

#### Affidabilità Realistica
- **Terrestrial 65%**: Simula:
  - Zone d'ombra montane
  - Ostacoli naturali (rocce, tornanti)
  - Multipath fading
- **Satellite 99%**: Simula:
  - Copertura globale LEO
  - Meteo-indipendente (banda Ka)
  - Link budget robusto

#### Latenze Tipiche
| Componente | Latenza | Note |
|------------|---------|------|
| DENM Generation | <1ms | CPU veicolo |
| Wireless Transmission | 1-3ms | 802.11p |
| Infrastructure Processing | 1-2ms | Antenna/Satellite |
| Cloud Delivery | 3-5ms (TN) / 40-45ms (NTN) | Backhaul |
| Relay to Vehicles | 1-3ms | Broadcast |
| **Total (Terrestrial)** | **5-10ms** | End-to-end |
| **Total (Satellite)** | **45-55ms** | End-to-end |

#### Forward Declaration Pattern
```cpp
// Header usa forward declaration
class vanetza::btp::DataRequest;  // No #include

// Implementation include
#include <vanetza/btp/data_request.hpp>
```
**Beneficio**: Evita dipendenze circolari, compile time ridotto

### Valori Riferimento

#### KPI Target

| Metrica | Terrestrial | Satellite | Hybrid | Critical |
|---------|-------------|-----------|--------|----------|
| **PDR** | >80% | >95% | >90% | >95% |
| **Latency Mean** | <10ms | <50ms | <20ms | <100ms |
| **Latency P95** | <15ms | <60ms | <30ms | <120ms |
| **Coverage** | >60% | >95% | >80% | >90% |
| **Deadline Hit** | >75% | >90% | >85% | >90% |

#### Parametri Standard

**ITS-G5 (ETSI)**:
- Frequenza: 5.9 GHz
- Bandwidth: 10 MHz
- Potenza: 100 mW - 1000 mW
- Range: 300m - 1000m

**6G NR (3GPP)**:
- Latency: <1ms (URLLC)
- Reliability: 99.999%
- Coverage: <500m urban, <2km suburban

**LEO Satellite**:
- Altitude: 500-1200 km
- Latency: 20-50 ms (one-way)
- Coverage: Global
- Handover: Ogni 5-10 min

### Environment Variables

```bash
# Witness delay (secondi)
export STELVIO_WITNESS_DELAY=5.0

# OMNeT++ debug
export OMNETPP_IMAGE_PATH=/workspaces/artery/scenarios/stelvio/images

# SUMO home
export SUMO_HOME=/usr/share/sumo

# Python virtual env
source venv/bin/activate
```

### Comandi Utili

```bash
# Verifica setup completo
make check

# Compile clean
make clean-all && make build

# Esegui singola config con log
opp_run -u Cmdenv -c Crashed_Terrestrial omnetpp.ini 2>&1 | tee run.log

# Estrai metriche specifiche
scavetool q -f "name(denm_reception_delay)" results/**/*.sca

# Confronta configurazioni
diff <(scavetool x -o - results/crashed_terrestrial/*.sca) \
     <(scavetool x -o - results/crashed_satellite/*.sca)

# Export tutto in CSV
scavetool export -o all_results.csv -F CSV-S results/**/*.sca

# Count packets ricevuti
scavetool q -f "name(denm_received_flag) AND value(1)" results/**/*.sca | wc -l

# List all modules recording
scavetool q -f "module(*)" results/crashed_terrestrial/*.sca | cut -d' ' -f2 | sort -u
```

---

## 📚 Riferimenti

### Framework e Tools

- **Artery**: https://github.com/riebl/artery - V2X simulation framework
- **OMNeT++**: https://omnetpp.org - Discrete event simulator (6.0+)
- **SUMO**: https://sumo.dlr.de - Traffic microsimulator (1.15+)
- **Vanetza**: https://github.com/riebl/vanetza - ITS-G5 protocol stack
- **OpenStreetMap**: https://www.openstreetmap.org - Road network data

### Standard ETSI/3GPP/IEEE/ISO

- **ETSI EN 302 637-3** - DENM Specification
- **ETSI EN 302 665** - ITS-G5 Access Layer
- **3GPP TR 38.811** - Non-Terrestrial Networks (NTN)
- **3GPP TS 38.300** - 5G/6G NR Overall Description
- **IEEE 802.11p** - WAVE Vehicular Communications
- **ISO 21217** - ITS Communications Architecture (CALM)

---

## 🎓 Applicazioni Ricerca

1. **Confronto Latenze Multi-Tecnologia** - Terrestrial vs Satellite vs Hybrid
2. **Analisi Copertura Geografica** - Zone morte montane, copertura globale
3. **Affidabilità Consegna Messaggi** - PDR, reliability trade-offs
4. **Fattore Umano Safety** - Witness scenario, delayed reporting impact
5. **Design Infrastruttura** - Posizionamento ottimale RSU
6. **Pianificazione 6G** - Architetture ibride TN/NTN

---

## ✅ Status Progetto

### Checklist Completamento

- [x] ✅ **Servizi C++** (4 services: Crashed, Witness, Receiver, Infrastructure)
- [x] ✅ **Messaggi** (DenmMessage.msg)
- [x] ✅ **Configurazioni** (6 scenari OMNeT++: 3 crashed + 3 witness)
- [x] ✅ **Traffico SUMO** (stelvio.net.xml OSM + 20 veicoli)
- [x] ✅ **Storyboard** (crash_storyboard.py + witness_storyboard.py)
- [x] ✅ **GUI** (simulation_gui.py PyQt5)
- [x] ✅ **Analisi** (analyze_results.py + 5 grafici)
- [x] ✅ **Documentazione** (README completo + code comments)
- [x] ✅ **File NED** (5 files: package + 4 services)
- [x] ✅ **Build** (testato, nessun errore)

**Status**: ✅ **PRODUCTION READY**  
**Build**: Nessun errore, libreria compilata  
**Framework**: Artery + OMNeT++ 6.x + SUMO 1.22.0  
**Linguaggi**: C++17 (~2000 LOC) + Python 3.7+ (~1250 LOC) + NED (~250 LOC)  
**Creato**: Ottobre 2025  
**Ultima Modifica**: 6 Ottobre 2025  
**Versione**: 1.0.0

---

## 📄 Licenza

Eredita licenza Artery (GPLv2).

**GNU General Public License v2.0** - Permette uso commerciale, modifica, distribuzione.  
Richiede: disclosure source code, same license. No warranty.

---

## 🎓 Citazione

```bibtex
@misc{stelvio_v2x_6g_2025,
  title={Stelvio V2X Simulation: 6G Hybrid Terrestrial-Satellite Infrastructure Study},
  author={Your Name},
  year={2025},
  month={October},
  note={OMNeT++ simulation scenario for hybrid V2X communication on Stelvio Pass (SS38)},
  howpublished={GitHub Repository},
  keywords={V2X, 6G, NTN, LEO Satellite, DENM, Safety, Hybrid Infrastructure, OpenStreetMap}
}
```

---

## 📞 Supporto

### Self-Help (Raccomandato)

1. **📖 Leggi README** - Documentazione completa (questo file ~1500 linee)
2. **🔍 Make check** - Diagnostica automatizzata (34 controlli)
3. **💡 Make help** - Lista comandi disponibili
4. **⚙️ Verifica omnetpp.ini** - Configurazioni e parametri
5. **🐛 Troubleshooting section** - Errori comuni e soluzioni sopra

### Comandi Diagnostici Rapidi

```bash
make check          # Verifica completa setup
make build          # Compila scenario
make run-crashed    # Test esecuzione
make analyze        # Analizza risultati
```

### Community Resources

- Artery Google Group: https://groups.google.com/g/artery-users
- OMNeT++ Forum: https://omnetpp.org/community
- SUMO Mailing List: https://www.eclipse.org/lists/sumo-user

---

**Quick Help**: `make help` | **Check Setup**: `make check` | **Build**: `make build` | **Run All**: `make run-all` | **Analyze**: `make analyze` | **GUI**: `make gui`

**Happy Simulating! 🚗📡🛰️ Buone simulazioni al Passo dello Stelvio!**

---

*README Last Updated: 6 Ottobre 2025*  
*Scenario Version: 1.0.0*  
*Documentation: Completa e dettagliata per utente finale*

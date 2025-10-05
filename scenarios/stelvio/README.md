# Stelvio V2X Simulation - 6G Hybrid Infrastructure Study

**Simulazione completa V2X per lo studio di trasmissione DENM in infrastruttura ibrida 6G al Passo dello Stelvio**

---

## 📋 Indice Rapido

- [Panoramica](#-panoramica) | [Quick Start](#-quick-start) | [Architettura](#-architettura)
- [Servizi](#-servizi-implementati) | [Configurazioni](#-configurazioni-simulazione) | [Metriche](#-metriche-e-analisi)
- [File NED](#-file-ned) | [Personalizzazione](#-personalizzazione) | [Troubleshooting](#-troubleshooting)

---

## 🎯 Panoramica

Simulazione comunicazione Vehicle-to-Cloud (V2C) per notifiche incidenti (DENM) al **Passo dello Stelvio** con:

- **6G Terrestrial Network (TN)** - Antenna terrestre (5ms, 600m, 65% affidabilità)
- **LEO Satellite (NTN)** - Satellite LEO (45ms, 5000m, 99% affidabilità)  
- **Architettura Ibrida** - Entrambe con fallback

### Caratteristiche Principali

✅ **2 Scenari**: Crashed (immediato) + Witness (ritardato)  
✅ **3 Infrastrutture**: Terrestrial, Satellite, Hybrid  
✅ **6 Configurazioni**: Tutte le combinazioni  
✅ **GUI Automatizzata**: Pannello Python per batch  
✅ **Analisi Completa**: KPI e visualizzazioni  
✅ **Codice Pulito**: Modulare e documentato  

---

## 🚀 Quick Start

```bash
# 1. Setup (prima volta)
cd /workspaces/artery/scenarios/stelvio
make install-deps    # Crea venv e installa dipendenze Python
make check          # Verifica (34 controlli)
make build          # Compila

# 2. Esegui
make run-crashed    # Scenario crashed
# oppure
./quickstart.sh run-all  # Tutte le 6 configurazioni

# 3. Analizza
make analyze        # Genera grafici in analysis/plots/
# oppure
make gui            # GUI interattiva
```

### Comandi Rapidi

| Comando | Descrizione |
|---------|-------------|
| `make help` | Mostra tutti i comandi |
| `make check` | Verifica setup |
| `make build` | Compila scenario |
| `make run-crashed` | Esegui scenari crashed |
| `make run-witness` | Esegui scenari witness |
| `make analyze` | Genera grafici |
| `make gui` | Avvia GUI |
| `make clean` | Pulisci risultati |

---

## 🏗️ Architettura

### Flusso Comunicazione

```
[Veicolo Crashed/Witness]
         ↓ (DENM via BTP:2001)
         |
    +---------+---------+
    ↓                   ↓
[Antenna]          [Satellite]
 (5ms, 600m)        (45ms, 5000m)
  65% reliable       99% reliable
    ↓                   ↓
    +-------+-------+
            ↓ (Relay via BTP:2002)
    [Altri Veicoli]
         ↓
   [Metriche PDR, Latenza, Copertura]
```

### Struttura Moduli

```
stelvio/
├── src/                        # C++ Services
│   ├── DenmMessage.msg         # Definizione messaggio
│   ├── CrashedVehicleService   # Invio immediato
│   ├── WitnessVehicleService   # Invio ritardato
│   ├── InfrastructureService   # Relay infrastruttura
│   ├── VehicleReceiverService  # Ricezione + metriche
│   └── *.ned                   # File NED (5 totali)
│
├── config/                     # Configurazioni XML
│   ├── services_crashed.xml
│   ├── services_witness.xml
│   └── services_infrastructure.xml
│
├── scripts/                    # Automazione Python
│   ├── simulation_gui.py       # GUI controllo
│   └── export_csv.py           # Export risultati
│
├── analysis/                   # Analisi dati
│   ├── analyze_results.py      # Grafici e statistiche
│   └── plots/                  # Output PNG
│
├── omnetpp.ini                 # 6 configurazioni
├── crash_storyboard.py         # Evento crash t=200s
├── witness_storyboard.py       # Evento witness t=200s+delay
└── results/                    # Output simulazioni
```

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

| ID | Nome | Scenario | Infrastruttura | Latenza | Use Case |
|----|------|----------|----------------|---------|----------|
| 1 | `Crashed_Terrestrial` | Immediato | Antenna | ~5ms | 6G urbano |
| 2 | `Crashed_Satellite` | Immediato | Satellite | ~45ms | Aree remote |
| 3 | `Crashed_Hybrid` | Immediato | Entrambi | 5-45ms | Ridondanza |
| 4 | `Witness_Terrestrial` | Ritardato | Antenna | ~5ms | Fattore umano |
| 5 | `Witness_Satellite` | Ritardato | Satellite | ~45ms | Testimone remoto |
| 6 | `Witness_Hybrid` | Ritardato | Entrambi | 5-45ms | Max affidabilità |

Ogni configurazione ha variante `_GUI` per debug visuale.

### Parametri Infrastruttura (omnetpp.ini)

**Antenna Terrestre (6G TN)**:
```ini
*.antenna.middleware.services.service[0].infrastructureType = "terrestrial"
*.antenna.middleware.services.service[0].latency = 5ms
*.antenna.middleware.services.service[0].coverageRadius = 600m
*.antenna.middleware.services.service[0].coverageReliability = 0.65
*.antenna.middleware.services.service[0].transmitPower = 500mW
```

**Satellite LEO (NTN)**:
```ini
*.satellite.middleware.services.service[0].infrastructureType = "satellite"
*.satellite.middleware.services.service[0].latency = 45ms
*.satellite.middleware.services.service[0].coverageRadius = 5000m
*.satellite.middleware.services.service[0].coverageReliability = 0.99
*.satellite.middleware.services.service[0].transmitPower = 1000mW
```

**Ritardo Testimone**:
```bash
export STELVIO_WITNESS_DELAY=5.0  # secondi
```

---

## 📊 Metriche e Analisi

### Metriche Primarie

1. **DENM Generation Time** - Timestamp creazione
2. **Infrastructure Reception Time** - Ricezione antenna/satellite
3. **Vehicle Reception Time** - Ricezione altri veicoli
4. **Cloud Delivery Time** - Ricezione cloud
5. **Reception Delay** ⭐ - Latenza generazione→ricezione
6. **Packet Delivery Ratio (PDR)** - Tasso successo
7. **Coverage** - % veicoli raggiunti

### Analisi Supportate

#### 1. Distribuzione Ritardo Ricezione
- **Metrica**: `denm_reception_delay`
- **Grafico**: Boxplot scenario × tecnologia
- **Confronto**: Terrestrial vs Satellite vs Hybrid

#### 2. Latenza Consegna Cloud
- **Metrica**: `cloud_delivery_latency`
- **Grafico**: Barre (media/mediana)
- **Confronto**: Tempi infrastruttura→cloud

#### 3. Packet Delivery Ratio (PDR)
- **Formula**: `PDR = ricevuti / (ricevuti + fuori_copertura + perdite) × 100%`
- **Grafico**: Barre per configurazione
- **Misura**: Successo consegna DENM

#### 4. Copertura Infrastruttura
- **Metriche**: `denm_in_coverage`, `denm_out_of_coverage`
- **Grafico**: % copertura per tecnologia
- **Confronto**: Effettiva vs teorica

### Grafici Generati (analysis/plots/)

1. **latency_cdf.png** - CDF ritardi ricezione
2. **latency_boxplot.png** - Confronto statistico
3. **cloud_latency.png** - Consegna infrastruttura
4. **pdr_comparison.png** - Packet delivery ratio
5. **coverage_comparison.png** - Raggiungibilità veicoli

### Esegui Analisi

```bash
make analyze
# oppure
./quickstart.sh analyze
# oppure
python3 analysis/analyze_results.py
```

Risultati in `analysis/summary_statistics.csv`:
- Nome configurazione, PDR (%), Latenza (media/mediana/P95), Copertura (%), Conteggio pacchetti

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

### Posizione Infrastruttura
Modifica `static_nodes.xml`:
```xml
<rsu id="antenna" positionX="NUOVO_X" positionY="NUOVO_Y" />
```

### Aggiungere Veicoli
Modifica `stelvio.rou.xml`, aggiungi `<trip>`.

### Parametri Radio
In `omnetpp.ini`:
```ini
*.antenna.wlan[*].radio.transmitter.power = 1000 mW
*.antenna.middleware.services.service[0].latency = 1ms
```

### Deadline DENM
```ini
*.node[*].middleware.VehicleReceiverService.denmDeadline = 0.12s
```

### Storyboard Personalizzato

**crash_storyboard.py** (t=200s):
```python
accident_veh_0 → StopEffect + SignalEffect("crash_incident")
→ CrashedVehicleService invia DENM
```

**witness_storyboard.py** (t=200s+delay):
```python
accident_veh_0 → StopEffect (silenzioso)
t=200+DELAY: witness_veh_0 → SignalEffect("witness_report")
→ WitnessVehicleService invia DENM
```

### Analisi Personalizzata
Estendi `analysis/analyze_results.py`:
```python
def plot_custom_metric(data_dict, output_file):
    # Tua visualizzazione
    fig, ax = plt.subplots(figsize=(10, 6))
    # ... codice ...
    plt.savefig(output_file)
```

---

## 🐛 Troubleshooting

### Errori Compilazione
```bash
cd /workspaces/artery/build/Release
make clean
cmake ../..
make stelvio
ls -lh scenarios/stelvio/libartery_stelvio.so  # Verifica
```

### Nessun Risultato
- Verifica simulazione completata (no errori console)
- Controlla `results/<config>/` esiste
- `**.scalar-recording = true` in `omnetpp.ini`

### GUI Non Si Avvia
```bash
pip install PyQt5 pandas matplotlib seaborn
python3 --version  # Richiede 3.7+
source venv/bin/activate  # Attiva ambiente
```

### Analisi Nessun Dato
- Esegui prima simulazioni
- Verifica `.sca` in `results/` subdirectory
- Usa scavetool:
  ```bash
  scavetool export -o output.csv results/crashed_terrestrial/*.sca
  ```

### Errori NED
```bash
ls src/*.ned            # Verifica esistenza
grep "import" src/*.ned  # Controlla import
head -n 5 src/package.ned  # Package declaration
```

---

## 📁 Struttura Completa

```
stelvio/
├── README.md                   # Questo file (documentazione completa)
├── CMakeLists.txt              # Build
├── omnetpp.ini                 # 6 configurazioni
├── Makefile                    # Comandi rapidi
├── quickstart.sh               # Script bash helper
├── requirements.txt            # Dipendenze Python
│
├── src/                        # C++ + NED
│   ├── DenmMessage.msg
│   ├── CrashedVehicleService.{h,cc,ned}
│   ├── WitnessVehicleService.{h,cc,ned}
│   ├── VehicleReceiverService.{h,cc,ned}
│   ├── InfrastructureService.{h,cc,ned}
│   └── package.ned
│
├── config/                     # XML
│   ├── services_crashed.xml
│   ├── services_witness.xml
│   └── services_infrastructure.xml
│
├── scripts/                    # Python automation
│   ├── simulation_gui.py
│   └── export_csv.py
│
├── analysis/                   # Analisi
│   ├── analyze_results.py
│   ├── plots/                  # PNG output
│   └── csv/                    # CSV export
│
├── results/                    # Output simulazioni
│   ├── crashed_terrestrial/
│   ├── crashed_satellite/
│   ├── crashed_hybrid/
│   ├── witness_terrestrial/
│   ├── witness_satellite/
│   └── witness_hybrid/
│
├── stelvio.{net,rou,sumocfg}   # SUMO traffic
├── static_nodes.xml            # Infrastruttura
├── crash_storyboard.py         # Eventi crash
├── witness_storyboard.py       # Eventi witness
└── venv/                       # Python virtual env
```

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

## 💡 Tips & Note Tecniche

### Pro Tips
1. Usa GUI per prime esecuzioni (feedback visuale)
2. Esegui ripetizioni multiple (`repeat=10`)
3. Controlla console per errori
4. Inizia con sim-time breve
5. Version control risultati (Git commit)
6. Ambiente virtuale: dipendenze isolate in `venv/`

### Note Tecniche
- **Broadcast**: SHB (Single Hop) invece di GeoBroadcast
- **Porte BTP**: 2001 (veicoli→infra), 2002 (infra→veicoli)
- **Affidabilità**: Terrestrial 65%, Satellite 99%
- **Forward Declaration**: Headers usano forward declaration per evitare dipendenze circolari

### Valori Riferimento

| Metrica | Formula | Valore Buono |
|---------|---------|--------------|
| PDR | (Ricevuti/Inviati)×100 | >90% |
| Latenza Terrestrial | Gen→Ricezione | <10ms |
| Latenza Satellite | Gen→Ricezione | 20-50ms |
| Copertura | (Raggiunti/Totale)×100 | >80% |

---

## ✅ Status Progetto

- [x] Servizi C++ implementati (4)
- [x] Messaggi definiti (DenmMessage.msg)
- [x] Configurazioni OMNeT++ (6 scenari)
- [x] Traffico SUMO configurato
- [x] Storyboard events
- [x] GUI automazione
- [x] Script analisi
- [x] Documentazione completa
- [x] File NED individuali (5)
- [x] Build testato

**Status**: ✅ **COMPLETO E PRONTO**  
**Build**: Nessun errore  
**Framework**: Artery + OMNeT++ 6.x + SUMO 1.15+  
**Linguaggi**: C++ (~2000 linee) + Python (~1250 linee) + NED  
**Creato**: Ottobre 2025

---

## 📄 Licenza

Eredita licenza Artery (GPLv2).

---

## 🎓 Citazione

```bibtex
@misc{stelvio_v2x_6g,
  title={Stelvio V2X Simulation - 6G Hybrid Infrastructure Study},
  author={Your Name},
  year={2025},
  note={OMNeT++ simulation for hybrid terrestrial/satellite V2X}
}
```

---

## 📞 Supporto

1. Controlla questo README (completo)
2. Esegui `make check` (diagnostica)
3. Usa `make help` (comandi)
4. Verifica `omnetpp.ini` (configurazioni)
5. Consulta log `results/` (debug)

---

**Quick Help**: `make help` | **Check**: `make check` | **Build**: `make build` | **Run**: `make run-crashed` | **Analyze**: `make analyze` | **GUI**: `make gui`

**Buone simulazioni! 🚗📡🛰️**

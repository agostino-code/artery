# Stelvio C++ Services Documentation

## Overview

This directory contains the C++ services for the Stelvio 6G hybrid V2X simulation scenario. The services are designed to be simple, modular, and export comprehensive metrics for analysis.

## Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STELVIO SCENARIO                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SENDER SERVICES (Event-driven)                              │
│  ├─ CrashedVehicleService  → Immediate DENM                 │
│  └─ WitnessVehicleService  → Delayed DENM                   │
│                                                              │
│  RECEIVER SERVICES (Always active)                           │
│  ├─ VehicleReceiverService → All vehicles receive           │
│  └─ InfrastructureService  → Antenna/Satellite relay        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Service Descriptions

### 1. CrashedVehicleService

**Purpose**: Handles crashed vehicle that sends immediate DENM alert.

**Trigger**: Storyboard signal `"crash_incident"`

**Behavior**:
- Listens for crash event from storyboard
- Immediately sends DENM broadcast message
- Records transmission time and delay

**Metrics Exported**:
- `denm_event_time`: When crash occurred (s)
- `denm_sent_time`: When DENM was transmitted (s)
- `denm_generation_delay`: Time between crash and transmission (s)
- `denm_sequence_number`: Message sequence number

**Configuration**: Used in `services_crashed.xml`

---

### 2. WitnessVehicleService

**Purpose**: Handles witness vehicle that sends delayed DENM alert.

**Trigger**: Storyboard signal `"witness_report"`

**Behavior**:
- Listens for witness event from storyboard
- Sends DENM after configured delay (delay is in storyboard)
- Records transmission time and delay

**Metrics Exported**:
- `denm_event_time`: When witness detected accident (s)
- `denm_sent_time`: When DENM was transmitted (s)
- `denm_generation_delay`: Witness reaction time (s)
- `denm_sequence_number`: Message sequence number

**Configuration**: Used in `services_witness.xml`

---

### 3. VehicleReceiverService

**Purpose**: Receives DENM on all vehicles and records reception metrics.

**Trigger**: Packet reception (BTP port 2002)

**Behavior**:
- Installed on ALL vehicles in scenario
- Records first DENM reception for each vehicle
- Calculates end-to-end latency
- Tracks coverage and packet delivery

**Metrics Exported** (per vehicle):
- `denm_received_flag`: 1 if received, 0 if not
- `denm_reception_time`: When DENM was received (s)
- `denm_event_time`: Original event time (s)
- `denm_reception_delay`: End-to-end latency (s)
- `denm_within_deadline`: 1 if within 120ms deadline
- `denm_in_coverage`: 1 if vehicle received message
- `denm_out_of_coverage`: 1 if never received (coverage issue)
- `denm_reliability_drop`: 1 if lost due to reliability

**Configuration**: Used in both `services_crashed.xml` and `services_witness.xml`

---

### 4. InfrastructureService

**Purpose**: Infrastructure relay (antenna/satellite) with cloud delivery simulation.

**Trigger**: Packet reception (BTP port 2001)

**Behavior**:
- Installed on RSU nodes (antenna/satellite)
- Receives DENM from crashed/witness vehicles
- Simulates cloud delivery with infrastructure latency
- Relays DENM to vehicles in coverage area
- Applies reliability factor (packet loss simulation)

**Metrics Exported** (per infrastructure):
- `cloud_reception_time`: When cloud received DENM (s)
- `cloud_event_time`: Original event time (s)
- `cloud_delivery_latency`: Event → Cloud latency (s)
- `infra_coverage_radius`: Coverage radius (m)
- `infra_coverage_reliability`: Reliability factor (0.0-1.0)
- `denms_relayed`: Total DENMs relayed

**Configuration Parameters**:
- `infrastructureType`: "terrestrial", "satellite", or "hybrid"
- `latency`: Processing latency (5ms for antenna, 45ms for satellite)
- `coverageRadius`: Coverage area (600m for antenna, 5000m for satellite)
- `coverageReliability`: Success rate (0.65 for antenna, 0.99 for satellite)
- `transmitPower`: Transmit power in mW

**Configuration**: Used in `services_infrastructure.xml`

---

## Message Format

### DenmMessage.msg

Simple DENM message containing essential fields:

```cpp
packet DenmMessage {
    uint32_t stationId;           // Sender ID
    uint32_t sequenceNumber;      // Message sequence
    simtime_t eventTime;          // Event occurrence time
    simtime_t generationTime;     // Message generation time
    string eventType;             // "CRASH" or "WITNESS"
    double positionX;             // X coordinate
    double positionY;             // Y coordinate
    string infrastructureType;    // "terrestrial", "satellite", "hybrid"
}
```

---

## Metrics Analysis

### 1. Vehicle Reception Delay Analysis
**Metric**: `denm_reception_delay` from VehicleReceiverService  
**Purpose**: Compare end-to-end latency across scenarios and technologies  
**Analysis**: Boxplot per scenario (Crashed/Witness) × technology (Terrestrial/Satellite/Hybrid)

### 2. Cloud Delivery Latency Analysis
**Metric**: `cloud_delivery_latency` from InfrastructureService  
**Purpose**: Compare infrastructure delivery time to cloud  
**Analysis**: Bar chart showing mean/median latency per technology

### 3. Packet Delivery Ratio (PDR)
**Metrics**: 
- `denm_received_flag` = 1 → received
- `denm_out_of_coverage` = 1 → coverage issue
- `denm_reliability_drop` = 1 → reliability issue

**Calculation**: 
```
PDR = (received) / (received + out_of_coverage + reliability_drops) × 100%
```

**Analysis**: Bar chart per scenario × technology

### 4. Coverage Analysis
**Metrics**:
- `denm_in_coverage` → vehicles that received
- `denm_out_of_coverage` → vehicles outside coverage
- `infra_coverage_radius` → theoretical coverage

**Analysis**: Compare theoretical vs actual coverage per technology

---

## Build Instructions

The services are automatically compiled by the CMakeLists.txt:

```bash
cd /workspaces/artery/scenarios/stelvio
make build
```

This will:
1. Generate message files from `DenmMessage.msg`
2. Compile all `.cc` service files
3. Link into `stelvio` library
4. Create `stelvio_scenario` executable

---

## Usage in Simulation

### Crashed Scenario
```ini
[Config Crashed_Terrestrial]
*.storyboard.python = "crash_storyboard"
*.node[*].middleware.services = xmldoc("config/services_crashed.xml")
```

### Witness Scenario
```ini
[Config Witness_Satellite]
*.storyboard.python = "witness_storyboard"
*.node[*].middleware.services = xmldoc("config/services_witness.xml")
```

---

## Design Principles

1. **Simplicity**: Each service has a single, well-defined responsibility
2. **Modularity**: Services are independent and composable
3. **Metrics-First**: All relevant data is exported as OMNeT++ scalars
4. **Documentation**: Code is heavily commented for maintainability
5. **Realistic**: Infrastructure parameters based on 6G standards

---

## Troubleshooting

### Service not receiving signals
- Check that storyboard is enabled: `*.withStoryboard = true`
- Verify signal name matches storyboard effect: `"crash_incident"` or `"witness_report"`

### DENM not received by vehicles
- Check BTP port numbers match (2001 for sender, 2002 for receiver)
- Verify coverage radius in infrastructure configuration
- Check reliability factor (< 1.0 means packet loss)

### Missing metrics in results
- Ensure `**.scalar-recording = true` in omnetpp.ini
- Check that service finished properly (no crashes)
- Verify result files exist in `results/` directory

---

## Authors

Generated for Stelvio 6G Hybrid V2X Simulation Study  
Date: October 2025

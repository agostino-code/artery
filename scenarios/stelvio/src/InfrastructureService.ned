//
// InfrastructureService.ned
//
// Service for antenna/satellite infrastructure that relays DENM messages
// with configurable latency, coverage, and reliability parameters.
//
// @author Stelvio Scenario
// @date October 2025
//

package src;

import artery.application.ItsG5Service;

//
// Infrastructure Service (Antenna/Satellite)
//
// This service runs on RSU nodes (antenna or satellite) to relay DENM
// messages between vehicles and simulate cloud delivery. It models
// realistic 6G Terrestrial Network (TN) and Non-Terrestrial Network (NTN)
// characteristics.
//
// Metrics exported (per infrastructure node):
// - cloud_reception_time: When cloud received DENM via this infrastructure
// - cloud_event_time: Original event time from DENM
// - cloud_delivery_latency: Time from event to cloud reception
// - infra_coverage_radius: Coverage radius in meters
// - infra_coverage_reliability: Reliability factor (0.0-1.0)
// - denms_relayed: Total number of DENMs successfully relayed
//
// Parameters:
//   infrastructureType - Type of infrastructure (terrestrial/satellite)
//   latency - Processing and propagation latency
//   coverageRadius - Maximum distance for signal coverage
//   coverageReliability - Probability of successful delivery (0.0-1.0)
//   transmitPower - Transmission power in milliwatts
//
// Configuration Examples:
//
//   6G Terrestrial Network (TN) - Antenna:
//     infrastructureType = "terrestrial"
//     latency = 5ms
//     coverageRadius = 600m
//     coverageReliability = 0.65
//     transmitPower = 500mW
//
//   LEO Non-Terrestrial Network (NTN) - Satellite:
//     infrastructureType = "satellite"
//     latency = 45ms
//     coverageRadius = 5000m
//     coverageReliability = 0.99
//     transmitPower = 1000mW
//
// Usage:
//   Install on RSU nodes (services_infrastructure.xml)
//   Receives from vehicles on BTP port 2001
//   Relays to vehicles on BTP port 2002
//
simple InfrastructureService like ItsG5Service
{
    parameters:
        @class(stelvio::InfrastructureService);
        
        // Infrastructure type identifier
        string infrastructureType = default("terrestrial"); 
        
        // Processing and propagation latency
        // TN: 1-5ms, LEO NTN: 20-40ms, GEO NTN: 250-300ms
        double latency @unit(s) = default(5ms);
        
        // Coverage radius in meters
        // TN: 200-1000m, LEO: 1000-5000m, GEO: up to 1000km
        double coverageRadius @unit(m) = default(600m);
        
        // Reliability factor: probability of successful packet delivery
        // TN: 0.6-0.8 (urban obstacles), LEO: 0.95-0.99 (clear sky)
        double coverageReliability = default(0.65);
        
        // Transmit power in milliwatts
        // TN: 100-1000mW, LEO: 500-2000mW
        double transmitPower @unit(mW) = default(500mW);
        
        @display("i=device/antennatower");
        
    gates:
        // No explicit gates needed - uses middleware BTP ports
        // Receives on port 2001, transmits on port 2002
}

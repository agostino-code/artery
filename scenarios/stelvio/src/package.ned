//
// package.ned
//
// Package definition for Stelvio scenario services
//
// This package contains all custom services for the Stelvio 6G Hybrid V2X
// simulation scenario, including sender services (crashed/witness vehicles),
// receiver services (all vehicles), and infrastructure relay services.
//
// @author Stelvio Scenario
// @date October 2025
//

package src;

//
// Stelvio Scenario Services Package
//
// Contains four main services:
//
// 1. CrashedVehicleService - Immediate DENM sender (crash scenario)
// 2. WitnessVehicleService - Delayed DENM sender (witness scenario)
// 3. VehicleReceiverService - DENM receiver for all vehicles
// 4. InfrastructureService - Infrastructure relay (antenna/satellite)
//
// These services work together to simulate a complete V2X emergency
// alert system using 6G Terrestrial and Non-Terrestrial Networks.
//
// Message Types:
//   DenmMessage - Simplified DENM for crash/witness alerts
//
// Usage:
//   Reference services in XML configuration files:
//   - services_crashed.xml (for crashed scenario)
//   - services_witness.xml (for witness scenario)
//   - services_infrastructure.xml (for RSU nodes)
//
// Example:
//   <service type="src.CrashedVehicleService">
//       <listener port="2001" />
//   </service>
//

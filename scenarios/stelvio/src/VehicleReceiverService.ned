//
// VehicleReceiverService.ned
//
// Service for receiving and analyzing DENM messages on all vehicles.
// Provides detailed metrics for latency analysis, PDR, and coverage.
//
// @author Stelvio Scenario
// @date October 2025
//

package src;

import artery.application.ItsG5Service;

//
// Vehicle Receiver Service
//
// This service is installed on ALL vehicles in the scenario to receive
// and analyze DENM messages. It records comprehensive metrics for each
// vehicle's reception experience.
//
// Metrics exported (per vehicle):
// - denm_received_flag: 1 if DENM was received, 0 otherwise
// - denm_reception_time: Simulation time when DENM was received
// - denm_event_time: Original event time from DENM
// - denm_reception_delay: End-to-end latency (event → reception)
// - denm_within_deadline: 1 if received within deadline
// - denm_in_coverage: 1 if vehicle was in coverage area
// - denm_out_of_coverage: 1 if DENM not received due to coverage
// - denm_reliability_drop: 1 if DENM lost due to reliability issues
//
// Parameters:
//   denmDeadline - Maximum useful delay for DENM (default: 120ms)
//
// Usage:
//   Install on all vehicles in both crashed and witness scenarios
//   Listens on BTP port 2002 for DENM messages from infrastructure
//
simple VehicleReceiverService like ItsG5Service
{
    parameters:
        @class(stelvio::VehicleReceiverService);
        
        // Maximum useful delay for DENM reception
        // Messages received after this delay are still counted but marked
        double denmDeadline @unit(s) = default(0.12s); // 120ms (6G requirement)
        
        @display("i=block/rx");
        
    gates:
        // No explicit gates needed - uses middleware BTP port 2002
}

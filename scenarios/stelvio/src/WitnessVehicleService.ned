//
// WitnessVehicleService.ned
//
// Service for witness vehicle that sends delayed DENM alert after observing
// an accident. The delay is configured through storyboard timing.
//
// @author Stelvio Scenario
// @date October 2025
//

package src;

import artery.application.ItsG5Service;

//
// Witness Vehicle Service
//
// This service handles the WITNESS scenario where a vehicle sends a DENM
// after observing an accident with a configurable reaction delay.
// The delay is handled by the storyboard timing.
//
// Metrics exported:
// - denm_sent_time: Simulation time when DENM was transmitted
// - denm_event_time: Simulation time when witness detected accident
// - denm_generation_delay: Witness reaction time
// - denm_sequence_number: Message sequence counter
//
// Environment Variables:
//   STELVIO_WITNESS_DELAY - Witness reporting delay in seconds (default: 5.0)
//
// Usage:
//   Install on vehicles that can witness accidents (services_witness.xml)
//   Requires storyboard to emit "witness_report" signal
//
simple WitnessVehicleService like ItsG5Service
{
    parameters:
        @class(stelvio::WitnessVehicleService);
        @signal[StoryboardSignal];
        @display("i=block/cogwheel");
}

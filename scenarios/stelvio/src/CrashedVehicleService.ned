//
// CrashedVehicleService.ned
//
// Service for crashed vehicle that sends immediate DENM alert upon crash event.
// This service is triggered by the storyboard signal "crash_incident" and
// immediately broadcasts a DENM message to nearby infrastructure.
//
// @author Stelvio Scenario
// @date October 2025
//

package src;

import artery.application.ItsG5Service;

//
// Crashed Vehicle Service
//
// This service handles the CRASHED scenario where a vehicle immediately sends
// a DENM alert upon crashing. It is event-driven and triggered by storyboard.
//
// Metrics exported:
// - denm_sent_time: Simulation time when DENM was transmitted
// - denm_event_time: Simulation time when crash event occurred  
// - denm_generation_delay: Time between crash and transmission
// - denm_sequence_number: Message sequence counter
//
// Usage:
//   Install on vehicles that can crash (typically via services_crashed.xml)
//   Requires storyboard to emit "crash_incident" signal
//
simple CrashedVehicleService like ItsG5Service
{
    parameters:
        @class(stelvio::CrashedVehicleService);
        @signal[StoryboardSignal];
        @display("i=block/routing");
}

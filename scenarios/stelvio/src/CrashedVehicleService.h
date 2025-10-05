//
// CrashedVehicleService.h - Service for crashed vehicle sending immediate DENM
//
// This service handles the CRASHED scenario where a vehicle immediately sends
// a DENM alert upon crashing. It is triggered by the storyboard signal.
//

#ifndef STELVIO_CRASHEDVEHICLESERVICE_H_
#define STELVIO_CRASHEDVEHICLESERVICE_H_

#include "artery/application/ItsG5Service.h"
#include <omnetpp.h>

namespace stelvio {

/**
 * @brief Service for crashed vehicle that sends immediate DENM alert
 * 
 * Metrics exported:
 * - denm_sent_time: Simulation time when DENM was transmitted
 * - denm_event_time: Simulation time when crash event occurred
 * - denm_generation_delay: Time between crash and transmission
 */
class CrashedVehicleService : public artery::ItsG5Service
{
public:
    void initialize() override;
    void finish() override;
    void trigger() override;
    void receiveSignal(omnetpp::cComponent*, omnetpp::simsignal_t, omnetpp::cObject*, omnetpp::cObject*) override;

private:
    void sendDenm();
    
    bool m_crashed = false;           ///< Whether this vehicle has crashed
    omnetpp::simtime_t m_eventTime;   ///< When the crash occurred
    uint32_t m_sequenceNumber = 0;    ///< Message sequence counter
};

} // namespace stelvio

#endif // STELVIO_CRASHEDVEHICLESERVICE_H_

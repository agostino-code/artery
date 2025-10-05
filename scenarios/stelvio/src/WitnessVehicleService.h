//
// WitnessVehicleService.h - Service for witness vehicle sending delayed DENM
//
// This service handles the WITNESS scenario where a vehicle sends a DENM
// after observing an accident with a configurable delay.
//

#ifndef STELVIO_WITNESSVEHICLESERVICE_H_
#define STELVIO_WITNESSVEHICLESERVICE_H_

#include "artery/application/ItsG5Service.h"
#include <omnetpp.h>

namespace stelvio {

/**
 * @brief Service for witness vehicle that sends delayed DENM alert
 * 
 * Metrics exported:
 * - denm_sent_time: Simulation time when DENM was transmitted
 * - denm_event_time: Simulation time when witness detected accident
 * - denm_generation_delay: Time between detection and transmission (witness delay)
 */
class WitnessVehicleService : public artery::ItsG5Service
{
public:
    void initialize() override;
    void finish() override;
    void trigger() override;
    void receiveSignal(omnetpp::cComponent*, omnetpp::simsignal_t, omnetpp::cObject*, omnetpp::cObject*) override;

private:
    void sendDenm();
    
    bool m_witnessed = false;         ///< Whether this vehicle witnessed accident
    omnetpp::simtime_t m_eventTime;   ///< When witness detected accident
    uint32_t m_sequenceNumber = 0;    ///< Message sequence counter
};

} // namespace stelvio

#endif // STELVIO_WITNESSVEHICLESERVICE_H_

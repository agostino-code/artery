//
// VehicleReceiverService.h - Service for receiving DENM on all vehicles
//
// This service is installed on ALL vehicles to receive and analyze DENM messages.
// It provides detailed metrics for latency analysis, PDR, and coverage.
//

#ifndef STELVIO_VEHICLERECEIVERSERVICE_H_
#define STELVIO_VEHICLERECEIVERSERVICE_H_

#include "artery/application/ItsG5Service.h"
#include <omnetpp.h>

namespace stelvio {

/**
 * @brief Service for receiving and analyzing DENM messages on vehicles
 * 
 * Metrics exported (per vehicle):
 * - denm_received_flag: 1 if DENM was received, 0 otherwise
 * - denm_reception_time: Simulation time when DENM was received
 * - denm_event_time: Original event time from DENM
 * - denm_reception_delay: Time from event to reception (end-to-end latency)
 * - denm_in_coverage: 1 if vehicle was in coverage area
 * - denm_out_of_coverage: 1 if DENM not received due to coverage
 * - denm_reliability_drop: 1 if DENM not received due to reliability issues
 */
class VehicleReceiverService : public artery::ItsG5Service
{
public:
    void initialize() override;
    void finish() override;
    void trigger() override;
    void indicate(const vanetza::btp::DataIndication&, omnetpp::cPacket*, const artery::NetworkInterface&) override;

private:
    bool m_receivedDenm = false;           ///< Whether this vehicle received DENM
    omnetpp::simtime_t m_receptionTime;    ///< When DENM was received
    omnetpp::simtime_t m_eventTime;        ///< Original event time from DENM
    omnetpp::simtime_t m_denmDeadline;     ///< Maximum useful delay for DENM
    
    // Statistics
    int m_denmsReceived = 0;               ///< Total DENMs received
};

} // namespace stelvio

#endif // STELVIO_VEHICLERECEIVERSERVICE_H_

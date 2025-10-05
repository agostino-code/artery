//
// InfrastructureService.h - Service for antenna/satellite infrastructure
//
// This service runs on RSU (antenna or satellite) to relay DENM messages.
// It simulates cloud delivery, coverage analysis, and infrastructure metrics.
//

#ifndef STELVIO_INFRASTRUCTURESERVICE_H_
#define STELVIO_INFRASTRUCTURESERVICE_H_

#include "artery/application/ItsG5Service.h"
#include "artery/utility/Geometry.h"
#include <omnetpp.h>
#include <set>

// Forward declaration
namespace stelvio_msgs {
    class DenmMessage;
}

namespace stelvio {

/**
 * @brief Service for infrastructure (antenna/satellite) relay and cloud delivery
 * 
 * Metrics exported (per infrastructure node):
 * - cloud_reception_time: When cloud received DENM via this infrastructure
 * - cloud_event_time: Original event time from DENM
 * - cloud_delivery_latency: Time from event to cloud reception
 * - infra_coverage_radius: Coverage radius in meters
 * - infra_coverage_reliability: Reliability factor (0.0-1.0)
 * - infra_type: Infrastructure type (terrestrial/satellite/hybrid)
 * - vehicles_in_coverage: Number of vehicles theoretically in coverage
 * - vehicles_reached: Number of vehicles that received DENM
 */
class InfrastructureService : public artery::ItsG5Service
{
public:
    void initialize() override;
    void finish() override;
    void trigger() override;
    void indicate(const vanetza::btp::DataIndication&, omnetpp::cPacket*, const artery::NetworkInterface&) override;

private:
    void relayDenm(stelvio_msgs::DenmMessage* denm);
    int countVehiclesInCoverage();
    
    // Infrastructure configuration
    std::string m_infrastructureType;      ///< "terrestrial", "satellite", "hybrid"
    omnetpp::simtime_t m_latency;          ///< Infrastructure processing latency
    double m_coverageRadius;               ///< Coverage radius in meters
    double m_coverageReliability;          ///< Reliability (0.0 = 0%, 1.0 = 100%)
    double m_transmitPower;                ///< Transmit power in mW
    
    // State tracking
    bool m_receivedDenm = false;           ///< Whether DENM was received
    omnetpp::simtime_t m_cloudReceptionTime; ///< When cloud received DENM
    omnetpp::simtime_t m_eventTime;        ///< Original event time
    std::set<uint32_t> m_seenMessages;     ///< Track message IDs to avoid duplicates
    
    // Statistics
    int m_denmsRelayed = 0;                ///< Total DENMs relayed
};

} // namespace stelvio

#endif // STELVIO_INFRASTRUCTURESERVICE_H_

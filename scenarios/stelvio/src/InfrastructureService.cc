//
// InfrastructureService.cc - Implementation of infrastructure service
//

#include "InfrastructureService.h"
#include "stelvio_msgs/DenmMessage_m.h"
#include "artery/application/Middleware.h"
#include <vanetza/btp/data_request.hpp>
#include <vanetza/dcc/profile.hpp>
#include <vanetza/geonet/interface.hpp>
#include <cmath>

using namespace omnetpp;

namespace stelvio {

Define_Module(InfrastructureService)

void InfrastructureService::initialize()
{
    artery::ItsG5Service::initialize();
    
    // Read infrastructure configuration parameters
    m_infrastructureType = par("infrastructureType").stdstringValue();
    m_latency = par("latency");
    m_coverageRadius = par("coverageRadius");
    m_coverageReliability = par("coverageReliability");
    m_transmitPower = par("transmitPower");
    
    EV_INFO << "InfrastructureService initialized:\n"
            << "  Type: " << m_infrastructureType << "\n"
            << "  Latency: " << m_latency << "\n"
            << "  Coverage: " << m_coverageRadius << "m\n"
            << "  Reliability: " << (m_coverageReliability * 100) << "%\n";
}

void InfrastructureService::indicate(const vanetza::btp::DataIndication& ind, 
                                      cPacket* packet, 
                                      const artery::NetworkInterface& ifc)
{
    Enter_Method("indicate");
    
    // Check if this is a DENM message
    auto* denm = dynamic_cast<stelvio_msgs::DenmMessage*>(packet);
    
    if (denm) {
        // Create unique message ID
        uint64_t msgId = ((uint64_t)denm->getStationId() << 32) | denm->getSequenceNumber();
        
        // Check if we've already seen this message
        if (m_seenMessages.find(msgId) != m_seenMessages.end()) {
            EV_INFO << "Duplicate DENM ignored (already relayed)\n";
            delete packet;
            return;
        }
        
        m_seenMessages.insert(msgId);
        
        EV_INFO << "Infrastructure received DENM from StationID=" << denm->getStationId()
                << " EventType=" << denm->getEventType() << "\n";
        
        // Record cloud delivery metrics (first reception only)
        if (!m_receivedDenm) {
            m_receivedDenm = true;
            m_eventTime = denm->getEventTime();
            m_cloudReceptionTime = simTime() + m_latency; // Add infrastructure latency
            
            simtime_t cloudLatency = m_cloudReceptionTime - m_eventTime;
            
            recordScalar("cloud_reception_time", m_cloudReceptionTime);
            recordScalar("cloud_event_time", m_eventTime);
            recordScalar("cloud_delivery_latency", cloudLatency);
            recordScalar("infra_coverage_radius", m_coverageRadius);
            recordScalar("infra_coverage_reliability", m_coverageReliability);
            
            EV_INFO << "Cloud delivery latency: " << cloudLatency << "s\n";
        }
        
        // Relay DENM to vehicles in coverage
        relayDenm(denm);
        m_denmsRelayed++;
    }
    
    delete packet;
}

void InfrastructureService::relayDenm(stelvio_msgs::DenmMessage* originalDenm)
{
    // Clone the message and mark infrastructure type
    auto* denm = originalDenm->dup();
    denm->setInfrastructureType(m_infrastructureType.c_str());
    
    // Configure BTP request for single hop broadcast from infrastructure
    using namespace vanetza;
    btp::DataRequestB req;
    req.destination_port = host_cast<uint16_t>(2002); // VehicleReceiverService port
    req.gn.transport_type = geonet::TransportType::SHB; // Single Hop Broadcast
    req.gn.traffic_class.tc_id(static_cast<unsigned>(dcc::Profile::DP2)); // Emergency
    req.gn.communication_profile = geonet::CommunicationProfile::ITS_G5;
    req.gn.maximum_hop_limit = 1;
    
    EV_INFO << "Relaying DENM via " << m_infrastructureType 
            << " infrastructure (coverage=" << m_coverageRadius << "m)\n";
    
    // Apply reliability factor (simulate packet loss)
    double randValue = uniform(0.0, 1.0);
    if (randValue <= m_coverageReliability) {
        // Successfully relay
        request(req, denm);
        EV_INFO << "DENM relayed successfully (reliability check passed)\n";
    } else {
        // Reliability drop
        EV_INFO << "DENM dropped due to reliability failure\n";
        delete denm;
    }
}

int InfrastructureService::countVehiclesInCoverage()
{
    // Count vehicles within coverage radius
    // This is a simplified implementation - in real scenario would use actual positions
    int count = 0;
    
    try {
        auto& middleware = getFacilities().get_const<artery::Middleware>();
        // Note: Accessing all vehicles requires TraCI - simplified for now
        // In a full implementation, we'd iterate through all vehicles and check distance
        count = 0; // Placeholder
    } catch (...) {
        count = 0;
    }
    
    return count;
}

void InfrastructureService::trigger()
{
    // Periodic updates if needed
}

void InfrastructureService::finish()
{
    artery::ItsG5Service::finish();
    
    // Record final statistics
    recordScalar("denms_relayed", m_denmsRelayed);
    
    if (m_receivedDenm) {
        EV_INFO << "InfrastructureService finished - Relayed " << m_denmsRelayed << " DENMs\n";
    } else {
        EV_INFO << "InfrastructureService finished - No DENMs received\n";
        
        // Record zero values for cloud metrics if nothing received
        recordScalar("cloud_reception_time", 0);
        recordScalar("cloud_event_time", 0);
        recordScalar("cloud_delivery_latency", 0);
    }
}

} // namespace stelvio

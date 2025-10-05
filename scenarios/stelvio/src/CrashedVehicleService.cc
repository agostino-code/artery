//
// CrashedVehicleService.cc - Implementation of crashed vehicle service
//

#include "CrashedVehicleService.h"
#include "stelvio_msgs/DenmMessage_m.h"
#include "artery/application/StoryboardSignal.h"
#include "artery/application/VehicleDataProvider.h"
#include <vanetza/btp/data_request.hpp>
#include <vanetza/dcc/profile.hpp>
#include <vanetza/geonet/interface.hpp>

using namespace omnetpp;

namespace stelvio {

Define_Module(CrashedVehicleService)

// Signal for storyboard
static const simsignal_t storyboardSignal = cComponent::registerSignal("StoryboardSignal");

void CrashedVehicleService::initialize()
{
    artery::ItsG5Service::initialize();
    
    // Subscribe to storyboard signals (crash event)
    subscribe(storyboardSignal);
    
    EV_INFO << "CrashedVehicleService initialized\n";
}

void CrashedVehicleService::receiveSignal(cComponent*, simsignal_t signal, cObject* obj, cObject*)
{
    if (signal == storyboardSignal && !m_crashed) {
        auto* storyboardSignalObj = dynamic_cast<artery::StoryboardSignal*>(obj);
        
        if (storyboardSignalObj && storyboardSignalObj->getCause() == "crash_incident") {
            EV_INFO << "Crash incident detected! Sending immediate DENM\n";
            
            m_crashed = true;
            m_eventTime = simTime();
            
            // Send DENM immediately
            sendDenm();
        }
    }
}

void CrashedVehicleService::sendDenm()
{
    if (!m_crashed) {
        return;
    }
    
    // Get vehicle information
    auto& vdp = getFacilities().get_const<artery::VehicleDataProvider>();
    auto position = vdp.position();
    
    // Create DENM message
    auto* denm = new stelvio_msgs::DenmMessage();
    denm->setStationId(vdp.station_id());
    denm->setSequenceNumber(++m_sequenceNumber);
    denm->setEventTime(m_eventTime);
    denm->setGenerationTime(simTime());
    denm->setEventType("CRASH");
    denm->setPositionX(position.x.value());
    denm->setPositionY(position.y.value());
    denm->setInfrastructureType("unknown"); // Will be set by infrastructure
    denm->setByteLength(200); // Realistic DENM size
    
    // Configure BTP request for single hop broadcast (simpler)
    using namespace vanetza;
    btp::DataRequestB req;
    req.destination_port = host_cast<uint16_t>(2001);
    req.gn.transport_type = geonet::TransportType::SHB; // Single Hop Broadcast
    req.gn.traffic_class.tc_id(static_cast<unsigned>(dcc::Profile::DP2)); // Emergency profile
    req.gn.communication_profile = geonet::CommunicationProfile::ITS_G5;
    req.gn.maximum_hop_limit = 1;
    
    EV_INFO << "Sending DENM: StationID=" << denm->getStationId() 
            << " SeqNum=" << denm->getSequenceNumber()
            << " EventTime=" << m_eventTime
            << " GenTime=" << simTime() << "\n";
    
    // Send packet
    request(req, denm);
    
    // Record metrics
    simtime_t generationDelay = simTime() - m_eventTime;
    recordScalar("denm_event_time", m_eventTime);
    recordScalar("denm_sent_time", simTime());
    recordScalar("denm_generation_delay", generationDelay);
    recordScalar("denm_sequence_number", m_sequenceNumber);
}

void CrashedVehicleService::trigger()
{
    // This service is event-driven (storyboard), not periodic
}

void CrashedVehicleService::finish()
{
    artery::ItsG5Service::finish();
    
    if (m_crashed) {
        EV_INFO << "CrashedVehicleService finished - Sent " << m_sequenceNumber << " DENMs\n";
    }
}

} // namespace stelvio

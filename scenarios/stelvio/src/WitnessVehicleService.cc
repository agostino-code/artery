//
// WitnessVehicleService.cc - Implementation of witness vehicle service
//

#include "WitnessVehicleService.h"
#include "stelvio_msgs/DenmMessage_m.h"
#include "artery/application/StoryboardSignal.h"
#include "artery/application/VehicleDataProvider.h"
#include <vanetza/btp/data_request.hpp>
#include <vanetza/dcc/profile.hpp>
#include <vanetza/geonet/interface.hpp>

using namespace omnetpp;

namespace stelvio {

Define_Module(WitnessVehicleService)

// Signal for storyboard
static const simsignal_t storyboardSignal = cComponent::registerSignal("StoryboardSignal");

void WitnessVehicleService::initialize()
{
    artery::ItsG5Service::initialize();
    
    // Subscribe to storyboard signals (witness event)
    subscribe(storyboardSignal);
    
    EV_INFO << "WitnessVehicleService initialized\n";
}

void WitnessVehicleService::receiveSignal(cComponent*, simsignal_t signal, cObject* obj, cObject*)
{
    if (signal == storyboardSignal && !m_witnessed) {
        auto* storyboardSignalObj = dynamic_cast<artery::StoryboardSignal*>(obj);
        
        if (storyboardSignalObj && storyboardSignalObj->getCause() == "witness_report") {
            EV_INFO << "Witness event detected! Sending delayed DENM\n";
            
            m_witnessed = true;
            m_eventTime = simTime();
            
            // Send DENM immediately (delay is already in storyboard timing)
            sendDenm();
        }
    }
}

void WitnessVehicleService::sendDenm()
{
    if (!m_witnessed) {
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
    denm->setEventType("WITNESS");
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
    
    // Record metrics (witness delay is already accounted in storyboard)
    simtime_t generationDelay = simTime() - m_eventTime;
    recordScalar("denm_event_time", m_eventTime);
    recordScalar("denm_sent_time", simTime());
    recordScalar("denm_generation_delay", generationDelay);
    recordScalar("denm_sequence_number", m_sequenceNumber);
}

void WitnessVehicleService::trigger()
{
    // This service is event-driven (storyboard), not periodic
}

void WitnessVehicleService::finish()
{
    artery::ItsG5Service::finish();
    
    if (m_witnessed) {
        EV_INFO << "WitnessVehicleService finished - Sent " << m_sequenceNumber << " DENMs\n";
    }
}

} // namespace stelvio

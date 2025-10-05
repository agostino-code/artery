//
// VehicleReceiverService.cc - Implementation of vehicle receiver service
//

#include "VehicleReceiverService.h"
#include "stelvio_msgs/DenmMessage_m.h"
#include "artery/application/VehicleDataProvider.h"
#include "artery/traci/VehicleController.h"
#include <omnetpp/cpacket.h>

using namespace omnetpp;

namespace stelvio {

Define_Module(VehicleReceiverService)

void VehicleReceiverService::initialize()
{
    artery::ItsG5Service::initialize();
    
    // Get DENM deadline from parent module parameter
    m_denmDeadline = par("denmDeadline");
    
    EV_INFO << "VehicleReceiverService initialized (deadline=" << m_denmDeadline << ")\n";
}

void VehicleReceiverService::indicate(const vanetza::btp::DataIndication& ind, 
                                      cPacket* packet, 
                                      const artery::NetworkInterface& ifc)
{
    Enter_Method("indicate");
    
    // Check if this is a DENM message
    auto* denm = dynamic_cast<stelvio_msgs::DenmMessage*>(packet);
    
    if (denm) {
        auto& vdp = getFacilities().get_const<artery::VehicleDataProvider>();
        
        // Skip if this is our own message
        if (denm->getStationId() == vdp.station_id()) {
            delete packet;
            return;
        }
        
        m_receptionTime = simTime();
        m_eventTime = denm->getEventTime();
        simtime_t receptionDelay = m_receptionTime - m_eventTime;
        
        EV_INFO << "DENM received from StationID=" << denm->getStationId()
                << " EventType=" << denm->getEventType()
                << " Delay=" << receptionDelay << "s"
                << " Infrastructure=" << denm->getInfrastructureType() << "\n";
        
        m_denmsReceived++;
        
        // Record reception metrics
        if (!m_receivedDenm) {
            m_receivedDenm = true;
            
            // Record scalars for this vehicle's first reception
            recordScalar("denm_received_flag", 1);
            recordScalar("denm_reception_time", m_receptionTime);
            recordScalar("denm_event_time", m_eventTime);
            recordScalar("denm_reception_delay", receptionDelay);
            
            // Check if within deadline
            bool withinDeadline = (receptionDelay <= m_denmDeadline);
            recordScalar("denm_within_deadline", withinDeadline ? 1 : 0);
            
            // Coverage flags (if received, vehicle was in coverage)
            recordScalar("denm_in_coverage", 1);
            recordScalar("denm_out_of_coverage", 0);
            recordScalar("denm_reliability_drop", 0);
        }
    }
    
    delete packet;
}

void VehicleReceiverService::trigger()
{
    // Periodic check - at end of simulation, record if DENM was never received
    // This is called periodically by middleware
}

void VehicleReceiverService::finish()
{
    artery::ItsG5Service::finish();
    
    // If DENM was never received, record appropriate metrics
    if (!m_receivedDenm) {
        EV_INFO << "Vehicle never received DENM - recording as out of coverage\n";
        
        recordScalar("denm_received_flag", 0);
        recordScalar("denm_reception_time", 0);
        recordScalar("denm_event_time", 0);
        recordScalar("denm_reception_delay", 0);
        recordScalar("denm_within_deadline", 0);
        recordScalar("denm_in_coverage", 0);
        
        // Mark as out of coverage (could also be reliability drop, but we assume coverage issue)
        recordScalar("denm_out_of_coverage", 1);
        recordScalar("denm_reliability_drop", 0);
    }
    
    EV_INFO << "VehicleReceiverService finished - Received " << m_denmsReceived << " DENMs\n";
}

} // namespace stelvio

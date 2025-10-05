//
// DenmMessage.msg - Simple DENM message for Stelvio scenario
// Contains essential fields for V2X alert transmission
//

namespace stelvio_msgs;

//
// Simplified DENM message for crash/witness alerts
// Used for 6G hybrid V2X infrastructure study
//
packet DenmMessage {
    // Message identification
    uint32_t stationId;           // Sender station ID
    uint32_t sequenceNumber;      // Message sequence number
    
    // Event information
    simtime_t eventTime;          // When the event occurred
    simtime_t generationTime;     // When the message was generated
    
    // Event type
    string eventType;             // "CRASH" or "WITNESS"
    
    // Position (simplified)
    double positionX;
    double positionY;
    
    // Metadata for analysis
    string infrastructureType;    // "terrestrial", "satellite", "hybrid"
}

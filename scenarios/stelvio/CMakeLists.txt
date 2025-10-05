# CMakeLists.txt for Stelvio Scenario
# Compiles custom C++ services for 6G hybrid V2X simulation

# Generate message files FIRST
add_opp_message(
    stelvio-message
    MESSAGE src/DenmMessage.msg
    MSG_PREFIX stelvio_msgs
)

# Then add the feature (services) that depends on the message
add_artery_feature(stelvio
    src/CrashedVehicleService.cc
    src/WitnessVehicleService.cc
    src/InfrastructureService.cc
    src/VehicleReceiverService.cc
)

# Link the message library and add dependencies
target_link_libraries(stelvio PRIVATE stelvio-message)
add_dependencies(stelvio stelvio-message)

# Include directories for source and generated message headers
target_include_directories(stelvio PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}
)

# Add NED folders for OMNeT++
add_opp_run(stelvio_scenario NED_FOLDERS 
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

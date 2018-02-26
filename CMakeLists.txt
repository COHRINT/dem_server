cmake_minimum_required(VERSION 2.8.3)
project(dem_server)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")
find_package(catkin REQUIRED
        COMPONENTS
            roscpp
            tf
            nav_msgs
        )

find_package(Boost REQUIRED COMPONENTS system)

find_package(PkgConfig)
pkg_check_modules(NEW_YAMLCPP yaml-cpp>=0.5)
if(NEW_YAMLCPP_FOUND)
add_definitions(-DHAVE_NEW_YAMLCPP)
endif(NEW_YAMLCPP_FOUND)

catkin_package(
    INCLUDE_DIRS
        include
    LIBRARIES
        image_loader
    CATKIN_DEPENDS
        roscpp
        tf
        nav_msgs
)

include_directories( include ${catkin_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS} )
add_library(image_loader src/image_loader.cpp)
target_link_libraries(image_loader SDL2 SDL2_image ${Boost_LIBRARIES})

add_executable(dem_server src/main.cpp)
target_link_libraries(dem_server
    image_loader
    yaml-cpp
    ${catkin_LIBRARIES}
)






## Install executables and/or libraries
install(TARGETS dem_server image_loader
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

## Install project namespaced headers
install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
  FILES_MATCHING PATTERN "*.h"
  PATTERN ".svn" EXCLUDE)

## Install excutable python script
install( 
    PROGRAMS
      scripts/crop_map
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

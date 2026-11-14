cmake_minimum_required(VERSION 3.20)
project(crm LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# The domain, storage and UI as a library, used by the program and by the tests.
add_library(crm_core
    src/text.cpp src/date.cpp src/interaction.cpp src/customer.cpp
    src/crm.cpp src/storage.cpp src/console_ui.cpp)
target_include_directories(crm_core PUBLIC include)

if(MSVC)
    target_compile_options(crm_core PUBLIC /W4 /permissive-)
else()
    target_compile_options(crm_core PUBLIC -Wall -Wextra -Wpedantic)
endif()

add_executable(crm src/main.cpp)
target_link_libraries(crm PRIVATE crm_core)

add_executable(crm_tests tests/tests.cpp)
target_link_libraries(crm_tests PRIVATE crm_core)

enable_testing()
add_test(NAME crm_tests COMMAND crm_tests)

cmake_minimum_required(VERSION 3.25)

get_filename_component(LADYBIRD_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
list(APPEND CMAKE_MODULE_PATH "${LADYBIRD_SOURCE_DIR}/Meta/CMake")

include(use_linker)

if (CMAKE_TOOLCHAIN_FILE MATCHES "vcpkg.cmake$")
    set(VCPKG_OVERLAY_TRIPLETS "${LADYBIRD_SOURCE_DIR}/Meta/CMake/vcpkg/release-triplets" CACHE STRING "" FORCE)
    set(VCPKG_INSTALL_OPTIONS "--no-print-usage" CACHE STRING "" FORCE)
    set(CMAKE_PROJECT_ladybird_js_only_INCLUDE_BEFORE "${LADYBIRD_SOURCE_DIR}/Meta/CMake/vcpkg/generate_vcpkg_toolchain_variables.cmake")

    if (NOT DEFINED CACHE{VCPKG_TARGET_TRIPLET} AND NOT DEFINED CACHE{VCPKG_HOST_TRIPLET})
        cmake_host_system_information(RESULT host_arch QUERY OS_PLATFORM)
        cmake_host_system_information(RESULT host_os QUERY OS_NAME)

        if (host_arch MATCHES "^(x86_64|AMD64|amd64)$")
            set(host_arch x64)
        elseif (host_arch MATCHES "^(aarch64|arm64|ARM64)$")
            set(host_arch arm64)
        elseif (host_arch STREQUAL "riscv64")
            set(host_arch riscv64)
        else()
            message(FATAL_ERROR "Unable to detect vcpkg architecture. Set VCPKG_TARGET_TRIPLET manually.")
        endif()

        if (host_os STREQUAL "Linux")
            set(host_os linux)
        elseif (host_os MATCHES "Darwin|macOS")
            set(host_os osx)
        elseif (host_os MATCHES "Windows")
            set(host_os windows)
        elseif (host_os MATCHES "FreeBSD")
            set(host_os freebsd)
        else()
            message(FATAL_ERROR "Unable to detect vcpkg OS. Set VCPKG_TARGET_TRIPLET manually.")
        endif()

        set(vcpkg_triplet "${host_arch}-${host_os}")
        if (NOT host_os STREQUAL "windows")
            set(vcpkg_triplet "${vcpkg_triplet}-dynamic")
        endif()

        message(STATUS "Determined JS-only VCPKG_TARGET_TRIPLET: ${vcpkg_triplet}")
        set(VCPKG_TARGET_TRIPLET "${vcpkg_triplet}" CACHE STRING "")
        set(VCPKG_HOST_TRIPLET "${vcpkg_triplet}" CACHE STRING "")
    endif()
endif()

project(ladybird_js_only
    VERSION 0.1.0
    LANGUAGES C CXX
    DESCRIPTION "Ladybird LibJS standalone shell"
)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(ENABLE_GUI_TARGETS OFF CACHE BOOL "" FORCE)
set(ENABLE_INSTALL_HEADERS OFF CACHE BOOL "" FORCE)
set(ENABLE_INSTALL_FREEDESKTOP_FILES OFF CACHE BOOL "" FORCE)
set(LADYBIRD_ENABLE_CPPTRACE OFF CACHE BOOL "" FORCE)

include(compile_options)
include(cmake_options)
include(lagom_install)
include(rust_crate)
include(targets)

find_package(PkgConfig REQUIRED)

find_package(mimalloc CONFIG REQUIRED)
find_package(Backtrace)
find_package(FastFloat CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)
find_package(simdutf REQUIRED)
find_package(ICU 78.2 EXACT REQUIRED COMPONENTS data i18n uc)
find_package(OpenSSL REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_package(simdjson CONFIG REQUIRED)
find_package(Threads REQUIRED)

pkg_check_modules(libtommath REQUIRED IMPORTED_TARGET libtommath)
pkg_check_modules(LIBPSL REQUIRED IMPORTED_TARGET libpsl)
if (NOT WIN32 AND NOT ANDROID)
    pkg_check_modules(LIBEDIT REQUIRED IMPORTED_TARGET libedit)
endif()

add_library(JSClangPlugin INTERFACE)
add_library(GenericClangPlugin INTERFACE)
add_lagom_library_install_rules(GenericClangPlugin)
add_lagom_library_install_rules(JSClangPlugin)

include_directories("${LADYBIRD_SOURCE_DIR}")
include_directories("${LADYBIRD_SOURCE_DIR}/Libraries")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_BINARY_DIR}/Libraries")

function(add_ladybird_source_dir relative_path)
    add_subdirectory("${LADYBIRD_SOURCE_DIR}/${relative_path}" "${CMAKE_BINARY_DIR}/${relative_path}")
endfunction()

add_ladybird_source_dir(AK)
add_ladybird_source_dir(Libraries/LibCore)
add_ladybird_source_dir(Libraries/LibFileSystem)
add_ladybird_source_dir(Libraries/LibMain)
add_ladybird_source_dir(Libraries/LibRegex)
add_ladybird_source_dir(Libraries/LibSync)
add_ladybird_source_dir(Libraries/LibTextCodec)
add_ladybird_source_dir(Libraries/LibUnicode)
add_ladybird_source_dir(Libraries/LibURL)
add_ladybird_source_dir(Libraries/LibCrypto)
add_ladybird_source_dir(Libraries/LibGC)
add_ladybird_source_dir(Libraries/LibJS)
add_ladybird_source_dir(Libraries/LibSyntax)
add_ladybird_source_dir(Libraries/LibThreading)

set(js_libraries
    LibCrypto
    LibJS
    LibMain
    LibTextCodec
    LibGC
    Threads::Threads
)

if (NOT WIN32)
    list(APPEND js_libraries PkgConfig::LIBEDIT)
endif()

ladybird_utility(js
    SOURCES "${LADYBIRD_SOURCE_DIR}/Utilities/js.cpp"
    LIBS ${js_libraries}
)

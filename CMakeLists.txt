cmake_minimum_required(VERSION 3.16)

# set the output directory for built objects.
# This makes sure that the dynamic library goes into the build directory automatically.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIGURATION>")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIGURATION>")

# prevent installing to system directories. 
set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE INTERNAL "")

# Declare the project
project(sdl-min)

set(SDL_SHARED ON)

if(MSVC)
    if(NOT CMAKE_GENERATOR STREQUAL "Ninja")
        add_definitions(/MP)				# parallelize each target, unless Ninja is the generator
    endif()
endif()

# Set the name of the executable
set(EXECUTABLE_NAME ${PROJECT_NAME})

# Create an executable and add our sources to it
add_executable(${EXECUTABLE_NAME})

# Add your sources to the target
target_sources(${EXECUTABLE_NAME} 
PRIVATE 
    src/main.cpp
)

# Set C++ version
target_compile_features(${EXECUTABLE_NAME} PUBLIC cxx_std_20)

# Configure SDL by calling its CMake file.
# we use EXCLUDE_FROM_ALL so that its install targets and configs don't
# pollute upwards into our configuration.
add_subdirectory(external/SDL EXCLUDE_FROM_ALL)

# If you don't want SDL_ttf, then remove this section.
set(SDLTTF_VENDORED ON) # tell SDL_ttf to build its own dependencies
add_subdirectory(external/SDL_ttf EXCLUDE_FROM_ALL)	

# SDL_mixer (used for playing audio)
set(SDLMIXER_MIDI_NATIVE OFF)     # disable formats we don't use to make the build faster and smaller. Also some of these don't work on all platforms so you'll need to do some experimentation.
set(SDLMIXER_GME OFF)
set(SDLMIXER_WAVPACK OFF)     
set(SDLMIXER_MOD OFF)
set(SDLMIXER_OPUS OFF)
set(SDLMIXER_MP3_MPG123 OFF)
set(SDLMIXER_VORBIS_VORBISFILE OFF)
set(SDLMIXER_FLAC_LIBFLAC OFF)
set(SDLMIXER_VENDORED ON)   # tell SDL_mixer to build its own dependencies
add_subdirectory(external/SDL_mixer EXCLUDE_FROM_ALL)

# SDL_image (used for loading various image formats)
set(SDLIMAGE_VENDORED ON)
set(SDLIMAGE_AVIF OFF)	# disable formats we don't use to make the build faster and smaller.
set(SDLIMAGE_BMP OFF)
set(SDLIMAGE_JPEG OFF)
set(SDLIMAGE_WEBP OFF)
add_subdirectory(external/SDL_image EXCLUDE_FROM_ALL)

# Link SDL to our executable. This also makes its include directory available to us. 
target_link_libraries(${EXECUTABLE_NAME} PUBLIC 
    SDL3_ttf::SDL3_ttf      # remove if you are not using SDL_ttf
    SDL3_mixer::SDL3_mixer  # remove if you are not using SDL_mixer
    SDL3_image::SDL3_image	# remove if you are not using SDL_image
    SDL3::SDL3              # If using satelite libraries, SDL must be the last item in the list. 
)

target_compile_definitions(${EXECUTABLE_NAME} PUBLIC SDL_MAIN_USE_CALLBACKS)

# Dealing with assets
# We have some non-code resources that our application needs in order to work. How we deal with those differs per platform.
macro(copy_helper filename)
    # for platforms that do not have a good packaging format, all we can do is copy the assets to the process working directory.
    set(outname "${CMAKE_BINARY_DIR}/$<CONFIGURATION>/${filename}")
    add_custom_command(POST_BUILD
        TARGET "${EXECUTABLE_NAME}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_LIST_DIR}/src/${filename}" "${outname}"
        DEPENDS "${filename}"
    )
endmacro()
copy_helper("Inter-VariableFont.ttf")
copy_helper("the_entertainer.ogg")
copy_helper("gs_tiger.svg")

# on Visual Studio, set our app as the default project
set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT "${EXECUTABLE_NAME}")

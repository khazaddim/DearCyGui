# Install script for directory: C:/Chris/DearCyGui/thirdparty/SDL

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files (x86)/SDL3")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/sdl3.pc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Chris/DearCyGui/build_SDL/RelWithDebInfo/SDL3-static.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Chris/DearCyGui/build_SDL/Debug/SDL3-static.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Chris/DearCyGui/build_SDL/Release/SDL3-static.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Chris/DearCyGui/build_SDL/MinSizeRel/SDL3-static.lib")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE FILE OPTIONAL FILES "C:/Chris/DearCyGui/build_SDL/${CMAKE_INSTALL_CONFIG_NAME}/SDL3-static.pdb")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3headersTargets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3headersTargets.cmake"
         "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3headersTargets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3headersTargets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3headersTargets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3headersTargets.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3staticTargets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3staticTargets.cmake"
         "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3staticTargets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3staticTargets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/SDL3staticTargets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3staticTargets.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3staticTargets-debug.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3staticTargets-minsizerel.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3staticTargets-relwithdebinfo.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "C:/Chris/DearCyGui/build_SDL/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/SDL3staticTargets-release.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES
    "C:/Chris/DearCyGui/build_SDL/SDL3Config.cmake"
    "C:/Chris/DearCyGui/build_SDL/SDL3ConfigVersion.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/SDL3" TYPE FILE FILES
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_assert.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_asyncio.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_atomic.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_audio.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_begin_code.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_bits.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_blendmode.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_camera.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_clipboard.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_close_code.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_copying.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_cpuinfo.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_dialog.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_egl.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_endian.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_error.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_events.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_filesystem.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_gamepad.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_gpu.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_guid.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_haptic.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_hidapi.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_hints.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_init.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_intrin.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_iostream.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_joystick.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_keyboard.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_keycode.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_loadso.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_locale.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_log.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_main.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_main_impl.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_messagebox.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_metal.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_misc.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_mouse.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_mutex.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_oldnames.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengl.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengl_glext.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengles.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengles2.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengles2_gl2.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengles2_gl2ext.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengles2_gl2platform.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_opengles2_khrplatform.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_pen.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_pixels.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_platform.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_platform_defines.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_power.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_process.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_properties.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_rect.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_render.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_scancode.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_sensor.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_stdinc.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_storage.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_surface.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_system.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_thread.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_time.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_timer.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_touch.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_tray.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_version.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_video.h"
    "C:/Chris/DearCyGui/thirdparty/SDL/include/SDL3/SDL_vulkan.h"
    "C:/Chris/DearCyGui/build_SDL/include-revision/SDL3/SDL_revision.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/licenses/SDL3" TYPE FILE FILES "C:/Chris/DearCyGui/thirdparty/SDL/LICENSE.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "C:/Chris/DearCyGui/build_SDL/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
if(CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_COMPONENT MATCHES "^[a-zA-Z0-9_.+-]+$")
    set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
  else()
    string(MD5 CMAKE_INST_COMP_HASH "${CMAKE_INSTALL_COMPONENT}")
    set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INST_COMP_HASH}.txt")
    unset(CMAKE_INST_COMP_HASH)
  endif()
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "C:/Chris/DearCyGui/build_SDL/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()

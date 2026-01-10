cmake_minimum_required(VERSION 3.16)
project(game_backend_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(game_backend
    src/main.cpp
    src/game.cpp
)

target_include_directories(game_backend PRIVATE src)



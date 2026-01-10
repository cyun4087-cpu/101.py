#include "game.hpp"

#include <cctype>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>

static void printHelp() {
  std::cout << "Commands:\n"
               "  help\n"
               "  state\n"
               "  tick [N]\n"
               "  left on|off\n"
               "  right on|off\n"
               "  shoot X Y           (screen coords)\n"
               "  buy coat|oxygenMask|downJacket|spacesuit\n"
               "  clearwarning        (like ESC)\n"
               "  reset\n"
               "  quit\n";
}

static void printState(const Game::Snapshot& s) {
  std::cout << "state=" << Game::toString(s.state) << " height=" << std::fixed << std::setprecision(1) << s.gameHeight
            << " oxygen=" << s.oxygen << " temp=" << s.temperature << " stress=" << s.stress << " coins=" << s.coins
            << " equip=" << Game::toString(s.equipment) << " arrows=" << s.arrows.size()
            << " monsters=" << s.monsters.size() << "\n";
  if (!s.warningMessage.empty()) {
    std::cout << "warningType=" << s.warningType << " message=" << s.warningMessage << "\n";
  }
}

int main(int argc, char** argv) {
  std::uint32_t seed = 1;
  if (argc >= 2) {
    seed = static_cast<std::uint32_t>(std::strtoul(argv[1], nullptr, 10));
  }

  Game game(seed);
  Game::Input held;

  std::cout << "C++ game backend (no UI). Type 'help'. Seed=" << seed << "\n";
  printState(game.snapshot());

  std::string line;
  while (std::cout << "> " && std::getline(std::cin, line)) {
    std::istringstream iss(line);
    std::string cmd;
    if (!(iss >> cmd))
      continue;

    // normalize command to lowercase
    for (auto& ch : cmd)
      ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));

    Game::Input in = held;
    in.shootTarget.reset();
    in.buy.reset();
    in.clearWarning = false;
    in.reset = false;

    if (cmd == "help") {
      printHelp();
      continue;
    }
    if (cmd == "quit" || cmd == "exit") {
      break;
    }
    if (cmd == "state") {
      printState(game.snapshot());
      continue;
    }
    if (cmd == "left") {
      std::string onoff;
      iss >> onoff;
      for (auto& ch : onoff)
        ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
      if (onoff == "on")
        held.leftHeld = true;
      else if (onoff == "off")
        held.leftHeld = false;
      else
        std::cout << "usage: left on|off\n";
      continue;
    }
    if (cmd == "right") {
      std::string onoff;
      iss >> onoff;
      for (auto& ch : onoff)
        ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
      if (onoff == "on")
        held.rightHeld = true;
      else if (onoff == "off")
        held.rightHeld = false;
      else
        std::cout << "usage: right on|off\n";
      continue;
    }
    if (cmd == "shoot") {
      double x = 0, y = 0;
      if (!(iss >> x >> y)) {
        std::cout << "usage: shoot X Y\n";
        continue;
      }
      in.shootTarget = Game::Vec2{x, y};
      game.tick(in);
      printState(game.snapshot());
      continue;
    }
    if (cmd == "buy") {
      std::string eq;
      if (!(iss >> eq)) {
        std::cout << "usage: buy coat|oxygenMask|downJacket|spacesuit\n";
        continue;
      }
      try {
        in.buy = Game::equipmentFromString(eq);
      } catch (const std::exception& e) {
        std::cout << e.what() << "\n";
        continue;
      }
      game.tick(in);
      printState(game.snapshot());
      continue;
    }
    if (cmd == "clearwarning") {
      in.clearWarning = true;
      game.tick(in);
      printState(game.snapshot());
      continue;
    }
    if (cmd == "reset") {
      in.reset = true;
      game.tick(in);
      printState(game.snapshot());
      continue;
    }
    if (cmd == "tick") {
      int n = 1;
      iss >> n;
      if (n < 1)
        n = 1;
      for (int i = 0; i < n; ++i) {
        game.tick(held);
        const auto s = game.snapshot();
        if (s.state == Game::State::GameOver || s.state == Game::State::Victory) {
          break;
        }
      }
      printState(game.snapshot());
      continue;
    }

    std::cout << "unknown command. type 'help'.\n";
  }

  return 0;
}



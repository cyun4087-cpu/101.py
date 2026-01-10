#pragma once

#include <cstdint>
#include <optional>
#include <random>
#include <string>
#include <vector>

class Game {
public:
  enum class State { Playing, Warning, GameOver, Victory };
  enum class Equipment { GrassSkirt, Coat, OxygenMask, DownJacket, Spacesuit };

  struct Vec2 {
    double x{};
    double y{};
  };

  struct Archer {
    Vec2 pos{200.0, 400.0};
    double width{30.0};
    double height{40.0};
    double riseSpeed{0.8};
    double moveSpeed{3.0};
  };

  struct Arrow {
    Vec2 pos{};
    Vec2 vel{};
    double angleRad{};
  };

  struct Monster {
    Vec2 pos{};
    double width{};
    double height{};
    int level{};
    double fallSpeed{};
    double horizontalSpeed{};
  };

  struct Input {
    bool leftHeld{false};
    bool rightHeld{false};
    std::optional<Vec2> shootTarget; // screen coords
    std::optional<Equipment> buy;
    bool clearWarning{false}; // similar to ESC in JS
    bool reset{false};
  };

  struct Snapshot {
    State state{};
    double gameHeight{};
    double oxygen{};
    double temperature{};
    double stress{}; // 0..100
    int coins{};
    Equipment equipment{};
    std::string warningMessage{};
    std::string warningType{}; // "oxygen" / "temperature" / ""
    Archer archer{};
    std::vector<Arrow> arrows;
    std::vector<Monster> monsters;
  };

  explicit Game(std::uint32_t seed = 1);

  void reset();
  void tick(const Input& input); // 1 frame (assumes 60fps like original)
  Snapshot snapshot() const;

  // Helpers for UI/CLI
  static std::string toString(State s);
  static std::string toString(Equipment e);
  static Equipment equipmentFromString(const std::string& s);

private:
  struct Env {
    double oxygen{};
    double temperature{};
  };
  struct Protection {
    double oxygen{};
    double temperature{};
  };

  static constexpr double kWidth = 800.0;
  static constexpr double kHeight = 600.0;
  static constexpr double kMonsterSpawnRate = 0.02; // per tick
  static constexpr double kArrowSpeed = 8.0;
  static constexpr double kMonsterBaseSpeed = 1.5;

  Env environmentParams(double height) const;
  Protection equipmentProtection(Equipment e) const;
  void checkSurvival();
  void updateStress(); // must be called each tick while running
  void createMonster();
  void shootAt(const Vec2& target);
  void updateArrows();
  void updateMonsters();
  void checkCollisions();
  bool buyEquipment(Equipment e);

  static double clamp(double v, double lo, double hi);

  // RNG
  std::mt19937 rng_;
  std::uniform_real_distribution<double> uni_{0.0, 1.0};

  // state
  State state_{State::Playing};
  double gameHeight_{0.0};
  double oxygen_{100.0};
  double temperature_{20.0};
  double stress_{0.0}; // 0..100
  int coins_{0};
  Equipment equipment_{Equipment::GrassSkirt};
  std::string warningMessage_{};
  std::string warningType_{};

  Archer archer_{};
  Archer archerBase_{}; // reference values (e.g., base moveSpeed)
  bool leftHeld_{false};
  bool rightHeld_{false};

  std::vector<Arrow> arrows_;
  std::vector<Monster> monsters_;
};



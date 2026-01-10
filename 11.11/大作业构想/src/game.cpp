#include "game.hpp"

#include <algorithm>
#include <cmath>
#include <sstream>
#include <stdexcept>

Game::Game(std::uint32_t seed) : rng_(seed) { reset(); }

void Game::reset() {
  state_ = State::Playing;
  gameHeight_ = 0.0;
  oxygen_ = 100.0;
  temperature_ = 20.0;
  stress_ = 0.0;
  coins_ = 0;
  equipment_ = Equipment::GrassSkirt;
  warningMessage_.clear();
  warningType_.clear();
  archer_ = Archer{};
  archerBase_ = archer_;
  leftHeld_ = false;
  rightHeld_ = false;
  arrows_.clear();
  monsters_.clear();
}

double Game::clamp(double v, double lo, double hi) { return std::max(lo, std::min(hi, v)); }

Game::Env Game::environmentParams(double h) const {
  double oxy = 0.0;
  double temp = 0.0;

  if (h < 1000.0) {
    oxy = 100.0;
    temp = 20.0;
  } else if (h < 3000.0) {
    oxy = 100.0 - (h - 1000.0) * 0.02;
    temp = 20.0 - (h - 1000.0) * 0.01;
  } else if (h < 6000.0) {
    oxy = 60.0 - (h - 3000.0) * 0.015;
    temp = 0.0 - (h - 3000.0) * 0.01;
  } else if (h < 10000.0) {
    oxy = 35.0 - (h - 6000.0) * 0.01;
    temp = -30.0 - (h - 6000.0) * 0.015;
  } else {
    oxy = std::max(0.0, 25.0 - (h - 10000.0) * 0.005);
    temp = -90.0 - (h - 10000.0) * 0.02;
  }

  return Env{std::max(0.0, oxy), temp};
}

Game::Protection Game::equipmentProtection(Equipment e) const {
  switch (e) {
  case Equipment::GrassSkirt:
    return Protection{0.0, 0.0};
  case Equipment::Coat:
    return Protection{0.0, 20.0};
  case Equipment::OxygenMask:
    return Protection{50.0, 0.0};
  case Equipment::DownJacket:
    return Protection{30.0, 50.0};
  case Equipment::Spacesuit:
    return Protection{100.0, 100.0};
  }
  return Protection{0.0, 0.0};
}

void Game::checkSurvival() {
  const auto env = environmentParams(gameHeight_);
  const auto prot = equipmentProtection(equipment_);
  // "Supply" oxygen from environment + equipment.
  // Stress increases oxygen consumption in real life, so we model it as reducing
  // effective oxygen available for survival checks.
  const double oxygenSupply = env.oxygen + prot.oxygen;
  const double stressOxygenPenalty = clamp(stress_, 0.0, 100.0) * 0.25; // up to -25
  const double effectiveOxygen = oxygenSupply - stressOxygenPenalty;
  const double effectiveTemp = env.temperature + prot.temperature;

  oxygen_ = effectiveOxygen;
  temperature_ = effectiveTemp;

  // warning priority: temperature > oxygen (match JS behavior)
  if (effectiveTemp < 5.0 && equipment_ != Equipment::DownJacket && equipment_ != Equipment::Spacesuit) {
    if (warningType_ != "temperature" || warningMessage_ != "温度极低！需要购买羽绒服！") {
      state_ = State::Warning;
      warningType_ = "temperature";
      warningMessage_ = "温度极低！需要购买羽绒服！";
    }
  } else if (effectiveTemp < 18.0 && equipment_ == Equipment::GrassSkirt) {
    if (warningType_ != "temperature" || warningMessage_ != "温度过低！需要购买大衣！") {
      state_ = State::Warning;
      warningType_ = "temperature";
      warningMessage_ = "温度过低！需要购买大衣！";
    }
  } else if (effectiveOxygen < 30.0 && warningType_ != "oxygen") {
    state_ = State::Warning;
    warningType_ = "oxygen";
    warningMessage_ = "氧气不足！需要购买氧气罩或更高级装备！";
  }

  if (effectiveOxygen < 10.0 || effectiveTemp < -30.0) {
    state_ = State::GameOver;
  }

  if (equipment_ == Equipment::Spacesuit && gameHeight_ > 15000.0) {
    state_ = State::Victory;
  }
}

void Game::updateStress() {
  // Stress is modeled 0..100. It rises with immediate threat (nearby monsters),
  // poor life support (low oxygen / cold), and being in warning state; it decays
  // slowly when safe.
  double delta = 0.0;

  // Threat: nearest monster proximity to archer (screen space)
  double nearest = 1e9;
  for (const auto& m : monsters_) {
    const double dx = archer_.pos.x - m.pos.x;
    const double dy = archer_.pos.y - m.pos.y;
    const double d = std::sqrt(dx * dx + dy * dy);
    nearest = std::min(nearest, d);
  }
  if (!monsters_.empty()) {
    // within 250px starts adding; within 80px adds a lot
    const double threat = clamp((250.0 - nearest) / 170.0, 0.0, 1.0);
    delta += threat * 1.8;
  }

  // Physiological stressors: low oxygen and cold increase stress
  if (oxygen_ < 40.0)
    delta += clamp((40.0 - oxygen_) / 30.0, 0.0, 1.0) * 1.2;
  if (temperature_ < 10.0)
    delta += clamp((10.0 - temperature_) / 30.0, 0.0, 1.0) * 1.0;

  // Being in warning state adds some sustained pressure
  if (state_ == State::Warning)
    delta += 0.6;

  // Natural recovery when conditions are okay
  const bool safe = monsters_.empty() && oxygen_ >= 60.0 && temperature_ >= 15.0 && state_ == State::Playing;
  if (safe)
    delta -= 0.8;
  else
    delta -= 0.15;

  stress_ = clamp(stress_ + delta, 0.0, 100.0);

  // Performance impact: high stress -> slightly slower lateral movement
  // (tremor/hesitation), but keep it mild so the sim stays playable.
  const double slowFactor = 1.0 - (stress_ / 100.0) * 0.25; // up to -25%
  archer_.moveSpeed = archerBase_.moveSpeed * clamp(slowFactor, 0.75, 1.0);
}

void Game::createMonster() {
  const int level = static_cast<int>(std::floor(uni_(rng_) * 3.0)) + 1; // 1..3
  Monster m;
  m.pos.x = uni_(rng_) * (kWidth - 60.0) + 30.0;
  m.pos.y = -50.0;
  m.width = 20.0 + level * 5.0;
  m.height = 20.0 + level * 5.0;
  m.level = level;
  m.fallSpeed = kMonsterBaseSpeed + level * 0.3;
  m.horizontalSpeed = (uni_(rng_) - 0.5) * 1.5;
  monsters_.push_back(m);
}

void Game::shootAt(const Vec2& target) {
  const double dx = target.x - archer_.pos.x;
  const double dy = target.y - archer_.pos.y;
  const double angle = std::atan2(dy, dx);

  Arrow a;
  a.pos = archer_.pos;
  a.vel.x = std::cos(angle) * kArrowSpeed;
  a.vel.y = std::sin(angle) * kArrowSpeed;
  a.angleRad = angle;
  arrows_.push_back(a);
}

void Game::updateArrows() {
  for (auto& a : arrows_) {
    a.pos.x += a.vel.x;
    a.pos.y += a.vel.y;
  }
  arrows_.erase(std::remove_if(arrows_.begin(), arrows_.end(),
                               [&](const Arrow& a) {
                                 return a.pos.x < -50.0 || a.pos.x > kWidth + 50.0 || a.pos.y < -50.0 ||
                                        a.pos.y > kHeight + 50.0;
                               }),
                arrows_.end());
}

void Game::updateMonsters() {
  for (auto& m : monsters_) {
    m.pos.x += m.horizontalSpeed;
    if (m.pos.x < m.width / 2.0 || m.pos.x > kWidth - m.width / 2.0) {
      m.horizontalSpeed *= -1.0;
      m.pos.x = clamp(m.pos.x, m.width / 2.0, kWidth - m.width / 2.0);
    }
    m.pos.y += m.fallSpeed - archer_.riseSpeed;
  }
  monsters_.erase(std::remove_if(monsters_.begin(), monsters_.end(), [&](const Monster& m) {
                   return m.pos.y > kHeight + 100.0;
                 }),
                 monsters_.end());
}

void Game::checkCollisions() {
  // arrow vs monster
  for (int i = static_cast<int>(arrows_.size()) - 1; i >= 0; --i) {
    for (int j = static_cast<int>(monsters_.size()) - 1; j >= 0; --j) {
      const auto& a = arrows_[static_cast<std::size_t>(i)];
      const auto& m = monsters_[static_cast<std::size_t>(j)];
      const double dx = a.pos.x - m.pos.x;
      const double dy = a.pos.y - m.pos.y;
      const double dist = std::sqrt(dx * dx + dy * dy);
      if (dist < (m.width + 10.0) / 2.0) {
        coins_ += m.level * 10;
        arrows_.erase(arrows_.begin() + i);
        monsters_.erase(monsters_.begin() + j);
        break;
      }
    }
  }

  // archer vs monster (AABB)
  for (int i = static_cast<int>(monsters_.size()) - 1; i >= 0; --i) {
    const auto& m = monsters_[static_cast<std::size_t>(i)];
    const double distX = std::abs(archer_.pos.x - m.pos.x);
    const double distY = std::abs(archer_.pos.y - m.pos.y);
    if (distX < (archer_.width + m.width) / 2.0 && distY < (archer_.height + m.height) / 2.0) {
      state_ = State::GameOver;
      break;
    }
  }
}

bool Game::buyEquipment(Equipment e) {
  const std::vector<Equipment> order = {Equipment::GrassSkirt, Equipment::Coat, Equipment::OxygenMask,
                                       Equipment::DownJacket, Equipment::Spacesuit};
  auto itCur = std::find(order.begin(), order.end(), equipment_);
  auto itTar = std::find(order.begin(), order.end(), e);
  if (itCur == order.end() || itTar == order.end())
    return false;
  if (std::distance(order.begin(), itTar) != std::distance(order.begin(), itCur) + 1)
    return false;

  const int price = [&]() -> int {
    switch (e) {
    case Equipment::Coat:
      return 400;
    case Equipment::OxygenMask:
      return 600;
    case Equipment::DownJacket:
      return 1000;
    case Equipment::Spacesuit:
      return 2500;
    case Equipment::GrassSkirt:
      return 0;
    }
    return 0;
  }();

  if (price > 0 && coins_ >= price) {
    coins_ -= price;
    equipment_ = e;
    state_ = State::Playing;
    warningMessage_.clear();
    warningType_.clear();
    return true;
  }
  return false;
}

void Game::tick(const Input& input) {
  if (input.reset) {
    reset();
    return;
  }

  // record held keys
  leftHeld_ = input.leftHeld;
  rightHeld_ = input.rightHeld;

  // allow clearing warning (like ESC)
  if (state_ == State::Warning && input.clearWarning) {
    state_ = State::Playing;
    warningMessage_.clear();
    warningType_.clear();
  }

  // handle buy (allowed in playing or warning; match JS)
  if ((state_ == State::Playing || state_ == State::Warning) && input.buy.has_value()) {
    buyEquipment(*input.buy);
  }

  // handle shoot
  if (state_ == State::Playing && input.shootTarget.has_value()) {
    shootAt(*input.shootTarget);
  }

  if (state_ != State::Playing && state_ != State::Warning) {
    return;
  }

  // move archer
  if (leftHeld_ && archer_.pos.x > archer_.width / 2.0) {
    archer_.pos.x -= archer_.moveSpeed;
  }
  if (rightHeld_ && archer_.pos.x < kWidth - archer_.width / 2.0) {
    archer_.pos.x += archer_.moveSpeed;
  }

  // rise
  gameHeight_ += archer_.riseSpeed;

  // environment/survival
  checkSurvival();
  // update stress after life-support calculation, so it reacts to current oxygen/temp
  updateStress();
  // stress affects oxygen via checkSurvival penalty; re-check survival once with updated stress
  checkSurvival();
  if (state_ == State::GameOver || state_ == State::Victory)
    return;

  // spawn monsters
  if (uni_(rng_) < kMonsterSpawnRate) {
    createMonster();
  }

  // update entities + collisions
  updateArrows();
  updateMonsters();
  checkCollisions();
}

Game::Snapshot Game::snapshot() const {
  Snapshot s;
  s.state = state_;
  s.gameHeight = gameHeight_;
  s.oxygen = oxygen_;
  s.temperature = temperature_;
  s.stress = stress_;
  s.coins = coins_;
  s.equipment = equipment_;
  s.warningMessage = warningMessage_;
  s.warningType = warningType_;
  s.archer = archer_;
  s.arrows = arrows_;
  s.monsters = monsters_;
  return s;
}

std::string Game::toString(State s) {
  switch (s) {
  case State::Playing:
    return "playing";
  case State::Warning:
    return "warning";
  case State::GameOver:
    return "gameOver";
  case State::Victory:
    return "victory";
  }
  return "unknown";
}

std::string Game::toString(Equipment e) {
  switch (e) {
  case Equipment::GrassSkirt:
    return "grassSkirt";
  case Equipment::Coat:
    return "coat";
  case Equipment::OxygenMask:
    return "oxygenMask";
  case Equipment::DownJacket:
    return "downJacket";
  case Equipment::Spacesuit:
    return "spacesuit";
  }
  return "unknown";
}

Game::Equipment Game::equipmentFromString(const std::string& s) {
  if (s == "grassSkirt")
    return Equipment::GrassSkirt;
  if (s == "coat")
    return Equipment::Coat;
  if (s == "oxygenMask")
    return Equipment::OxygenMask;
  if (s == "downJacket")
    return Equipment::DownJacket;
  if (s == "spacesuit")
    return Equipment::Spacesuit;
  throw std::invalid_argument("unknown equipment: " + s);
}



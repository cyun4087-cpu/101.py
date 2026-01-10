# 游戏后端（C++，无UI）

本仓库仅保留**游戏后端逻辑**（状态机/规则/模拟），已去除所有前端渲染与风格化设定（像素风画面、HTML/p5.js 等）。

如果你计划用虚幻引擎把它做成第一视角独立游戏，请看：`UE5_WORKFLOW.md`。

## 规则概览

- **高度**：每帧（60fps）固定上升 \(0.8m\)
- **环境**：氧气/温度随高度变化（见 `src/game.cpp` 的 `environmentParams`）
- **紧张度**：新增 0~100 的紧张度，受威胁/恶劣环境影响上升，安全时下降；紧张度会提高耗氧（等价于降低有效氧气）并轻微降低左右移动速度
- **装备**：只能按顺序购买，提供氧气/温度加成
- **怪物**：随机生成（1~3级），下落并左右摆动；碰到主角则失败
- **箭矢**：按目标点射击；命中怪物获得金币（等级×10）
- **胜利/失败**
  - 失败：有效氧气 < 10 或有效温度 < -30 或被怪物撞到
  - 胜利：穿上宇航服且高度 > 15000

### 装备价格（与当前后端实现一致）

- `coat`：400
- `oxygenMask`：600
- `downJacket`：1000
- `spacesuit`：2500

## 构建与运行（CMake）

在项目根目录执行：

```bash
cmake -S . -B build
cmake --build build --config Release
```

运行（可选传入随机种子）：

```bash
./build/game_backend 1
```

## 命令行用法（无UI）

启动后输入命令：

- `tick [N]`：推进 N 帧（默认 1）
- `left on|off` / `right on|off`：设置左右移动按键状态
- `shoot X Y`：向屏幕坐标 (X,Y) 射击（仅 `playing` 状态可射击）
- `buy coat|oxygenMask|downJacket|spacesuit`：购买装备（必须按顺序且金币足够）
- `clearwarning`：清除警告（类似原版 ESC）
- `state`：打印当前状态
- `reset`：重置
- `quit`：退出



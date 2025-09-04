# 🎮 Cube Comando: Alone Warrior

A intense 3D tower defense shooter where you play as the last square warrior defending your bridge against an endless invasion of geometric enemies. Built with PyGame and OpenGL for stunning visual effects and smooth gameplay.

[![PyGame](https://img.shields.io/badge/PyGame-2.5.2-brightgreen.svg)](https://www.pygame.org/)
[![OpenGL](https://img.shields.io/badge/OpenGL-3D%20Graphics-orange.svg)](https://www.opengl.org/)
[![Status](https://img.shields.io/badge/Status-Playable-success.svg)]()

![Gameplay](https://img.shields.io/badge/Gameplay-Fast%20Paced-blue) ![Style](https://img.shields.io/badge/Style-Action%20Tower%20Defense-red)

---

## ✨ Features

### 🎯 Core Gameplay
*   **Dual Enemy Types:** Battle regular spheres and tougher, health-based enemies with unique behaviors.
*   **Epic Boss Fights:** Giant enemy spheres with health bars that require sustained fire to defeat.
*   **Strategic Power-ups:** Collect health packs, ammo refills, and score bonuses that spawn throughout the battle.
*   **Multiple Loss Conditions:** Game over if you lose all health, waste too much ammo, or let too many enemies escape.

### 🎨 Visual Experience
*   **Dynamic 3D Environment:** Rendered with OpenGL for smooth, immersive graphics.
*   **Pulsing Visual Effects:** Enemies pulse and change color based on their health status.
*   **Sphere Markers:** Strategic indicators show spawn and exit points with colorful blink effects.
*   **Pickup Notifications:** Clear visual feedback when collecting power-ups.

### ⚙️ Game Mechanics
*   **Smart Enemy AI:** Enemies move strategically toward your position and the exit.
*   **Precision Shooting:** Physics-based bullet collision system with knockback effects.
*   **Cheat Mode:** Secret mode (`C` key) with auto-aim and rapid fire for when things get tough!
*   **Camera Control:** Free camera movement or follow player with toggleable perspectives.

### 📊 Progression System
*   **Score Tracking:** Comprehensive scoring system with bonuses for different enemy types.
*   **Health Management:** Balance offensive play with defensive awareness.
*   **Ammo Conservation:** Strategic shooting required - missed shots count against you!
*   **Enemy Escaped Counter:** Keep track of how many invaders have breached your defenses.

---

## 🕹️ How to Play

### Controls
| Key | Action |
| :--- | :--- |
| `W` `A` `S` `D` | Move and rotate your warrior |
| `Mouse Left` | Fire your weapon |
| `Mouse Right` | Toggle camera follow mode |
| `Arrow Keys` | Control camera angle and height |
| `C` | Toggle cheat mode (auto-aim + rapid fire) |
| `R` | Restart after game over |
| `Z`/`X` | Adjust field of view |

### Objectives
1. **Defend the bridge** from invading geometric enemies
2. **Prevent enemies** from reaching the exit (right side of bridge)
3. **Manage your resources** - health, ammo, and positioning
4. **Achieve the highest score** possible before being overwhelmed

### Enemy Types
*   **Regular Spheres:** Basic enemies - 1 hit to eliminate
*   **Advanced Spheres:** Have health bars - require multiple hits
*   **Giant Spheres:** Boss enemies with massive health pools - deal extra damage

### Power-ups
*   **Health Pack** (Green): Restores 5 health points
*   **Ammo Crate** (Blue): Reduces missed shot count by 5
*   **Score Bonus** (Pink): Instantly adds 30 points to your score

---

## 🛠️ Installation & Requirements

### Prerequisites
```bash
pip install pygame PyOpenGL PyOpenGL_accelerate

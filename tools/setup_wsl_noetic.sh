#!/usr/bin/env bash
# Установка ROS Noetic + Gazebo 11 в WSL2 Ubuntu 20.04 и сборка проекта.
# Запуск (внутри Ubuntu):  bash /mnt/c/Diplom_Multiagent_robots_ROS/tools/setup_wsl_noetic.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_DIR="$HOME/catkin_ws"

. /etc/os-release
if [ "$VERSION_CODENAME" != "focal" ]; then
  echo "Нужна Ubuntu 20.04 (focal), а сейчас: $PRETTY_NAME" >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y curl gnupg lsb-release

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros/ubuntu focal main" \
  | sudo tee /etc/apt/sources.list.d/ros1.list > /dev/null

sudo apt-get update
sudo apt-get install -y \
  ros-noetic-desktop-full \
  ros-noetic-gazebo-ros-control \
  ros-noetic-ros-controllers \
  ros-noetic-map-server \
  python3-rosdep \
  python3-pytest \
  python-is-python3

if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update

grep -qxF "source /opt/ros/noetic/setup.bash" "$HOME/.bashrc" \
  || echo "source /opt/ros/noetic/setup.bash" >> "$HOME/.bashrc"
source /opt/ros/noetic/setup.bash

mkdir -p "$WS_DIR/src"
ln -sfn "$REPO_DIR" "$WS_DIR/src/diplom"

cd "$WS_DIR"
rosdep install --from-paths src --ignore-src -y
catkin_make

grep -qxF "source $WS_DIR/devel/setup.bash" "$HOME/.bashrc" \
  || echo "source $WS_DIR/devel/setup.bash" >> "$HOME/.bashrc"

echo
echo "Готово. Откройте новый терминал Ubuntu и запустите:"
echo "  roslaunch my_robot_simulation_control ten_tobots.launch"

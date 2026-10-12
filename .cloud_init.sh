#!/bin/bash
# 山水工程云服务器初始化脚本 v2（补 sudo）
set -e
echo "== 1. 时区 =="
sudo timedatectl set-timezone Asia/Shanghai
date

echo "== 2. hostname =="
sudo hostnamectl set-hostname shanshui
hostname; hostnamectl | grep -i "static hostname"

echo "== 3. swap 2G =="
if swapon --show | grep -q swapfile; then
  echo "swap already active"
else
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  free -h | head -3
fi

echo "== 4. 基础工具 =="
sudo apt-get update -y
sudo apt-get install -y git tmux curl wget htop unzip jq
git --version; tmux -V

echo "== 5. 安全更新 =="
sudo apt-get upgrade -y
echo "== 内核状态 =="
uname -r; ls /boot/vmlinuz-* 2>/dev/null | tail -3

echo "== INIT DONE =="

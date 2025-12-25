<script setup>
import { computed, ref } from 'vue'
import { useGameStore, FISH_TYPES } from '../stores/game'

// 导入背景缩略图
import pondBg1 from '@/assets/pond-bg-1.jpg'
import pondBg2 from '@/assets/pond-bg-2.jpg'
import pondBg3 from '@/assets/pond-bg-3.jpg'
import pondBg4 from '@/assets/pond-bg-4.jpg'

const gameStore = useGameStore()

const emit = defineEmits(['feedAll', 'showScan', 'showCoupons', 'showShare'])

// 主题选择器状态
const showThemePicker = ref(false)

// 背景列表
const backgrounds = [
  { id: 1, src: pondBg1, name: '金沙海底' },
  { id: 2, src: pondBg2, name: '珊瑚礁石' },
  { id: 3, src: pondBg3, name: '清澈浅滩' },
  { id: 4, src: pondBg4, name: '粉紫岩礁' },
]

// 切换背景
function selectBackground(id) {
  gameStore.setBackground(id)
  showThemePicker.value = false
}

// 总可用饲料
const totalFeed = computed(() => gameStore.totalFeedAvailable)
</script>

<template>
  <div class="ui-panel">
    <!-- 顶部状态栏 -->
    <div class="ui-panel__header glass">
      <div class="header__left">
        <span class="header__title">🔥 Ocean Flame Pod</span>
      </div>
      <div class="header__right">
        <!-- 主题切换 -->
        <button 
          class="icon-btn" 
          @click="showThemePicker = !showThemePicker"
          title="切换背景主题"
        >
          🎨
        </button>
        <!-- 鱼数量 -->
        <div class="stat-badge">
          <span class="stat-icon">🐟</span>
          <span class="stat-value">{{ gameStore.fishes.length }}</span>
        </div>
      </div>
    </div>
    
    <!-- 主题选择器 -->
    <Transition name="theme-picker">
      <div v-if="showThemePicker" class="theme-picker glass">
        <div class="theme-picker__title">🎨 选择背景主题</div>
        <div class="theme-picker__grid">
          <div 
            v-for="bg in backgrounds" 
            :key="bg.id"
            class="theme-option"
            :class="{ 'theme-option--active': gameStore.currentBackground === bg.id }"
            @click="selectBackground(bg.id)"
          >
            <img :src="bg.src" :alt="bg.name" />
            <span class="theme-option__name">{{ bg.name }}</span>
            <span v-if="gameStore.currentBackground === bg.id" class="theme-option__check">✓</span>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- 左侧操作按钮组 -->
    <div class="ui-panel__sidebar">
      <!-- 喂食按钮（显示数量） -->
      <button 
        class="sidebar-btn sidebar-btn--feed" 
        @click="$emit('feedAll')"
        :disabled="totalFeed <= 0 || gameStore.fishes.length === 0"
        title="喂食所有鱼"
      >
        <span class="btn-icon">🍞</span>
        <span class="btn-badge">{{ totalFeed }}</span>
      </button>
      
      <!-- 添加鱼苗（鱼缸图标） -->
      <button 
        class="sidebar-btn sidebar-btn--add" 
        @click="$emit('showScan')"
        title="添加鱼苗"
      >
        <span class="btn-icon">🐠</span>
      </button>
      
      <!-- 渔获（鱼图标） -->
      <button 
        class="sidebar-btn sidebar-btn--coupon" 
        @click="$emit('showCoupons')"
        title="渔获"
      >
        <span class="btn-icon">🐟</span>
        <span v-if="gameStore.coupons.length > 0" class="btn-badge btn-badge--gold">{{ gameStore.coupons.length }}</span>
      </button>
      
      <!-- 分享 -->
      <button 
        class="sidebar-btn sidebar-btn--share" 
        @click="$emit('showShare')"
        title="分享获取饲料"
      >
        <span class="btn-icon">👥</span>
      </button>
    </div>
    
    <!-- 成鱼提示（右下角浮动） -->
    <Transition name="hint-fade">
      <div v-if="gameStore.adultFishCount > 0" class="harvest-float glass">
        <span class="pulse-dot"></span>
        {{ gameStore.adultFishCount }} 条成熟鱼可捕捞
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.ui-panel {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 100;
}

/* 顶部状态栏 */
.ui-panel__header {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-radius: 16px;
  pointer-events: auto;
}

.header__title {
  font-size: 18px;
  font-weight: 700;
  /* Ocean Flame 品牌色标准: 深蓝底 + 霓虹渐变 */
  background: linear-gradient(90deg, #00f5ff, #ff00ff, #ff6b00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.header__right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.25);
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.stat-icon {
  font-size: 16px;
}

.stat-value {
  font-weight: 600;
}

/* 左侧操作按钮 */
.ui-panel__sidebar {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: auto;
}

.sidebar-btn {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
}

.sidebar-btn:hover:not(:disabled) {
  transform: translateX(4px) scale(1.05);
}

.sidebar-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.sidebar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 24px;
}

.btn-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  background: #22c55e;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.btn-badge--gold {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.sidebar-btn--feed {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.6), rgba(22, 163, 74, 0.6));
}

.sidebar-btn--add {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.6), rgba(14, 165, 233, 0.6));
}

.sidebar-btn--coupon {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.6), rgba(234, 88, 12, 0.6));
}

.sidebar-btn--share {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.6), rgba(139, 92, 246, 0.6));
}

/* 成鱼提示 */
.harvest-float {
  position: absolute;
  bottom: 24px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 13px;
  color: #fbbf24;
  font-weight: 600;
  pointer-events: auto;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #fbbf24;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.3);
  }
}

/* 主题选择器 */
.theme-picker {
  position: absolute;
  top: 80px;
  right: 16px;
  left: 80px;
  padding: 16px;
  border-radius: 16px;
  pointer-events: auto;
}

.theme-picker__title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  text-align: center;
}

.theme-picker__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.theme-option {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  border: 3px solid transparent;
}

.theme-option img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  display: block;
}

.theme-option__name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px;
  font-size: 11px;
  text-align: center;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
}

.theme-option__check {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  background: #22c55e;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.theme-option--active {
  border-color: #22c55e;
  box-shadow: 0 0 15px rgba(34, 197, 94, 0.5);
}

.theme-option:hover:not(.theme-option--active) {
  border-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.02);
}

/* 动画 */
.theme-picker-enter-active,
.theme-picker-leave-active {
  transition: all 0.3s ease;
}

.theme-picker-enter-from,
.theme-picker-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.hint-fade-enter-active,
.hint-fade-leave-active {
  transition: all 0.3s ease;
}

.hint-fade-enter-from,
.hint-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>

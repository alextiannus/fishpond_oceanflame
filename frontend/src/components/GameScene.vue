<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useGameStore, FISH_STATUS } from '../stores/game'
import FishComponent from './FishComponent.vue'

// 导入背景图片
import pondBg1 from '@/assets/pond-bg-1.jpg'
import pondBg2 from '@/assets/pond-bg-2.jpg'
import pondBg3 from '@/assets/pond-bg-3.jpg'
import pondBg4 from '@/assets/pond-bg-4.jpg'

const gameStore = useGameStore()

// 背景图片列表
const backgrounds = {
  1: pondBg1,
  2: pondBg2,
  3: pondBg3,
  4: pondBg4,
}

// 背景和装饰
const seaweeds = ref([])
const bubbles = ref([])
const sceneRef = ref(null)

// 渔网动画
const showNetAnimation = ref(false)
const netX = ref(0)
const netY = ref(0)

// 初始化装饰
onMounted(() => {
  // 生成水草
  for (let i = 0; i < 8; i++) {
    seaweeds.value.push({
      id: i,
      left: 5 + (i * 12) + Math.random() * 5,
      height: 60 + Math.random() * 80,
      delay: Math.random() * 2,
    })
  }
  
  // 生成气泡
  spawnBubbles()
})

function spawnBubbles() {
  for (let i = 0; i < 15; i++) {
    setTimeout(() => {
      if (bubbles.value.length < 30) {
        bubbles.value.push({
          id: Date.now() + i,
          left: Math.random() * 100,
          size: 4 + Math.random() * 12,
          duration: 4 + Math.random() * 4,
        })
      }
    }, i * 500)
  }
  
  const interval = setInterval(() => {
    if (bubbles.value.length < 30) {
      bubbles.value.push({
        id: Date.now(),
        left: Math.random() * 100,
        size: 4 + Math.random() * 12,
        duration: 4 + Math.random() * 4,
      })
    }
    bubbles.value = bubbles.value.slice(-30)
  }, 800)
  
  onUnmounted(() => clearInterval(interval))
}

// 处理点击撒网
function handleSceneClick(event) {
  if (!sceneRef.value) return
  
  const rect = sceneRef.value.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 100
  const y = ((event.clientY - rect.top) / rect.height) * 100
  
  // 设置渔网位置
  netX.value = x
  netY.value = y
  showNetAnimation.value = true
  
  // 撒网捕鱼
  const caught = gameStore.castNet(x, y)
  
  // 动画结束后隐藏渔网
  setTimeout(() => {
    showNetAnimation.value = false
    if (caught > 0) {
      emit('caught', gameStore.caughtFish)
    }
  }, 1000)
}

// 处理鱼点击
function handleFishClick(fish) {
  if (fish.status === FISH_STATUS.ADULT) {
    emit('harvest', fish)
  } else if (fish.status !== FISH_STATUS.DEAD && fish.status !== FISH_STATUS.CAUGHT) {
    emit('feed', fish)
  }
}

const emit = defineEmits(['feed', 'harvest', 'caught'])

// 背景类
const backgroundClass = computed(() => {
  return gameStore.isNight ? 'scene--night' : 'scene--day'
})

// 背景图片样式
const backgroundStyle = computed(() => {
  const bgImage = backgrounds[gameStore.currentBackground] || backgrounds[1]
  return {
    backgroundImage: `url(${bgImage})`,
  }
})
</script>

<template>
  <div 
    ref="sceneRef"
    class="game-scene" 
    :class="backgroundClass"
    :style="backgroundStyle"
    @click="handleSceneClick"
  >
    <!-- 背景渐变层 -->
    <div class="scene__gradient"></div>
    
    <!-- 光线效果 -->
    <div class="scene__light-rays" v-if="!gameStore.isNight">
      <div class="light-ray" v-for="i in 5" :key="i" :style="{ left: `${i * 20}%` }"></div>
    </div>
    
    <!-- 星星效果（夜间） -->
    <div class="scene__stars" v-if="gameStore.isNight">
      <span class="star" v-for="i in 20" :key="i" :style="{
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 30}%`,
        animationDelay: `${Math.random() * 2}s`
      }"></span>
    </div>
    
    <!-- 水面波纹 -->
    <div class="scene__surface">
      <div class="wave wave--1"></div>
      <div class="wave wave--2"></div>
    </div>
    
    <!-- 漂浮的气泡 -->
    <div class="scene__bubbles">
      <span 
        v-for="bubble in bubbles" 
        :key="bubble.id"
        class="floating-bubble"
        :style="{
          left: `${bubble.left}%`,
          width: `${bubble.size}px`,
          height: `${bubble.size}px`,
          animationDuration: `${bubble.duration}s`
        }"
      ></span>
    </div>
    
    <!-- 水草 -->
    <div class="scene__seaweeds">
      <div 
        v-for="weed in seaweeds" 
        :key="weed.id"
        class="seaweed"
        :style="{
          left: `${weed.left}%`,
          height: `${weed.height}px`,
          animationDelay: `${weed.delay}s`
        }"
      ></div>
    </div>
    
    <!-- 沙地 -->
    <div class="scene__sand"></div>
    
    <!-- 渔网动画 -->
    <div 
      v-if="showNetAnimation || gameStore.isNetActive"
      class="fishing-net"
      :class="{ 'fishing-net--active': showNetAnimation }"
      :style="{
        left: `${netX}%`,
        top: `${netY}%`,
      }"
    >
      <!-- 撕网绳 -->
      <div class="net-rope"></div>
      
      <svg class="net-svg" viewBox="0 0 140 140" width="140" height="140">
        <!-- 圆形渔网外轮廓 -->
        <circle class="net-outer" cx="70" cy="70" r="65" />
        
        <!-- 同心圆纹理 -->
        <circle class="net-ring" cx="70" cy="70" r="50" />
        <circle class="net-ring" cx="70" cy="70" r="35" />
        <circle class="net-ring" cx="70" cy="70" r="20" />
        
        <!-- 放射状网统 -->
        <line class="net-line" x1="70" y1="5" x2="70" y2="135" />
        <line class="net-line" x1="5" y1="70" x2="135" y2="70" />
        <line class="net-line" x1="20" y1="20" x2="120" y2="120" />
        <line class="net-line" x1="120" y1="20" x2="20" y2="120" />
        <line class="net-line" x1="70" y1="5" x2="20" y2="70" />
        <line class="net-line" x1="70" y1="5" x2="120" y2="70" />
        <line class="net-line" x1="70" y1="135" x2="20" y2="70" />
        <line class="net-line" x1="70" y1="135" x2="120" y2="70" />
        
        <!-- 中心点 -->
        <circle class="net-center" cx="70" cy="70" r="8" />
      </svg>
      
      <!-- 水花效果 -->
      <div class="splash-container">
        <div class="splash splash-1"></div>
        <div class="splash splash-2"></div>
        <div class="splash splash-3"></div>
        <div class="splash splash-4"></div>
      </div>
      
      <!-- 波纹 -->
      <div class="net-ripple"></div>
      <div class="net-ripple net-ripple--2"></div>
      <div class="net-ripple net-ripple--3"></div>
    </div>
    
    <!-- 鱼食颗粒 -->
    <div class="scene__food-pellets">
      <div 
        v-for="pellet in gameStore.foodPellets"
        :key="pellet.id"
        class="food-pellet"
        :class="{ 'food-pellet--eaten': pellet.eaten }"
        :style="{
          left: `${pellet.x}%`,
          '--target-y': `${pellet.targetY}%`,
        }"
      >
        <span class="pellet-icon">🟤</span>
      </div>
    </div>
    
    <!-- 鱼群 -->
    <div class="scene__fishes">
      <FishComponent
        v-for="fish in gameStore.fishes"
        :key="fish.id"
        :fish="fish"
        @click="handleFishClick"
      />
    </div>
    
    <!-- 点击提示 -->
    <div class="scene__click-hint">
      点击水面撒网捕鱼 🎣
    </div>
    
    <!-- 空状态提示 -->
    <div v-if="gameStore.fishes.length === 0" class="scene__empty">
      <span>🎣</span>
      <p>鱼塘空空如也</p>
      <p>扫描二维码添加鱼苗吧！</p>
    </div>
  </div>
</template>

<style scoped>
.game-scene {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #0369a1;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: background-image 0.5s ease;
  cursor: crosshair;
}

.scene--night {
  background: linear-gradient(180deg, 
    #1e3a5f 0%, 
    #0c4a6e 30%, 
    #083344 60%, 
    #042f2e 100%
  );
}

.scene__gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

/* 光线效果 */
.scene__light-rays {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.light-ray {
  position: absolute;
  top: -50px;
  width: 80px;
  height: 300px;
  background: linear-gradient(180deg, 
    rgba(255, 255, 255, 0.15) 0%, 
    transparent 100%
  );
  transform: rotate(15deg);
  animation: light-sway 8s ease-in-out infinite;
}

.light-ray:nth-child(2) { animation-delay: -2s; }
.light-ray:nth-child(3) { animation-delay: -4s; }
.light-ray:nth-child(4) { animation-delay: -6s; }

/* 星星 */
.scene__stars {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.star {
  position: absolute;
  width: 3px;
  height: 3px;
  background: white;
  border-radius: 50%;
  animation: twinkle 2s ease-in-out infinite;
}

/* 水面 */
.scene__surface {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 40px;
  overflow: hidden;
  pointer-events: none;
}

.wave {
  position: absolute;
  top: 0;
  left: -100%;
  width: 300%;
  height: 20px;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 10px,
    rgba(255, 255, 255, 0.1) 10px,
    rgba(255, 255, 255, 0.1) 20px
  );
  animation: wave-flow 8s linear infinite;
}

.wave--2 {
  top: 15px;
  animation-duration: 12s;
  animation-direction: reverse;
  opacity: 0.5;
}

/* 气泡 */
.scene__bubbles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.floating-bubble {
  position: absolute;
  bottom: 100px;
  background: radial-gradient(circle at 30% 30%, 
    rgba(255, 255, 255, 0.8), 
    rgba(255, 255, 255, 0.2)
  );
  border-radius: 50%;
  animation: bubble-float linear infinite;
}

/* 水草 */
.scene__seaweeds {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 150px;
  pointer-events: none;
}

.seaweed {
  position: absolute;
  bottom: 30px;
  width: 12px;
  background: linear-gradient(0deg, 
    #22c55e 0%, 
    #15803d 50%, 
    #166534 100%
  );
  border-radius: 50% 50% 0 0;
  transform-origin: bottom center;
  animation: seaweed-sway 3s ease-in-out infinite;
}

/* 沙地 */
.scene__sand {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(0deg, 
    #c2a878 0%, 
    #d4b896 30%, 
    transparent 100%
  );
  pointer-events: none;
}

.scene--night .scene__sand {
  background: linear-gradient(0deg, 
    #5c5040 0%, 
    #7a6b52 30%, 
    transparent 100%
  );
}

/* 渔网动画 */
.fishing-net {
  position: absolute;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 100;
}

.net-rope {
  position: absolute;
  top: -80px;
  left: 50%;
  width: 3px;
  height: 80px;
  background: linear-gradient(180deg, #8b7355, #a08060);
  transform-origin: bottom center;
  animation: rope-swing 0.5s ease-out;
}

.net-svg {
  animation: net-cast 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.fishing-net--active .net-svg {
  animation: net-cast 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards, 
             net-shake 0.4s ease-in-out 0.6s;
}

.net-outer {
  fill: rgba(135, 206, 235, 0.15);
  stroke: rgba(255, 255, 255, 0.9);
  stroke-width: 3;
}

.net-ring {
  fill: none;
  stroke: rgba(255, 255, 255, 0.5);
  stroke-width: 1.5;
  stroke-dasharray: 8 4;
}

.net-line {
  stroke: rgba(255, 255, 255, 0.4);
  stroke-width: 1;
}

.net-center {
  fill: rgba(255, 255, 255, 0.6);
}

/* 水花效果 */
.splash-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
  height: 160px;
}

.splash {
  position: absolute;
  width: 12px;
  height: 30px;
  background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(135,206,235,0.3));
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  animation: splash-up 0.8s ease-out forwards;
}

.splash-1 { left: 20%; top: 20%; transform: rotate(-45deg); animation-delay: 0.1s; }
.splash-2 { right: 20%; top: 20%; transform: rotate(45deg); animation-delay: 0.15s; }
.splash-3 { left: 15%; bottom: 30%; transform: rotate(-30deg); animation-delay: 0.2s; }
.splash-4 { right: 15%; bottom: 30%; transform: rotate(30deg); animation-delay: 0.25s; }

.net-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 60px;
  height: 60px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: net-ripple-expand 1s ease-out forwards;
}

.net-ripple--2 {
  animation-delay: 0.15s;
}

.net-ripple--3 {
  animation-delay: 0.3s;
}

/* 点击提示 */
.scene__click-hint {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  pointer-events: none;
  animation: hint-pulse 2s ease-in-out infinite;
}

/* 鱼群容器 */
.scene__fishes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.scene__fishes > * {
  pointer-events: auto;
}

/* 空状态 */
.scene__empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  pointer-events: none;
}

.scene__empty span {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
  animation: float 2s ease-in-out infinite;
}

.scene__empty p {
  margin: 8px 0;
}

/* 动画 */
@keyframes light-sway {
  0%, 100% { transform: rotate(15deg) translateX(0); }
  50% { transform: rotate(15deg) translateX(30px); }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

@keyframes wave-flow {
  0% { transform: translateX(0); }
  100% { transform: translateX(33.33%); }
}

@keyframes bubble-float {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0.8;
  }
  100% {
    transform: translateY(-500px) translateX(20px);
    opacity: 0;
  }
}

@keyframes seaweed-sway {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes net-drop {
  0% {
    transform: scale(0.3) translateY(-100px);
    opacity: 0;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

@keyframes net-shake {
  0%, 100% { transform: rotate(0); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

@keyframes net-ripple-expand {
  0% {
    width: 40px;
    height: 40px;
    opacity: 1;
  }
  100% {
    width: 200px;
    height: 200px;
    opacity: 0;
  }
}

@keyframes hint-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes rope-swing {
  0% {
    transform: rotate(-20deg);
    opacity: 0;
  }
  50% {
    transform: rotate(10deg);
  }
  100% {
    transform: rotate(0);
    opacity: 1;
  }
}

@keyframes net-cast {
  0% {
    transform: scale(0.2) translateY(-80px);
    opacity: 0;
  }
  60% {
    transform: scale(1.1) translateY(10px);
    opacity: 1;
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

@keyframes splash-up {
  0% {
    transform: translateY(0) scale(0.5);
    opacity: 0;
  }
  30% {
    opacity: 1;
  }
  100% {
    transform: translateY(-40px) scale(0.3);
    opacity: 0;
  }
}

/* 鱼食颗粒 */
.scene__food-pellets {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 50;
}

.food-pellet {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  animation: pellet-fall 1.5s ease-out forwards;
}

.food-pellet--eaten {
  animation: pellet-fall 1.5s ease-out forwards, pellet-eaten 0.3s ease-out 1.5s forwards;
}

.pellet-icon {
  font-size: 16px;
  display: block;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

@keyframes pellet-fall {
  0% {
    top: 5%;
    opacity: 0;
    transform: translateX(-50%) scale(0.5);
  }
  20% {
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
  100% {
    top: var(--target-y, 40%);
    opacity: 1;
    transform: translateX(-50%) scale(1);
  }
}

@keyframes pellet-eaten {
  0% {
    transform: translateX(-50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateX(-50%) scale(0);
    opacity: 0;
  }
}
</style>

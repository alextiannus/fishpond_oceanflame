<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { FISH_TYPES, FISH_STATUS } from '../stores/game'

// 使用 import.meta.glob 动态导入各文件夹中的所有GIF
const newfishGifs = import.meta.glob('@/assets/newfish/*.gif', { eager: true, import: 'default' })
const hailuyuGifs = import.meta.glob('@/assets/hailuyu/*.gif', { eager: true, import: 'default' })
const qingjiangyuGifs = import.meta.glob('@/assets/qingjiangyu/*.gif', { eager: true, import: 'default' })
const lingboyuGifs = import.meta.glob('@/assets/lingboyu/*.gif', { eager: true, import: 'default' })

// 将导入的模块转换为数组
const fishGifLibrary = {
  qingjiang: Object.values(qingjiangyuGifs),
  lingbo: Object.values(lingboyuGifs),
  hailu: Object.values(hailuyuGifs),
  newfish: Object.values(newfishGifs),
}

// 为 basha 和 jinmu 使用备用GIF库
fishGifLibrary.basha = fishGifLibrary.qingjiang
fishGifLibrary.jinmu = fishGifLibrary.lingbo

const props = defineProps({
  fish: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'feed', 'harvest'])

// 获取鱼类型信息
const fishType = computed(() => FISH_TYPES[props.fish.type.toUpperCase()])

// 判断是否是幼鱼（喂食次数少于5次时显示小鱼）
const isBaby = computed(() => (props.fish.foodEaten || 0) < 5)

// 根据鱼的ID生成一个固定的随机索引（确保同一条鱼始终显示相同的GIF）
function getRandomGifIndex(fishId, arrayLength) {
  // 使用鱼的ID生成一个稳定的哈希值
  let hash = 0
  for (let i = 0; i < fishId.length; i++) {
    hash = ((hash << 5) - hash) + fishId.charCodeAt(i)
    hash = hash & hash // 转换为32位整数
  }
  return Math.abs(hash) % arrayLength
}

// 根据状态和类型获取鱼GIF
const fishImage = computed(() => {
  if (isBaby.value) {
    // 幼鱼从 newfish 文件夹随机选择
    const gifs = fishGifLibrary.newfish
    if (gifs.length > 0) {
      const index = getRandomGifIndex(props.fish.id, gifs.length)
      return gifs[index]
    }
  }
  
  // 成鱼从对应类型的文件夹随机选择
  const gifs = fishGifLibrary[props.fish.type] || fishGifLibrary.qingjiang
  if (gifs.length > 0) {
    const index = getRandomGifIndex(props.fish.id, gifs.length)
    return gifs[index]
  }
  
  // 兜底返回第一个
  return fishGifLibrary.qingjiang[0]
})

// 特殊状态显示的emoji
const statusEmoji = computed(() => {
  if (props.fish.status === FISH_STATUS.DEAD) return '💀'
  if (props.fish.status === FISH_STATUS.SICK) return '🤢'
  if (props.fish.status === FISH_STATUS.HUNGRY) return '😰'
  if (props.fish.status === FISH_STATUS.CAUGHT) return '🎣'
  return null
})

// 根据重量计算鱼的大小
const fishScale = computed(() => {
  const weight = props.fish.weight || 50
  // 50g = 0.6x, 900g = 1.5x
  const scale = 0.6 + (weight / 900) * 0.9
  return Math.min(scale, 1.6)
})

const isClickable = computed(() => {
  return props.fish.status !== FISH_STATUS.DEAD && props.fish.status !== FISH_STATUS.CAUGHT
})

// 游动样式 - 使用 transform 让鱼头朝向游动方向
const swimStyle = computed(() => {
  const angle = props.fish.angle || 0
  const flipX = props.fish.direction > 0 ? -1 : 1
  return {
    left: `${props.fish.x}%`,
    top: `${props.fish.y}%`,
    transform: `scaleX(${flipX}) rotate(${angle}deg) scale(${fishScale.value})`,
    transition: 'left 0.1s linear, top 0.1s linear',
  }
})

// 说话气泡样式 - 反转scaleX以确保文字始终正面显示给用户
const speechStyle = computed(() => {
  const flipX = props.fish.direction > 0 ? -1 : 1
  const angle = props.fish.angle || 0
  return {
    transform: `scaleX(${flipX}) rotate(${-angle}deg) translateX(-50%)`,
  }
})

// 鱼说话功能
const showSpeech = ref(false)
const speechText = ref('')
let speechTimer = null

// 随机对话列表
const speeches = {
  normal: [
    '今天天气真好~',
    '水里好舒服！',
    '游来游去真开心',
    '饿了饿了...',
    '主人好！',
    '快来喂我~',
    '我想长大！',
    '哇，好漂亮的水~',
    '嘿嘿嘿~',
    '你在看我吗？',
  ],
  hungry: [
    '好饿啊！！',
    '快给我吃的！',
    '再不吃要饿瘪了...',
    '有没有好吃的？',
  ],
  adult: [
    '我长大啦！',
    '可以捕捞我了~',
    '我已经成熟啦！',
    '快来抓我呀~',
  ],
  growing: [
    '我在努力长大！',
    '再吃一点就好了',
    '快喂我嘛~',
    '成长中...',
  ]
}

function getRandomSpeech() {
  let pool = speeches.normal
  if (props.fish.status === FISH_STATUS.HUNGRY) {
    pool = speeches.hungry
  } else if (props.fish.status === FISH_STATUS.ADULT) {
    pool = [...speeches.adult, ...speeches.normal]
  } else if (props.fish.status === FISH_STATUS.GROWING) {
    pool = [...speeches.growing, ...speeches.normal]
  }
  return pool[Math.floor(Math.random() * pool.length)]
}

function triggerSpeech() {
  if (props.fish.status === FISH_STATUS.DEAD || props.fish.status === FISH_STATUS.CAUGHT) return
  if (showSpeech.value) return
  
  speechText.value = getRandomSpeech()
  showSpeech.value = true
  
  setTimeout(() => {
    showSpeech.value = false
  }, 2500)
}

onMounted(() => {
  // 随机时间后开始说话
  const startDelay = 2000 + Math.random() * 5000
  setTimeout(() => {
    triggerSpeech()
    // 之后每隔一段时间随机说话
    speechTimer = setInterval(() => {
      if (Math.random() < 0.3) { // 30% 概率说话
        triggerSpeech()
      }
    }, 5000 + Math.random() * 5000)
  }, startDelay)
})

onUnmounted(() => {
  if (speechTimer) clearInterval(speechTimer)
})

function handleClick() {
  if (!isClickable.value) return
  triggerSpeech()
  emit('click', props.fish)
}
</script>

<template>
  <div
    class="fish"
    :class="[
      `fish--${fish.status}`,
      { 'fish--clickable': isClickable }
    ]"
    :style="swimStyle"
    @click="handleClick"
  >
    <!-- 鱼本体 -->
    <div class="fish__body">
      <!-- 所有鱼都使用GIF（支持透明背景） -->
      <img 
        :src="fishImage" 
        :alt="fish.name" 
        class="fish__image"
        :class="{ 'fish__image--wiggle': fish.status !== FISH_STATUS.DEAD }"
      />
      <!-- 特殊状态emoji覆盖 -->
      <span v-if="statusEmoji" class="fish__status-emoji">{{ statusEmoji }}</span>
    </div>
    
    <!-- 说话气泡 -->
    <Transition name="speech">
      <div v-if="showSpeech" class="fish__speech" :style="speechStyle">
        {{ speechText }}
      </div>
    </Transition>
    
    <!-- 成鱼标记 -->
    <div v-if="fish.status === FISH_STATUS.ADULT" class="fish__adult-mark">✨</div>
    
    <!-- 气泡效果 -->
    <div class="fish__bubbles" v-if="fish.status !== FISH_STATUS.DEAD && fish.status !== FISH_STATUS.CAUGHT">
      <span class="bubble"></span>
      <span class="bubble"></span>
      <span class="bubble"></span>
    </div>
  </div>
</template>

<style scoped>
.fish {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: default;
  z-index: 10;
  transform-origin: center center;
  will-change: left, top, transform;
}

.fish--clickable {
  cursor: pointer;
}

.fish--clickable:hover {
  filter: brightness(1.2);
}

.fish__body {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.fish__video {
  width: 80px;
  height: auto;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
  transition: transform 0.2s;
  background: transparent;
}

.fish__video--wiggle {
  animation: fish-wiggle 2s ease-in-out infinite;
}

.fish__image {
  width: 80px;
  height: auto;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
  transition: transform 0.2s;
}

.fish__image--wiggle {
  animation: fish-wiggle 2s ease-in-out infinite;
}

.fish__status-emoji {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}

.fish--hungry .fish__video {
  animation: shake 0.5s ease-in-out infinite;
}

.fish--sick .fish__video {
  filter: saturate(0.3) brightness(0.8) drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
}

/* 死亡的鱼直接隐藏，不做动画 */
.fish--dead {
  display: none;
}

.fish--caught .fish__video {
  animation: caught-bounce 0.5s ease-in-out infinite;
}

.fish--adult .fish__video {
  filter: drop-shadow(0 0 20px rgba(251, 191, 36, 0.6));
}

/* 成鱼标记 */
.fish__adult-mark {
  position: absolute;
  top: -15px;
  right: -10px;
  font-size: 20px;
  animation: sparkle 1s ease-in-out infinite;
}

/* 说话气泡 */
.fish__speech {
  position: absolute;
  bottom: 100%;
  left: 50%;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  margin-bottom: 8px;
}

.fish__speech::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid rgba(255, 255, 255, 0.95);
}

/* 气泡效果 */
.fish__bubbles {
  position: absolute;
  top: -20px;
  left: 50%;
}

.bubble {
  position: absolute;
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: bubble-rise 2s ease-out infinite;
}

.bubble:nth-child(1) {
  left: -10px;
  animation-delay: 0s;
}

.bubble:nth-child(2) {
  left: 0;
  animation-delay: 0.5s;
}

.bubble:nth-child(3) {
  left: 10px;
  animation-delay: 1s;
}

@keyframes fish-wiggle {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(3deg); }
  75% { transform: rotate(-3deg); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-3px); }
  75% { transform: translateX(3px); }
}

@keyframes caught-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes bubble-rise {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0.8;
  }
  100% {
    transform: translateY(-30px) scale(0.5);
    opacity: 0;
  }
}

@keyframes sparkle {
  0%, 100% { 
    opacity: 1;
    transform: scale(1);
  }
  50% { 
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* 说话动画 */
.speech-enter-active {
  animation: speech-in 0.3s ease-out;
}

.speech-leave-active {
  animation: speech-out 0.3s ease-in;
}

@keyframes speech-in {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(10px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

@keyframes speech-out {
  0% {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px) scale(0.8);
  }
}
</style>

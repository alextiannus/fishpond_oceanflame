<script setup>
import { computed } from 'vue'
import { FISH_TYPES } from '../stores/game'

// 鱼类描述和烹饪建议
const fishDescriptions = {
  qingjiang: {
    description: '清江鱼产自长江清江流域，肉质鲜嫩细腻，食用无骨刺，口感滑嫩，是烤鱼的上佳之选。',
    cooking: ['麻辣烤鱼', '青花椒烤鱼', '酱香烤鱼', '蒜香烤鱼', '豆豉烤鱼']
  },
  lingbo: {
    description: '凌波鱼身形优美，肉质紧实弹牙，富含蛋白质，鲜香味美，适合多种烹饪方式。',
    cooking: ['香辣烤鱼', '泡椒烤鱼', '酸菜烤鱼', '番茄烤鱼', '黑椒烤鱼']
  },
  basha: {
    description: '巴沙鱼肉质洁白无腥，口感嫩滑，无骨刺，易于烹饪，老少皆宜。',
    cooking: ['蒜香烤鱼', '柠檬烤鱼', '孜然烤鱼', '咖喱烤鱼', '葱香烤鱼']
  },
  jinmu: {
    description: '金目鲈鱼肉质肥美，鲜甜可口，富含DHA和优质蛋白，营养价值极高。',
    cooking: ['豉汁烤鱼', '椒盐烤鱼', '蜜汁烤鱼', '五香烤鱼', '葱姜烤鱼']
  },
  hailu: {
    description: '海鲈鱼为名贵海产，肉厚刺少，味道鲜美，富含多种氨基酸，是高档宴席首选。',
    cooking: ['清蒸烤鱼', '红烧烤鱼', '糖醋烤鱼', '剁椒烤鱼', '蒜蓉烤鱼']
  }
}

// 导入鱼GIF动画
import fishBabyGif from '@/assets/newfish.gif'
import fishQingjiangGif from '@/assets/qingjiangyu.gif'
import fishLingboGif from '@/assets/lingboyu.gif'
import fishHailuGif from '@/assets/hailuyu.gif'

const props = defineProps({
  fishInfo: {
    type: Object,
    required: true
  },
  coupon: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'share', 'navigate'])

// 鱼GIF映射
const fishGifs = {
  qingjiang: fishQingjiangGif,
  lingbo: fishLingboGif,
  basha: fishQingjiangGif,
  jinmu: fishLingboGif,
  hailu: fishHailuGif,
}

const fishGif = computed(() => {
  return fishGifs[props.fishInfo?.type] || fishQingjiangGif
})

const fishType = computed(() => {
  return FISH_TYPES[props.fishInfo?.type?.toUpperCase()]
})

// 门店地址
const storeAddress = "47 Jln Pemimpin, #01-02, Singapore 577200"
const storeMapUrl = "https://maps.google.com/?q=47+Jln+Pemimpin+Singapore+577200"

// 获取鱼类描述信息
const fishDescription = computed(() => {
  return fishDescriptions[props.fishInfo?.type] || fishDescriptions.qingjiang
})

// 分享功能
function handleShare(platform) {
  emit('share', platform)
}

// 导航到门店
function handleNavigate() {
  window.open(storeMapUrl, '_blank')
  emit('navigate')
}

// 保存到相册（模拟）
function handleSave() {
  emit('share', 'save')
}
</script>

<template>
  <div class="processing-voucher">
    <!-- 头部 -->
    <div class="voucher__header">
      <h2>🐟 渔获评证</h2>
      <button class="voucher__close" @click="$emit('close')">✕</button>
    </div>
    
    <div class="voucher__content">
      <!-- 鱼展示区 -->
      <div class="voucher__fish">
        <img :src="fishGif" :alt="fishInfo?.name" class="fish-gif" />
        <div class="fish-details">
          <h3>{{ fishInfo?.name }}</h3>
          <p class="fish-weight">{{ fishInfo?.weight?.toFixed(0) }}g</p>
        </div>
      </div>
      
      <!-- 二维码区 -->
      <div class="voucher__qr">
        <div class="qr-code">
          <span class="qr-icon">📱</span>
          <div class="qr-pattern">
            <div class="qr-row" v-for="i in 5" :key="i">
              <span v-for="j in 5" :key="j" :class="['qr-dot', { 'qr-dot--dark': (i + j) % 2 === 0 }]"></span>
            </div>
          </div>
        </div>
        <p class="qr-code-text">{{ coupon?.code }}</p>
        <p class="qr-hint">到店出示此二维码</p>
      </div>
      
      <!-- 鱼类描述 -->
      <div class="voucher__description">
        <h4>🐟 鱼种介绍</h4>
        <p class="description-text">{{ fishDescription.description }}</p>
        <h5>🔥 推荐烹饪方式</h5>
        <div class="cooking-tags">
          <span v-for="(style, index) in fishDescription.cooking" :key="index" class="cooking-tag">
            {{ style }}
          </span>
        </div>
      </div>
      
      <!-- 代加工详情 -->
      <div class="voucher__fees">
        <h4>🔥 代加工详情</h4>
        <div class="fee-list">
          <div class="fee-item">
            <span>服务费</span>
            <span class="fee-price">$12</span>
          </div>
          <div class="fee-item">
            <span>GST</span>
            <span class="fee-price">9%</span>
          </div>
        </div>
        <p class="fee-note">* 配料费用另计，最终价格以门店实际结算为准</p>
      </div>
      
      <!-- 门店信息 -->
      <div class="voucher__store">
        <div class="store-header">
          <span class="store-icon">🔥</span>
          <div class="store-info">
            <h4>Ocean Flame 门店</h4>
            <p class="store-address">{{ storeAddress }}</p>
          </div>
        </div>
        <button class="navigate-btn" @click="handleNavigate">
          📍 导航到门店
        </button>
      </div>
      
      <!-- 有效期 -->
      <div class="voucher__expires">
        有效期至: {{ new Date(coupon?.expiresAt).toLocaleDateString() }}
      </div>
      
      <!-- 操作按钮 -->
      <div class="voucher__actions">
        <button class="action-btn action-btn--share" @click="handleShare('wechat')">
          💬 分享给好友
        </button>
        <button class="action-btn action-btn--save" @click="handleSave">
          💾 保存凭证
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.processing-voucher {
  width: 100%;
  max-width: 380px;
  max-height: 90vh;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(180deg, 
    rgba(30, 41, 59, 0.98) 0%, 
    rgba(15, 23, 42, 0.98) 100%
  );
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: modal-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.voucher__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(234, 88, 12, 0.1));
}

.voucher__header h2 {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.voucher__close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.voucher__close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.voucher__content {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 60px);
}

/* 鱼展示 */
.voucher__fish {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.fish-gif {
  width: 100px;
  height: auto;
  margin-bottom: 12px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
  animation: fish-float 2s ease-in-out infinite;
}

@keyframes fish-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.fish-details h3 {
  font-size: 20px;
  color: white;
  margin-bottom: 4px;
}

.fish-weight {
  font-size: 28px;
  font-weight: 700;
  color: #fbbf24;
}

/* 二维码 */
.voucher__qr {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.qr-code {
  width: 120px;
  height: 120px;
  margin: 0 auto 12px;
  background: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.qr-icon {
  font-size: 24px;
  position: absolute;
  top: 8px;
  z-index: 2;
}

.qr-pattern {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
}

.qr-row {
  display: flex;
  gap: 4px;
}

.qr-dot {
  width: 12px;
  height: 12px;
  background: #e5e7eb;
  border-radius: 2px;
}

.qr-dot--dark {
  background: #1f2937;
}

.qr-code-text {
  font-family: monospace;
  font-size: 14px;
  color: #fbbf24;
  margin-bottom: 4px;
}

.qr-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* 鱼类描述 */
.voucher__description {
  padding: 16px;
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.1), rgba(6, 182, 212, 0.05));
  border-radius: 12px;
  margin: 16px 0;
  border: 1px solid rgba(34, 211, 238, 0.2);
}

.voucher__description h4 {
  font-size: 14px;
  color: white;
  margin-bottom: 8px;
}

.voucher__description h5 {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin: 12px 0 8px 0;
}

.description-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
}

.cooking-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cooking-tag {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.3), rgba(234, 88, 12, 0.2));
  border-radius: 16px;
  font-size: 12px;
  color: #fbbf24;
  border: 1px solid rgba(251, 146, 60, 0.3);
}

/* 代金券价值 */
.voucher__value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.1));
  border-radius: 12px;
  margin: 16px 0;
}

.value-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.value-amount {
  font-size: 28px;
  font-weight: 700;
  color: #fbbf24;
}

/* 费用明细 */
.voucher__fees {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 16px;
}

.voucher__fees h4 {
  font-size: 14px;
  color: white;
  margin-bottom: 12px;
}

.fee-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fee-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: white;
}

.fee-item--note {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.fee-price {
  font-weight: 600;
}

.fee-free {
  color: #22c55e;
}

.fee-note {
  margin-top: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* 门店信息 */
.voucher__store {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 16px;
}

.store-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.store-icon {
  font-size: 32px;
}

.store-info h4 {
  font-size: 16px;
  color: white;
  margin-bottom: 4px;
}

.store-address {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.navigate-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.navigate-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

/* 有效期 */
.voucher__expires {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 16px;
}

/* 操作按钮 */
.voucher__actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn--share {
  background: #07c160;
  color: white;
}

.action-btn--save {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}
</style>

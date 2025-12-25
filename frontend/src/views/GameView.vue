<script setup>
import { ref, onMounted } from 'vue'
import { useGameStore, FISH_TYPES, FISH_STATUS } from '../stores/game'
import GameScene from '../components/GameScene.vue'
import UIPanel from '../components/UIPanel.vue'
import ProcessingVoucher from '../components/ProcessingVoucher.vue'

// 导入鱼GIF动画
import fishBabyGif from '@/assets/newfish.gif'
import fishQingjiangGif from '@/assets/qingjiangyu.gif'
import fishLingboGif from '@/assets/lingboyu.gif'
import fishHailuGif from '@/assets/hailuyu.gif'

const gameStore = useGameStore()

// 鱼GIF映射
const fishGifs = {
  qingjiang: fishQingjiangGif,
  lingbo: fishLingboGif,
  basha: fishQingjiangGif,
  jinmu: fishLingboGif,
  hailu: fishHailuGif,
}

// 弹窗状态
const showQRScanModal = ref(false)
const showCouponModal = ref(false)
const showCaughtModal = ref(false)
const showShareModal = ref(false)
const showProcessingVoucher = ref(false)
const selectedFish = ref(null)
const processingFishInfo = ref(null)
const processingCoupon = ref(null)
const toast = ref({ show: false, message: '', type: 'info' })

// 初始化游戏
onMounted(() => {
  gameStore.initGame()
})

// 显示 Toast
function showToast(message, type = 'info') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 2500)
}

// 模拟扫码添加鱼苗
function handleQRScan(typeId) {
  const fish = gameStore.addFish(typeId, true)
  if (fish) {
    showToast(`🎉 扫码成功！获得一条 ${fish.name} 鱼苗！`, 'success')
    showQRScanModal.value = false
  }
}

// 喂食所有鱼
function handleFeedAll() {
  const result = gameStore.feedAllFish()
  if (result.success) {
    showToast(`🍞 ${result.message}`, 'success')
  } else {
    showToast(result.message, 'warning')
  }
}

// 处理场景中鱼的点击（喂食）
function handleFishFeed(fish) {
  const result = gameStore.feedFish(fish.id)
  showToast(result.message, result.success ? 'success' : 'warning')
}

// 处理成鱼点击（开始捕获流程）
function handleFishHarvest(fish) {
  selectedFish.value = fish
  // 不再直接收获，而是通过撒网捕获
}

// 处理捕获到鱼
function handleFishCaught(fish) {
  if (fish) {
    selectedFish.value = fish
    showCaughtModal.value = true
  }
}

// 放生鱼
function handleRelease() {
  const result = gameStore.releaseFish()
  if (result.success) {
    showToast('🐟 鱼已放回鱼塘', 'info')
    showCaughtModal.value = false
    selectedFish.value = null
  }
}

// 送去餐厅加工
function handleSendToRestaurant() {
  // 保存鱼的信息用于展示
  const fish = gameStore.caughtFish
  const fishType = FISH_TYPES[fish?.type?.toUpperCase()]
  
  processingFishInfo.value = {
    name: fish?.name,
    weight: fish?.weight,
    value: fishType?.value,
    type: fish?.type,
  }
  
  const result = gameStore.sendToRestaurant()
  if (result.success) {
    processingCoupon.value = result.coupon
    showCaughtModal.value = false
    selectedFish.value = null
    // 显示代加工凭证页面
    showProcessingVoucher.value = true
  }
}

// 分享获取饲料
function handleShare() {
  const result = gameStore.shareToFriend()
  showToast(result.message, 'success')
  showShareModal.value = false
}

// 鱼类型列表
const fishTypes = Object.values(FISH_TYPES)
</script>

<template>
  <div class="game-view container">
    <!-- 游戏场景 -->
    <GameScene 
      @feed="handleFishFeed"
      @harvest="handleFishHarvest"
      @caught="handleFishCaught"
    />
    
    <!-- UI 面板 -->
    <UIPanel 
      @feedAll="handleFeedAll"
      @showScan="showQRScanModal = true"
      @showCoupons="showCouponModal = true"
      @showShare="showShareModal = true"
    />
    
    <!-- 扫码添加鱼苗弹窗 -->
    <Teleport to="body">
      <div v-if="showQRScanModal" class="modal-overlay" @click.self="showQRScanModal = false">
        <div class="modal glass">
          <div class="modal__header">
            <h2>📱 扫码添加鱼苗</h2>
            <button class="modal__close" @click="showQRScanModal = false">✕</button>
          </div>
          <div class="modal__content">
            <!-- 模拟扫码界面 -->
            <div class="qr-scanner">
              <div class="scanner-frame">
                <div class="scanner-line"></div>
                <span class="scanner-icon">📷</span>
              </div>
              <p class="scanner-hint">将二维码对准扫描框</p>
            </div>
            
            <!-- 演示：直接选择鱼苗 -->
            <div class="fish-demo-list">
              <p class="demo-hint">🎮 演示模式：点击领取鱼苗</p>
              <div class="fish-grid">
                <div 
                  v-for="fishType in fishTypes" 
                  :key="fishType.id"
                  class="fish-card"
                  @click="handleQRScan(fishType.id)"
                >
                  <span class="fish-card__emoji">{{ fishType.emoji }}</span>
                  <span class="fish-card__name">{{ fishType.name }}</span>
                  <span class="fish-card__info">目标 {{ fishType.targetWeight }}g</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- 优惠券/烤鱼券弹窗 -->
    <Teleport to="body">
      <div v-if="showCouponModal" class="modal-overlay" @click.self="showCouponModal = false">
        <div class="modal glass">
          <div class="modal__header">
            <h2>🍖 我的烤鱼券</h2>
            <button class="modal__close" @click="showCouponModal = false">✕</button>
          </div>
          <div class="modal__content">
            <div v-if="gameStore.coupons.length === 0" class="empty-state">
              <span>📭</span>
              <p>暂无烤鱼券</p>
              <p>捕获成熟的鱼送去加工即可获得！</p>
            </div>
            <div v-else class="coupon-list">
              <div 
                v-for="coupon in gameStore.coupons" 
                :key="coupon.id"
                class="coupon-card"
                :class="{ 'coupon-card--used': coupon.used }"
              >
                <div class="coupon-card__badge">🍖</div>
                <div class="coupon-card__left">
                  <span class="coupon-value">¥{{ coupon.value }}</span>
                  <span class="coupon-name">{{ coupon.fishName }} 烤鱼券</span>
                  <span class="coupon-weight">{{ coupon.fishWeight?.toFixed(0) }}g</span>
                </div>
                <div class="coupon-card__right">
                  <div class="coupon-qr">
                    <span>📱</span>
                    <small>{{ coupon.code }}</small>
                  </div>
                  <div class="coupon-expires">
                    {{ new Date(coupon.expiresAt).toLocaleDateString() }} 到期
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- 捕获鱼弹窗 -->
    <Teleport to="body">
      <div v-if="showCaughtModal && gameStore.caughtFish" class="modal-overlay">
        <div class="modal modal--caught glass">
          <div class="modal__header">
            <h2>🎣 捕获成功!</h2>
          </div>
          <div class="modal__content text-center">
            <div class="caught-fish-preview">
              <img 
                :src="fishGifs[gameStore.caughtFish?.type] || fishQingjiangGif" 
                :alt="gameStore.caughtFish?.name"
                class="caught-fish-image"
              />
              <div class="caught-fish-info">
                <h3>{{ gameStore.caughtFish?.name }}</h3>
                <p class="caught-fish-weight">{{ gameStore.caughtFish?.weight?.toFixed(0) }}g</p>
                <p v-if="gameStore.caughtFish?.status === FISH_STATUS.ADULT" class="caught-fish-status">✨ 已成熟，可加工</p>
                <p v-else class="caught-fish-status">🌱 尚未成熟</p>
              </div>
            </div>
            
            <div class="caught-actions">
              <button class="btn btn-secondary" @click="handleRelease">
                🐟 放回鱼塘
              </button>
              <button 
                class="btn btn-gold" 
                @click="handleSendToRestaurant"
                :disabled="gameStore.caughtFish?.weight < 600"
              >
                🍖 送去加工烤鱼
              </button>
            </div>
            
            <p v-if="gameStore.caughtFish?.weight < 600" class="caught-hint">
              提示：鱼需要重量达到600g以上才能送去加工
            </p>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- 分享获取饲料弹窗 -->
    <Teleport to="body">
      <div v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
        <div class="modal modal--share glass">
          <div class="modal__header">
            <h2>🎁 分享获取饲料</h2>
            <button class="modal__close" @click="showShareModal = false">✕</button>
          </div>
          <div class="modal__content text-center">
            <div class="share-info">
              <span class="share-icon">👥</span>
              <p>分享给好友，邀请他来养鱼</p>
              <p>每次分享可获得 <strong class="text-gold">3份饲料</strong></p>
            </div>
            
            <div class="share-buttons">
              <button class="share-btn share-btn--wechat" @click="handleShare">
                <span>💬</span> 微信好友
              </button>
              <button class="share-btn share-btn--moments" @click="handleShare">
                <span>🌅</span> 朋友圈
              </button>
              <button class="share-btn share-btn--link" @click="handleShare">
                <span>🔗</span> 复制链接
              </button>
            </div>
            
            <div class="share-bonus">
              <p>当前额外饲料: <strong class="text-gold">{{ gameStore.shareBonus }}</strong></p>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- 代加工凭证页面 -->
    <Teleport to="body">
      <div v-if="showProcessingVoucher && processingFishInfo" class="modal-overlay">
        <ProcessingVoucher
          :fishInfo="processingFishInfo"
          :coupon="processingCoupon"
          @close="showProcessingVoucher = false"
          @share="(platform) => { showToast('分享成功！', 'success') }"
          @navigate="() => { showToast('正在打开导航...', 'info') }"
        />
      </div>
    </Teleport>
    
    <!-- Toast 提示 -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show" class="toast" :class="`toast--${toast.type}`">
          {{ toast.message }}
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.game-view {
  position: relative;
}

/* 弹窗遮罩 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  width: 100%;
  max-width: 380px;
  max-height: 85vh;
  border-radius: 20px;
  overflow: hidden;
  animation: modal-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal--caught {
  max-width: 340px;
}

.modal--share {
  max-width: 340px;
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

.modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal__header h2 {
  font-size: 18px;
  font-weight: 600;
}

.modal__close {
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

.modal__close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal__content {
  padding: 20px;
  overflow-y: auto;
  max-height: 65vh;
}

/* 扫码界面 */
.qr-scanner {
  text-align: center;
  margin-bottom: 20px;
}

.scanner-frame {
  width: 200px;
  height: 200px;
  margin: 0 auto 12px;
  border: 3px solid #38bdf8;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.scanner-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #38bdf8, transparent);
  animation: scan-line 2s ease-in-out infinite;
}

.scanner-icon {
  font-size: 48px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.5;
}

.scanner-hint {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.demo-hint {
  text-align: center;
  color: #fbbf24;
  font-size: 12px;
  margin-bottom: 12px;
}

.fish-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.fish-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.fish-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.fish-card__emoji {
  font-size: 36px;
}

.fish-card__name {
  font-weight: 600;
  font-size: 14px;
}

.fish-card__info {
  font-size: 11px;
  opacity: 0.7;
}

@keyframes scan-line {
  0%, 100% { top: 0; }
  50% { top: 100%; }
}

/* 捕获鱼预览 */
.caught-fish-preview {
  padding: 20px;
}

.caught-fish-image {
  width: 120px;
  height: auto;
  margin-bottom: 12px;
  animation: caught-bounce 1s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
}

.caught-fish-info h3 {
  font-size: 20px;
  margin-bottom: 4px;
}

.caught-fish-weight {
  font-size: 24px;
  font-weight: 700;
  color: #fbbf24;
}

.caught-fish-status {
  font-size: 14px;
  margin-top: 8px;
}

.caught-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.caught-actions .btn {
  flex: 1;
  padding: 14px;
}

.caught-hint {
  margin-top: 16px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

@keyframes caught-bounce {
  0%, 100% { transform: translateY(0) rotate(-5deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}

/* 分享界面 */
.share-info {
  padding: 20px 0;
}

.share-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.share-info p {
  margin: 6px 0;
}

.share-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 20px 0;
}

.share-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.share-btn--wechat {
  background: #07c160;
  color: white;
}

.share-btn--moments {
  background: linear-gradient(135deg, #07c160, #1aad19);
  color: white;
}

.share-btn--link {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.share-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.share-bonus {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 优惠券列表 */
.coupon-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coupon-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(234, 88, 12, 0.1));
  border-radius: 12px;
  border-left: 4px solid #fb923c;
  position: relative;
}

.coupon-card__badge {
  position: absolute;
  top: -8px;
  right: 12px;
  font-size: 24px;
}

.coupon-card--used {
  opacity: 0.5;
  filter: grayscale(1);
}

.coupon-card__left {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.coupon-value {
  font-size: 28px;
  font-weight: 700;
  color: #fb923c;
}

.coupon-name {
  font-size: 13px;
}

.coupon-weight {
  font-size: 11px;
  opacity: 0.7;
}

.coupon-card__right {
  text-align: right;
}

.coupon-qr {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(0, 0, 0, 0.3);
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 6px;
}

.coupon-qr span {
  font-size: 20px;
}

.coupon-qr small {
  font-size: 9px;
  font-family: monospace;
}

.coupon-expires {
  font-size: 10px;
  opacity: 0.6;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 32px;
  color: rgba(255, 255, 255, 0.7);
}

.empty-state span {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-gold:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Toast */
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 500;
  z-index: 2000;
  backdrop-filter: blur(12px);
}

.toast--success {
  background: rgba(34, 197, 94, 0.9);
}

.toast--warning {
  background: rgba(234, 179, 8, 0.9);
  color: #1e1e1e;
}

.toast--error {
  background: rgba(239, 68, 68, 0.9);
}

.toast--info {
  background: rgba(56, 189, 248, 0.9);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

/* 烤鱼结果弹窗 */
.modal--grilled {
  max-width: 360px;
}

.grilled-fish-preview {
  padding: 20px;
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(234, 88, 12, 0.1));
  border-radius: 16px;
  margin-bottom: 16px;
}

.grilled-fish-image {
  position: relative;
  display: inline-block;
}

.grilled-emoji {
  font-size: 72px;
  display: block;
  animation: sizzle 0.5s ease-in-out infinite;
}

.steam {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
}

.steam span {
  position: absolute;
  width: 8px;
  height: 20px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: steam-rise 1.5s ease-out infinite;
}

.steam span:nth-child(1) { left: -15px; animation-delay: 0s; }
.steam span:nth-child(2) { left: 0; animation-delay: 0.3s; }
.steam span:nth-child(3) { left: 15px; animation-delay: 0.6s; }

@keyframes steam-rise {
  0% { transform: translateY(0) scale(1); opacity: 0.6; }
  100% { transform: translateY(-40px) scale(0.5); opacity: 0; }
}

@keyframes sizzle {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.grilled-fish-info h3 {
  font-size: 20px;
  margin: 12px 0 4px;
  color: #fbbf24;
}

.grilled-weight {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
}

.coupon-earned {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.1));
  border-radius: 12px;
  margin-bottom: 16px;
}

.coupon-icon {
  font-size: 24px;
}

.coupon-earned p {
  font-size: 15px;
}

.store-info {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid rgba(251, 146, 60, 0.3);
}

.store-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.store-header span {
  font-size: 24px;
}

.store-header h4 {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(90deg, #ff7b00, #fbbf24);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.store-service {
  font-size: 14px;
  margin-bottom: 8px;
}

.service-details {
  background: rgba(251, 146, 60, 0.15);
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.service-fee {
  font-size: 16px;
  margin-bottom: 4px;
}

.service-fee strong {
  color: #fbbf24;
  font-size: 20px;
}

.service-note {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.store-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.btn-full {
  width: 100%;
  margin-top: 8px;
}
</style>

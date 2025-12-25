import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 鱼类类型定义
export const FISH_TYPES = {
    QINGJIANG: {
        id: 'qingjiang',
        name: '清江鱼',
        emoji: '🐟',
        color: '#22d3ee',
        targetWeight: 900, // 目标重量 (克)
        weightVariance: 200, // 重量浮动范围
        foodRequired: 30, // 成长需要的饲料量
        value: 50, // 优惠券价值
    },
    LINGBO: {
        id: 'lingbo',
        name: '凌波鱼',
        emoji: '🐠',
        color: '#f472b6',
        targetWeight: 900,
        weightVariance: 200,
        foodRequired: 40,
        value: 80,
    },
    BASHA: {
        id: 'basha',
        name: '巴沙鱼',
        emoji: '🐡',
        color: '#facc15',
        targetWeight: 900,
        weightVariance: 200,
        foodRequired: 50,
        value: 100,
    },
    JINMU: {
        id: 'jinmu',
        name: '金目鲈',
        emoji: '🎏',
        color: '#fb923c',
        targetWeight: 900,
        weightVariance: 200,
        foodRequired: 70,
        value: 150,
    },
    HAILU: {
        id: 'hailu',
        name: '海鲈鱼',
        emoji: '🐟',
        color: '#4ade80',
        targetWeight: 950,
        weightVariance: 250,
        foodRequired: 60,
        value: 120,
    },
}

// 鱼状态
export const FISH_STATUS = {
    BABY: 'baby',
    GROWING: 'growing',
    ADULT: 'adult',
    HUNGRY: 'hungry',
    SICK: 'sick',
    DEAD: 'dead',
    CAUGHT: 'caught', // 被捕获状态
}

export const useGameStore = defineStore('game', () => {
    // 测试模式 - 无限饲料
    const isTestMode = ref(true) // 设置为 true 开启测试模式

    // 用户状态
    const userId = ref(null)
    const username = ref('访客')
    const feedCount = ref(10) // 每日饲料次数
    const lastFeedDate = ref(null)
    const shareBonus = ref(0) // 分享获得的额外饲料

    // 鱼塘状态
    const fishes = ref([])
    const caughtFish = ref(null) // 当前捕获的鱼
    const coupons = ref([])

    // 渔网状态
    const isNetActive = ref(false)
    const netPosition = ref({ x: 0, y: 0 })

    // 时间状态
    const isNight = ref(false)
    const currentTime = ref(new Date())

    // 背景主题 (1-4)
    const currentBackground = ref(1)

    // 计算属性
    const totalFishValue = computed(() => {
        return fishes.value
            .filter(f => f.status === FISH_STATUS.ADULT)
            .reduce((sum, f) => sum + FISH_TYPES[f.type.toUpperCase()].value, 0)
    })

    const adultFishCount = computed(() => {
        return fishes.value.filter(f => f.status === FISH_STATUS.ADULT).length
    })

    const totalFeedAvailable = computed(() => {
        if (isTestMode.value) return 9999 // 测试模式无限饲料
        return feedCount.value + shareBonus.value
    })

    // 方法
    function addFish(type, fromQRCode = false) {
        const fishType = FISH_TYPES[type.toUpperCase()]
        if (!fishType) return null

        // 初始重量 50-100g 幼鱼
        const initialWeight = 50 + Math.random() * 50

        const fish = {
            id: `fish_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: fishType.id,
            name: fishType.name,
            status: FISH_STATUS.BABY,
            weight: initialWeight, // 重量（克）
            hunger: 100,
            health: 100,
            foodEaten: 0, // 已吃的饲料量
            growth: 0,
            createdAt: new Date().toISOString(),
            lastFedAt: new Date().toISOString(), // 上次喂食时间
            fromQRCode: fromQRCode,
            // 位置和运动
            x: Math.random() * 70 + 15, // 15-85% position
            y: Math.random() * 50 + 25, // 25-75% position
            targetX: Math.random() * 70 + 15,
            targetY: Math.random() * 50 + 25,
            direction: 1, // 1 = 右, -1 = 左
            speed: 0.1 + Math.random() * 0.2,
            angle: 0, // 游动角度
        }

        fishes.value.push(fish)
        saveToPersistence()
        return fish
    }

    // 更新鱼的游动
    function updateFishMovement() {
        for (const fish of fishes.value) {
            if (fish.status === FISH_STATUS.DEAD || fish.status === FISH_STATUS.CAUGHT) continue

            // 计算与目标的距离
            const dx = fish.targetX - fish.x
            const dy = fish.targetY - fish.y
            const distance = Math.sqrt(dx * dx + dy * dy)

            // 如果接近目标，设置新目标
            if (distance < 3) {
                fish.targetX = Math.random() * 70 + 15
                fish.targetY = Math.random() * 50 + 25
            } else {
                // 朝目标移动
                const moveX = (dx / distance) * fish.speed
                const moveY = (dy / distance) * fish.speed

                fish.x += moveX
                fish.y += moveY

                // 更新方向（鱼头朝向游动方向）
                if (moveX !== 0) {
                    fish.direction = moveX > 0 ? 1 : -1
                }

                // 计算角度
                fish.angle = Math.atan2(moveY, Math.abs(moveX)) * (180 / Math.PI) * 0.3
            }
        }
    }

    function feedFish(fishId) {
        // 测试模式跳过饲料检查
        if (!isTestMode.value) {
            const availableFeed = feedCount.value + shareBonus.value
            if (availableFeed <= 0) {
                return { success: false, message: '饲料不足！分享给好友可获得更多饲料' }
            }
        }

        const fish = fishes.value.find(f => f.id === fishId)
        if (!fish || fish.status === FISH_STATUS.DEAD || fish.status === FISH_STATUS.CAUGHT) {
            return { success: false, message: '找不到这条鱼' }
        }

        const fishType = FISH_TYPES[fish.type.toUpperCase()]

        // 每次喂食增加一天的成长重量 (~60g)
        const DAILY_GROWTH = 60
        const weightGain = DAILY_GROWTH + (Math.random() - 0.5) * 20 // 50-70g
        fish.weight += weightGain
        fish.hunger = 100 // 重置饥饿度
        fish.lastFedAt = new Date().toISOString() // 更新喂食时间
        fish.foodEaten += 1

        // 成熟标准：重量达到 800g
        const MATURE_WEIGHT = 800
        fish.growth = Math.min(100, (fish.weight / MATURE_WEIGHT) * 100)

        // 检查是否成熟
        if (fish.weight >= MATURE_WEIGHT) {
            fish.status = FISH_STATUS.ADULT
        } else if (fish.status === FISH_STATUS.BABY && fish.weight > 100) {
            fish.status = FISH_STATUS.GROWING
        }

        // 恢复饥饿状态
        if (fish.status === FISH_STATUS.HUNGRY && fish.hunger > 30) {
            fish.status = fish.weight >= MATURE_WEIGHT ? FISH_STATUS.ADULT : FISH_STATUS.GROWING
        }

        // 扣除饲料（测试模式不扣除）
        if (!isTestMode.value) {
            if (shareBonus.value > 0) {
                shareBonus.value--
            } else {
                feedCount.value--
            }
        }

        saveToPersistence()

        return {
            success: true,
            message: `喂食成功！重量 +${weightGain.toFixed(0)}g`,
            newWeight: fish.weight
        }
    }

    function feedAllFish() {
        let fed = 0
        let totalWeightGain = 0
        for (const fish of fishes.value) {
            // 测试模式不检查饲料
            if (!isTestMode.value) {
                const availableFeed = feedCount.value + shareBonus.value
                if (availableFeed <= 0) break
            }
            if (fish.status !== FISH_STATUS.DEAD && fish.status !== FISH_STATUS.CAUGHT) {
                const result = feedFish(fish.id)
                if (result.success) {
                    fed++
                    totalWeightGain += result.newWeight || 0
                }
            }
        }
        return { success: true, fed, message: `喂了 ${fed} 条鱼！` }
    }

    // 撒网捕鱼
    function castNet(x, y) {
        netPosition.value = { x, y }
        isNetActive.value = true

        // 检查是否捕到鱼
        const caughtFishes = []
        for (const fish of fishes.value) {
            if (fish.status === FISH_STATUS.DEAD || fish.status === FISH_STATUS.CAUGHT) continue

            // 计算鱼与渔网的距离（渔网范围 15%）
            const dx = fish.x - x
            const dy = fish.y - y
            const distance = Math.sqrt(dx * dx + dy * dy)

            if (distance < 15) {
                // 75% 捕获概率
                if (Math.random() < 0.75) {
                    caughtFishes.push(fish)
                }
            }
        }

        // 延迟后关闭渔网动画
        setTimeout(() => {
            isNetActive.value = false

            // 处理捕获的鱼（只取第一条）
            if (caughtFishes.length > 0) {
                const fish = caughtFishes[0]
                fish.status = FISH_STATUS.CAUGHT
                caughtFish.value = fish
            }
        }, 1000)

        return caughtFishes.length
    }

    // 放生捕获的鱼
    function releaseFish() {
        if (!caughtFish.value) return { success: false }

        const fish = fishes.value.find(f => f.id === caughtFish.value.id)
        if (fish) {
            fish.status = fish.weight >= FISH_TYPES[fish.type.toUpperCase()].targetWeight
                ? FISH_STATUS.ADULT
                : FISH_STATUS.GROWING
        }
        caughtFish.value = null
        saveToPersistence()

        return { success: true, message: '鱼已放回鱼塘' }
    }

    // 送去餐厅加工（生成烤鱼二维码）
    function sendToRestaurant() {
        if (!caughtFish.value) return { success: false }

        const fish = caughtFish.value
        const fishType = FISH_TYPES[fish.type.toUpperCase()]

        // 生成烤鱼券
        const coupon = {
            id: `coupon_${Date.now()}`,
            fishId: fish.id,
            fishName: fish.name,
            fishWeight: fish.weight,
            type: 'grilled_fish', // 烤鱼券
            value: fishType.value,
            code: generateCouponCode(),
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            used: false,
        }

        coupons.value.push(coupon)

        // 移除鱼
        fishes.value = fishes.value.filter(f => f.id !== fish.id)
        caughtFish.value = null

        saveToPersistence()

        return {
            success: true,
            coupon,
            message: `🍖 已送去加工！获得 ${fish.name} 烤鱼券 ¥${fishType.value}`
        }
    }

    function harvestFish(fishId) {
        const fish = fishes.value.find(f => f.id === fishId)
        if (!fish || fish.status !== FISH_STATUS.ADULT) {
            return { success: false, message: '只能收获成年鱼' }
        }

        const fishType = FISH_TYPES[fish.type.toUpperCase()]
        const coupon = {
            id: `coupon_${Date.now()}`,
            fishId: fish.id,
            fishName: fish.name,
            fishWeight: fish.weight,
            type: 'grilled_fish',
            value: fishType.value,
            code: generateCouponCode(),
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            used: false,
        }

        coupons.value.push(coupon)
        fishes.value = fishes.value.filter(f => f.id !== fishId)
        saveToPersistence()

        return { success: true, coupon, message: `获得 ${fishType.value} 元烤鱼券！` }
    }

    function generateCouponCode() {
        return 'GF' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substr(2, 4).toUpperCase()
    }

    // 分享获得额外饲料
    function shareToFriend() {
        shareBonus.value += 3 // 每次分享获得3份饲料
        saveToPersistence()
        return { success: true, message: '分享成功！获得 3 份饲料' }
    }

    // 切换背景主题
    function setBackground(id) {
        if (id >= 1 && id <= 4) {
            currentBackground.value = id
            saveToPersistence()
        }
    }

    function updateFishStates() {
        const now = new Date()
        isNight.value = now.getHours() >= 19 || now.getHours() < 6
        currentTime.value = now

        // 更新鱼的游动
        updateFishMovement()

        // 游戏常量
        const MS_PER_DAY = 24 * 60 * 60 * 1000
        const DAILY_GROWTH = 60      // 每天自动成长 60g
        const MATURE_WEIGHT = 800    // 成熟重量
        const HUNGRY_DAYS = 3        // 超过3天没喂 -> 饥饿
        const DEAD_DAYS = 15         // 超过15天没喂 -> 死亡

        for (const fish of fishes.value) {
            if (fish.status === FISH_STATUS.DEAD || fish.status === FISH_STATUS.CAUGHT) continue

            // 计算距离创建和上次喂食的天数
            const createdAt = new Date(fish.createdAt)
            const lastFed = fish.lastFedAt ? new Date(fish.lastFedAt) : createdAt
            const daysSinceCreated = (now - createdAt) / MS_PER_DAY
            const daysSinceLastFed = (now - lastFed) / MS_PER_DAY

            // 计算自然生长重量（基于创建天数）
            // 自然生长 = 天数 * 每日成长量 + 随机浮动
            const naturalGrowth = daysSinceCreated * DAILY_GROWTH
            const randomVariance = (Math.sin(fish.id.charCodeAt(5) || 0) * 0.2 + 0.9) // 每条鱼固定的随机因子
            const initialWeight = 50 + (fish.id.charCodeAt(10) || 50) % 50 // 初始重量 50-100g

            // 喂食加成 = 喂食次数 * 每日成长量
            const feedingBonus = (fish.foodEaten || 0) * DAILY_GROWTH

            // 计算总重量
            fish.weight = initialWeight + naturalGrowth * randomVariance + feedingBonus
            fish.growth = Math.min(100, (fish.weight / MATURE_WEIGHT) * 100)

            // 超过15天没喂 -> 死亡
            if (daysSinceLastFed > DEAD_DAYS) {
                fish.status = FISH_STATUS.DEAD
                fish.deathTime = Date.now()
                fish.hunger = 0
            }
            // 超过3天没喂 -> 饥饿
            else if (daysSinceLastFed > HUNGRY_DAYS) {
                if (fish.status !== FISH_STATUS.HUNGRY && fish.status !== FISH_STATUS.ADULT) {
                    fish.status = FISH_STATUS.HUNGRY
                }
                fish.hunger = Math.max(0, 100 - ((daysSinceLastFed - HUNGRY_DAYS) / (DEAD_DAYS - HUNGRY_DAYS)) * 100)
            } else {
                fish.hunger = 100
                // 检查是否成熟
                if (fish.weight >= MATURE_WEIGHT) {
                    fish.status = FISH_STATUS.ADULT
                } else if (fish.weight > 100 && fish.status === FISH_STATUS.BABY) {
                    fish.status = FISH_STATUS.GROWING
                }
            }
        }

        // 移除死亡的鱼
        fishes.value = fishes.value.filter(fish => fish.status !== FISH_STATUS.DEAD)

        saveToPersistence()
    }

    function resetDailyFeed() {
        const today = new Date().toDateString()
        if (lastFeedDate.value !== today) {
            feedCount.value = 10
            lastFeedDate.value = today
            saveToPersistence()
        }
    }

    function saveToPersistence() {
        localStorage.setItem('oceanFlameGame', JSON.stringify({
            userId: userId.value,
            username: username.value,
            feedCount: feedCount.value,
            shareBonus: shareBonus.value,
            lastFeedDate: lastFeedDate.value,
            fishes: fishes.value,
            coupons: coupons.value,
            currentBackground: currentBackground.value,
        }))
    }

    function loadFromPersistence() {
        const saved = localStorage.getItem('oceanFlameGame')
        if (saved) {
            const data = JSON.parse(saved)
            userId.value = data.userId
            username.value = data.username || '访客'
            feedCount.value = data.feedCount ?? 10
            shareBonus.value = data.shareBonus ?? 0
            lastFeedDate.value = data.lastFeedDate
            fishes.value = data.fishes || []
            coupons.value = data.coupons || []
            currentBackground.value = data.currentBackground || 1
        }
        resetDailyFeed()
    }

    function initGame() {
        loadFromPersistence()

        // 如果没有鱼，送一条初始鱼
        if (fishes.value.length === 0) {
            addFish('qingjiang', false)
        }

        // 启动状态更新定时器（更快的更新速度以实现平滑游动）
        setInterval(updateFishStates, 100)
    }

    return {
        // State
        userId,
        username,
        feedCount,
        shareBonus,
        fishes,
        caughtFish,
        coupons,
        isNight,
        currentTime,
        isNetActive,
        netPosition,
        currentBackground,

        // Computed
        totalFishValue,
        adultFishCount,
        totalFeedAvailable,

        // Actions
        addFish,
        feedFish,
        feedAllFish,
        castNet,
        releaseFish,
        sendToRestaurant,
        harvestFish,
        shareToFriend,
        setBackground,
        updateFishStates,
        initGame,
        loadFromPersistence,
        saveToPersistence,
    }
})

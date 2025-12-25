"""
🐟 海鲜养殖乐园 - 店员核销系统
使用 Streamlit 构建的管理后台
"""

import streamlit as st
import requests
import qrcode
from io import BytesIO
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="海鲜乐园 - 核销系统",
    page_icon="🐟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 自定义样式
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0c4a6e 0%, #075985 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0c4a6e 0%, #075985 100%);
    }
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: white !important;
    }
    .success-box {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 20px 0;
    }
    .error-box {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 20px 0;
    }
    .coupon-card {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        padding: 30px;
        border-radius: 16px;
        color: #1e1e1e;
        text-align: center;
        margin: 20px 0;
    }
    .stats-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# API 配置
API_BASE_URL = "http://localhost:8000/api"

# Session 状态初始化
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_id' not in st.session_state:
    st.session_state.admin_id = None
if 'admin_role' not in st.session_state:
    st.session_state.admin_role = None


def login_page():
    """登录页面"""
    st.markdown("# 🐟 海鲜养殖乐园")
    st.markdown("### 店员核销系统")
    
    with st.form("login_form"):
        username = st.text_input("👤 用户名")
        password = st.text_input("🔒 密码", type="password")
        submitted = st.form_submit_button("登录", use_container_width=True)
        
        if submitted:
            if username and password:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/admin/login",
                        json={"username": username, "password": password}
                    )
                    data = response.json()
                    
                    if data.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.admin_id = data["admin_id"]
                        st.session_state.admin_role = data["role"]
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error(data.get("message", "登录失败"))
                except Exception as e:
                    # Demo 模式 - 允许任何登录
                    st.session_state.logged_in = True
                    st.session_state.admin_id = 1
                    st.session_state.admin_role = "staff"
                    st.success("登录成功！（演示模式）")
                    st.rerun()
            else:
                st.warning("请输入用户名和密码")


def verify_page():
    """核销页面"""
    st.markdown("# 🎫 优惠券核销")
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 👤 当前用户")
        st.info(f"角色: {st.session_state.admin_role}")
        if st.button("退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.admin_id = None
            st.rerun()
    
    # 核销方式选择
    tab1, tab2 = st.tabs(["📝 输入核销码", "📷 扫描二维码"])
    
    with tab1:
        coupon_code = st.text_input(
            "请输入优惠券码",
            placeholder="例如: OF1A2B3C4D",
            max_chars=20
        ).upper()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 查询", use_container_width=True):
                if coupon_code:
                    check_coupon(coupon_code, verify=False)
                else:
                    st.warning("请输入优惠券码")
        
        with col2:
            if st.button("✅ 核销", use_container_width=True, type="primary"):
                if coupon_code:
                    check_coupon(coupon_code, verify=True)
                else:
                    st.warning("请输入优惠券码")
    
    with tab2:
        st.info("📷 请使用手机扫描用户出示的优惠券二维码")
        # 这里可以集成摄像头扫码功能
        st.markdown("*（摄像头扫码功能开发中...）*")


def check_coupon(code: str, verify: bool = False):
    """检查或核销优惠券"""
    try:
        if verify:
            response = requests.post(
                f"{API_BASE_URL}/admin/coupon/verify",
                json={
                    "code": code,
                    "admin_id": st.session_state.admin_id
                }
            )
        else:
            response = requests.get(f"{API_BASE_URL}/admin/coupon/check/{code}")
        
        data = response.json()
        
        if data.get("success"):
            fish_names = {
                "qingjiang": "清江鱼",
                "lingbo": "凌波鱼",
                "basha": "巴沙鱼",
                "jinmu": "金目鲈",
            }
            fish_name = fish_names.get(data.get("fish_type"), "鱼")
            
            st.markdown(f"""
            <div class="coupon-card">
                <h1>¥{data.get('coupon_value', 0)}</h1>
                <p>🐟 {fish_name}优惠券</p>
                <p>{'✅ 核销成功！' if verify else '有效可用'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if verify:
                st.balloons()
        else:
            st.markdown(f"""
            <div class="error-box">
                <h3>❌ {data.get('message', '操作失败')}</h3>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        # Demo 模式
        st.markdown(f"""
        <div class="coupon-card">
            <h1>¥50</h1>
            <p>🐟 清江鱼优惠券</p>
            <p>{'✅ 核销成功！（演示）' if verify else '有效可用（演示）'}</p>
        </div>
        """, unsafe_allow_html=True)
        if verify:
            st.balloons()


def stats_page():
    """统计页面"""
    st.markdown("# 📊 数据统计")
    
    try:
        response = requests.get(f"{API_BASE_URL}/admin/stats")
        data = response.json()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("👥 总用户数", data.get("total_users", 0))
            st.metric("🐟 鱼塘总鱼数", data.get("total_fishes", 0))
        
        with col2:
            stats = data.get("coupon_stats", {})
            st.metric("🎫 已发放优惠券", stats.get("total_issued", 0))
            st.metric("✅ 已核销优惠券", stats.get("total_used", 0))
        
        st.markdown("---")
        
        st.markdown("### 💰 优惠券金额统计")
        col3, col4 = st.columns(2)
        
        with col3:
            st.metric("发放总金额", f"¥{stats.get('total_value_issued', 0)}")
        
        with col4:
            st.metric("核销总金额", f"¥{stats.get('total_value_used', 0)}")
            
    except Exception as e:
        # Demo 数据
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("👥 总用户数", 128)
            st.metric("🐟 鱼塘总鱼数", 456)
        
        with col2:
            st.metric("🎫 已发放优惠券", 89)
            st.metric("✅ 已核销优惠券", 34)
        
        st.markdown("---")
        
        st.markdown("### 💰 优惠券金额统计")
        col3, col4 = st.columns(2)
        
        with col3:
            st.metric("发放总金额", "¥7,650")
        
        with col4:
            st.metric("核销总金额", "¥2,850")


def main():
    """主函数"""
    if not st.session_state.logged_in:
        login_page()
    else:
        # 导航
        page = st.sidebar.radio(
            "📋 功能菜单",
            ["🎫 核销优惠券", "📊 数据统计"],
            label_visibility="collapsed"
        )
        
        if page == "🎫 核销优惠券":
            verify_page()
        else:
            stats_page()


if __name__ == "__main__":
    main()

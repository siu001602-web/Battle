import streamlit as st
import random
from abilities_data import ABILITIES_POOL

# 페이지 설정
st.set_page_config(page_title="능력 뽑기 시스템", page_icon="✨", layout="centered")

# 세션 상태 초기화
if "gems" not in st.session_state:
    st.session_state.gems = 1000
if "abilities" not in st.session_state:
    st.session_state.abilities = []

# 단일 뽑기 함수 (확률: 3성 94.9%, 4성 5.0%, 5성 0.1%)
def roll_single(abilities_pool):
    rand = random.random() * 100
    if rand < 0.1:
        tier = "5성"
    elif rand < 5.1:
        tier = "4성"
    else:
        tier = "3성"
    
    name = random.choice(abilities_pool[tier])
    return {"tier": tier, "name": name}

def run_gacha_app(abilities_pool):
    st.title("✨ 능력 뽑기 시스템")
    st.write("보석을 소모하여 강력한 전투 능력을 뽑아보세요!")

    # 📊 확률 안내 박스 추가
    st.info("""
    **📋 [뽑기 확률 안내]**
    * 🌟 **5성 (광대)** : **0.1%**
    * ✨ **4성 (힐러, 경찰)** : **5.0%**
    * 🔹 **3성 (검투사)** : **94.9%**
    *(※ 10연차 시 4성 이상 능력 1개 확정!)*
    """)

    st.metric("보유 보석", f"💎 {st.session_state.gems}개")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎲 1회 뽑기 (보석 100개)"):
            if st.session_state.gems >= 100:
                st.session_state.gems -= 100
                result = roll_single(abilities_pool)
                st.session_state.abilities.append(result)
                
                if result["tier"] == "5성":
                    st.balloons()
                    st.success(f"🎉 [대박!] 5성 능력 획득: **{result['name']}**")
                elif result["tier"] == "4성":
                    st.info(f"✨ [특급] 4성 능력 획득: **{result['name']}**")
                else:
                    st.write(f"🔹 [일반] 3성 능력 획득: {result['name']}")
            else:
                st.error("보석이 부족합니다!")

    with col2:
        if st.button("✨ 10연차 뽑기 (보석 1000개 - 4성 이상 1개 확정!)"):
            if st.session_state.gems >= 1000:
                st.session_state.gems -= 1000
                results = []
                
                for _ in range(10):
                    results.append(roll_single(abilities_pool))
                
                # 4성 이상 확정 보장 로직
                has_4star_or_higher = any(item["tier"] in ["4성", "5성"] for item in results)
                if not has_4star_or_higher:
                    guaranteed_tier = "5성" if (random.random() * 100) < 2 else "4성"
                    results[-1] = {
                        "tier": guaranteed_tier, 
                        "name": random.choice(abilities_pool[guaranteed_tier])
                    }
                
                st.session_state.abilities.extend(results)
                
                st.success("📦 10연차 뽑기 완료! (4성 이상 1개 확정 포함)")
                for item in results:
                    prefix = "🌟" if item["tier"] in ["4성", "5성"] else "🔹"
                    st.write(f"{prefix} **[{item['tier']}]** {item['name']}")
                
                if any(item["tier"] == "5성" for item in results):
                    st.balloons()
            else:
                st.error("보석이 부족합니다!")

    if st.button("💎 보석 1000개 무료 충전"):
        st.session_state.gems += 1000
        st.success("보석 1000개가 충전되었습니다!")
        st.rerun()

    st.divider()
    st.subheader("🎒 내가 얻은 능력 목록")

    if st.session_state.abilities:
        counts = {}
        for ab in st.session_state.abilities:
            key = f"[{ab['tier']}] {ab['name']}"
            counts[key] = counts.get(key, 0) + 1
            
        for ab_name, cnt in counts.items():
            st.write(f"- **{ab_name}** : {cnt}개 보유")
            
        if st.button("🗑️ 능력 목록 초기화"):
            st.session_state.abilities = []
            st.rerun()
    else:
        st.write("아직 획득한 능력이 없습니다. 뽑기를 진행해 보세요!")

if __name__ == "__main__":
    run_gacha_app(ABILITIES_POOL)

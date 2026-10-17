import streamlit as st
import random

# 페이지 설정 (가장 처음에 위치해야 함)
st.set_page_config(page_title="심리전 턴제 게임", page_icon="🎮", layout="centered")

# 세션 상태 초기화 (데이터가 없는 경우에만 안전하게 생성)
if "initialized" not in st.session_state:
    st.session_state.max_hp = 5
    st.session_state.player_hp = 5
    st.session_state.ai_hp = 5
    st.session_state.turn = 1
    st.session_state.player_wait_turns = 0
    st.session_state.ai_wait_turns = 0
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.log = "게임을 시작합니다! 난이도를 고르고 버튼을 선택해주세요."
    st.session_state.player_history = []
    st.session_state.initialized = True

def reset_game():
    st.session_state.player_hp = 5
    st.session_state.ai_hp = 5
    st.session_state.turn = 1
    st.session_state.player_wait_turns = 0
    st.session_state.ai_wait_turns = 0
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.player_history = []
    st.session_state.log = "게임이 초기화되었습니다. 다시 시작하세요!"

# 체력을 하트(❤️/🖤) 5칸으로 보여주는 함수
def render_hp(current_hp, max_hp=5):
    red_hearts = "❤️" * current_hp
    black_hearts = "🖤" * (max_hp - current_hp)
    return f"{red_hearts}{black_hearts} ({current_hp}/{max_hp})"

# 스마트 AI의 선택 로직
def get_ai_choice(difficulty, player_history):
    choices = ["공격", "방어", "치료", "존버"]
    
    if not player_history:
        return random.choice(choices)
    
    last_action = player_history[-1]
    
    if difficulty == "보통":
        weights = []
        for c in choices:
            if last_action == "공격" and c == "방어":
                weights.append(4)
            elif last_action == "존버" and c == "공격":
                weights.append(4)
            else:
                weights.append(1)
        return random.choices(choices, weights=weights, k=1)[0]
        
    elif difficulty == "매운맛":
        attack_count = player_history.count("공격")
        wait_count = player_history.count("존버")
        
        weights = []
        for c in choices:
            if attack_count >= len(player_history) / 2 and c == "방어":
                weights.append(5)
            elif wait_count > 0 and c == "공격":
                weights.append(4)
            elif c == "치료" and random.random() < 0.3:
                weights.append(3)
            else:
                weights.append(1)
        return random.choices(choices, weights=weights, k=1)[0]
    
    return random.choice(choices)

st.title("🎮 심리전 턴제 미니게임")
st.write("공격, 방어, 치료, 존버(대기) 중 하나를 선택해 상대를 쓰러트리세요!")

# 난이도 선택 라디오 버튼
difficulty = st.radio("🤖 AI 난이도 선택", ["보통", "매운맛"], horizontal=True)

st.divider()

# 상단 체력 및 턴 표시 (안전하게 .get() 또는 세션 상태 체크 후 출력)
p_wait = st.session_state.get("player_wait_turns", 0)
ai_wait = st.session_state.get("ai_wait_turns", 0)
p_hp = st.session_state.get("player_hp", 5)
ai_hp = st.session_state.get("ai_hp", 5)
turn = st.session_state.get("turn", 1)

col1, col2, col3 = st.columns(3)
with col1:
    buff_text = f" 🔥버프({p_wait}턴)" if p_wait > 0 else ""
    st.metric("내 체력", f"{render_hp(p_hp)}{buff_text}")
with col2:
    st.metric("현재 턴", f"{turn}턴")
with col3:
    ai_buff_text = f" 🔥버프({ai_wait}턴)" if ai_wait > 0 else ""
    st.metric("상대 체력", f"{render_hp(ai_hp)}{ai_buff_text}")

st.divider()

# 게임 종료 확인
if st.session_state.get("game_over", False):
    if st.session_state.winner == "player":
        st.success("🎉 승리했습니다! 상대를 쓰러트렸어요!")
    elif st.session_state.winner == "ai":
        st.error("💀 패배했습니다... 상대에게 졌습니다.")
    else:
        st.info("🤝 무승부입니다!")
    
    if st.button("다시 시작하기"):
        reset_game()
        st.rerun()
else:
    st.subheader("행동을 선택하세요")
    
    # 버튼 배치
    c1, c2, c3, c4 = st.columns(4)
    
    player_choice = None
    with c1:
        if st.button("⚔️ 공격"):
            player_choice = "공격"
    with c2:
        if st.button("🛡️ 방어"):
            player_choice = "방어"
    with c3:
        if st.button("💊 치료"):
            player_choice = "치료"
    with c4:
        if st.button("⏳ 존버"):
            player_choice = "존버"

    # 플레이어가 행동을 골랐을 때 로직 처리
    if player_choice:
        st.session_state.player_history.append(player_choice)
        if len(st.session_state.player_history) > 5:
            st.session_state.player_history.pop(0)

        ai_choice = get_ai_choice(difficulty, st.session_state.player_history)
        
        base_damage = 2 if st.session_state.turn >= 10 else 1
        
        log_message = f"**[결과 ({difficulty} 난이도)]** 당신: {player_choice} | 상대: {ai_choice}\n\n"
        
        # --- 플레이어 행동 처리 ---
        p_dmg_deal = 0
        if player_choice == "공격":
            if ai_choice != "방어":
                has_buff = st.session_state.player_wait_turns > 0
                p_dmg_deal = base_damage * (2 if has_buff else 1)
                log_message += f"▶ 당신의 공격 성공! 상대에게 {p_dmg_deal}의 데미지를 줬습니다."
                if has_buff:
                    log_message += " (존버 버프 사용!)\n"
                    st.session_state.player_wait_turns = 0
                else:
                    log_message += "\n"
            else:
                log_message += "▶ 당신의 공격이 상대의 방어에 막혔습니다!\n"
                if st.session_state.player_wait_turns > 0:
                    st.session_state.player_wait_turns -= 1
            
        elif player_choice == "치료":
            if st.session_state.player_hp < st.session_state.max_hp:
                st.session_state.player_hp += 1
                log_message += "▶ 치료 성공! 체력이 1 회복되었습니다.\n"
            else:
                log_message += "▶ 체력이 이미 가득 차 있어 치료가 실패했습니다.\n"
            
            if st.session_state.player_wait_turns > 0:
                st.session_state.player_wait_turns -= 1
            
        elif player_choice == "존버":
            st.session_state.player_wait_turns = 2
            log_message += "▶ 존버(대기) 상태! 앞으로 2턴 동안 공격 성공 시 데미지가 2배가 됩니다.\n"
            
        elif player_choice == "방어":
            log_message += "▶ 방어 태세를 취했습니다.\n"
            if st.session_state.player_wait_turns > 0:
                st.session_state.player_wait_turns -= 1

        # --- AI 행동 처리 ---
        ai_dmg_deal = 0
        if ai_choice == "공격":
            if player_choice != "방어":
                ai_has_buff = st.session_state.ai_wait_turns > 0
                ai_dmg_deal = base_damage * (2 if ai_has_buff else 1)
                log_message += f"▶ 상대의 공격 명중! 당신이 {ai_dmg_deal}의 데미지를 입었습니다."
                if ai_has_buff:
                    log_message += " (상대 존버 버프 사용!)\n"
                    st.session_state.ai_wait_turns = 0
                else:
                    log_message += "\n"
            else:
                log_message += "▶ 상대의 공격을 방어해냈습니다!\n"
                if st.session_state.ai_wait_turns > 0:
                    st.session_state.ai_wait_turns -= 1
            
        elif ai_choice == "치료":
            if st.session_state.ai_hp < st.session_state.max_hp:
                st.session_state.ai_hp += 1
                log_message += "▶ 상대가 치료하여 체력을 1 회복했습니다.\n"
            else:
                log_message += "▶ 상대의 치료가 실패했습니다.\n"
            
            if st.session_state.ai_wait_turns > 0:
                st.session_state.ai_wait_turns -= 1
            
        elif ai_choice == "존버":
            st.session_state.ai_wait_turns = 2
            log_message += "▶ 상대가 존버(대기) 상태에 돌입했습니다.\n"
            
        elif ai_choice == "방어":
            log_message += "▶ 상대가 방어 태세를 취했습니다.\n"
            if st.session_state.ai_wait_turns > 0:
                st.session_state.ai_wait_turns -= 1

        # 체력 반영
        st.session_state.player_hp = max(0, st.session_state.player_hp - ai_dmg_deal)
        st.session_state.ai_hp = max(0, st.session_state.ai_hp - p_dmg_deal)
        
        # 턴 증가
        st.session_state.turn += 1
        st.session_state.log = log_message
        
        # 승리 조건 확인
        if st.session_state.player_hp == 0 and st.session_state.ai_hp == 0:
            st.session_state.game_over = True
            st.session_state.winner = "draw"
        elif st.session_state.player_hp == 0:
            st.session_state.game_over = True
            st.session_state.winner = "ai"
        elif st.session_state.ai_hp == 0:
            st.session_state.game_over = True
            st.session_state.winner = "player"
            
        st.rerun()

# 게임 로그 출력 영역
st.divider()
st.subheader("📜 이번 턴 기록")
st.info(st.session_state.get("log", "게임을 시작해주세요!"))

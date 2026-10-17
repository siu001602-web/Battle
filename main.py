import streamlit as st
import random

# 페이지 설정
st.set_page_config(page_title="심리전 턴제 게임", page_icon="🎮", layout="centered")

# 세션 상태 초기화 (게임 데이터 유지)
if "initialized" not in st.session_state:
    st.session_state.player_hp = 5
    st.session_state.ai_hp = 5
    st.session_state.turn = 1
    st.session_state.player_waiting = False
    st.session_state.ai_waiting = False
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.log = "게임을 시작합니다! 버튼을 골라주세요."
    st.session_state.initialized = True

def reset_game():
    st.session_state.player_hp = 5
    st.session_state.ai_hp = 5
    st.session_state.turn = 1
    st.session_state.player_waiting = False
    st.session_state.ai_waiting = False
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.log = "게임이 초기화되었습니다. 다시 시작하세요!"

st.title("🎮 심리전 턴제 미니게임")
st.write("공격, 방어, 치료, 존버(대기) 중 하나를 선택해 상대를 쓰러트리세요!")

# 상단 체력 및 턴 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("내 체력", f"{'❤️' * st.session_state.player_hp} ({st.session_state.player_hp}/5)")
with col2:
    st.metric("현재 턴", f"{st.session_state.turn}턴")
with col3:
    st.metric("상대 체력", f"{'❤️' * st.session_state.ai_hp} ({st.session_state.ai_hp}/5)")

st.divider()

# 게임 종료 확인
if st.session_state.game_over:
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
        # AI 선택 (공격, 방어, 치료, 존버 중 랜덤)
        ai_choices = ["공격", "방어", "치료", "존버"]
        ai_choice = random.choice(ai_choices)
        
        # 10턴 이상일 때 공격 피해량 설정 (기본 1, 10턴 이상 2)
        damage = 2 if st.session_state.turn >= 10 else 1
        
        log_message = f"**[결과]** 당신: {player_choice} | 상대: {ai_choice}\n\n"
        
        # --- 플레이어 행동 처리 ---
        p_dmg_deal = 0
        if player_choice == "공격":
            if ai_choice != "방어":
                p_dmg_deal = damage * (2 if st.session_state.player_waiting else 1)
                log_message += f"▶ 당신의 공격 성공! 상대에게 {p_dmg_deal}의 데미지를 줬습니다.\n"
            else:
                log_message += "▶ 당신의 공격이 상대의 방어에 막혔습니다!\n"
            st.session_state.player_waiting = False
            
        elif player_choice == "치료":
            if st.session_state.player_hp < 5:
                st.session_state.player_hp += 1
                log_message += "▶ 치료 성공! 체력이 1 회복되었습니다.\n"
            else:
                log_message += "▶ 체력이 이미 가득 차 있어 치료가 실패했습니다.\n"
            st.session_state.player_waiting = False
            
        elif player_choice == "존버":
            st.session_state.player_waiting = True
            log_message += "▶ 존버(대기) 상태! 다음 공격 성공 시 데미지가 2배가 됩니다.\n"
            
        elif player_choice == "방어":
            log_message += "▶ 방어 태세를 취했습니다.\n"
            st.session_state.player_waiting = False

        # --- AI 행동 처리 ---
        ai_dmg_deal = 0
        if ai_choice == "공격":
            if player_choice != "방어":
                ai_dmg_deal = damage * (2 if st.session_state.ai_waiting else 1)
                log_message += f"▶ 상대의 공격 명중! 당신이 {ai_dmg_deal}의 데미지를 입었습니다.\n"
            else:
                log_message += "▶ 상대의 공격을 방어해냈습니다!\n"
            st.session_state.ai_waiting = False
            
        elif ai_choice == "치료":
            if st.session_state.ai_hp < 5:
                st.session_state.ai_hp += 1
                log_message += "▶ 상대가 치료하여 체력을 1 회복했습니다.\n"
            else:
                log_message += "▶ 상대의 치료가 실패했습니다.\n"
            st.session_state.ai_waiting = False
            
        elif ai_choice == "존버":
            st.session_state.ai_waiting = True
            log_message += "▶ 상대가 존버(대기) 상태에 돌입했습니다.\n"
            
        elif ai_choice == "방어":
            log_message += "▶ 상대가 방어 태세를 취했습니다.\n"
            st.session_state.ai_waiting = False

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
st.info(st.session_state.log)

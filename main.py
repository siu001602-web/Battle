import streamlit as st
import random

# 페이지 설정
st.set_page_config(page_title="심리전 턴제 게임 - 궁극기 고정", page_icon="🎮", layout="centered")

# 세션 상태 초기화
if "initialized" not in st.session_state:
    st.session_state.max_hp = 5
    st.session_state.player_hp = 5
    st.session_state.ai_hp = 5
    st.session_state.turn = 1
    st.session_state.player_wait_turns = 0
    st.session_state.ai_wait_turns = 0
    st.session_state.player_consecutive = 0
    st.session_state.ai_consecutive = 0
    st.session_state.player_ultimate = 0
    st.session_state.ai_ultimate = 0
    st.session_state.player_counter_cooldown = 0
    st.session_state.ai_counter_cooldown = 0
    st.session_state.player_phoenix_turns = 0
    st.session_state.ai_phoenix_turns = 0
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.log = "궁극기 능력을 선택하고 게임을 시작하세요!"
    st.session_state.player_history = []
    # 게임 시작 전 선택할 임시 기본값
    st.session_state.player_ult_type = "전투사 (공격력 3 / 실패시 피-1)"
    st.session_state.ai_ult_type = random.choice(["전투사 (공격력 3 / 실패시 피-1)", "피닉스 (2턴내 사망시 풀피 부활)"])
    st.session_state.initialized = True

def reset_game():
    st.session_state.player_hp = 5
    st.session_state.ai_hp = 5
    st.session_state.turn = 1
    st.session_state.player_wait_turns = 0
    st.session_state.ai_wait_turns = 0
    st.session_state.player_consecutive = 0
    st.session_state.ai_consecutive = 0
    st.session_state.player_ultimate = 0
    st.session_state.ai_ultimate = 0
    st.session_state.player_counter_cooldown = 0
    st.session_state.ai_counter_cooldown = 0
    st.session_state.player_phoenix_turns = 0
    st.session_state.ai_phoenix_turns = 0
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.player_history = []
    st.session_state.log = "게임이 초기화되었습니다. 다시 시작하세요!"
    st.session_state.ai_ult_type = random.choice(["전투사 (공격력 3 / 실패시 피-1)", "피닉스 (2턴내 사망시 풀피 부활)"])

def render_hp(current_hp, max_hp=5):
    red_hearts = "❤️" * current_hp
    black_hearts = "🖤" * (max_hp - current_hp)
    return f"{red_hearts}{black_hearts} ({current_hp}/{max_hp})"

# 스마트 AI 선택 로직
def get_ai_choice(difficulty, player_history, ai_ultimate, ai_counter_cooldown):
    if ai_ultimate >= 3 and random.random() < 0.7:
        return "필살기"
        
    choices = ["공격", "방어", "치료", "존버"]
    if ai_counter_cooldown == 0:
        choices.append("반격")
        
    if not player_history:
        return random.choice(choices)
    
    last_action = player_history[-1]
    
    if difficulty == "보통":
        weights = []
        for c in choices:
            if last_action == "공격" and c in ["방어", "반격"]:
                weights.append(3)
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
            if attack_count >= 2 and c == "반격":
                weights.append(5)
            elif wait_count > 0 and c == "공격":
                weights.append(4)
            elif c == "치료" and random.random() < 0.3:
                weights.append(3)
            else:
                weights.append(1)
        return random.choices(choices, weights=weights, k=1)[0]
    
    return random.choice(choices)

st.title("🔥 하드코어 심리전 턴제 게임")
st.write("공격, 방어, 치료, 존버, 반격, 그리고 궁극기를 활용해 상대를 쓰러트리세요!")

# 1턴일 때만 능력을 변경할 수 있고, 게임이 진행되면 변경 불가하도록 설정
is_game_started = st.session_state.turn > 1

col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    difficulty = st.radio("🤖 AI 난이도", ["보통", "매운맛"], horizontal=True, disabled=is_game_started)
with col_opt2:
    player_ult_type = st.selectbox(
        "✨ 내 궁극기 선택 (게임 시작 후 변경 불가)", 
        ["전투사 (공격력 3 / 실패시 피-1)", "피닉스 (2턴내 사망시 풀피 부활)"],
        index=0 if "전투사" in st.session_state.player_ult_type else 1,
        disabled=is_game_started
    )
    # 선택된 궁극기를 세션에 저장
    st.session_state.player_ult_type = player_ult_type

st.divider()

# 안전한 상태 가져오기
p_wait = st.session_state.get("player_wait_turns", 0)
ai_wait = st.session_state.get("ai_wait_turns", 0)
p_hp = st.session_state.get("player_hp", 5)
ai_hp = st.session_state.get("ai_hp", 5)
turn = st.session_state.get("turn", 1)
p_ult = st.session_state.get("player_ultimate", 0)
ai_ult = st.session_state.get("ai_ultimate", 0)
p_cd = st.session_state.get("player_counter_cooldown", 0)
p_phoenix = st.session_state.get("player_phoenix_turns", 0)
ai_phoenix = st.session_state.get("ai_phoenix_turns", 0)

col1, col2, col3 = st.columns(3)
with col1:
    buff_text = f" 🔥버프({p_wait}턴)" if p_wait > 0 else ""
    ult_text = f" ✨게이지({p_ult}/3)"
    phoenix_text = f" 🦅피닉스({p_phoenix}턴)" if p_phoenix > 0 else ""
    st.metric("내 체력", f"{render_hp(p_hp)}{buff_text}{phoenix_text}\n{ult_text}")
with col2:
    st.metric("현재 턴", f"{turn}턴")
with col3:
    ai_buff_text = f" 🔥버프({ai_wait}턴)" if ai_wait > 0 else ""
    ai_ult_text = f" ✨게이지({ai_ult}/3)"
    ai_phoenix_text = f" 🦅피닉스({ai_phoenix}턴)" if ai_phoenix > 0 else ""
    st.metric("상대 체력", f"{render_hp(ai_hp)}{ai_buff_text}{ai_phoenix_text}\n{ai_ult_text} (상대 궁: {st.session_state.ai_ult_type.split()[0]})")

st.divider()

if st.session_state.get("game_over", False):
    if st.session_state.winner == "player":
        st.success("🎉 승리했습니다! 상대를 완벽하게 제압했어요!")
    elif st.session_state.winner == "ai":
        st.error("💀 패배했습니다... 상대의 심리전에 당했습니다.")
    else:
        st.info("🤝 무승부입니다!")
    
    if st.button("다시 시작하기"):
        reset_game()
        st.rerun()
else:
    st.subheader("행동을 선택하세요")
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
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
    with c5:
        if p_cd > 0:
            st.button(f"🥊 반격({p_cd}턴)", disabled=True)
        else:
            if st.button("🥊 반격"):
                player_choice = "반격"
    with c6:
        if p_ult >= 3:
            if st.button("✨ 궁극기"):
                player_choice = "필살기"
        else:
            st.button("✨ 궁극기", disabled=True)

    if player_choice:
        if "player_history" not in st.session_state:
            st.session_state.player_history = []
            
        st.session_state.player_history.append(player_choice)
        if len(st.session_state.player_history) > 5:
            st.session_state.player_history.pop(0)

        ai_choice = get_ai_choice(difficulty, st.session_state.player_history, st.session_state.ai_ultimate, st.session_state.ai_counter_cooldown)
        
        base_damage = 2 if st.session_state.turn >= 10 else 1
        log_message = f"**[결과 ({difficulty} 난이도)]** 당신: {player_choice} | 상대: {ai_choice}\n\n"
        
        p_dmg_deal = 0
        ai_dmg_deal = 0
        p_self_damage = 0
        ai_self_damage = 0
        
        # 연속 공격 처리
        if player_choice == "공격":
            st.session_state.player_consecutive += 1
        else:
            st.session_state.player_consecutive = 0
            
        if ai_choice == "공격":
            st.session_state.ai_consecutive += 1
        else:
            st.session_state.ai_consecutive = 0

        is_player_exhausted = st.session_state.player_consecutive >= 3
        is_ai_exhausted = st.session_state.ai_consecutive >= 3

        # --- 플레이어 행동 처리 ---
        if player_choice == "필살기":
            st.session_state.player_ultimate = 0
            if "전투사" in st.session_state.player_ult_type:
                if ai_choice in ["방어", "반격"]:
                    p_self_damage += 1
                    log_message += f"⚔️ [전투사 궁극기 실패!] 상대의 방어/반격에 막혀 체력이 1 깎였습니다!\n"
                else:
                    p_dmg_deal = 3
                    log_message += f"⚔️ [전투사 궁극기 작렬!] 상대에게 3의 강력한 대미지를 줬습니다!\n"
            elif "피닉스" in st.session_state.player_ult_type:
                st.session_state.player_phoenix_turns = 2
                log_message += f"🦅 [피닉스 부활 발동!] 앞으로 2턴 내에 사망 시 체력이 풀피로 부활합니다!\n"
                
        elif player_choice == "공격":
            if is_player_exhausted:
                log_message += "⚠️ 연속 공격으로 지쳐서 공격이 빗나갔습니다!\n"
                st.session_state.player_consecutive = 0
            elif ai_choice == "방어":
                log_message += "▶ 당신의 공격이 상대의 방어에 막혔습니다!\n"
                if st.session_state.player_wait_turns > 0:
                    st.session_state.player_wait_turns -= 1
            elif ai_choice == "반격":
                log_message += "💥 상대의 반격에 당했습니다! 공격이 카운터당해 대미지를 입습니다!\n"
                ai_dmg_deal += base_damage + 1
            else:
                has_buff = st.session_state.player_wait_turns > 0
                p_dmg_deal = base_damage * (2 if has_buff else 1)
                log_message += f"▶ 당신의 공격 성공! 상대에게 {p_dmg_deal}의 대미지를 줬습니다."
                if has_buff:
                    log_message += " (존버 버프 사용!)\n"
                    st.session_state.player_wait_turns = 0
                else:
                    log_message += "\n"
                    
        elif player_choice == "치료":
            if ai_choice == "공격" and not is_ai_exhausted:
                log_message += "⚠️ 치료 중 상대에게 공격당해 치료가 실패하고 대미지를 입었습니다!\n"
            else:
                if st.session_state.player_hp < st.session_state.max_hp:
                    st.session_state.player_hp += 1
                    log_message += "💊 치료 성공! 체력이 1 회복되었습니다.\n"
                else:
                    log_message += "▶ 체력이 이미 가득 차 있습니다.\n"
            if st.session_state.player_wait_turns > 0:
                st.session_state.player_wait_turns -= 1
                
        elif player_choice == "존버":
            st.session_state.player_wait_turns = 2
            if st.session_state.player_ultimate < 3:
                st.session_state.player_ultimate += 1
            log_message += "⏳ 존버(대기) 상태 돌입! (궁극기 게이지 +1)\n"
            
        elif player_choice == "방어":
            if st.session_state.player_ultimate < 3:
                st.session_state.player_ultimate += 1
            log_message += "🛡️ 방어 태세! (궁극기 게이지 +1)\n"
            if st.session_state.player_wait_turns > 0:
                st.session_state.player_wait_turns -= 1
                
        elif player_choice == "반격":
            st.session_state.player_counter_cooldown = 3
            if ai_choice == "공격" and not is_ai_exhausted:
                p_dmg_deal += base_damage + 1
                log_message += f"🥊 완벽한 반격 성공! 상대의 공격을 받아쳐 {p_dmg_deal}의 대미지를 돌려줬습니다! (반격 쿨다운 3턴)\n"
            else:
                log_message += "❌ 반격 실패! 상대가 공격하지 않았습니다. (반격 쿨다운 3턴)\n"

        # --- AI 행동 처리 ---
        if ai_choice == "필살기":
            st.session_state.ai_ultimate = 0
            if "전투사" in st.session_state.ai_ult_type:
                if player_choice in ["방어", "반격"]:
                    ai_self_damage += 1
                    log_message += f"⚔️ [상대 전투사 궁극기 실패!] 당신의 방어/반격에 막혀 상대 체력이 1 깎였습니다!\n"
                else:
                    ai_dmg_deal += 3
                    log_message += f"⚔️ [상대 전투사 궁극기 작렬!] 당신이 3의 강력한 대미지를 입었습니다!\n"
            elif "피닉스" in st.session_state.ai_ult_type:
                st.session_state.ai_phoenix_turns = 2
                log_message += f"🦅 [상대 피닉스 부활 발동!] 앞으로 2턴 내 사망 시 풀피로 부활합니다!\n"
                
        elif ai_choice == "공격":
            if is_ai_exhausted:
                log_message += "⚠️ 상대가 지쳐서 공격이 빗나갔습니다!\n"
                st.session_state.ai_consecutive = 0
            elif player_choice == "방어":
                log_message += "▶ 상대의 공격을 완벽하게 방어해냈습니다!\n"
                if st.session_state.ai_wait_turns > 0:
                    st.session_state.ai_wait_turns -= 1
            elif player_choice == "반격":
                log_message += "▶ 상대의 공격을 반격하여 무효화했습니다!\n"
            else:
                ai_has_buff = st.session_state.ai_wait_turns > 0
                ai_dmg_deal += base_damage * (2 if ai_has_buff else 1)
                log_message += f"▶ 상대의 공격 명중! 당신이 {ai_dmg_deal}의 대미지를 입었습니다."
                if ai_has_buff:
                    log_message += " (상대 존버 버프 사용!)\n"
                    st.session_state.ai_wait_turns = 0
                else:
                    log_message += "\n"
                    
        elif ai_choice == "치료":
            if player_choice == "공격" and not is_player_exhausted:
                log_message += "⚠️ 상대가 치료 중 당신의 공격을 받아 치료가 실패했습니다!\n"
            else:
                if st.session_state.ai_hp < st.session_state.max_hp:
                    st.session_state.ai_hp += 1
                    log_message += "💊 상대가 치료에 성공해 체력을 1 회복했습니다.\n"
                else:
                    log_message += "▶ 상대의 치료가 실패했습니다.\n"
            if st.session_state.ai_wait_turns > 0:
                st.session_state.ai_wait_turns -= 1
                
        elif ai_choice == "존버":
            st.session_state.ai_wait_turns = 2
            if st.session_state.ai_ultimate < 3:
                st.session_state.ai_ultimate += 1
            log_message += "⏳ 상대가 존버(대기) 상태에 돌입했습니다. (상대 게이지 +1)\n"
            
        elif ai_choice == "방어":
            if st.session_state.ai_ultimate < 3:
                st.session_state.ai_ultimate += 1
            log_message += "🛡️ 상대가 방어 태세를 취했습니다. (상대 게이지 +1)\n"
            if st.session_state.ai_wait_turns > 0:
                st.session_state.ai_wait_turns -= 1
                
        elif ai_choice == "반격":
            st.session_state.ai_counter_cooldown = 3
            if player_choice == "공격" and not is_player_exhausted:
                ai_dmg_deal += base_damage + 1
                log_message += f"❌ 상대의 반격에 당해 추가 대미지를 입었습니다!\n"
            else:
                log_message += "▶ 상대의 반격이 헛스윙으로 끝났습니다.\n"

        # 쿨다운 및 피닉스 지속 턴 감소
        if st.session_state.player_counter_cooldown > 0:
            st.session_state.player_counter_cooldown -= 1
        if st.session_state.ai_counter_cooldown > 0:
            st.session_state.ai_counter_cooldown -= 1
        if st.session_state.player_phoenix_turns > 0:
            st.session_state.player_phoenix_turns -= 1
        if st.session_state.ai_phoenix_turns > 0:
            st.session_state.ai_phoenix_turns -= 1

        # 체력 최종 반영 (자해 대미지 포함)
        st.session_state.player_hp = max(0, st.session_state.player_hp - ai_dmg_deal - p_self_damage)
        st.session_state.ai_hp = max(0, st.session_state.ai_hp - p_dmg_deal - ai_self_damage)

        # --- 피닉스 부활 체크 ---
        if st.session_state.player_hp == 0 and st.session_state.player_phoenix_turns > 0:
            st.session_state.player_hp = st.session_state.max_hp
            st.session_state.player_phoenix_turns = 0
            log_message += "\n🦅 **[피닉스 부활 발동!]** 죽음의 문턱에서 체력을 모두 회복하고 부활했습니다!\n"
            
        if st.session_state.ai_hp == 0 and st.session_state.ai_phoenix_turns > 0:
            st.session_state.ai_hp = st.session_state.max_hp
            st.session_state.ai_phoenix_turns = 0
            log_message += "\n🦅 **[상대 피닉스 부활 발동!]** 상대가 풀피로 부활했습니다!\n"
        
        st.session_state.turn += 1
        st.session_state.log = log_message
        
        # 승리/패배 판정
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

st.divider()
st.subheader("📜 이번 턴 기록")
st.info(st.session_state.get("log", "게임을 시작해주세요!"))

import streamlit as st

class GuildMember:
    def __init__(self, name, fame, activity_points, guild_rank_count=0):
        self.name = name
        self.fame = fame
        self.activity_points = activity_points
        self.guild_rank_count = guild_rank_count

    def meets_condition(
        self,
        base_fame,
        base_activity_points,
        fame_bonus_step,
        fame_bonus_reduce,
        activity_bonus_step,
        activity_bonus_reduce,
        guild_rank_deductions=None
    ):
        if guild_rank_deductions is None or all(deduction == 0 for _, deduction in guild_rank_deductions):
            guild_rank_deductions = []

        fame_bonus = max(0, (self.fame - base_fame) // fame_bonus_step * fame_bonus_reduce)
        activity_bonus = max(0, (self.activity_points - base_activity_points) // activity_bonus_step * activity_bonus_reduce)

        adjusted_min_activity_points = max(0, base_activity_points - fame_bonus)
        adjusted_min_fame = max(0, base_fame - activity_bonus)

        for threshold, deduction in guild_rank_deductions:
            while self.guild_rank_count >= threshold:
                adjusted_min_activity_points -= deduction
                self.guild_rank_count -= threshold
                if self.guild_rank_count < threshold:
                    break

        fame_deficit = max(0, adjusted_min_fame - self.fame)
        activity_deficit = max(0, adjusted_min_activity_points - self.activity_points)

        meets_condition = fame_deficit == 0 and activity_deficit == 0
        return meets_condition, fame_deficit, activity_deficit


def main():
    st.title("길드 조건 확인")

    # 길드 조건 입력
    st.sidebar.header("길드 기본 조건")
    base_fame = st.sidebar.number_input("명성", min_value=0, value=200, step=1)
    base_activity_points = st.sidebar.number_input("활동포인트", min_value=0, value=30000, step=1000)
    
    st.sidebar.header("명성 당 활포 조건 감소")
    fame_bonus_step = st.sidebar.number_input("명성", min_value=1, value=50, step=1)
    fame_bonus_reduce = st.sidebar.number_input("활동포인트", min_value=0, value=5000, step=1000)
    
    st.sidebar.header("활포 당 명성 조건 감소")
    activity_bonus_step = st.sidebar.number_input("활동포인트", min_value=1, value=10000, step=1000)
    activity_bonus_reduce = st.sidebar.number_input("명성", min_value=0, value=20, step=1)

    st.sidebar.header("길랭 조건 설정")
    guild_rank_deductions = []
    num_deductions = st.sidebar.number_input("길랭 활포 차감 조건 개수", min_value=0, value=1, step=1)
    if num_deductions > 0:
        for i in range(num_deductions):
            st.sidebar.subheader(f"길랭 조건 {i + 1}")
            num_wars = st.sidebar.number_input(f"{i + 1} 조건 길랭 회차 수", min_value=1, value=3, step=1, key=f"war_count_{i}")
            deduction_amount = st.sidebar.number_input(f"{i + 1} 조건 활포 차감액", min_value=0, value=10000, step=1000, key=f"deduction_{i}")
            guild_rank_deductions.append((num_wars, deduction_amount))
    
    st.sidebar.markdown(
        """
        <div style="text-align: right; font-size: small;">
            <b>by 쵸우 (맢닉)</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.header("명성 입력")
    fame_input = st.text_area('''
    닉네임, 명성 (줄바꿈으로 구분)
    -필수 입력 정보입니다 정확한 닉네임을 입력해주세요.
    ''')
    
    st.header("활동포인트 입력")
    activity_input = st.text_area('''
    닉네임, 활동포인트 (줄바꿈으로 구분)
    -필수 입력 정보입니다 정확한 닉네임을 입력해주세요.
    ''')
    
    st.header("길랭 횟수 입력")
    rank_input = st.text_area('''
    닉네임, 길랭횟수 (줄바꿈으로 구분)
    -입력값이 없을시 0회로 간주합니다. 정확한 닉네임을 입력해주세요.
    ''')

    members = {}
    if fame_input:
        for line in fame_input.split('\n'):
            try:
                name, fame = line.split(',')
                fame = int(fame)
                if name not in members:
                    members[name] = GuildMember(name, fame, 0, 0)
                else:
                    members[name].fame = fame
            except ValueError:
                st.warning(f"명성 입력 오류: {line}")

    if activity_input:
        for line in activity_input.split('\n'):
            try:
                name, activity_points = line.split(',')
                activity_points = int(activity_points)
                if name not in members:
                    members[name] = GuildMember(name, 0, activity_points, 0)
                else:
                    members[name].activity_points = activity_points
            except ValueError:
                st.warning(f"활동포인트 입력 오류: {line}")

    if rank_input:
        for line in rank_input.split('\n'):
            try:
                name, rank_count = line.split(',')
                rank_count = int(rank_count)
                if name not in members:
                    members[name] = GuildMember(name, 0, 0, rank_count)
                else:
                    members[name].guild_rank_count = rank_count
            except ValueError:
                st.warning(f"길랭 횟수 입력 오류: {line}")

    if st.button("결과 확인"):
        st.subheader("길드 조건 확인")
        missing_data = []
        for name, member in sorted(members.items()):
            missing_info = []
            if member.fame == 0:
                missing_info.append("명성")
            if member.activity_points == 0:
                missing_info.append("활동포인트")

            if missing_info:
                missing_data.append(f"{name} ({', '.join(missing_info)})")
            else:
                meets_condition, fame_deficit, activity_deficit = member.meets_condition(
                    base_fame, base_activity_points,
                    fame_bonus_step, fame_bonus_reduce,
                    activity_bonus_step, activity_bonus_reduce,
                    guild_rank_deductions
                )

                if meets_condition:
                    st.write(f"🟢 {name} - 조건 충족")
                else:
                    deficit_message = []
                    if fame_deficit > 0:
                        deficit_message.append(f"명성 부족: {fame_deficit}")
                    if activity_deficit > 0:
                        deficit_message.append(f"활동포인트 부족: {activity_deficit}")
                    st.write(f"🔴 {name} - 조건 미충족 ({', '.join(deficit_message)})")

        if missing_data:
            st.warning(f"{', '.join(missing_data)} 데이터가 부족합니다.")


if __name__ == "__main__":
    main()

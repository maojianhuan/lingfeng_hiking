import streamlit as st
from finance import read_members, make_report, make_insurance_report
from duties import DUTIES, assign_duties, duty_rows

st.set_page_config(page_title='凌峰出队助手', page_icon='🏔️', layout='wide')
st.title('🏔️ 凌峰出队助手')
st.caption('上传报名问卷 → 选择成员和领队 → 填写费用 → 导出报表')
source = st.file_uploader('上传报名明细 Excel', type=['xlsx'])
if source:
    try:
        members = read_members(source)
    except (ValueError, OSError) as exc:
        st.error(str(exc))
        st.stop()
    if not members:
        st.warning('报名表没有成员记录。')
        st.stop()
    selected = st.multiselect('本次出队成员（按报名时间排列）', range(len(members)),
                              format_func=lambda i: members[i]['姓名'], default=list(range(len(members))))
    if not selected:
        st.info('请至少选择一名出队成员。')
        st.stop()
    selected = sorted(selected)
    left, middle, right = st.columns(3)
    leader = left.selectbox('领队', selected, index=None, placeholder='请选择领队',
                            format_func=lambda i: members[i]['姓名'])
    deputy = middle.selectbox('副领队', selected, index=None, placeholder='请选择副领队',
                              format_func=lambda i: members[i]['姓名'])
    finance = right.selectbox('财务', selected, index=None, placeholder='请选择财务',
                              format_func=lambda i: members[i]['姓名'])
    left, right = st.columns(2)
    bus = left.number_input('包车总费用（元）', min_value=0, value=1000, step=1)
    radios = right.number_input('对讲机数量', min_value=0, value=2, step=1)
    st.caption('每人预收 100 元；普通队员领队费 10 元，领队及副领队免收；保险每人 2 元；登山杖 12 元、头灯 8 元，按问卷借用记录计算；对讲机每台 12 元，和包车费一起全员均摊。')
    if leader is None:
        st.info('请选择领队后生成报表。')
        st.stop()
    if finance is None:
        st.info('请选择财务后生成报表。')
        st.stop()
    specified = [i for i in (leader, deputy, finance) if i is not None]
    if len(set(specified)) != len(specified):
        st.error('领队、副领队和财务不能由同一人兼任，请调整选择。')
        st.stop()
    chosen = [{**members[i], '角色': '领队' if i == leader else '副领队' if i == deputy else '财务' if i == finance else '队员'}
              for i in selected]
    if any(m['入学年份'] is None for m in chosen if m['角色'] == '队员'):
        st.error('缺少入学年份，请在报名明细中补充“入学年份”列后重新上传。')
        st.stop()
    if st.session_state.get('assignment_input') != chosen:
        st.session_state.assignment_result = assign_duties(chosen)
        st.session_state.assignment_input = chosen
    chosen = st.session_state.assignment_result
    with st.expander('查看自动职能安排'):
        st.caption('领队、副领队及财务均手动指定，不参与其他职能分配。其他职能人数上限按剩余队员人数÷5 向上取整。优先较早入学者，同年份按报名顺序满足志愿；未满足志愿者随机补入剩余职能。负责人优先愿意负责者，再选入学最早者，同年随机；无人愿意则从该职能入学最早者中随机指定。')
        rows = duty_rows(chosen)
        st.write(f'领队：{rows[0][1]}　　副领队：{rows[0][3]}　　财务：{rows[0][5]}')
        for duty, names in rows[1:]:
            st.write(f'{duty}：{names}')
    st.download_button('下载财务与职能报表', make_report(chosen, bus, radios, 12),
                       '出队财务报表.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    try:
        insurance = make_insurance_report(chosen)
    except ValueError as exc:
        st.warning('保险名单无法导出：' + str(exc) + '。请更正报名明细后重新上传。')
    else:
        st.download_button('下载购买保险信息', insurance, '出队保险名单.xlsx',
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

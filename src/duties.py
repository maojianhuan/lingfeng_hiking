"""联合优化职能分组与负责人；各层目标依次求最优。"""
from ortools.sat.python import cp_model

DUTIES = ['后勤', '队医', '装备', '摄影', '财务', '队记']


def assign_duties(members):
    participants = [i for i, m in enumerate(members) if m['角色'] not in ('领队', '副领队', '财务')]
    duties = [d for d in DUTIES if d != '财务']
    if len(participants) < len(duties):
        raise ValueError('五项职能各需一名负责人，普通队员至少需要 5 人')
    for i in participants:
        m = members[i]
        if not isinstance(m.get('是否新人'), bool) or not m.get('校区'):
            raise ValueError(f"{m['姓名']}缺少校区或是否新人，请补全报名明细（是否新人填写是或否）")
    if sum(members[i]['校区'] == '学院路' for i in participants) < 3:
        raise ValueError('装备、后勤、队医各需一名学院路校区负责人，普通队员中至少需要 3 名学院路成员')
    result = [{**m, '职能': '财务' if m['角色'] == '财务' else '',
               '职能负责': m['角色'] == '财务'} for m in members]
    capacity = (len(participants) + len(duties) - 1) // len(duties)
    model = cp_model.CpModel()
    assigned = {(i, d): model.new_bool_var(f'group_{i}_{d}') for i in participants for d in duties}
    leaders = {(i, d): model.new_bool_var(f'leader_{i}_{d}') for i in participants for d in duties}
    for i in participants:
        model.add(sum(assigned[i, d] for d in duties) == 1)
        for d in duties:
            model.add(leaders[i, d] <= assigned[i, d])
            if d in ('装备', '后勤', '队医') and members[i]['校区'] != '学院路':
                model.add(leaders[i, d] == 0)
    for d in duties:
        model.add(sum(leaders[i, d] for i in participants) == 1)
        model.add(sum(assigned[i, d] for i in participants) <= capacity)
    unwilling = sum(leaders[i, d] for i in participants for d in duties if not members[i]['愿意负责'])
    newcomers = sum(leaders[i, d] for i in participants for d in duties if members[i]['是否新人'])
    # 未列入志愿的职能统一排在所有已填志愿之后；最小化总排名损失。
    preference_loss = sum(assigned[i, d] * (members[i]['职能意向'].index(d)
                          if d in members[i]['职能意向'] else len(DUTIES))
                          for i in participants for d in duties)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0

    def minimize(objective):
        model.minimize(objective)
        status = solver.solve(model)
        if status == cp_model.INFEASIBLE:
            raise ValueError('无法同时满足职能人数和负责人校区要求，请调整出队名单')
        if status != cp_model.OPTIMAL:
            raise ValueError(f'职能分配未得到最优解：{solver.status_name(status)}')
        model.add(objective == solver.value(objective))

    for objective in (unwilling, newcomers, preference_loss):
        minimize(objective)
    # 固定前三层最优值后，按报名时间及原始位置逐人选择，消除同分歧义。
    for i in sorted(participants, key=lambda i: (members[i]['报名时间'], i)):
        minimize(sum((2 * j + 1) * assigned[i, d] - leaders[i, d]
                     for j, d in enumerate(duties)))
        for d in duties:
            if solver.value(assigned[i, d]):
                result[i]['职能'] = d
                result[i]['职能负责'] = bool(solver.value(leaders[i, d]))
    return result


def duty_rows(members):
    """每项职能一行，负责人置于首位。"""
    leaders = '、'.join(m['姓名'] for m in members if m['角色'] == '领队') or '未指定'
    deputies = '、'.join(m['姓名'] for m in members if m['角色'] == '副领队') or '未指定'
    finance = '、'.join(m['姓名'] for m in members if m['角色'] == '财务') or '未指定'
    rows = [('领队', leaders, '副领队', deputies, '财务', finance)]
    for duty in [d for d in DUTIES if d != '财务']:
        group = [m for m in members if m.get('职能') == duty and m['角色'] not in ('领队', '副领队', '财务')]
        group.sort(key=lambda m: not m.get('职能负责', False))
        names = '、'.join(m['姓名'] + ('（职能负责）' if m.get('职能负责') else '') for m in group)
        rows.append((duty, names or '暂无成员'))
    return rows

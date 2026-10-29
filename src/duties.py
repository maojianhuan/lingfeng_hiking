"""按入学年份、职能志愿分配职能与负责人。"""
import random

DUTIES = ['后勤', '队医', '装备', '摄影', '财务', '队记']


def assign_duties(members):
    participants = [i for i, m in enumerate(members) if m['角色'] not in ('领队', '副领队', '财务')]
    if any(not isinstance(members[i].get('入学年份'), int) for i in participants):
        raise ValueError('职能分配需要每位成员的入学年份，请补全报名明细')
    capacity = (len(participants) + len(DUTIES) - 2) // (len(DUTIES) - 1)
    remaining = dict.fromkeys(DUTIES, capacity)
    remaining['财务'] = 0
    result = [{**m, '职能': '财务' if m['角色'] == '财务' else '' if m['角色'] in ('领队', '副领队') else '未分配',
               '职能负责': m['角色'] == '财务'} for m in members]
    order = sorted(participants, key=lambda i: (result[i]['入学年份'], result[i]['报名时间']))
    for i in order:
        member = result[i]
        duty = next((d for d in member['职能意向'] if remaining[d] > 0), None)
        if duty is not None:
            remaining[duty] -= 1
            member['职能'] = duty
    # 未满足志愿者补入尚有名额的职能，较早入学者优先。
    for i in order:
        if result[i]['职能'] == '未分配':
            available = [d for d in DUTIES if remaining[d] > 0]
            duty = random.choice(available)
            remaining[duty] -= 1
            result[i]['职能'] = duty
    for duty in [d for d in DUTIES if d != '财务']:
        group = [m for m in result if m['职能'] == duty]
        if not group:
            continue
        candidates = [m for m in group if m['愿意负责']] or group
        year = min(m['入学年份'] for m in candidates)
        random.choice([m for m in candidates if m['入学年份'] == year])['职能负责'] = True
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

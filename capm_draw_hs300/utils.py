import numpy as np


'''纯多策略'''
def forward_chunduo(hs300, spearman, threshold):
    state = -1
    change_state = 0
    weeknum = 0
    idx0 = 0
    idx1 = 0
    money = 1000000
    idxs = []
    add_times = 0
    sub_times = 0
    num = 0
    record_money = []
    record = [money]
    for i in range(0,len(spearman)):
        record_money.append(money)
        if state == -1:
            if spearman[i] >= threshold:
                idx0 = i #记录买点
                change_state=1 #改变仓位信号
                num = money//(100*hs300[idx0])*100 #记录买卖股数
                cost = hs300[idx0]*num #记录买入金额
        if state == 1:
            if i == len(spearman) - 1:
                idx1 = i
                profit = hs300[i]*num #记录卖出金额
                money = money-cost+profit #记录当前金额
                money_last = record[-1]
                record.append(money)
                idxs.append([[idx0,i], [hs300[idx0],hs300[i]],[num],[money],[(money/money_last)- 1]]) #记录交易信息（买卖时间，买入价格，卖出价格,交易了多少股）
                if hs300[i] > hs300[idx0]:
                    add_times = add_times + 1
                else:
                    sub_times = sub_times + 1
                change_state=1
            if spearman[i] <= -threshold:
                idx1 = i
                profit = hs300[i]*num #记录卖出金额
                money = money-cost+profit #记录当前金额
                money_last = record[-1]
                record.append(money)
                idxs.append([[idx0,i], [hs300[idx0],hs300[i]],[num],[money],[(money/money_last)- 1]]) #记录交易信息（买卖时间，买入价格，卖出价格,交易了多少股）

                if hs300[i] > hs300[idx0]:
                    add_times = add_times + 1
                else:
                    sub_times = sub_times + 1
                change_state=1
            weeknum = weeknum + 1
        if change_state:
            change_state=0
            state = -state

    res = {}

    # print('最终金额', money)
    # print('年化收益率',(money/1000000)**(1/13)-1)
    # print('交易次数', len(idxs))
    # print('总交易次数/盈利/亏损', add_times+sub_times, add_times, sub_times)

    money_finale = money  # 最终金额
    res['money_finale'] = money_finale

    Rp = (money_finale / 1000000) ** (1 / (len(spearman)/52)) - 1
    res['Rp'] = Rp  # 年化收益率

    k = 4
    ratio = []
    for i in range(len(record_money) // k - 1):
        ratio.append(record_money[i*k+k] / record_money[i*k])
    flow = np.std(ratio)*(12**0.5)  # 年化波动率
    res['flow'] = flow

    sharp = Rp / flow  # 夏普比率
    res['sharp'] = sharp

    # res['record'] = record
    res['record_money'] = record_money

    res['add_times'] = add_times

    res['sub_times'] = sub_times

    res['record_idxs'] = idxs
    return res 


'''多空策略_hs300'''

def forward_duokong(hs300, spearman, threshold):

    # 模拟购买
    state = 0  # 0代表空仓，1代表有多单未平，-1代表有空单未平
    change_state = 0

    idx0 = 0
    idx1 = 0
    money = 1000000

    add_times = 0
    sub_times = 0

    record = []
    record_money = []
    num_duo = 0
    num_kong = 0

    for i in range(0, len(spearman)):
        record_money.append(money)
        if spearman[i] >= threshold:  # 看多信号
            if state == -1 or state == 0:  # 如果 有空单未平或者空仓
                idx0 = i  # 记录买点
                change_state = 1  # 改变仓位信号
                if num_kong == 0:
                    num_duo = money // (100 * hs300[idx0]) * 100  # 记录买卖股数
                else:
                    money = money - num_kong * hs300[idx0] + num_kong * hs300[idx1]  # 平空单后的金额
                    if hs300[idx0] < hs300[idx1]:
                        record.append([[money], [idx1, idx0], [hs300[idx1], hs300[idx0]], ['平空胜，做多']])
                        add_times = add_times + 1
                    else:
                        record.append([[money], [idx1, idx0], [hs300[idx1], hs300[idx0]], ['平空负，做多']])
                        sub_times = sub_times + 1
                    num_kong = 0
                    num_duo = money // (100 * hs300[idx0]) * 100  # 看多买入股数

                if change_state == 1 and state == 0:  # 改变信号 且空仓  改为多单信号
                    change_state = 0
                    state = 1
                elif change_state == -1 and state == 0:  # 改变信号 且空仓  改为空单信号
                    change_state = 0
                    state = -1
                else:
                    change_state = 0  # 改变信号 多变空 空变多
                    state = -state

        if spearman[i] <= -threshold:
            if state == 1 or state == 0:  # 如果有多单未平或空仓
                idx1 = i
                change_state = -1  # 改变仓位信号
                if num_duo == 0:
                    num_kong = money // (100 * hs300[idx1]) * 100  # 记录买卖股数

                else:
                    money = money + num_duo * hs300[idx1] - num_duo * hs300[idx0]  # 平多单后的金额
                    if hs300[idx0] < hs300[idx1]:
                        record.append([[money], [idx0, idx1], [hs300[idx0], hs300[idx1]], ['平多胜，做空']])
                        add_times = add_times + 1
                    else:
                        record.append([[money], [idx0, idx1], [hs300[idx0], hs300[idx1]], ['平多负，做空']])
                        sub_times = sub_times + 1
                    num_duo = 0
                    num_kong = money // (100 * hs300[idx0]) * 100  # 看空借入股数

                if change_state == 1 and state == 0:  # 改变信号 且空仓  改为多单信号
                    change_state = 0
                    state = 1
                elif change_state == -1 and state == 0:  # 改变信号 且空仓  改为空单信号
                    change_state = 0
                    state = -1
                else:
                    change_state = 0  # 改变信号 多变空 空变多
                    state = -state
        if i == len(spearman) - 1:
            if state == 1:
                money = money + hs300[i] * num_duo
            else:
                money = money + hs300[i] * num_kong

    res = {}
    
    money_finale = record[-1][0][0]  # 最终金额
    res['money_finale'] = money_finale

    Rp = (record[-1][0][0] / 1000000) ** (1 / (len(spearman)/52)) - 1
    res['Rp'] = Rp  # 年化收益率

    k = 4
    ratio = []
    for i in range(len(record_money) // k - 1):
        ratio.append(record_money[i*k+k] / record_money[i*k])
    flow = np.std(ratio)*(12**0.5)  # 年化波动率
    res['flow'] = flow

    sharp = Rp / flow  # 夏普比率
    res['sharp'] = sharp

    res['record'] = record
    res['record_money'] = record_money
    res['add_times'] = add_times

    res['sub_times'] = sub_times

    return res
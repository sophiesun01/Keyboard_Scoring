import csv
import pathlib

import numpy as np
import pandas as pd
import statistics as st
import matplotlib.pyplot as plt
from scipy.stats import norm


def calc_average(folder_name, missing, mis_loc):
    num_att = 25
    con_sum = 0.0
    dis_sum = 0.0
    averages = []
    csv_file = "keyboard.csv"
    csv_path = pathlib.Path.cwd() / 'data_sbl' / folder_name / csv_file
    f = open(csv_path)
    csv_f = csv.reader(f)
    count = 0
    for row in csv_f:
        count += 1
        if row[0] == 'type' or count == 104:
            if con_sum != 0.0:
                if count <= 30:
                    averages.append(con_sum / (num_att-missing[0]))
                else:
                    averages.append(con_sum / (num_att-missing[2]))
            elif dis_sum != 0.0:
                if count <= 60:
                    averages.append(dis_sum / (num_att-missing[1]))
                else:
                    averages.append(dis_sum / (num_att-missing[3]))
            con_sum = 0.0
            dis_sum = 0.0
        elif count in mis_loc:
            continue
        elif row[0] == 'concordant':
            con_sum = con_sum + float(row[3]) * 1000
        elif row[0] == 'discordant':
            dis_sum = dis_sum + float(row[3]) * 1000
    f.close()
    return averages

#print(calc_average("20210723-111524_default_green-frog"))

def calc_error(folder_name):
    csv_file = "keyboard.csv"
    csv_path = pathlib.Path.cwd() / 'data_sbl' / folder_name / csv_file
    f = open(csv_path)
    error = 0.0
    errors = {}
    count = 0
    csv_f = csv.reader(f)
    cols = ['green', 'yellow', "red"]
    keys = ['left', 'down', 'right']
    missing = [0]*4
    mis_loc = []

    for row in csv_f:
        response = row[1]
        if response == "left":
            if row[4] == "green":
                count += 1
                continue
            else:
                errors[count] = [row[1], row[4]]
                error += 1
                count += 1
        elif response == "up" or response == "down":
            if row[4] == "yellow":
                count += 1
                continue
            else:
                errors[count] = [row[1], row[4]]
                error += 1
                count += 1
        elif response == "right":
            if row[4] == "red":
                count += 1
                continue
            else:
                errors[count] = [row[1], row[4]]
                error += 1
                count += 1
        elif response == "none":
            if 0 < count <= 21:
                missing[0] += 1
            elif 21 < count <= 42:
                missing[1] += 1
            elif 42 < count <= 63:
                missing[2] += 1
            elif 63 < count <= 104:
                missing[3] += 1
            mis_loc.append(count)
            count += 1
    f.close()
    return errors, missing, mis_loc
#print(calc_error("20210721-130946_default_red-fish"))

def keyboard_interference(folder_name):
    error, missing, mis_loc = calc_error(folder_name)
    average = calc_average(folder_name, missing, mis_loc)
    con_1 = 0
    dis_1 = 0
    con_2 = 0
    dis_2 = 0
    for i in error.keys():
        # score 1
        if i < 50:
            if i < 25:
                con_1 += 1
            else:
                dis_1 += 1
        # score 2
        elif 50 <= i <100:
            if i < 75:
                con_2 += 1
            else:
                dis_2 += 1
    score_1_con = average[0] + (con_1 * 2 * average[0]/(100-missing[0]))
    score_1_dis = average[1] + (dis_1 * 2 * average[1]/(100-missing[1]))
    score_2_con = average[2] + (con_2 * 2 * average[2] /(100-missing[2]))
    score_2_dis = average[3] + (dis_2 * 2 * average[3]/(100-missing[3]))
    return [score_1_con, con_1, missing[0], score_1_dis, dis_1, missing[1], score_2_con, con_2, missing[2], score_2_dis, dis_2, missing[3]]
    # return [average[0], con_1, missing[0], average[1], dis_1, missing[1], average[2], con_2, missing[2], average[3],
    #         dis_2, missing[3]]


files = [
"20210615-140808_default_yellow_shark",
"20210705-204204_default_Blue-Dolphin",
"20210706-183817_default_Pink-Lion",
"20210714-222856_default_Purple-Bear",
"20210729-131241_default_orange-crocodile",
"20210729-140708_default_pink-flamingo",
"20210730-122020_default_gold-dog",
# "20210716-122310_default_orange-crocodile",
"20210721-130946_default_red-fish",
"20210723-103705_default_black-goose",
"20210723-111524_default_green-frog",
"20210726-105905_default_navy-giraffe",
"20210726-121112_default_red-moose",
"20210726-123246_default_blue-lion",
"20210726-131049_default_blue-dog",
"20210727-125315_default_blue-jay",
"20210727-132652_default_pink-sealion"]

scores = []

for n in files:
    score = [n[24:]]
    score.extend(keyboard_interference(n))
    scores.append(score)

df = pd.DataFrame(scores, columns=["Filename", "First Session: Concordant - Score", "First Session: Concordant - Num of Errors", "First Session: Concordant - Missed", "First Session: Discordant - Score", "First Session: Discordant - Num of Errors", "First Session: Discordant - Missed", "Second Session: Concordant - Score", "Second Session: Concordant - Num of Errors", "Second Session: Concordant - Missed", "Second Session: Discordant - Score", "Second Session: Discordant - Num of Errors", "Second Session: Discordant - Missed"])
#df.to_csv("keyboard_scores.csv", mode="w", index=False)

mean_first_conc = st.mean(df["First Session: Concordant - Score"])
sd_first_conc = st.stdev(df["First Session: Concordant - Score"])

sort_first_conc = np.sort(df["First Session: Concordant - Score"])
norm_first_conc = norm.pdf(sort_first_conc, mean_first_conc , sd_first_conc )
plt.plot(sort_first_conc, norm_first_conc)
plt.fill_between(sort_first_conc, norm_first_conc, where=(sort_first_conc>=(mean_first_conc-sd_first_conc)) & (sort_first_conc<=(mean_first_conc+sd_first_conc)), color="blue", alpha=0.3)
#
mean_first_dis = st.mean(df["First Session: Discordant - Score"])
sd_first_dis = st.stdev(df["First Session: Discordant - Score"])

sort_first_dis = np.sort(df["First Session: Discordant - Score"])
norm_first_dis = norm.pdf(sort_first_dis, mean_first_dis, sd_first_dis)
plt.plot(sort_first_dis, norm_first_dis)
plt.fill_between(sort_first_dis, norm_first_dis, where=(sort_first_dis>=(mean_first_dis-sd_first_dis)) & (sort_first_dis<=(mean_first_dis+sd_first_dis)), color="orange", alpha=0.3)
#
mean_second_conc = st.mean(df["Second Session: Concordant - Score"])
sd_second_conc = st.stdev(df["Second Session: Concordant - Score"])

sort_second_conc = np.sort(df["Second Session: Concordant - Score"])
norm_second_conc = norm.pdf(sort_second_conc, mean_second_conc, sd_second_conc)
plt.plot(sort_second_conc, norm_second_conc)
plt.fill_between(sort_second_conc, norm_second_conc, where=(sort_second_conc>=(mean_second_conc-sd_second_conc)) & (sort_second_conc<=(mean_second_conc+sd_second_conc)), color="green", alpha=0.3)
#
mean_second_dis = st.mean(df["Second Session: Discordant - Score"])
sd_second_dis = st.stdev(df["Second Session: Discordant - Score"])

sort_second_dis = np.sort(df["Second Session: Discordant - Score"])
norm_second_dis = norm.pdf(sort_second_dis, mean_second_dis, sd_second_dis)
plt.plot(sort_second_dis, norm_second_dis)
plt.fill_between(sort_second_dis, norm_second_dis, where=(sort_second_dis >= (mean_second_dis-sd_second_dis)) & (sort_second_dis<=(mean_second_dis+sd_second_dis)), color="red", alpha=0.3)


plt.legend(["First Session: Concordant", "First Session: Discordant", "Second Session: Concordant", "Second Session: Discordant"])
plt.title("Stroop Test: Interference Score Distribution", fontsize=24)
plt.xlabel("Interference Score", fontsize=16)
plt.ylabel("Probability", fontsize=16)
means = [mean_first_conc, mean_first_dis, mean_second_conc, mean_second_dis]
norms = [norm_first_conc, norm_first_dis, norm_second_conc, norm_second_dis]
col = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
for i in range(len(means)):
    y_end = norms[i][len(norms)//2+3]
    plt.plot((means[i], means[i]), (0, y_end), col[i])
    # plt.axvline(x=means[i], ymin=0, ymax=0.5)
plt.show()

##STROOP INDIVIDUAL STATISTICS
fig, (ax_0, ax_1, ax_2) = plt.subplots(3, 1, sharex='all')
fig.tight_layout()
ax_0.plot(df["Filename"], df[["First Session: Concordant - Score", "First Session: Discordant - Score", "Second Session: Concordant - Score", "Second Session: Discordant - Score"]], marker='o', linestyle="--")
ax_0.set_title("Stroop Test Interference Score")
ax_0.set_ylabel("Interference Score")
ax_1.plot(df["Filename"], df[["First Session: Concordant - Num of Errors", "First Session: Discordant - Num of Errors", "Second Session: Concordant - Num of Errors", "Second Session: Discordant - Num of Errors"]], marker='o', linestyle="--")
ax_1.set_title("Stroop Test Number of Errors")
ax_1.set_ylabel("Num of Errors")
ax_2.plot(df["Filename"], df[["First Session: Concordant - Missed", "First Session: Discordant - Missed", "Second Session: Concordant - Missed", "Second Session: Discordant - Missed"]], marker='o', linestyle="--")
ax_2.set_title("Stroop Test Number of Missed")
ax_2.set_ylabel("Num of Missed")
plt.legend(["First Session: Concordant", "First Session: Discordant", "Second Session: Concordant", "Second Session: Discordant"], bbox_to_anchor=(1.25, 3))
plt.xlabel("Test Subjects")
plt.xticks(rotation=45)
plt.show()







#[["First Session: Concordant - Score", "First Session: Discordant - Score", "Second Session: Concordant - Score", "Second Session: Discordant - Score"]]
# plt.title("Stroop Test Interference Score")
# plt.legend(["First Session: Concordant", "First Session: Discordant", "Second Session: Concordant", "Second Session: Discordant"])
# plt.ylim(bottom=0)
# plt.show()
# plt.title("Stroop Test Number of Errors")
# plt.plot(df["Filename"], df[["First Session: Concordant - Num of Errors", "First Session: Discordant - Num of Errors", "Second Session: Concordant - Num of Errors", "Second Session: Discordant - Num of Errors"]], marker='o', linestyle="--")
# plt.legend(["First Session: Concordant", "First Session: Discordant", "Second Session: Concordant", "Second Session: Discordant"])
# plt.ylim(bottom=0)
# plt.show()
# plt.title("Stroop Test Number of Missed")
# plt.plot(df["Filename"], df[["First Session: Concordant - Missed", "First Session: Discordant - Missed", "Second Session: Concordant - Missed", "Second Session: Discordant - Missed"]], marker='o', linestyle="--")
# plt.legend(["First Session: Concordant", "First Session: Discordant", "Second Session: Concordant", "Second Session: Discordant"])
# plt.ylim(bottom=0)
# plt.show()


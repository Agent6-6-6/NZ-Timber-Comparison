# file to look at fundamental differences between NZS3604 and non-SED design
import matplotlib.pyplot as plt
import numpy as np

timber_ref = ['SG8', 'LVL8', 'LVL11', 'LVL13', 'LVL16']  # , 'GL8', 'GL10', 'GL12']
timber_type = ['SG', 'LVL', 'LVL', 'LVL', 'LVL']  # , 'GL', 'GL', 'GL']
modulus = [8000, 8000, 11000, 13200, 16000]  # , 8000, 10000, 11500]
axial_strength = [18, 30, 32, 38, 45]  # , 19, 22, 25]

moisture = 'dry'
phi_sg = 0.8
phi_lvl = 0.9
d = 90
b = 45
k_1_nzs3603 = 0.8
k_1_as1720 = 0.8


def k_8_nzs3603(slenderness, moisture='dry'):
    if moisture.lower() == 'dry':
        a = [0, 0.21, 0.175, -0.0116, 1 / 5000, 235.5, -1.937]
    elif moisture.lower() == 'green':
        a = [0, 0.45, 0.1237, -0.0082, 1 / 7500, 251.4, -1.933]
    else:
        print(f'moisture should be dry or green, {moisture} provided')

    k_8 = []
    i = 0
    for S in slenderness:
        if S <= 10:
            k_8.append(1.0)
        elif S <= 25:
            k_8.append(a[1] + a[2] * S + a[3] * S**2 + a[4] * S**3)
        else:
            k_8.append(a[5] * S ** a[6])
        i += 1
    return k_8


def k_12_as1720(slenderness, E, f_b, r=0.25, moisture='dry'):
    k_12 = []
    i = 0
    rho = rho_c(E, f_b, r, moisture)
    for S in slenderness:
        if rho * S <= 10:
            k_12.append(1.0)
        elif rho * S <= 20:
            k_12.append(1.5 - 0.05 * rho * S)
        else:
            k_12.append(200 / (rho * S) ** 2)
        i += 1
    return k_12


def rho_b(E, f_b, r=0.25, moisture='dry'):
    if moisture.lower() == 'dry':
        rho_b = 14.71 * (E / f_b) ** -0.480 * r**-0.061
    elif moisture.lower() == 'green':
        rho_b = 11.63 * (E / f_b) ** -0.435 * r**-0.110
    else:
        print(f'moisture should be dry or green, {moisture} provided')
    return rho_b


def rho_c(E, f_b, r=0.25, moisture='dry'):
    if moisture.lower() == 'dry':
        rho_c = 11.39 * (E / f_b) ** -0.408 * r**-0.074
    elif moisture.lower() == 'green':
        rho_c = 9.29 * (E / f_b) ** -0.367 * r**-0.146
    else:
        print(f'moisture should be dry or green, {moisture} provided')
    return rho_c


label_offset = 35
division = 0.01
S = np.arange(0, 100, division)

# Determine equivalent length for given slenderness for NZS3604 and NZS3603
L_3604 = S * d / 0.75
L_3603 = S * d / 0.9

plt.xkcd(scale=0.3, length=100, randomness=10)

phi_Ncx_1 = []
result_nz = []
result_as = []
result_ratio = []
label_loc = int(14 / division)

plt.figure(1)
# subplot 1
plt.subplot(131)
plt.ylabel('Compression Capacity ($kN$)')
plt.xlabel('Slenderness')
plt.title(f'{d}x{b} - SLENDERNESS VS COMPRESSION CAPACITY')
for i in range(len(timber_ref)):
    # modulus and axial_strength:
    phi_Ncx_nz = []
    phi_Ncx_as = []
    E = modulus[i]
    f_c = axial_strength[i]
    if timber_type[i].upper() in ['SG', 'GL']:
        phi = phi_sg
    elif timber_type[i].upper() in ['LVL']:
        phi = phi_lvl
    k_8 = k_8_nzs3603(S, moisture)
    k_12 = k_12_as1720(S, E, f_c, 0.25, moisture)
    for k in k_8:
        phi_Ncx_nz.append(phi * k_1_nzs3603 * b * d * k * f_c / 1000)
    for k in k_12:
        phi_Ncx_as.append(phi * k_1_as1720 * b * d * k * f_c / 1000)

    plt.annotate(
        text=f'{timber_ref[i]} NZ3603',
        xy=(S[label_loc], phi_Ncx_nz[label_loc]),
        xytext=(S[label_loc] + label_offset, phi_Ncx_nz[label_loc]),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3'),
        ha='left',
        color='green',
    )
    plt.annotate(
        text=f'{timber_ref[i]} NZS/AS1720.1',
        xy=(S[label_loc], phi_Ncx_as[label_loc]),
        xytext=(S[label_loc] + label_offset, phi_Ncx_as[label_loc]),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3'),
        ha='left',
        color='red',
    )
    plt.plot(S, phi_Ncx_nz, label=f'$\phi N_c$$_x$ {timber_ref[i]} NZ3603', color='green')
    plt.plot(S, phi_Ncx_as, label=f'$\phi N_c$$_x$ {timber_ref[i]} NZS/AS1720.1', color='red')

    result_nz.append(phi_Ncx_nz)
    result_as.append(phi_Ncx_as)
plt.legend(fontsize='x-small')

# subplot 2
plt.figure(2)
plt.subplot(131)
plt.xlabel('Slenderness')
plt.ylabel('Ratio between NZS/AS1720.1 to NZS3603 Compression Capacity')
plt.title(f'{d}x{b} - SLENDERNESS VS NZS1720.1 TO NZS3603 COMPRESSION CAPACITY RATIO')
plt.ylim((0, 1.05))
prev = 1
for i in range(len(result_nz)):
    result_ratio = []

    for n in range(len(result_nz[i])):
        result_ratio.append(result_as[i][n] / result_nz[i][n])

    # code to avoid placing annotation labels on top of one another
    y_pos = result_ratio[int(40 / division)] + 0.05
    if i == 0:
        prev = max(result_ratio)
    if i > 0:
        while abs(y_pos - prev) < 0.025:
            y_pos = y_pos + 0.001  # 0.025
        prev = y_pos
    plt.annotate(
        text=f'{timber_ref[i]}',
        xy=(40, result_ratio[int(40 / division)]),
        xytext=(60, y_pos),
        arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=0.2'),
        ha='center',
    )
    plt.plot(S, result_ratio, label=f'Ratio {timber_ref[i]}', color='orange')

plt.legend(fontsize='x-small')

# subplot 3
plt.figure(1)
# plt.figure(figsize=(3840 / 3 / my_dpi, 2160 / my_dpi), dpi=my_dpi)
plt.subplot(133)
plt.xlabel('$L_{ax}$ - Member length between restraints about major axis')
plt.ylabel('Compression Capacity ($kN$}')
plt.title(f'{d}x{b} - MEMBER LENGTH VS COMPRESSION CAPACITY')
plt.xlim((-100, 5100))
for i in range(len(result_nz)):
    plt.annotate(
        text=f'{timber_ref[i]}',
        xy=(250, result_nz[i][250]),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3'),
        va='center',
    )
    plt.plot(L_3603, result_nz[i], label=f'$\phi N_c$$_x$ {timber_ref[i]} NZ3603', color='green')
    plt.plot(L_3604, result_nz[i], label=f'$\phi N_c$$_x$ {timber_ref[i]} NZS3604', color='orange')
    plt.plot(L_3603, result_as[i], label=f'$\phi N_c$$_x$ {timber_ref[i]} NZS/AS1720.1', color='red')

plt.legend(fontsize='x-small')

# figure to show ratios
plt.figure(2)

# subplot 2
plt.subplot(133)
plt.xlabel('$L_{ax}$ - Member length between restraints about major axis')
plt.ylabel('Ratio between NZS/AS1720.1 & NZS3604 Compression Capacity')
plt.title(f'{d}x{b} - MEMBER LENGTH VS NZS/AS1720.1 TO NZS3604 COMPRESSION CAPACITY RATIO')
plt.ylim((0, 1.05))
L = np.arange(0, 5000, 5)
label_loc = 1500
for i in range(len(timber_ref)):
    # modulus and axial_strength:
    phi_Ncx_nz = []
    phi_Ncx_as = []
    S_nzs3604 = []
    S_as1720 = []
    E = modulus[i]
    f_c = axial_strength[i]
    if timber_type[i].upper() in ['SG', 'GL']:
        phi = phi_sg
    elif timber_type[i].upper() in ['LVL']:
        phi = phi_lvl

    # convert member length to slenderness
    for n in L:
        S_nzs3604.append(0.75 * n / d)
        S_as1720.append(0.9 * n / d)

    k_8 = k_8_nzs3603(S_nzs3604, moisture)
    k_12 = k_12_as1720(S_as1720, E, f_c, 0.25, moisture)
    for k in k_8:
        phi_Ncx_nz.append(phi * k_1_nzs3603 * b * d * k * f_c / 1000)
    for k in k_12:
        phi_Ncx_as.append(phi * k_1_as1720 * b * d * k * f_c / 1000)
    result_ratio = []
    for j in range(len(phi_Ncx_as)):
        # for n in range(len(result_nz[j])):
        result_ratio.append(phi_Ncx_as[j] / phi_Ncx_nz[j])

    # code to avoid placing annotation labels on top of one another
    y_pos = result_ratio[int(3000 / 5000 * 1000)] + 0.1
    if i == 0:
        prev = max(result_ratio)

    if i > 0:
        while abs(y_pos - prev) < 0.025:
            y_pos = y_pos + 0.01
        prev = y_pos
    plt.annotate(
        text=f'{timber_ref[i]}',
        xy=(3000, result_ratio[int(3000 / 5000 * 1000)]),
        xytext=(4000, y_pos),
        arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=0.2'),
        va='center',
    )
    plt.plot(L, result_ratio, label=f'RATIO {timber_ref[i]}', color='orange')

plt.legend(fontsize='x-small')
plt.show()

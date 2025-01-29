from datetime import date

MAX_YEAR = date.today().year + 1

# these are the acceptable ranges for answers from the master codebook
RANGE_LIST = {
    'g1_01d': list(range(1, 31 + 1)) + [99],
    'g1_01m': list(range(1, 12 + 1)) + [99],
    'g1_01y': list(range(1900, MAX_YEAR)) + [9999],
    'g1_05': [1, 2, 8, 9],
    'g1_06d': list(range(1, 31 + 1)) + [99],
    'g1_06m': list(range(1, 12 + 1)) + [99],
    'g1_06y': list(range(1900, MAX_YEAR)) + [9999],
    'g1_07a': list(range(0, 120 + 1)) + [999],
    'g1_07b': list(range(0, 12 + 1)) + [99],
    'g1_07c': list(range(0, 31 + 1)) + [99],
    'g1_08': [1, 2, 3, 4, 5, 8, 9],
    'g1_09': [1, 2, 3, 4, 9],
    'g1_10': list(range(0, 99 + 1)),
    'g2_03ad': list(range(1, 31 + 1)) + [99],
    'g2_03am': list(range(1, 12 + 1)) + [99],
    'g2_03ay': list(range(1900, MAX_YEAR)) + [9999],
    'g2_03bd': list(range(1, 31 + 1)) + [99],
    'g2_03bm': list(range(1, 12 + 1)) + [99],
    'g2_03by': list(range(1900, MAX_YEAR)) + [9999],
    'g2_03cd': list(range(1, 31 + 1)) + [99],
    'g2_03cm': list(range(1, 12 + 1)) + [99],
    'g2_03cy': list(range(1900, MAX_YEAR)) + [9999],
    'g2_03dd': list(range(1, 31 + 1)) + [99],
    'g2_03dm': list(range(1, 12 + 1)) + [99],
    'g2_03dy': list(range(1900, MAX_YEAR)) + [9999],
    'g2_03ed': list(range(1, 31 + 1)) + [99],
    'g2_03em': list(range(1, 12 + 1)) + [99],
    'g2_03ey': list(range(1900, MAX_YEAR)) + [9999],
    'g2_03fd': list(range(1, 31 + 1)) + [99],
    'g2_03fm': list(range(1, 12 + 1)) + [99],
    'g2_03fy': list(range(1900, MAX_YEAR)) + [9999],
    'g3_01': [0, 1, 8, 9],
    'g4_02': [1, 2, 8, 9],
    'g4_03a': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 99],
    'g4_05': [1, 2, 3, 4, 9],
    'g4_08': [0, 1, 8, 9],
    'g5_01d': list(range(1, 31 + 1)) + [99],
    'g5_01m': list(range(1, 12 + 1)) + [99],
    'g5_01y': list(range(1900, MAX_YEAR)) + [999, 9999],
    'g5_02': [1, 2, 8, 9],
    'g5_03d': list(range(1, 31 + 1)) + [99],
    'g5_03m': list(range(1, 12 + 1)) + [99],
    'g5_03y': list(range(1900, MAX_YEAR)) + [999, 9999],
    'g5_04a': list(range(0, 120 + 1)),
    'g5_04b': list(range(0, 12 + 1)),
    'g5_04c': list(range(0, 31 + 1)),
    'g5_05': [1, 2, 3, 4, 5, 8, 9],
    'g5_06a': [1, 2, 3, 4, 9],
    'g5_06b': list(range(0, 99 + 1)),
    'g5_07': [0, 1, 8, 9],
    'a1_01_1': [0, 1, 8, 9],
    'a1_01_2': [0, 1, 8, 9],
    'a1_01_3': [0, 1, 8, 9],
    'a1_01_4': [0, 1, 8, 9],
    'a1_01_5': [0, 1, 8, 9],
    'a1_01_6': [0, 1, 8, 9],
    'a1_01_7': [0, 1, 8, 9],
    'a1_01_8': [0, 1, 8, 9],
    'a1_01_9': [0, 1, 8, 9],
    'a1_01_10': [0, 1, 8, 9],
    'a1_01_11': [0, 1, 8, 9],
    'a1_01_12': [0, 1, 8, 9],
    'a1_01_13': [0, 1, 8, 9],
    'a1_01_14': [0, 1, 8, 9],
    'a2_01a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_02': [0, 1, 8, 9],
    'a2_03a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_04': [1, 2, 3, 8, 9],
    'a2_05': [1, 2, 3, 8, 9],
    'a2_06': [0, 1, 8, 9],
    'a2_07': [0, 1, 8, 9],
    'a2_08a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_09_1a': [1, 2, 3, 4, 5, 8, 9],
    'a2_09_2a': [0, 1, 2, 3, 4, 5, 8, 9],
    'a2_10': [0, 1, 8, 9],
    'a2_11': [0, 1, 8, 9],
    'a2_12': [0, 1, 8, 9],
    'a2_13': [0, 1, 8, 9],
    'a2_14': [0, 1, 8, 9],
    'a2_15a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_16': [0, 1, 8, 9],
    'a2_17': [0, 1, 8, 9],
    'a2_18': [0, 1, 8, 9],
    'a2_19': [1, 2, 3, 8, 9],
    'a2_20': [0, 1, 8, 9],
    'a2_21': [0, 1, 8, 9],
    'a2_22a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_23': [0, 1, 8, 9],
    'a2_24a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_25': [0, 1, 8, 9],
    'a2_26a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_27': [0, 1, 8, 9],
    'a2_28a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_29': [0, 1, 8, 9],
    'a2_30': [0, 1, 8, 9],
    'a2_31': [0, 1, 8, 9],
    'a2_32': [0, 1, 8, 9],
    'a2_33a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_34': [0, 1, 8, 9],
    'a2_35': [0, 1, 8, 9],
    'a2_36': [0, 1, 8, 9],
    'a2_37a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_38': [1, 2, 8, 9],
    'a2_39_1': [1, 2, 3, 4, 8, 9],
    'a2_39_2': [1, 2, 3, 4, 8, 9],
    'a2_40': [0, 1, 8, 9],
    'a2_41a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_42': [0, 1, 8, 9],
    'a2_43': [0, 1, 8, 9],
    'a2_44': [1, 2, 3, 8, 9],
    'a2_45': [0, 1, 8, 9],
    'a2_46a': [1, 2, 3, 4, 8, 9],
    'a2_47': [0, 1, 8, 9],
    'a2_48a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_49': [0, 1, 8, 9],
    'a2_50': [0, 1, 8, 9],
    'a2_51': [0, 1, 8, 9],
    'a2_52': [0, 1, 8, 9],
    'a2_53': [0, 1, 8, 9],
    'a2_54a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_55': [0, 1, 8, 9],
    'a2_56': [0, 1, 8, 9],
    'a2_57': [0, 1, 8, 9],
    'a2_58a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_59': [1, 2, 3, 8, 9],
    'a2_60': [0, 1, 8, 9],
    'a2_61': [0, 1, 8, 9],
    'a2_62a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_63_1': [1, 2, 8, 9],
    'a2_63_2': [1, 2, 8, 9],
    'a2_64': [0, 1, 8, 9],
    'a2_65a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_66': [1, 2, 8, 9],
    'a2_67': [0, 1, 8, 9],
    'a2_68a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_69': [0, 1, 8, 9],
    'a2_70a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_71': [1, 2, 8, 9],
    'a2_72': [0, 1, 8, 9],
    'a2_73a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_74': [0, 1, 8, 9],
    'a2_75': [1, 2, 8, 9],
    'a2_76a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_77': [0, 1, 8, 9],
    'a2_78': [0, 1, 8, 9],
    'a2_79a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_80': [1, 2, 8, 9],
    'a2_81': [0, 1, 8, 9],
    'a2_82': [0, 1, 8, 9],
    'a2_83a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_84': [0, 1, 8, 9],
    'a2_85': [0, 1, 8, 9],
    'a2_86a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a2_87_1': [0, 1, 8, 9],
    'a2_87_2': [0, 1, 8, 9],
    'a2_87_3': [0, 1, 8, 9],
    'a2_87_4': [0, 1, 8, 9],
    'a2_87_5': [0, 1, 8, 9],
    'a2_87_6': [0, 1, 8, 9],
    'a2_87_7': [0, 1, 8, 9],
    'a2_87_8': [0, 1, 8, 9],
    'a2_87_9': [0, 1, 8, 9],
    'a2_87_10a': [0, 1, 8, 9],
    'a3_01': [0, 1, 8, 9],
    'a3_02': [0, 1, 8, 9],
    'a3_03': [0, 1, 8, 9],
    'a3_04': [0, 1, 8, 9],
    'a3_05': [0, 1, 8, 9],
    'a3_06': [0, 1, 8, 9],
    'a3_07': [0, 1, 8, 9],
    'a3_08a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a3_09': [0, 1, 8, 9],
    'a3_10': [0, 1, 8, 9],
    'a3_11a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a3_12': [0, 1, 8, 9],
    'a3_13': [0, 1, 8, 9],
    'a3_14': [0, 1, 8, 9],
    'a3_15': [0, 1, 8, 9],
    'a3_16a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a3_17': [0, 1, 8, 9],
    'a3_18': [0, 1, 8, 9],
    'a3_19': [0, 1, 8, 9],
    'a3_20': [0, 1, 8, 9],
    'a4_01': [0, 1, 8, 9],
    'a4_02_1': [0, 1, 8, 9],
    'a4_02_2': [0, 1, 8, 9],
    'a4_02_3': [0, 1, 8, 9],
    'a4_02_4': [0, 1, 8, 9],
    'a4_02_5a': [0, 1, 8, 9],
    'a4_02_6': [0, 1, 8, 9],
    'a4_02_7': [0, 1, 8, 9],
    'a4_05': [0, 1, 8, 9],
    'a4_06': [1, 2, 3, 8, 9],
    'a5_01_1': [0, 1, 8, 9],
    'a5_01_2': [0, 1, 8, 9],
    'a5_01_3': [0, 1, 8, 9],
    'a5_01_4': [0, 1, 8, 9],
    'a5_01_5': [0, 1, 8, 9],
    'a5_01_6': [0, 1, 8, 9],
    'a5_01_7': [0, 1, 8, 9],
    'a5_01_8': [0, 1, 8, 9],
    'a5_01_9a': [0, 1, 8, 9],
    'a5_02': [0, 1, 8, 9],
    'a5_03': [0, 1, 8, 9],
    'a5_04a': [1, 2, 3, 4, 5, 6, 8, 9],
    'a6_01': [0, 1, 8, 9],
    'a6_02_1': [0, 1, 8, 9],
    'a6_02_2': [0, 1, 8, 9],
    'a6_02_3': [0, 1, 8, 9],
    'a6_02_4': [0, 1, 8, 9],
    'a6_02_5': [0, 1, 8, 9],
    'a6_02_6': [0, 1, 8, 9],
    'a6_02_7': [0, 1, 8, 9],
    'a6_02_8': [0, 1, 8, 9],
    'a6_02_9': [0, 1, 8, 9],
    'a6_02_10': [0, 1, 8, 9],
    'a6_02_11': [0, 1, 8, 9],
    'a6_02_12a': [0, 1, 8, 9],
    'a6_02_13': [0, 1, 8, 9],
    'a6_02_14': [0, 1, 8, 9],
    'a6_02_15': [0, 1, 8, 9],
    'a6_04': [0, 1, 8, 9],
    'a6_05': [0, 1, 8, 9],
    'a6_06_1d': list(range(1, 31 + 1)) + [99],
    'a6_06_1m': list(range(1, 12 + 1)) + [99],
    'a6_06_1y': list(range(1900, MAX_YEAR)) + [9999],
    'a6_06_2d ': list(range(1, 31 + 1)) + [99],
    'a6_06_2m': list(range(1, 12 + 1)) + [99],
    'a6_06_2y': list(range(1900, MAX_YEAR)) + [9999],
    'a6_07d': list(range(1, 31 + 1)) + [99],
    'a6_07m': list(range(1, 12 + 1)) + [99],
    'a6_07y': list(range(1900, MAX_YEAR)) + [9999],
    'a6_09': [0, 1, 8, 9],
    'a6_10': [0, 1, 8, 9],
    'c1_01': [1, 2, 8, 9],
    'c1_02': [1, 2, 3, 8, 9],
    'c1_03': [0, 1, 8, 9],
    'c1_04': [1, 2, 8, 9],
    'c1_05a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c1_06a': [1, 2, 3, 4, 5, 8, 9],
    'c1_07': [1, 2, 3, 4, 8, 9],
    'c1_08a': [1, 2, 8, 9],
    'c1_09': [1, 2, 8, 9],
    'c1_10': [1, 8, 9],
    'c1_10d': list(range(1, 31 + 1)) + [99],
    'c1_10m': list(range(1, 12 + 1)) + [99],
    'c1_10y': list(range(1900, MAX_YEAR)) + [9999],
    'c1_11': [1, 2, 8, 9],
    'c1_12': [0, 1, 8, 9],
    'c1_13': [0, 1, 8, 9],
    'c1_14': [0, 1, 8, 9],
    'c1_15': [0, 1, 8, 9],
    'c1_16': [0, 1, 8, 9],
    'c1_17': [0, 1, 8, 9],
    'c1_18': [0, 1, 8, 9],
    'c1_19_1': [0, 1, 8, 9],
    'c1_19_2': [0, 1, 8, 9],
    'c1_19_3': [0, 1, 8, 9],
    'c1_19_4a': [0, 1, 8, 9],
    'c1_19_5': [0, 1, 8, 9],
    'c1_19_6': [0, 1, 8, 9],
    'c1_20a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c1_21a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c1_22a': [1, 2, 3, 4, 5, 8, 9],
    'c1_24': [1, 8, 9],
    'c1_24d': list(range(1, 31 + 1)) + [99],
    'c1_24m': list(range(1, 12 + 1)) + [99],
    'c1_24y': list(range(1900, MAX_YEAR)) + [9999],
    'c1_25a': [0, 1, 2, 3, 4, 5, 6, 8, 9],
    'c1_26': [0, 1, 2],
    'c2_01_1': [0, 1, 8, 9],
    'c2_01_2': [0, 1, 8, 9],
    'c2_01_3': [0, 1, 8, 9],
    'c2_01_4': [0, 1, 8, 9],
    'c2_01_5': [0, 1, 8, 9],
    'c2_01_6': [0, 1, 8, 9],
    'c2_01_7': [0, 1, 8, 9],
    'c2_01_8': [0, 1, 8, 9],
    'c2_01_9': [0, 1, 8, 9],
    'c2_01_10': [0, 1, 8, 9],
    'c2_01_11': [0, 1, 8, 9],
    'c2_01_12': [0, 1, 8, 9],
    'c2_01_14': [0, 1, 8, 9],
    'c2_02a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c2_03': [1, 2, 3, 8, 9],
    'c2_04': [0, 1, 8, 9],
    'c2_05a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c2_06': [1, 2, 8, 9],
    'c2_07': [1, 2, 8, 9],
    'c2_08a': [1, 2, 3, 8, 9],
    'c2_09': [0, 1, 8, 9],
    'c2_10a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c2_11': [0, 1, 8, 9],
    'c2_12': [1, 2, 3, 4, 5, 8, 9],
    'c2_13a': [1, 2, 3, 4, 5, 8, 9],
    'c2_15a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c2_17': [1, 2, 3, 4, 8, 9],
    'c2_18': [0, 1, 8, 9],
    'c3_01': [0, 1, 8, 9],
    'c3_02': [0, 1, 8, 9],
    'c3_03_1': [0, 1, 8, 9],
    'c3_03_2': [0, 1, 8, 9],
    'c3_03_3': [0, 1, 8, 9],
    'c3_03_4a': [0, 1, 8, 9],
    'c3_03_5': [0, 1, 8, 9],
    'c3_03_6': [0, 1, 8, 9],
    'c3_04': [0, 1, 8, 9],
    'c3_05': [0, 1, 8, 9],
    'c3_06': [0, 1, 8, 9],
    'c3_07': [0, 1, 8, 9],
    'c3_08': [1, 2, 3, 4, 8, 9],
    'c3_09': [0, 1, 8, 9],
    'c3_10': [1, 2, 8, 9],
    'c3_11': [0, 1, 8, 9],
    'c3_12': [0, 1, 8, 9],
    'c3_13': [0, 1, 8, 9],
    'c3_14a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_15': [1, 2, 8, 9],
    'c3_16': [0, 1, 8, 9],
    'c3_17': [0, 1, 8, 9],
    'c3_18a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_19a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_20': [0, 1, 8, 9],
    'c3_21a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_22a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_23': [0, 1, 8, 9],
    'c3_24': [0, 1, 8, 9],
    'c3_25': [0, 1, 8, 9],
    'c3_26': [0, 1, 8, 9],
    'c3_27a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_28a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_29': [0, 1, 8, 9],
    'c3_30a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_31a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c3_32': [0, 1, 8, 9],
    'c3_33': [0, 1, 8, 9],
    'c3_34': [0, 1, 8, 9],
    'c3_35': [0, 1, 8, 9],
    'c3_36': [0, 1, 8, 9],
    'c3_37': [0, 1, 8, 9],
    'c3_38': [0, 1, 8, 9],
    'c3_39': [0, 1, 8, 9],
    'c3_40': [0, 1, 8, 9],
    'c3_41': [0, 1, 8, 9],
    'c3_42': [0, 1, 8, 9],
    'c3_44': [0, 1, 8, 9],
    'c3_45a': [1, 8, 9],
    'c3_46': [0, 1, 8, 9],
    'c3_47': [0, 1, 8, 9],
    'c3_48': [0, 1, 8, 9],
    'c3_49': [0, 1, 8, 9],
    'c4_01': [0, 1, 8, 9],
    'c4_02a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_03': [0, 1, 8, 9],
    'c4_04': [1, 2, 3, 8, 9],
    'c4_05': [1, 2, 3, 8, 9],
    'c4_06': [0, 1, 8, 9],
    'c4_07a': [1, 8, 9],
    'c4_08a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_09': [0, 1, 8, 9],
    'c4_10a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_11': [0, 1, 8, 9],
    'c4_12': [0, 1, 8, 9],
    'c4_13a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_14': [0, 1, 8, 9],
    'c4_15': [0, 1, 8, 9],
    'c4_16': [0, 1, 8, 9],
    'c4_17a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_18': [0, 1, 8, 9],
    'c4_19a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_20': [0, 1, 8, 9],
    'c4_22': [0, 1, 8, 9],
    'c4_23': [0, 1, 8, 9],
    'c4_24': [0, 1, 8, 9],
    'c4_25': [0, 1, 8, 9],
    'c4_26': [0, 1, 8, 9],
    'c4_27': [1, 2, 3, 8, 9],
    'c4_28': [0, 1, 8, 9],
    'c4_29': [0, 1, 8, 9],
    'c4_30': [0, 1, 8, 9],
    'c4_31_1': [1, 2, 3, 4, 5, 8, 9],
    'c4_31_2': [1, 2, 3, 4, 5, 8, 9],
    'c4_32': [1, 2, 3, 4, 5, 8, 9],
    'c4_33a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_34': [0, 1, 8, 9],
    'c4_35': [0, 1, 8, 9],
    'c4_36': [0, 1, 8, 9],
    'c4_37a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c4_38': [0, 1, 8, 9],
    'c4_39': [0, 1, 8, 9],
    'c4_40': [0, 1, 8, 9],
    'c4_41': [0, 1, 8, 9],
    'c4_42': [0, 1, 8, 9],
    'c4_43': [0, 1, 8, 9],
    'c4_44': [0, 1, 8, 9],
    'c4_46': [0, 1, 8, 9],
    'c4_47_1': [0, 1, 8, 9],
    'c4_47_2': [0, 1, 8, 9],
    'c4_47_3': [0, 1, 8, 9],
    'c4_47_4': [0, 1, 8, 9],
    'c4_47_5': [0, 1, 8, 9],
    'c4_47_6': [0, 1, 8, 9],
    'c4_47_7': [0, 1, 8, 9],
    'c4_47_8a': [0, 1, 8, 9],
    'c4_47_9': [0, 1, 8, 9],
    'c4_47_10': [0, 1, 8, 9],
    'c4_47_11': [0, 1, 8, 9],
    'c4_48': [0, 1, 8, 9],
    'c4_49a': [1, 2, 3, 4, 5, 6, 8, 9],
    'c5_01': [0, 1, 8, 9],
    'c5_02_1': [0, 1, 8, 9],
    'c5_02_2': [0, 1, 8, 9],
    'c5_02_3': [0, 1, 8, 9],
    'c5_02_4': [0, 1, 8, 9],
    'c5_02_5': [0, 1, 8, 9],
    'c5_02_6': [0, 1, 8, 9],
    'c5_02_7': [0, 1, 8, 9],
    'c5_02_8': [0, 1, 8, 9],
    'c5_02_9': [0, 1, 8, 9],
    'c5_02_10': [0, 1, 8, 9],
    'c5_02_11a': [0, 1, 8, 9],
    'c5_02_12': [0, 1, 8, 9],
    'c5_02_13': [0, 1, 8, 9],
    'c5_02_14': [0, 1, 8, 9],
    'c5_04': [0, 1, 8, 9],
    'c5_05': [0, 1, 8, 9],
    'c5_06_1d': list(range(1, 31 + 1)) + [99],
    'c5_06_1m': list(range(1, 12 + 1)) + [99],
    'c5_06_1y': list(range(1900, MAX_YEAR)) + [9999],
    'c5_06_2d ': list(range(1, 31 + 1)) + [99],
    'c5_06_2m': list(range(1, 12 + 1)) + [99],
    'c5_06_2y': list(range(1900, MAX_YEAR)) + [9999],
    'c5_07_1a': [1, 2, 8, 9],
    'c5_07_2a': [1, 2, 8, 9],
    'c5_08d': list(range(1, 31 + 1)) + [99],
    'c5_08m': list(range(1, 12 + 1)) + [99],
    'c5_08y': list(range(1900, MAX_YEAR)) + [9999],
    'c5_10': [0, 1, 8, 9],
    'c5_11': [0, 1, 8, 9],
    'c5_17': [0, 1, 8, 9],
    'c5_18': [0, 1, 8, 9],
    'c5_19': [0, 1, 8, 9]
}

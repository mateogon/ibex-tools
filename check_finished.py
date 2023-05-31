
def find_single_execution(log_str):
    import re
    from collections import Counter

    # Regular expression pattern for matching filenames
    pattern = r'(Starting|Finished) execution for: (\S+)'

    # Find all filenames
    filenames = re.findall(pattern, log_str)

    # Count occurrences
    counter = Counter(name for status, name in filenames)

    # Find and return filenames that only appear once
    single_occurrences = [name for name, count in counter.items() if count == 1]
    
    return single_occurrences

# Use the function
log_str = """"
Starting execution for: ackley_5 (1 out of 101)
Starting execution for: ex3_1_3 (2 out of 101)
Starting execution for: ex8_1_1 (3 out of 101)
Starting execution for: ex9_2_5 (4 out of 101)
Finished execution for: ex8_1_1
Finished execution for: ex3_1_3
Starting execution for: chance (5 out of 101)
Starting execution for: ex3_1_3bis (6 out of 101)
Finished execution for: chance
Starting execution for: ex8_1_2 (7 out of 101)
Finished execution for: ex3_1_3bis
Finished execution for: ex9_2_5
Starting execution for: ex9_2_6 (8 out of 101)
Finished execution for: ackley_5
Starting execution for: ex14_1_1 (9 out of 101)
Finished execution for: ex8_1_2
Starting execution for: ex3_1_4 (10 out of 101)
Starting execution for: ex8_1_4 (11 out of 101)
Finished execution for: ex14_1_1
Starting execution for: ex9_2_7 (12 out of 101)
Finished execution for: ex3_1_4
Starting execution for: ex14_1_2 (13 out of 101)
Finished execution for: ex8_1_4
Starting execution for: ex4_1_5 (14 out of 101)
Finished execution for: ex9_2_6
Starting execution for: ex8_1_5 (15 out of 101)
Finished execution for: ex9_2_7
Starting execution for: ex9_2_8 (16 out of 101)
Starting execution for: ex14_1_3 (17 out of 101)
Finished execution for: ex4_1_5
Finished execution for: ex8_1_5
Finished execution for: ex9_2_8
Starting execution for: ex4_1_8 (18 out of 101)
Starting execution for: ex8_1_6 (19 out of 101)
Finished execution for: ex4_1_8
Finished execution for: ex14_1_3
Starting execution for: exbaron (20 out of 101)
Starting execution for: ex14_1_4 (21 out of 101)
Finished execution for: exbaron
Finished execution for: ex8_1_6
Starting execution for: ex4_1_9 (22 out of 101)
Starting execution for: ex8_1_6bis (23 out of 101)
Finished execution for: ex14_1_4
Starting execution for: exinfinity2 (24 out of 101)
Finished execution for: ex4_1_9
Starting execution for: ex14_1_5 (25 out of 101)
Finished execution for: exinfinity2
Starting execution for: ex5_2_2_case1 (26 out of 101)
Finished execution for: ex8_1_6bis
Starting execution for: ex8_1_7 (27 out of 101)
Finished execution for: ex14_1_5
Starting execution for: exinfinity3 (28 out of 101)
Finished execution for: exinfinity3
Starting execution for: ex14_1_8 (29 out of 101)
Starting execution for: ex5_2_2_case2 (30 out of 101)
Finished execution for: ex14_1_8
Finished execution for: ex14_1_2
Starting execution for: ex8_1_8 (31 out of 101)
Starting execution for: exp40 (32 out of 101)
Finished execution for: ex8_1_8
Finished execution for: exp40
Starting execution for: ex14_1_9 (33 out of 101)
Finished execution for: ex14_1_9
Starting execution for: ex5_2_4 (34 out of 101)
Finished execution for: ex5_2_2_case2
Starting execution for: ex8_1_8bis (35 out of 101)
Finished execution for: ex5_2_2_case1
Starting execution for: f1 (36 out of 101)
Finished execution for: f1
Starting execution for: ex14_2_1 (37 out of 101)
Starting execution for: ex5_4_2 (38 out of 101)
Starting execution for: ex8_4inf-1 (39 out of 101)
Finished execution for: ex8_1_8bis
Finished execution for: ex5_2_4
Finished execution for: ex5_4_2
Starting execution for: griewank (40 out of 101)
Finished execution for: griewank
Starting execution for: ex14_2_2 (41 out of 101)
Finished execution for: ex14_2_2
Starting execution for: ex5_4_2bis (42 out of 101)
Starting execution for: ex8_5_3-1 (43 out of 101)
Finished execution for: ex8_4inf-1
Finished execution for: ex5_4_2bis
Starting execution for: himmel11 (44 out of 101)
Finished execution for: ex14_2_1
Finished execution for: ex8_1_7
Starting execution for: ex14_2_4 (45 out of 101)
Starting execution for: ex5_4_3 (46 out of 101)
Finished execution for: himmel11
Starting execution for: ex8_5_3 (47 out of 101)
Starting execution for: house (48 out of 101)
Starting execution for: ex14_2_5 (49 out of 101)
Starting execution for: ex6_1_2 (50 out of 101)
Finished execution for: house
Starting execution for: ex8_5_4 (51 out of 101)
Finished execution for: ex8_5_3-1
Finished execution for: ex6_1_2
Starting execution for: hs071 (52 out of 101)
Finished execution for: ex5_4_3
Starting execution for: ex14_2_6 (53 out of 101)
Starting execution for: ex7_2_10 (54 out of 101)
Finished execution for: ex8_5_3
Starting execution for: ex8_5_5-1 (55 out of 101)
Finished execution for: ex7_2_10
Starting execution for: m4wd (56 out of 101)
Finished execution for: ex14_2_5
Starting execution for: ex14_2_8 (57 out of 101)
Finished execution for: hs071
Finished execution for: ex8_5_5-1
Starting execution for: ex7_2_1 (58 out of 101)
Starting execution for: ex8_5_5 (59 out of 101)
Finished execution for: ex14_2_4
Finished execution for: ex14_2_6
Starting execution for: pressure-vessel (60 out of 101)
Finished execution for: ex14_2_8
Finished execution for: pressure-vessel
Starting execution for: ex14_2_9 (61 out of 101)
Finished execution for: ex7_2_1
Starting execution for: ex7_2_1bis (62 out of 101)
Finished execution for: ex14_2_9
Starting execution for: ex8_5_6-1 (63 out of 101)
Finished execution for: m4wd
Finished execution for: ex7_2_1bis
Starting execution for: rastrigin (64 out of 101)
Starting execution for: ex2_1_10 (65 out of 101)
Finished execution for: ex8_5_4
Starting execution for: ex7_2_2 (66 out of 101)
Finished execution for: rastrigin
Starting execution for: ex9_1_10 (67 out of 101)
Starting execution for: rosenbrock10 (68 out of 101)
Finished execution for: ex8_5_6-1
Starting execution for: ex2_1_1 (69 out of 101)
Finished execution for: ex9_1_10
Starting execution for: ex7_2_3 (70 out of 101)
Starting execution for: ex9_1_1 (71 out of 101)
Finished execution for: ex2_1_1
Finished execution for: ex7_2_2
Starting execution for: rosenbrock (72 out of 101)
Finished execution for: ex9_1_1
Finished execution for: rosenbrock
Starting execution for: ex2_1_2 (73 out of 101)
Finished execution for: ex2_1_2
Starting execution for: ex7_2_3bis (74 out of 101)
Starting execution for: ex9_1_2 (75 out of 101)
Finished execution for: rosenbrock10
Starting execution for: schaffer (76 out of 101)
Finished execution for: ex9_1_2
Starting execution for: ex2_1_3 (77 out of 101)
Starting execution for: ex7_2_5 (78 out of 101)
Finished execution for: ex7_2_5
Finished execution for: ex8_5_5
Finished execution for: schaffer
Starting execution for: ex9_1_4 (79 out of 101)
Starting execution for: ship-1 (80 out of 101)
Finished execution for: ex9_1_4
Finished execution for: ex2_1_3
Starting execution for: ex2_1_4 (81 out of 101)
Finished execution for: ex2_1_4
Starting execution for: ex7_2_6 (82 out of 101)
Starting execution for: ex9_1_5 (83 out of 101)
Finished execution for: ex7_2_6
Finished execution for: ex2_1_10
Starting execution for: test_infinity1 (84 out of 101)
Starting execution for: ex2_1_5 (85 out of 101)
Starting execution for: ex7_2_7 (86 out of 101)
Finished execution for: ex9_1_5
Finished execution for: ex7_2_3bis
Starting execution for: ex9_1_8 (87 out of 101)
Finished execution for: ex7_2_7
Finished execution for: ex2_1_5
Starting execution for: test_infinity2 (88 out of 101)
Finished execution for: ex9_1_8
Finished execution for: test_infinity1
Finished execution for: test_infinity2
Starting execution for: ex2_1_5bis (89 out of 101)
Starting execution for: ex7_3_1 (90 out of 101)
Finished execution for: ex2_1_5bis
Starting execution for: ex9_2_1 (91 out of 101)
Starting execution for: wall (92 out of 101)
Finished execution for: ex9_2_1
Starting execution for: ex2_1_6 (93 out of 101)
Finished execution for: wall
Finished execution for: ex7_3_1
Starting execution for: ex7_3_2 (94 out of 101)
Starting execution for: ex9_2_2 (95 out of 101)
Finished execution for: ex9_2_2
Starting execution for: ex3_1_1 (96 out of 101)
Starting execution for: ex7_3_3 (97 out of 101)
Starting execution for: ex9_2_3 (98 out of 101)
Starting execution for: ex3_1_2 (99 out of 101)
Finished execution for: ex3_1_2
Starting execution for: ex7_3_6 (100 out of 101)
Finished execution for: ex7_3_2
Finished execution for: ex9_2_3
Starting execution for: ex9_2_4 (101 out of 101)
Finished execution for: ex9_2_4
Finished execution for: ex3_1_1
Finished execution for: ex7_3_3
Finished execution for: ex7_3_6
Finished execution for: ex2_1_6"""  # Insert your log string here
print(find_single_execution(log_str))

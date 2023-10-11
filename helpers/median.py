def median(values):
    num_vals = len(values)
    values_sorted = sorted(values)
    indx = num_vals // 2
    if num_vals % 2 == 1:
        return values_sorted[indx]
    else:
        mean_val = 0.5 * (values_sorted[indx] + values_sorted[indx + 1])
        return mean_val

def minWindow(s1: str, s2: str) -> str:
    n, m = len(s1), len(s2)
    min_len = float('inf')
    start_idx = -1

    i = 0
    while i < n:
        if s1[i] == s2[0]:
            j = i
            k = 0
            while j < n and k < m:
                if s1[j] == s2[k]:
                    k += 1
                j += 1

            if k == m:
                end = j - 1

                k = m - 1
                j = end
                while j >= i:
                    if s1[j] == s2[k]:
                        k -= 1
                        if k < 0:
                            break
                    j -= 1

                start = j
                window_len = end - start + 1

                if window_len < min_len:
                    min_len = window_len
                    start_idx = start

                i = start + 1
                continue
        i += 1

    return "" if start_idx == -1 else s1[start_idx:start_idx + min_len]
    

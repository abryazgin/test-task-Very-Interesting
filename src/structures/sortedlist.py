def insort(a, x, lo=0, hi=None, key=lambda x: x):
    """
    copied from bisect.insort
    ```
    Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    ```
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if key(x) < key(a[mid]): hi = mid
        else: lo = mid+1
    a.insert(lo, x)

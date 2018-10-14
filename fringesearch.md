



# Data Base Points

SNR : 4 SNR per telescope   written by rtdscope
Scan counter :   written by rtdscope
Movement counter :  written by the fringe search process 


# rtdscope process (search mode)

- wait that DLs have moved (from Movement counter)
- make one scan
- If SNR>2:
    + Center the fringes (internal piezzo)
    + new scan
    + Compute a good SNR
    + Increment Scan counter
- Else:
    + Increment Scan counter

# search scan process 

- move one DL
- increment Movement counter 
- Wait for new scan from rtdscope (Scan Counter)
- check SNR (from rtdscope)
- If good SNR:
    + Change DL





| Process search |  pndrtdscope   |
|----------------|----------------|
|                | 1/ compute SNR |
|                |    No fringes:   |
|                |                |
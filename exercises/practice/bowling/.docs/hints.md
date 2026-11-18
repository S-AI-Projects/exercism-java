## Debugging Hint

When scoring a strike, the bonus is the total of the **next two rolls** — not the next two *frames*.

A common mistake is to assume that after two consecutive strikes, the bonus for the first strike is `10 + 10 = 20`. This is **wrong**: the second ball of the bonus for the first strike is the *first roll of the third frame*, not 10 (the second strike).

**Diagnostic input to test your understanding:**

Roll three strikes then knock down 5 and 3:

```
Frame 1: X (strike)
Frame 2: X (strike)
Frame 3: X (strike)
Frame 4: 5, 3
...rest zeros...
```

Frame 1 score = 10 + (next two rolls) = 10 + 10 + 10 = 30  
Frame 2 score = 10 + (next two rolls) = 10 + 10 + 5 = 25  
Frame 3 score = 10 + (next two rolls) = 10 + 5 + 3 = 18  
Frame 4 score = 5 + 3 = 8  

Total = 30 + 25 + 18 + 8 = 81

If your code returns a different number, check how you look up the second bonus roll after a strike — specifically when the **immediately following frame is also a strike**.

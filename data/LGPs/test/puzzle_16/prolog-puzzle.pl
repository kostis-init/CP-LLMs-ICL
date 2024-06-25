all_members([H], L) :- member(H, L).
all_members([H|T], L) :- member(H, L), all_members(T, L).

all_not_members([H], L) :- not(member(H, L)).
all_not_members([H|T], L) :- not(member(H, L)), all_not_members(T, L).

and([H]) :- H.
and([H|T]) :- H, and(T).

or([H]) :- H, !.
or([H|_]) :- H, !.
or([_|T]) :- or(T).

solve(B0,B1,B2,B3) :-
B0 = [A0, C0],
B1 = [A1, C1],
B2 = [A2, C2],
B3 = [A3, C3],

All = [B0,B1,B2,B3],

all_members([c0, c1, c2, c3], [C0, C1, C2, C3]),
all_members([1, 2, 3, 4], [A0, A1, A2, A3]),
member([3, c2], All),
and([or([member([4, c0], All),member([4, c3], All)]), not(and([member([4, c0], All),member([4, c3], All)]))]),
or([and([member([2, c1], All),C2 = c3]),and([C2 = c1,member([2, c3], All)])]),
A0 = 2,
member([C1_val, c1], All),
C1_val-A1=:=1.
